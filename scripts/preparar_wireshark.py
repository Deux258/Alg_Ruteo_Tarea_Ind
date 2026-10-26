#!/usr/bin/env python3
"""Preparar GUI local durante la pausa entre rondas para no contaminar RTT."""
import json
import os
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
print(
    "Esperando el cierre de la ronda 1 antes de descargar la imagen gráfica.",
    flush=True,
)
while True:
    state = json.loads((ROOT / ".state/campaign.json").read_text())
    rd = state["rounds"]["1"]
    if any(v["status"] == "needs_review" for v in rd.get("jobs", {}).values()):
        if os.environ.get("PD_GUI_REVIEWED_PAUSE") == "1":
            print(
                "Pausa revisada expresamente: campaña detenida, descarga sin mediciones simultáneas.",
                flush=True,
            )
            break
        raise SystemExit(
            "La campaña requiere revisión; no se descarga automáticamente."
        )
    if rd.get("finished_at"):
        break
    time.sleep(10)
image = "lscr.io/linuxserver/wireshark:latest"
subprocess.run(["docker", "pull", image], check=True)
info = json.loads(
    subprocess.check_output(["docker", "image", "inspect", image], text=True)
)[0]
digest = next(d for d in info["RepoDigests"] if "linuxserver/wireshark@" in d)
envpath = ROOT / ".state/wireshark.env"
envpath.write_text("PD_WIRESHARK_IMAGE=" + digest + "\n")
compose = [
    "docker",
    "compose",
    "--env-file",
    str(envpath),
    "-f",
    str(ROOT / "compose.wireshark.yaml"),
    "--profile",
    "gui",
]
subprocess.run(compose + ["up", "-d", "wireshark"], cwd=ROOT, check=True)
(ROOT / ".state/wireshark_image.json").write_text(
    json.dumps(
        {
            "image": digest,
            "image_id": info["Id"],
            "source": "https://docs.linuxserver.io/images/docker-wireshark/",
            "url": "http://127.0.0.1:8767/",
            "pcap_mount": "/captures (solo lectura)",
            "host_capture_capabilities_added": False,
        },
        indent=2,
    )
    + "\n"
)
print("Wireshark gráfico disponible en http://127.0.0.1:8767/", flush=True)
