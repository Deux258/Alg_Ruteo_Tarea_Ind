#!/usr/bin/env python3
"""Piloto y tres rondas rusas del enunciado actualizado con estado aislado."""
import csv,hashlib,json,os,sys,time
from datetime import datetime,timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from path_discovery.common import ROOT,config,load_credentials,campaign_lock,json_write,utc,sha256,verify_manifest
from path_discovery.acquire import preflight,measure_scamper,measure_ripe,plan_jobs
from path_discovery.packets import review_udp_pilots
from path_discovery.analysis import load_dataset

SELECTION=ROOT/'config/seleccion_revision.json';STATE=ROOT/'.state/campana_rusia_revision.json'
def atomic(path,obj):
 tmp=path.with_name(path.name+'.tmp');json_write(tmp,obj);os.replace(tmp,path)
def fingerprint(cfg):return hashlib.sha256(json.dumps(cfg,sort_keys=True).encode()).hexdigest()
def metadata(path):
 verify_manifest(path);m=json.loads((path/'metadata.json').read_text())
 if m.get('status')!='completed':raise RuntimeError('Medición sin resultado válido: '+path.name)
 return {**m,'run_id':path.name}
def check_selection(data):
 ids=[v['run_id'] for v in data['accepted_runs']]
 if len(ids)!=len(set(ids)):raise RuntimeError('La selección contiene originales duplicados')
 for e in data['accepted_runs']:
  p=ROOT/'datos/originales'/e['run_id'];verify_manifest(p)
  if sha256(p/'manifest.json')!=e['manifest_sha256']:raise RuntimeError('Manifiesto seleccionado modificado: '+e['run_id'])
def store_run(path,job):
 m=metadata(path);d=load_dataset(SELECTION)
 if any(e['run_id']==path.name for e in d['accepted_runs']):return
 for e in d['accepted_runs']:
  old=json.loads((ROOT/'datos/originales'/e['run_id']/'metadata.json').read_text())
  if all(old.get(k)==job[k] for k in ('round','target','tool','family','method','direction')):
   raise RuntimeError('Ya existe una medición aceptada para la celda: '+path.name)
 d['accepted_runs'].append({'run_id':path.name,'manifest_sha256':sha256(path/'manifest.json'),'reason':'Nueva medición del destino ruso del enunciado actualizado'})
 atomic(SELECTION,d)
def main():
 load_credentials();selection=load_dataset(SELECTION);check_selection(selection)
 cfg={**config(),'targets':selection['targets']};target=next(t for t in cfg['targets'] if t['ip']=='37.79.226.46' and t['probe_id']==3959)
 state=json.loads(STATE.read_text()) if STATE.exists() else {'dataset_id':selection['dataset_id'],'fingerprint':fingerprint(cfg),'pilot':{},'rounds':{},'created_at':utc()}
 if state['fingerprint']!=fingerprint(cfg):raise RuntimeError('Cambió la configuración de la revisión; inspeccionar antes de reanudar')
 if any(j.get('status') in ('running','needs_review') for j in state.get('pilot',{}).values()):raise RuntimeError('Piloto incierto: revisar originales y solicitudes antes de repetir')
 if any(j.get('status') in ('running','needs_review') for r in state['rounds'].values() for j in r.get('jobs',{}).values()):raise RuntimeError('Celda incierta: revisar antes de repetir')
 atomic(STATE,state)
 _,checks=preflight({**cfg,'targets':[target]})
 if checks['blockers']:raise RuntimeError('Preflight: '+'; '.join(checks['blockers']))
 print('Preflight correcto; IP pública:',checks['public_ipv4'],flush=True)
 pilots=[('scamper', 'ida'),('ripe','ida'),('ripe','vuelta')]
 with campaign_lock():
  for tool,direction in pilots:
   key=tool+'_'+direction
   if state['pilot'].get(key,{}).get('status')=='completed':continue
   state['pilot'][key]={'status':'running','started_at':utc()};atomic(STATE,state)
   try:
    path=measure_scamper(cfg,target,'trace','udp',0,pilot=True) if tool=='scamper' else measure_ripe(cfg,target,'UDP',direction,0,pilot=True)
    m=metadata(path);state['pilot'][key]={'status':'completed','run_id':path.name,'manifest_sha256':sha256(path/'manifest.json')};atomic(STATE,state)
   except BaseException:
    state['pilot'][key]['status']='needs_review';atomic(STATE,state);raise
   print('Piloto completado:',key,path.name,flush=True)
  runs=[metadata(ROOT/'datos/originales'/state['pilot'][tool+'_'+direction]['run_id']) for tool,direction in pilots]
  review=review_udp_pilots(runs);data=json.loads((review/'review.json').read_text());ripe=next(r for r in data['reviews'] if r['run_id']==state['pilot']['ripe_ida']['run_id'])
  if not ripe['udp_ports'] or min(ripe['udp_ports'])!=cfg['udp_base_port']:raise RuntimeError('Puerto UDP observado difiere del valor configurado')
  state['pilot_review']={'path':str(review.relative_to(ROOT)),'manifest_sha256':sha256(review/'manifest.json'),'accepted_at':utc()};atomic(STATE,state)
 print('Piloto revisado y aceptado:',review,flush=True)
 jobs=[j for j in plan_jobs(cfg) if j['target']==target['ip']]
 for n in (1,2,3):
  if n>1:
   previous=state['rounds'].get(str(n-1),{})
   if not previous.get('finished_at'):raise RuntimeError('Falta cerrar ronda anterior')
   deadline=datetime.fromisoformat(previous['finished_at']).timestamp()+cfg['round_gap_seconds']
   print('Esperando separación de ronda',n,'hasta',datetime.fromtimestamp(deadline,timezone.utc).isoformat(),flush=True)
   while time.time()<deadline:time.sleep(min(30,max(.1,deadline-time.time())))
  rd=state['rounds'].setdefault(str(n),{'started_at':utc(),'jobs':{}});atomic(STATE,state)
  with campaign_lock():
   for job in [j for j in jobs if j['round']==n]:
    key='|'.join(str(job[k]) for k in ('target','tool','family','method','direction'))
    old=rd['jobs'].get(key)
    if old:
     if old['status']!='completed':raise RuntimeError('Celda no cerrada; requiere revisión')
     store_run(ROOT/'datos/originales'/old['run_id'],job);continue
    rd['jobs'][key]={'status':'running','started_at':utc()};atomic(STATE,state)
    print('Midiendo',n,key,flush=True)
    try:
     path=measure_scamper(cfg,target,job['family'],job['method'],n) if job['tool']=='scamper' else measure_ripe(cfg,target,job['method'],job['direction'],n)
     metadata(path);rd['jobs'][key]={'status':'completed','run_id':path.name,'finished_at':utc()};atomic(STATE,state);store_run(path,job)
    except BaseException:
     rd['jobs'][key]['status']='needs_review';atomic(STATE,state);raise
  rd['finished_at']=utc();atomic(STATE,state);print('Ronda rusa terminada:',n,flush=True)
 check_selection(load_dataset(SELECTION));state['finished_at']=utc();atomic(STATE,state)
 print('Campaña rusa terminada: 51 celdas; procesar con --dataset config/seleccion_revision.json.',flush=True)
if __name__=='__main__':
 try:main()
 except Exception as e:print('ERROR:',str(e),file=sys.stderr,flush=True);sys.exit(1)
