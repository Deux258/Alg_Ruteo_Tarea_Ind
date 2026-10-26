#!/usr/bin/env python3
"""Configuración interactiva local; nunca imprime la API key."""
import argparse
import getpass
import json
import os
import re
import sys
import tempfile
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def configure():
    if not sys.stdin.isatty():
        raise RuntimeError(
            "Ejecutar en una terminal interactiva del equipo, sin pegar la clave en el chat"
        )
    probe_id = int(input("ID numérico de tu sonda RIPE: ").strip())
    if probe_id <= 0:
        raise ValueError("ID de sonda inválido")
    isp = input("Proveedor comercial de tu conexión fija (ISP): ").strip()
    if not isp:
        raise ValueError("Indicar el ISP comercial")
    key = str(uuid.UUID(getpass.getpass("API key RIPE (entrada oculta): ").strip()))
    cfg_path = ROOT / "config/local.json"
    cfg = json.loads(cfg_path.read_text()) if cfg_path.exists() else {}
    cfg.update(local_probe_id=probe_id, isp_comercial=isp)
    env_path = ROOT / ".env"
    lines = env_path.read_text().splitlines() if env_path.exists() else []
    lines = [
        line
        for line in lines
        if not re.match(r"\s*(?:export\s+)?RIPE_ATLAS_API_KEY\s*=", line)
    ]
    lines.append("RIPE_ATLAS_API_KEY=" + key)
    with tempfile.NamedTemporaryFile(
        mode="w", dir=ROOT, prefix=".env.", delete=False
    ) as f:
        temp = Path(f.name)
        f.write("\n".join(lines) + "\n")
    os.chmod(temp, 0o600)
    os.replace(temp, env_path)
    cfg_path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n")
    os.chmod(cfg_path, 0o600)
    print("Configuración guardada. La API key no se mostró y no se agregó a Git.")
    print("Ya puedes avisar al agente indicando únicamente el ID de la sonda.")


if __name__ == "__main__":
    try:
        configure()
    except (ValueError, RuntimeError, OSError):
        print(
            "No se completó la configuración. Verifica ID, ISP y API key UUID desde una terminal local.",
            file=sys.stderr,
        )
        sys.exit(1)
