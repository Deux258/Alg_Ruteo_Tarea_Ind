"""Adquisición con trazabilidad, capturas y solicitudes RIPE sin POST repetidos."""
from __future__ import annotations

import json
import os
import socket
import subprocess
import time
from pathlib import Path

from .common import (ROOT, TRACE_METHODS, LB_METHODS, RIPE_METHODS, campaign_lock,
                     command, config, identifier, json_write, public_ip, records,
                     request_json, save_manifest, tool_command, utc, work_path)
from .common import egress_observations, compose_command, sha256

ATLAS = "https://atlas.ripe.net/api/v2/"


def probe_info(pid):
    return request_json(f"{ATLAS}probes/{int(pid)}/")


def probe_issues(cfg, probes):
    issues = []
    for target in cfg["targets"]:
        probe = probes.get(str(target["probe_id"]), {})
        if probe.get("status", {}).get("id") != 1:
            issues.append(f"Sonda {target['probe_id']} no conectada: {probe.get('status', {}).get('name', 'desconocido')}")
        if probe.get("address_v4") != target["ip"]:
            issues.append(f"Sonda {target['probe_id']}: IP actual {probe.get('address_v4')} difiere de {target['ip']}")
    return issues


def preflight():
    cfg = config()
    folder = ROOT / "datos/originales" / ("preflight_" + identifier())
    folder.mkdir(parents=True)
    evidence = {"created_at": utc(), "kind": "preflight", "checks": {}, "blockers": []}
    for tool in ("scamper", "tshark", "dumpcap"):
        try:
            result = command(tool_command(tool, ["-v"], cfg=cfg), timeout=30)
            evidence["checks"][tool] = (result.stdout + result.stderr).strip()[:3000]
        except (subprocess.SubprocessError, OSError):
            evidence["blockers"].append(f"No se pudo ejecutar {tool}")
    if cfg["scamper_version"] not in evidence["checks"].get("scamper", ""):
        evidence["blockers"].append("Versión de Scamper no acreditada")
    try:
        route = json.loads(command(["ip", "-j", "route", "get", "1.1.1.1"]).stdout)[0]
        evidence["route"] = route
        if any(word in route.get("dev", "").lower() for word in ("tun", "wg", "tailscale", "ppp", "vpn")):
            evidence["blockers"].append("Interfaz de túnel detectada; confirmar salida BAF")
    except (OSError, subprocess.SubprocessError, ValueError, IndexError):
        evidence["blockers"].append("No se pudo identificar la interfaz de salida")
    try:
        evidence["clock_synced"] = command(["timedatectl", "show", "-p", "NTPSynchronized", "--value"]).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        evidence["clock_synced"] = "no comprobado"
    evidence["proxy_variables_present"] = [k for k in ("HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY") if os.environ.get(k)]
    try:
        evidence["egress_observations"] = egress_observations()
        ip = public_ip(evidence["egress_observations"])
        evidence["public_ipv4"] = ip
        net = request_json(f"https://stat.ripe.net/data/network-info/data.json?resource={ip}")
        json_write(folder / "network-info.json", net, exclusive=True)
        evidence["prefix"] = net["data"]["prefix"]
        evidence["asns"] = net["data"]["asns"]
        evidence["bgp_he_url"] = f"https://bgp.he.net/ip/{ip}"
        evidence["nat"] = "posible NAT; CGNAT requiere comprobar la WAN del router" if evidence.get("route", {}).get("prefsrc") != ip else "sin NAT observado entre origen y servicio"
    except (RuntimeError, ValueError, KeyError) as e:
        evidence["blockers"].append("No se pudo caracterizar una IPv4 pública consistente: " + str(e))
    probes = {}
    for target in cfg["targets"]:
        try:
            pid = target["probe_id"]
            probes[str(pid)] = probe_info(pid)
            json_write(folder / f"probe_{pid}.json", probes[str(pid)], exclusive=True)
        except RuntimeError:
            evidence["blockers"].append(f"API de sonda {target['probe_id']} inaccesible")
    evidence["blockers"] += probe_issues(cfg, probes)
    if not cfg["local_probe_id"]:
        evidence["blockers"].append("Falta registrar y configurar local_probe_id")
    else:
        local = probe_info(cfg["local_probe_id"])
        json_write(folder / "local_probe.json", local, exclusive=True)
        if local.get("status", {}).get("id") != 1 or local.get("address_v4") != evidence.get("public_ipv4"):
            evidence["blockers"].append("Sonda local desconectada o en otra IPv4 pública")
    if cfg["udp_base_port"] is None:
        evidence["blockers"].append("Falta validar udp_base_port desde piloto RIPE/PCAP")
    if not os.environ.get("RIPE_ATLAS_API_KEY"):
        evidence["blockers"].append("Falta RIPE_ATLAS_API_KEY en el entorno local")
    evidence["isp_comercial"] = cfg["isp_comercial"]
    evidence["cg_nat_confirmado"] = cfg.get("cg_nat_confirmado", "pendiente")
    evidence["baf_confirmada_por_usuario"] = cfg.get("baf_confirmed", False)
    if not evidence["baf_confirmada_por_usuario"]:
        evidence["blockers"].append("Confirmar BAF del domicilio en config/local.json antes de medir")
    json_write(folder / "preflight.json", evidence, exclusive=True)
    save_manifest(folder, evidence)
    return folder, evidence


class Capture:
    def __init__(self, folder, interface, destination, cfg):
        self.folder, self.cfg = Path(folder), cfg
        self.name = "pd-cap-" + identifier().lower()
        self.path = self.folder / "capture.pcapng"
        self.log = (self.folder / "capture.log").open("w")
        self.output = self.path.open("xb")
        self.cmd = tool_command("dumpcap", ["-i", interface, "-s", "0", "-f",
                    f"icmp or host {destination}", "-w", "-"], cfg=cfg, name=self.name)
        self.process = subprocess.Popen(self.cmd, stdout=self.output, stderr=self.log)
        for _ in range(100):
            if self.process.poll() is not None:
                self.log.close()
                self.output.close()
                raise RuntimeError("Dumpcap no inició; revisar capture.log")
            if "File:" in (self.folder / "capture.log").read_text(errors="replace"):
                return
            time.sleep(0.2)
        self.stop()
        raise RuntimeError("Dumpcap no confirmó captura en 20 segundos")

    def stop(self):
        if self.process.poll() is None:
            if os.environ.get("PD_NATIVE") == "1":
                self.process.terminate()
            else:
                subprocess.run(["docker", "stop", "--timeout", "5", self.name], capture_output=True, timeout=15)
            self.process.wait(timeout=15)
        self.log.close()
        self.output.close()


def interface(cfg):
    if cfg["interface"]:
        return cfg["interface"]
    return json.loads(command(["ip", "-j", "route", "get", "1.1.1.1"]).stdout)[0]["dev"]


def scamper_args(cfg, family, method, dest, output):
    allowed = TRACE_METHODS if family == "trace" else LB_METHODS
    if family not in ("trace", "tracelb") or method not in allowed:
        raise ValueError("Método Scamper inválido")
    spec = [family, "-P", method]
    if method.startswith("tcp"):
        spec += ["-d", str(cfg["tcp_port"])]
        if cfg.get("tcp_source_port") is not None:
            sport = int(cfg["tcp_source_port"])
            if not 1 <= sport <= 65535:
                raise ValueError("Puerto TCP de origen fuera de rango")
            spec += ["-s", str(sport)]
    elif method.startswith("udp") and cfg["udp_base_port"] is not None:
        spec += ["-d", str(int(cfg["udp_base_port"]))]
    raw_options = ["-O", "rawtcp"] if cfg.get("diagnostic_raw_tcp") and method.startswith("tcp") else []
    return [*raw_options, "-p", str(cfg["pps"]), "-w", "1", "-O", "warts", "-o", "-" if str(output) == "-" else work_path(output), "-c", " ".join(spec), "-i", dest]


def measure_scamper(cfg, target, family, method, round_no, *, pilot=False, kind="measurement"):
    if not cfg.get("baf_confirmed"):
        raise RuntimeError("Mediciones pendientes: confirmar conexión BAF de casa antes de lanzar un piloto")
    folder = ROOT / "datos/originales" / ("scamper_" + identifier())
    folder.mkdir(parents=True)
    meta = {"kind": kind, "tool": "scamper", "family": family, "method": method,
            "round": round_no, "direction": "ida", "target": target["ip"], "probe_id": None,
            "destination": target["ip"], "started_at": utc(), "pilot": pilot, "config": cfg}
    cap = None
    try:
        meta["public_ipv4"] = public_ip()
        meta["tool_image_id"] = command(["docker", "image", "inspect", "--format", "{{.Id}}", cfg["tool_image"]]).stdout.strip() if os.environ.get("PD_NATIVE") != "1" else "native"
        meta["version"] = command(tool_command("scamper", ["-v"], cfg=cfg)).stdout.strip()
        if cfg["scamper_version"] not in meta["version"]:
            raise RuntimeError("Versión Scamper incorrecta")
        cap = Capture(folder, interface(cfg), target["ip"], cfg)
        args = scamper_args(cfg, family, method, target["ip"], "-")
        meta["command"] = tool_command("scamper", args, cfg=cfg)
        with (folder / "result.warts").open("xb") as out, (folder / "stderr.txt").open("x") as err:
            proc = subprocess.run(meta["command"], stdout=out, stderr=err, timeout=3600)
        if proc.returncode:
            raise RuntimeError(f"Scamper terminó con código {proc.returncode}")
        cap.stop()
        cap = None
        result = command(tool_command("sc_warts2json", [work_path(folder / "result.warts")], cfg=cfg))
        (folder / "result.jsonl").write_text(result.stdout)
        original = [x for x in records(folder / "result.jsonl") if x.get("type") == family]
        if len(original) != 1 or original[0].get("dst") != target["ip"]:
            raise RuntimeError("WARTS no contiene exactamente la medición pedida")
        meta["status"] = "completed"
        meta["stop_reason"] = original[0].get("stop_reason")
        meta["public_ipv4_after"] = public_ip()
        if meta["public_ipv4_after"] != meta["public_ipv4"]:
            meta["status"] = "invalid_public_ip_changed"
    except Exception as e:
        meta["status"] = "failed"
        meta["error"] = str(e) if isinstance(e, (RuntimeError, ValueError)) else type(e).__name__
    finally:
        if cap:
            cap.stop()
        meta["finished_at"] = utc()
        json_write(folder / "metadata.json", meta, exclusive=True)
        save_manifest(folder, meta)
    if meta["status"] != "completed":
        raise RuntimeError(f"Medición no válida ({folder.name}): {meta.get('error', meta['status'])}")
    return folder


def ripe_body(cfg, target, protocol, direction, source_ip):
    if protocol not in RIPE_METHODS or direction not in ("ida", "vuelta"):
        raise ValueError("Protocolo/sentido RIPE inválido")
    pid = cfg["local_probe_id"] if direction == "ida" else target["probe_id"]
    if not pid:
        raise ValueError("Falta local_probe_id")
    definition = {"target": target["ip"] if direction == "ida" else source_ip,
                  "description": f"PathDiscovery {target['label']} {direction} {protocol}",
                  "type": "traceroute", "af": 4, "protocol": protocol}
    if protocol == "TCP":
        definition["port"] = cfg["tcp_port"]
    return {"definitions": [definition], "probes": [{"requested": 1, "type": "probes", "value": str(pid)}], "is_oneoff": True}


def fetch_ripe(folder, *, wait_seconds=300):
    folder = Path(folder)
    # Recuperar un POST de resultado incierto requiere fijar measurement_id manualmente,
    # nunca crear otra medición automáticamente.
    meta = json.loads((folder / "pending.json").read_text())
    mid = meta.get("measurement_id")
    if not mid:
        raise RuntimeError("POST sin ID confirmado: buscar en el panel RIPE antes de reintentar")
    deadline = time.monotonic() + wait_seconds
    while True:
        result = request_json(f"{ATLAS}measurements/{mid}/results/")
        valid = [r for r in result if r.get("prb_id") == meta["probe_id"] and r.get("msm_id") == mid]
        if valid:
            json_write(folder / "results.json", result, exclusive=True)
            definition = request_json(f"{ATLAS}measurements/{mid}/")
            json_write(folder / "definition.json", definition, exclusive=True)
            expected = meta["destination"]
            matching = [r for r in valid if r.get("dst_addr") == expected and r.get("result") and not r.get("error")]
            meta["status"] = "completed" if matching else "failed_result"
            meta["finished_at"] = utc()
            meta["public_ipv4_after"] = public_ip()
            if meta["public_ipv4_after"] != meta["public_ipv4"]:
                meta["status"] = "invalid_public_ip_changed"
            json_write(folder / "metadata.json", meta, exclusive=True)
            return meta
        if time.monotonic() >= deadline:
            raise RuntimeError(f"Sin resultado RIPE para {mid}; usar ripe-fetch {folder.name}; no repetir POST")
        time.sleep(5)


def measure_ripe(cfg, target, protocol, direction, round_no, *, pilot=False, wait_seconds=300, kind="measurement"):
    if not cfg.get("baf_confirmed"):
        raise RuntimeError("Mediciones pendientes: confirmar conexión BAF de casa")
    key = os.environ.get("RIPE_ATLAS_API_KEY")
    if not key:
        raise RuntimeError("Configurar RIPE_ATLAS_API_KEY en el entorno local")
    ip = public_ip()
    local = probe_info(cfg["local_probe_id"])
    remote = probe_info(target["probe_id"])
    issues = probe_issues({"targets": [target]}, {str(target["probe_id"]): remote})
    if local.get("status", {}).get("id") != 1 or local.get("address_v4") != ip:
        issues.append("La sonda local no corresponde a la BAF actual")
    if issues:
        raise RuntimeError("; ".join(issues))
    body = ripe_body(cfg, target, protocol, direction, ip)
    folder = ROOT / "datos/originales" / ("ripe_" + identifier())
    folder.mkdir(parents=True)
    meta = {"kind": kind, "tool": "ripe", "family": "traceroute", "method": protocol,
            "round": round_no, "direction": direction, "target": target["ip"],
            "public_ipv4": ip, "probe_id": int(body["probes"][0]["value"]),
            "destination": body["definitions"][0]["target"], "started_at": utc(),
            "pilot": pilot, "status": "pending", "config": cfg}
    json_write(folder / "request.json", body, exclusive=True)
    json_write(folder / "pending.json", meta, exclusive=True)
    cap = Capture(folder, interface(cfg), target["ip"], cfg)
    try:
        response = request_json(ATLAS + "measurements/", body,
                                headers={"Authorization": "Key " + key})
        json_write(folder / "created.json", response, exclusive=True)
        ids = response.get("measurements", [])
        if len(ids) != 1:
            raise RuntimeError("RIPE no devolvió exactamente un measurement_id")
        meta["measurement_id"] = int(ids[0])
        json_write(folder / "pending.json", meta)
        fetch_ripe(folder, wait_seconds=wait_seconds)
    finally:
        cap.stop()
        save_manifest(folder, meta)
    return folder


def plan_jobs(cfg):
    jobs = []
    for round_no in range(1, cfg["rounds"] + 1):
        for t in cfg["targets"]:
            for method in TRACE_METHODS:
                jobs.append({"round": round_no, "target": t["ip"], "tool": "scamper", "family": "trace", "method": method, "direction": "ida"})
            for method in LB_METHODS:
                jobs.append({"round": round_no, "target": t["ip"], "tool": "scamper", "family": "tracelb", "method": method, "direction": "ida"})
            for method in RIPE_METHODS:
                for direction in ("ida", "vuelta"):
                    jobs.append({"round": round_no, "target": t["ip"], "tool": "ripe", "family": "traceroute", "method": method, "direction": direction})
    return jobs


def init_probe():
    """Reutilizar identidad persistente y migrar contenedor detenido a Compose."""
    state = ROOT / ".state"
    state.mkdir(exist_ok=True)
    name = "path-discovery-atlas"
    inspected = subprocess.run(["docker", "inspect", name], capture_output=True, text=True)
    old = json.loads(inspected.stdout)[0] if inspected.returncode == 0 else None
    legacy = None
    volumes = {"pd-atlas-etc", "pd-atlas-run", "pd-atlas-spool"}
    if old and (old["Config"].get("Labels") or {}).get("com.docker.compose.project") != "path-discovery":
        actual = {v.get("Name") for v in old["Mounts"] if v["Type"] == "volume"}
        if not volumes.issubset(actual):
            raise RuntimeError("El contenedor previo no usa los volúmenes esperados; no se migrará")
        if old["State"]["Running"]:
            raise RuntimeError("Detener la sonda previa antes de migrarla a Compose")
        legacy = name + "-legacy-" + identifier().lower()
        json_write(state / ("probe_migration_" + identifier() + ".json"),
                   {"old_container_id": old["Id"], "legacy_name": legacy, "volumes": sorted(volumes), "created_at": utc()}, exclusive=True)
        command(["docker", "rename", name, legacy])
    # Para una instalación nueva se crean los volúmenes; nunca se eliminan.
    for volume in sorted(volumes):
        command(["docker", "volume", "create", volume])
    for port in (12023, 18080):
        if not old or not old["State"]["Running"]:
            with socket.socket() as s:
                s.bind(("127.0.0.1", port))
    key_path = ROOT / "resultados/sonda_clave_publica.txt"
    previous_key = key_path.read_text().strip() if key_path.exists() else None
    command(compose_command("up", "-d", "--no-deps", "atlas"), timeout=120)
    info = json.loads(command(["docker", "inspect", name]).stdout)[0]
    json_write(state / "probe_image.json", {"image": info["Config"]["Image"], "container_id": info["Id"], "created_at": utc(), "manager": "docker-compose", "legacy_container": legacy})
    for _ in range(30):
        result = subprocess.run(["docker", "exec", "path-discovery-atlas", "cat", "/etc/ripe-atlas/probe_key.pub"], capture_output=True, text=True)
        if result.returncode == 0 and result.stdout.strip():
            if previous_key and previous_key != result.stdout.strip():
                command(compose_command("stop", "atlas"))
                raise RuntimeError("Cambió la clave pública; sonda detenida y archivo previo conservado")
            key_path.parent.mkdir(exist_ok=True)
            if not previous_key:
                key_path.write_text(result.stdout)
            return {"image": info["Config"]["Image"], "manager": "docker-compose", "identity_preserved": bool(previous_key),
                    "public_key_sha256": sha256(key_path), "public_key_file": "resultados/sonda_clave_publica.txt", "register_url": "https://atlas.ripe.net/apply/swprobe/"}
        time.sleep(1)
    raise RuntimeError("Contenedor creado; clave pública aún no disponible. Consultar docker logs path-discovery-atlas")
