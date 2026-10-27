#!/usr/bin/env python3
"""Preparar copias de PCAP completos; registrar solamente capturas GUI ya observadas."""
import argparse,json,shutil,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from path_discovery.common import ROOT,config,sha256,json_write,save_manifest,verify_manifest,utc
from path_discovery.analysis import collect

def main():
 p=argparse.ArgumentParser();p.add_argument('--record-method');p.add_argument('--screenshot');a=p.parse_args();cfg=config();sid=cfg['session_id']
 folder=ROOT/'datos/originales'/('gui_'+sid);folder.mkdir(exist_ok=True)
 runs=collect()[1];examples={}
 for r in runs:
  if r['round']==1 and r['direction']=='ida':examples.setdefault('_'.join(r[k] for k in ('tool','family','method')),r)
 prepared=[]
 for method,r in examples.items():
  original=ROOT/'datos/originales'/r['run_id'];verify_manifest(original)
  dest=folder/(method+'__'+r['run_id']+'.pcapng');src=original/'capture.pcapng'
  if not dest.exists():
   if (folder/'manifest.json').exists():raise ValueError('Revisión sellada: no agregar copias')
   shutil.copyfile(src,dest)
  if sha256(src)!=sha256(dest):raise ValueError('Copia PCAP diferente del original')
  prepared.append({'method':method,'run_id':r['run_id'],'source':str(src.relative_to(ROOT)),'copy':str(dest.relative_to(ROOT)),'container_path':'/captures/'+str(dest.relative_to(ROOT/'datos/originales')),'sha256':sha256(src),'session_public_ipv4':r['public_ipv4']})
 provenance=folder/'provenance.json'
 if not (folder/'manifest.json').exists():
  json_write(provenance,{'session_id':sid,'prepared':prepared})
  if len(prepared)==14:save_manifest(folder,{'kind':'gui_input_copies','session_id':sid})
 if a.record_method:
  entry=dict(next(x for x in prepared if x['method']==a.record_method));shot=Path(a.screenshot).resolve()
  if not shot.is_relative_to(ROOT/'capturas') or not shot.is_file():raise ValueError('Seleccionar captura guardada dentro del proyecto')
  entry.update(screenshot=str(shot.relative_to(ROOT)),screenshot_sha256=sha256(shot),scope='Inspección real en Wireshark 4.6.6 mediante navegador local; encabezados y bytes. No acredita por sí sola contraste entre rondas.')
  out=ROOT/'resultados/revision_wireshark_gui.json';review=json.loads(out.read_text()) if out.exists() else {'session_id':sid,'session_public_ipv4':cfg['session_public_ipv4'],'mode':'real_wireshark_gui_via_local_browser','wireshark_version':'4.6.6','reviewed_runs':[]}
  if review.get('session_id')!=sid:raise ValueError('No sobrescribir revisión de otra sesión')
  if any(x['method']==a.record_method for x in review['reviewed_runs']):raise ValueError('Método ya registrado: no sustituir evidencia')
  review['reviewed_at']=utc();review['reviewed_runs'].append(entry);json_write(out,review)
  if len(review['reviewed_runs'])==14:
   sealed=ROOT/'datos/originales'/('revision_wireshark_'+sid);sealed.mkdir();json_write(sealed/'review.json',review,exclusive=True);save_manifest(sealed,{'kind':'real_wireshark_gui_review','session_id':sid})
 print(json.dumps({'prepared':prepared,'recorded':a.record_method},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
