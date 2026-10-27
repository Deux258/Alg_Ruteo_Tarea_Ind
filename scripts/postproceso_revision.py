#!/usr/bin/env python3
"""Procesar la selección revisada únicamente tras una campaña rusa completa."""
import json, subprocess, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
DATASET = 'config/seleccion_revision.json'
STATE = ROOT / '.state/campana_rusia_revision.json'

def run(args):
    print('Ejecutando:', ' '.join(args), flush=True)
    subprocess.run(args, cwd=ROOT, check=True)

def main():
    while True:
        state = json.loads(STATE.read_text()) if STATE.exists() else {}
        if state.get('finished_at'):
            break
        result = subprocess.run(['systemctl', '--user', 'is-active', '--quiet', 'path-discovery-rusia-revision.service'])
        if result.returncode:
            raise RuntimeError('La campaña terminó sin cierre válido; inspeccionar el supervisor antes de procesar')
        time.sleep(30)
    from path_discovery.analysis import collect
    from path_discovery.common import ROOT as root
    from path_discovery.acquire import plan_jobs
    from path_discovery.common import config
    from path_discovery.analysis import load_dataset
    selection = load_dataset(DATASET)
    rows, runs, invalid = collect(dataset=DATASET)
    expected = {tuple(j[k] for k in ('round','target','tool','family','method','direction')) for j in plan_jobs({**config(), 'targets': selection['targets']})}
    found = {tuple(r[k] for k in ('round','target','tool','family','method','direction')) for r in runs}
    if invalid or len(runs)!=153 or found!=expected:
        raise RuntimeError('La selección no contiene las 153 celdas íntegras esperadas')
    run([sys.executable, 'scripts/evidencia_paquetes.py', '--dataset', DATASET])
    run([sys.executable, 'scripts/correlacion_tcp.py', '--dataset', DATASET])
    run([sys.executable, 'scripts/verificar_checksums.py', '--dataset', DATASET])
    patterns_run = subprocess.run(['./main', 'patterns', '--dataset', DATASET], cwd=ROOT, check=True, text=True, capture_output=True)
    patterns_folder = json.loads(patterns_run.stdout)['folder']
    run([sys.executable, 'scripts/auditar_patrones.py', patterns_folder])
    print('Generando análisis con enriquecimiento ASN y selección sellada...', flush=True)
    output = subprocess.run(['./main','analyze','--online-asn','--dataset',DATASET],cwd=ROOT,check=True,text=True,capture_output=True)
    result=json.loads(output.stdout)
    if not result.get('complete_campaign'):
        raise RuntimeError('El análisis final no considera la campaña completa')
    path=ROOT/'resultados/analisis_revision_final.json'
    path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print('Análisis listo:',result['folder'],flush=True)
    run([sys.executable, 'scripts/validar_respuesta_selectiva.py', '--dataset', DATASET])
    print('Pendientes revisión científica, capturas adicionales, publicación NDEx y entrega final.',flush=True)
if __name__ == '__main__':
    try: main()
    except Exception as e:
        print('ERROR:',str(e),file=sys.stderr,flush=True)
        sys.exit(1)
