#!/usr/bin/env python3
"""Resumir la verificabilidad de reglas observadas sin convertirlas en universales."""
import argparse, collections, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('patterns');p.add_argument('--output',default='resultados/auditoria_patrones_revision.json');a=p.parse_args()
    folder=Path(a.patterns).resolve()
    if not folder.is_relative_to(ROOT/'resultados'):
        raise ValueError('La carpeta debe estar dentro de resultados')
    rules=json.loads((folder/'predictions.json').read_text()); groups={}
    for r in rules:
        key=(r['target'],r['tool'],r['family'],r['method'])
        group=groups.setdefault(key,{'target':key[0],'tool':key[1],'family':key[2],'method':key[3],'rules':0,'rule_kinds':collections.Counter(),'validation':collections.Counter(),'fields_without_later_test':[]})
        group['rules']+=1;group['rule_kinds'][r['rule'].get('kind','unknown')]+=1
        validations=r.get('validation',{})
        if not validations:group['fields_without_later_test'].append(r['field'])
        for value in validations.values():group['validation'][value.get('status','unknown')]+=1
    result={'source':str(folder.relative_to(ROOT)),'scope':'Cuenta verificaciones de campos y bytes, no paquetes ni puntajes. Un pase describe las capturas observadas; un fallo no se oculta ni invalida automáticamente otra regla.','groups':list(groups.values())}
    path=ROOT/a.output;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'output':str(path),'method_target_groups':len(groups),'rules':len(rules)},ensure_ascii=False))
if __name__=='__main__':
    try:main()
    except (ValueError,OSError,KeyError) as e:print('ERROR:',e,file=sys.stderr);sys.exit(1)
