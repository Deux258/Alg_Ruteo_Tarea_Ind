#!/usr/bin/env python3
"""Una ejecución finita: piloto nuevo, revisión sellada y campaña de tres rondas."""
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from path_discovery.common import load_credentials,config,json_write,utc
from path_discovery.cli import selected_udp_pilots,accept_pilot,fingerprint
from path_discovery.packets import review_udp_pilots
from argparse import Namespace

def run(*args):
 print('Ejecutando:', ' '.join(args),flush=True)
 subprocess.run(args,cwd=ROOT,check=True)

def main():
 load_credentials(); cfg=config()
 if (ROOT/'.state/pilot.json').exists():
  raise RuntimeError('Ya hay piloto aceptado: revisar antes de lanzar este inicio de sesión otra vez.')
 intent=ROOT/'.state/session_bootstrap.json'
 if intent.exists():
  raise RuntimeError('Inicio ya registrado: inspeccionar antes de repetir cualquier POST.')
 json_write(intent,{'session_id':cfg['session_id'],'started_at':utc(),'status':'running'},exclusive=True)
 from path_discovery.acquire import preflight
 _, checks = preflight()
 if checks['blockers']:
  raise RuntimeError('Preflight bloquea: ' + '; '.join(checks['blockers']))
 run('./main','pilot','--method','udp')
 run('./main','pilot','--tool','ripe','--method','UDP','--direction','ida')
 run('./main','pilot','--tool','ripe','--method','UDP','--direction','vuelta')
 review=review_udp_pilots(selected_udp_pilots('200.14.48.134'))
 value=accept_pilot(Namespace(target='200.14.48.134',packet_review=str(review),wireshark_reviewed=False))
 print('Piloto aceptado:',json.dumps(value,ensure_ascii=False),flush=True)
 json_write(intent,{'session_id':cfg['session_id'],'finished_pilot_at':utc(),'status':'pilot_accepted'})
 run(sys.executable,'scripts/continuar_campana.py')
 json_write(intent,{'session_id':cfg['session_id'],'finished_at':utc(),'status':'campaign_processed'})
if __name__=='__main__': main()
