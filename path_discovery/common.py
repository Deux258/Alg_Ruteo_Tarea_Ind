from __future__ import annotations

import csv
import hashlib
import ipaddress
import json
import os
import shutil
import shlex
import subprocess
import time
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
TRACE_METHODS = ("udp", "icmp", "udp-paris", "icmp-paris", "tcp", "tcp-ack")
LB_METHODS = ("udp-dport", "icmp-echo", "udp-sport", "tcp-sport", "tcp-ack-sport")
RIPE_METHODS = ("UDP", "ICMP", "TCP")


def utc():
    return datetime.now(timezone.utc).isoformat()


def identifier():
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S") + "_" + uuid.uuid4().hex[:8]


def config():
    cfg = json.loads((ROOT / "config/campana.json").read_text())
    local = ROOT / "config/local.json"
    if local.exists():
        cfg.update(json.loads(local.read_text()))
    if cfg["rounds"] != 3 or not 1 <= cfg["pps"] <= 20:
        raise ValueError("La campaña exige tres rondas y una tasa de 1 a 20 pps")
    if len(cfg["targets"]) != 3 or len({t["ip"] for t in cfg["targets"]}) != 3:
        raise ValueError("Se requieren tres destinos distintos")
    if cfg["udp_base_port"] is not None and not 1 <= int(cfg["udp_base_port"]) <= 65535:
        raise ValueError("Puerto UDP fuera de rango")
    for t in cfg["targets"]:
        ipaddress.IPv4Address(t["ip"])
        if not isinstance(t["probe_id"], int):
            raise ValueError("probe_id debe ser entero")
    return cfg


def json_write(path, obj, *, exclusive=False):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x" if exclusive else "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write("\n")


def sha256(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def save_manifest(folder, metadata):
    folder = Path(folder)
    metadata = {**metadata, "sealed_at": utc(), "sha256": {
        str(p.relative_to(folder)): sha256(p) for p in sorted(folder.rglob("*"))
        if p.is_file() and p.name != "manifest.json"
    }}
    json_write(folder / "manifest.json", metadata, exclusive=True)
    return metadata


def verify_manifest(folder):
    folder = Path(folder)
    m = json.loads((folder / "manifest.json").read_text())
    for name, expected in m["sha256"].items():
        path = (folder / name).resolve()
        if not path.is_relative_to(folder.resolve()) or not path.is_file() or sha256(path) != expected:
            raise ValueError(f"Original alterado o ausente: {folder.name}/{name}")
    return m


def records(path):
    text = Path(path).read_text()
    try:
        obj = json.loads(text)
        return obj if isinstance(obj, list) else [obj]
    except json.JSONDecodeError:
        return [json.loads(line) for line in text.splitlines() if line.strip()]


def csv_write(path, rows, fields=None):
    rows = list(rows)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = fields or list(dict.fromkeys(k for row in rows for k in row))
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def request_json(url, body=None, *, headers=None, method=None):
    """GET: reintentos limitados. POST: nunca se reenvía automáticamente."""
    data = None if body is None else json.dumps(body).encode()
    hdr = {"User-Agent": "PathDiscovery-Academic/0.1", **(headers or {})}
    if data is not None:
        hdr["Content-Type"] = "application/json"
    req = Request(url, data=data, headers=hdr, method=method)
    for attempt in range(3 if req.get_method() == "GET" else 1):
        try:
            with urlopen(req, timeout=30) as response:
                raw = response.read()
                return json.loads(raw) if raw.strip() else None
        except HTTPError as e:
            # No incluir URL ni encabezados: pueden contener credenciales.
            if req.get_method() == "GET" and e.code in (429, 502, 503, 504) and attempt < 2:
                time.sleep(min(5, int(e.headers.get("Retry-After", "2")) if e.headers.get("Retry-After", "2").isdigit() else 2))
                continue
            raise RuntimeError(f"HTTP {e.code} al consultar servicio externo") from None
        except (URLError, TimeoutError, OSError):
            if req.get_method() == "GET" and attempt < 2:
                time.sleep(1)
                continue
            raise RuntimeError("Servicio externo inaccesible; comprobar red/DNS. No se reintentó ningún POST.") from None


def egress_observations():
    ipify = request_json("https://api.ipify.org?format=json&_pd=" + identifier(), headers={"Cache-Control": "no-cache"})["ip"]
    try:
        with urlopen(Request("https://checkip.amazonaws.com", headers={"Cache-Control": "no-cache"}), timeout=20) as response:
            amazon = response.read().decode().strip()
    except (URLError, OSError):
        raise RuntimeError("No se pudo corroborar la IPv4 con el segundo servicio") from None
    return {"ipify": ipify, "checkip_amazon": amazon}


def public_ip(observations=None):
    observations = observations or egress_observations()
    if len(set(observations.values())) != 1:
        raise RuntimeError("Los servicios de IP discrepan: " + json.dumps(observations) + "; comprobar salida BAF")
    value = next(iter(observations.values()))
    ip = ipaddress.IPv4Address(value)
    if not ip.is_global:
        raise ValueError("El servicio no entregó una IPv4 pública")
    return value


def command(args, **kwargs):
    return subprocess.run([str(a) for a in args], capture_output=True, text=True, check=True, **kwargs)


def load_credentials():
    """Leer solo claves conocidas como datos; nunca ejecutar contenido de .env."""
    path = ROOT / ".env"
    if not path.exists():
        return
    allowed = {"RIPE_ATLAS_API_KEY", "NDEX_USERNAME", "NDEX_PASSWORD"}
    for line in path.read_text().splitlines():
        line = line.strip()
        if line.startswith("export "):
            line = line[7:].lstrip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        name, value = line.split("=", 1)
        name = name.strip()
        if name not in allowed:
            continue
        try:
            tokens = shlex.split(value, comments=True, posix=True)
        except ValueError:
            raise ValueError("Formato de credencial inválido en .env; revisar comillas localmente") from None
        if len(tokens) > 1:
            raise ValueError("En .env, escribir las credenciales que contienen espacios entre comillas")
        value = tokens[0] if tokens else ""
        if value and not os.environ.get(name):
            os.environ[name] = value


def compose_command(*args):
    return ["docker", "compose", "--env-file", "/dev/null", "--project-directory", str(ROOT),
            "-f", str(ROOT / "compose.yaml"), *map(str, args)]


def tool_command(tool, args=(), *, cfg=None, name=None):
    cfg = cfg or config()
    if os.environ.get("PD_NATIVE") == "1":
        binary = ROOT / ".tools/bin" / tool
        return [str(binary) if binary.exists() else tool, *map(str, args)]
    cmd = ["env", "PD_TOOL_IMAGE=" + cfg["tool_image"], *compose_command("run", "--rm", "--no-deps", "-T", "--interactive=false", "--pull", "never", "--quiet-pull")]
    if name:
        cmd += ["--name", name]
    return cmd + ["tools", tool, *map(str, args)]


def work_path(path):
    path = Path(path).resolve()
    return str(path) if os.environ.get("PD_NATIVE") == "1" else "/work/" + str(path.relative_to(ROOT))


@contextmanager
def campaign_lock():
    import fcntl
    path = ROOT / ".state/campaign.lock"
    path.parent.mkdir(exist_ok=True)
    with path.open("w") as f:
        try:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError("Ya existe una medición/campaña local en ejecución") from None
        yield


def clone_sources():
    from zipfile import ZipFile
    from xml.etree import ElementTree as ET
    folder = ROOT / "datos/originales/enunciado"
    if folder.exists():
        return verify_manifest(folder)
    folder.mkdir(parents=True)
    src = Path("/home/diego/Escritorio/Universidad/Semestre 10/Algoritmos de Ruteo/Tarea Individual/Tarea Individual.docx")
    shutil.copyfile(src, folder / src.name)
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    with ZipFile(src) as z:
        root = ET.fromstring(z.read("word/document.xml"))
        lines = ["".join(t.text or "" for t in p.findall(".//w:t", ns)) for p in root.findall(".//w:p", ns)]
    (folder / "enunciado.txt").write_text("\n".join(lines))
    return save_manifest(folder, {"kind": "source", "source": str(src), "created_at": utc()})
