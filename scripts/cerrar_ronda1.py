import json, subprocess, time, sys
from pathlib import Path
R=Path(__file__).resolve().parents[1];O=R/'resultados/cierre_ronda1_logs';O.mkdir(exist_ok=True);PY='/home/diego/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3'
active=json.loads((R/'config/local.json').read_text())['session_id'];deadline=time.monotonic()+1800
while True:
 try:
  cp=json.loads((R/'.state/postprocessing.json').read_text())
  diagnostic=json.loads((R/'resultados/diagnostico_recepcion_tcp.json').read_text())
  if '1' in cp and diagnostic.get('session_id')==active:break
 except (FileNotFoundError,json.JSONDecodeError):pass
 running=subprocess.run(['systemctl','--user','is-active','path-discovery-casa-20261026-204144.service'],capture_output=True,text=True).stdout.strip()
 if running!='active':raise RuntimeError('El servicio se detuvo antes de cerrar y procesar la ronda; revisar, sin repetir POST.')
 if time.monotonic()>deadline:raise RuntimeError('No se cerró la ronda en el plazo del control; se conserva el servicio de medición sin intervenir.')
 time.sleep(15)
analysis=Path(cp['1']['analysis']);summary=json.loads((analysis/'summary.json').read_text())
assert summary['valid_measurements']==51 and summary['session_public_ipv4']=='186.189.89.115'
print('Ronda 1 cerrada y diagnóstico terminado:',analysis,flush=True)
def call(args,filename):
 with (O/filename).open('w') as f:subprocess.run(args,cwd=R,stdout=f,stderr=subprocess.STDOUT,check=True)
 return (O/filename).read_text()
package=json.loads(call(['./main','bundle',str(analysis)],'bundle_r1.json'))
tar=next(Path(package['folder']).glob('*.tar.gz'))
print('Paquete preparado:',tar,flush=True)
print(call(['python3','scripts/reproducir_entrega.py',str(tar)],'replay_r1.log'),flush=True)
print(call([PY,'scripts/informe_academico.py',str(analysis)],'report_r1.log'),flush=True)
result={'session_id':active,'analysis':str(analysis),'preparation_package':str(tar),'proof':'resultados/reproduccion_ronda_1.json','status':'round_1_locally_reproduced_not_final_assignment'}
(R/'resultados/cierre_ronda_1_sesion_activa.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result),flush=True)
