#!/usr/bin/env python3
"""Contrastar un segundo candidato Scamper sin borrar el primer resultado."""
import json, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from path_discovery.common import ROOT,config,campaign_lock,json_write,save_manifest,identifier,sha256,utc
from path_discovery.acquire import measure_scamper
from path_discovery.analysis import collect,normalize_trace
from path_discovery.common import records
from path_discovery.packets import export_packets
from scripts.validar_respuesta_selectiva import candidates

def main():
 cfg=config();sid=cfg['session_id'];out=ROOT/'resultados/respuesta_selectiva_segundo_scamper.json'
 if out.exists():raise RuntimeError('La prueba adicional ya está cerrada; no repetir.')
 if any(json.loads(p.read_text()).get('session_id')==sid for p in (ROOT/'datos/originales').glob('validacion_segundo_scamper_*/intent.json')):raise RuntimeError('Hay un intento previo; revisar antes de reintentar.')
 rows,runs,invalid=collect()
 if len(runs)!=153 or invalid:raise RuntimeError('La campaña no está completa y válida.')
 choices=candidates(rows,runs,'scamper')
 candidate=next((c for c in choices if c['target']=='90.150.251.81' and c['ip']=='195.22.211.61' and c['responds_method']=='icmp' and c['not_observed_method']=='udp'),None)
 if not candidate:raise RuntimeError('El candidato no cumple los criterios originales.')
 folder=ROOT/'datos/originales'/('validacion_segundo_scamper_'+identifier());folder.mkdir()
 original=json.loads((ROOT/'resultados/respuesta_selectiva_validacion.json').read_text());json_write(folder/'resultado_anterior.json',original,exclusive=True)
 json_write(folder/'intent.json',{'session_id':sid,'started_at':utc(),'candidate':candidate,'maximum_additional_runs':4,'purpose':'Comprobar un segundo candidato tras no corroborar el primero; conserva ambos resultados.'},exclusive=True)
 target=next(t for t in cfg['targets'] if t['ip']==candidate['target']);extra=[]
 with campaign_lock():
  for repeat in (1,2):
   for method in (candidate['responds_method'],candidate['not_observed_method']):
    path=measure_scamper(cfg,target,'trace',method,0,kind='targeted_validation')
    meta=json.loads((path/'metadata.json').read_text());observations=[]
    for obj in records(path/'result.jsonl'):
     if obj.get('type')=='trace':observations+=normalize_trace(obj,meta,path.name)
    ips={r['ip'] for r in observations if r.get('ip')};export=export_packets(path)
    extra.append({'repeat':repeat,'method':method,'run_id':path.name,'measurement_id':None,'ip_observed':candidate['ip'] in ips,'unique_ips':sorted(ips),'export':str(export.relative_to(ROOT)),'manifest_sha256':sha256(path/'manifest.json')})
    json_write(folder/'progress.json',extra)
 a=[x for x in extra if x['method']==candidate['responds_method']];b=[x for x in extra if x['method']==candidate['not_observed_method']]
 confirmed=all(x['ip_observed'] for x in a) and not any(x['ip_observed'] for x in b)
 case={'tool':'scamper','candidate':candidate,'additional_runs':extra,'status':'corroborated_observation' if confirmed else 'not_corroborated','interpretation':'Observación acotada; la ausencia puede deberse a rutas, pérdida o balanceo y no prueba una regla de firewall.'}
 result={'session_id':sid,'session_public_ipv4':cfg['session_public_ipv4'],'performed_at':utc(),'evidence':str(folder.relative_to(ROOT)),'case':case}
 json_write(folder/'result.json',result,exclusive=True);save_manifest(folder,{'kind':'supplemental_selective_response_validation'});json_write(out,result,exclusive=True)
 combined={**original,'cases':original['cases']+[case],'supplemental_evidence':result['evidence'],'requirements_corroborated':all(any(c.get('tool')==t and c.get('status')=='corroborated_observation' for c in original['cases']+[case]) for t in ('scamper','ripe')),'updated_at':utc()}
 json_write(ROOT/'resultados/respuesta_selectiva_validacion.json',combined)
 print(json.dumps({'status':case['status'],'requirements_corroborated':combined['requirements_corroborated'],'evidence':result['evidence']},ensure_ascii=False),flush=True)
if __name__=='__main__':main()
