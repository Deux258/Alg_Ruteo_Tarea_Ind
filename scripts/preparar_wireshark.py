#!/usr/bin/env python3
"""Abrir la GUI fijada por digest; descargar solo fuera de una ronda activa."""
import json, re, subprocess, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
public_env = ROOT / 'config/wireshark-image.env.example'
image = next(line.split('=', 1)[1].strip() for line in public_env.read_text().splitlines() if line.startswith('PD_WIRESHARK_IMAGE='))
if not re.fullmatch(r'lscr\.io/linuxserver/wireshark@sha256:[0-9a-f]{64}', image):
    raise SystemExit('Se requiere la imagen oficial fijada por digest en configuración pública.')
inspected = subprocess.run(['docker', 'image', 'inspect', image], capture_output=True, text=True)
if inspected.returncode:
    print('Imagen no disponible localmente; esperando cierre de ronda 1 antes de descargar.', flush=True)
    while True:
        statefile = ROOT / '.state/campaign.json'
        if not statefile.exists():
            raise SystemExit('Validar la campaña antes de descargar durante las mediciones.')
        rd = json.loads(statefile.read_text())['rounds'].get('1', {})
        if any(j['status'] == 'needs_review' for j in rd.get('jobs', {}).values()):
            raise SystemExit('Campaña pendiente de revisión; no se descarga automáticamente.')
        if rd.get('finished_at'):
            break
        time.sleep(10)
    subprocess.run(['docker', 'pull', image], check=True)
    inspected = subprocess.run(['docker', 'image', 'inspect', image], capture_output=True, text=True, check=True)
info = json.loads(inspected.stdout)[0]
subprocess.run(['docker', 'compose', '--env-file', str(public_env), '-f', str(ROOT / 'compose.wireshark.yaml'), '--profile', 'gui', 'up', '-d', 'wireshark'], cwd=ROOT, check=True)
(ROOT / '.state/wireshark_image.json').write_text(json.dumps({'image': image, 'image_id': info['Id'], 'source': 'https://docs.linuxserver.io/images/docker-wireshark/', 'url': 'http://127.0.0.1:8767/', 'pcap_mount': '/captures (solo lectura)', 'host_capture_capabilities_added': False}, indent=2)+'\n')
print('Wireshark gráfico disponible en http://127.0.0.1:8767/', flush=True)
