#!/usr/bin/env python3
"""Verificar un paquete propio y regenerar su análisis con la red bloqueada."""
import argparse, hashlib, json, os, shutil, subprocess, sys, tarfile, tempfile
from datetime import datetime, timezone
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for data in iter(lambda:f.read(1024*1024), b''): h.update(data)
    return h.hexdigest()


def relative_path(root, name):
    value=Path(name)
    if value.is_absolute() or '..' in value.parts:
        raise ValueError('Ruta no relativa dentro del paquete')
    path=(root/value).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError('Ruta fuera del directorio de reproducción')
    return path


def unpack(package, root):
    with tarfile.open(package) as tar:
        for member in tar.getmembers():
            relative_path(root, member.name)
            if member.issym() or member.islnk() or not (member.isfile() or member.isdir()):
                raise ValueError('La reproducción admite únicamente archivos y directorios ordinarios')
        tar.extractall(root, filter='data')
    manifest=json.loads((root/'SHA256.json').read_text())
    for name, expected in manifest.items():
        path=relative_path(root, name)
        if not path.is_file() or sha(path)!=expected:
            raise ValueError('Hash de archivo distinto o ausente: '+name)
    actual={str(p.relative_to(root)) for p in root.rglob('*') if p.is_file()}
    if actual-set(manifest)-{'SHA256.json','package_status.json'}:
        raise ValueError('El paquete contiene archivos ajenos al manifiesto')
    if (root/'.env').exists() or (root/'config/local.json').exists():
        raise ValueError('El paquete contiene configuración privada activa')
    return manifest


RUNNER = '''import runpy, sys, urllib.request
blocked = []
def refuse_network(*args, **kwargs):
    blocked.append(True)
    raise RuntimeError("Reproduccion offline: intento de red bloqueado")
urllib.request.urlopen = refuse_network
sys.argv = ["path_discovery.cli", *sys.argv[1:]]
runpy.run_module("path_discovery.cli", run_name="__main__")
if blocked:
    raise SystemExit(85)
'''


def offline_cli(root, *args):
    env={k:v for k,v in os.environ.items() if k not in ('RIPE_ATLAS_API_KEY','NDEX_USERNAME','NDEX_PASSWORD','PYTHONPATH','PYTHONHOME')}
    env['PYTHONDONTWRITEBYTECODE']='1'
    result=subprocess.run([sys.executable,'-c',RUNNER,*args],cwd=root,env=env,capture_output=True,text=True,timeout=180)
    if result.returncode:
        raise RuntimeError('Falló la reproducción offline: '+result.stderr[-1200:])
    return json.loads(result.stdout)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('package');p.add_argument('--output');a=p.parse_args()
    package=Path(a.package).resolve()
    if not package.is_file():raise ValueError('Paquete inexistente')
    with tempfile.TemporaryDirectory(prefix='path_discovery_replay_') as td:
        root=Path(td);manifest=unpack(package,root)
        package_status=json.loads((root/'package_status.json').read_text())
        source=relative_path(root,package_status['analysis'])
        original_summary=json.loads((source/'summary.json').read_text())
        shutil.copyfile(root/'config/reproduccion.json',root/'config/local.json')
        verified=offline_cli(root,'verify')
        analyze_args = ['analyze']
        if original_summary.get('dataset_manifest'):
            analyze_args += ['--dataset', original_summary['dataset_manifest']]
        replay=offline_cli(root,*analyze_args)
        generated=Path(replay['folder'])
        if not generated.is_relative_to(root/'resultados'):raise ValueError('Análisis regenerado fuera de resultados')
        files=[source/name for name in ('responses.json','responses.csv','runs.json','invalid.json','rankings.json','tracelb_additional.json','selective_candidates.json','symmetry.json')]
        files+=sorted((source/'tablas').glob('*.csv'))+sorted((source/'grafos').glob('*.json'))
        compared=[]
        for old in files:
            rel=old.relative_to(source);new=generated/rel
            if not new.exists() or sha(old)!=sha(new):raise ValueError('Resultado regenerado diferente: '+str(rel))
            compared.append(str(rel))
        expected={k:v for k,v in original_summary.items() if k!='created_at'}
        actual={k:v for k,v in json.loads((generated/'summary.json').read_text()).items() if k!='created_at'}
        if expected!=actual:raise ValueError('El resumen regenerado difiere del análisis del paquete; comprobar si se empaquetó durante una ronda activa')
        runs=json.loads((generated/'runs.json').read_text());round_no=max((r['round'] for r in runs),default=0)
        output=Path(a.output).resolve() if a.output else ROOT/'resultados'/f'reproduccion_ronda_{round_no}.json'
        proof={'verified_at':datetime.now(timezone.utc).isoformat(),'package':str(package),'package_sha256':sha(package),'source_analysis':package_status['analysis'],'source_analysis_manifest_sha256':sha(source/'manifest.json'),'session_public_ipv4':original_summary.get('session_public_ipv4'),'offline_valid_measurements':replay['valid_measurements'],'verified_package_files':len(manifest),'verified_original_manifests':verified['verified_manifests'],'network_policy':'urllib.request.urlopen bloqueado antes de importar el CLI; ninguna nueva medición ni consulta ASN permitida','comparison':'byte-identical tables, metrics, responses and CX2; summary identical except creation timestamp','identical_files':compared,'complete_campaign':original_summary['complete_campaign']}
        output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'proof':str(output),'offline_valid_measurements':proof['offline_valid_measurements'],'identical_files':len(compared),'verified_package_files':len(manifest)},ensure_ascii=False))


if __name__=='__main__':
    try:main()
    except (ValueError,RuntimeError,OSError,tarfile.TarError,subprocess.SubprocessError) as e:
        print('ERROR: '+str(e),file=sys.stderr);sys.exit(1)
