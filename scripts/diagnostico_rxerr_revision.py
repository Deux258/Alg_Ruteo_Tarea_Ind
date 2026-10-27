#!/usr/bin/env python3
import json,sys,os
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from path_discovery.common import ROOT,config,campaign_lock,json_write,save_manifest,identifier,records,utc,sha256
from path_discovery.acquire import measure_scamper
from path_discovery.packets import export_packets

def main():
 cfg=config();target=cfg['targets'][0];out=ROOT/'resultados/diagnostico_tcp_rxerr_revision.json'
 if out.exists(): raise RuntimeError('Diagnóstico ya realizado; no repetir automáticamente')
 if list((ROOT/'datos/originales').glob('diagnostico_tcp_rxerr_revision_*/intent.json')):raise RuntimeError('Intento anterior existe; inspeccionar antes de repetir')
 folder=ROOT/'datos/originales'/('diagnostico_tcp_rxerr_revision_'+identifier());folder.mkdir()
 json_write(folder/'intent.json',{'started_at':utc(),'target':target['ip'],'options':['baseline','ICMP-rxerr'],'methods':['tcp','tcp-ack'],'max_runs':4},exclusive=True)
 result=[]
 with campaign_lock():
  for method in ('tcp','tcp-ack'):
   for rxerr in (False,True):
    c={**cfg,'diagnostic_icmp_rxerr':rxerr};path=measure_scamper(c,target,'trace',method,0,kind='targeted_validation')
    meta=json.loads((path/'metadata.json').read_text());obj=next(x for x in records(path/'result.jsonl') if x.get('type')=='trace');exp=export_packets(path)
    result.append({'method':method,'icmp_rxerr':rxerr,'run_id':path.name,'status':meta['status'],'unique_ips':sorted({x['addr'] for x in obj.get('hops',[]) if x.get('addr')}),'probe_count':obj.get('probe_count'),'stop_reason':obj.get('stop_reason'),'export':str(exp.relative_to(ROOT)),'manifest_sha256':sha256(path/'manifest.json')})
    json_write(folder/'progress.json',result)
 data={'performed_at':utc(),'target':target['ip'],'runs':result,'evidence':str(folder.relative_to(ROOT)),'scope':'Diagnóstico de recepción separado; no demuestra filtrado por routers ni cambia los resultados históricos.'}
 json_write(folder/'result.json',data,exclusive=True);save_manifest(folder,{'kind':'tcp_receive_diagnostic'});json_write(out,data,exclusive=True);print(json.dumps(data,ensure_ascii=False),flush=True)
if __name__=='__main__':main()
