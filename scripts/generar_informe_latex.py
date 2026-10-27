#!/usr/bin/env python3
"""Informe LaTeX reproducible desde una selección sellada, sin nuevas mediciones."""
import argparse,csv,json,hashlib,shutil,sys,statistics,math,shlex
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from path_discovery.common import verify_manifest,sha256,TRACE_METHODS,LB_METHODS,RIPE_METHODS,utc
from path_discovery.delivery import delivery_checks

def read(p):return json.loads(Path(p).read_text())
def tex(s):
    return ''.join({'\\':r'\textbackslash{}','&':r'\&','%':r'\%','$':r'\$','#':r'\#','_':r'\_\allowbreak{}','{':r'\{','}':r'\}','~':r'\textasciitilde{}','^':r'\textasciicircum{}'}.get(c,c) for c in str(s))
def mono(s):return r'\texttt{'+tex(s)+'}'
def para(s):return tex(s)+'\n\n'
def heading(s,level='subsection',label=None):return '\\'+level+'{'+tex(s)+'}'+(('\\label{'+label+'}') if label else '')+'\n'
def table(headers,rows,widths=None,caption=None,label=None,small=True):
    spec=''.join('p{'+str(w)+'cm}' for w in widths) if widths else 'l'+'r'*(len(headers)-1)
    out=r'\begingroup'+('\n\\fontsize{9}{11}\\selectfont\n' if small else '\n')
    if not caption:out+='\\addtocounter{table}{-1}\n'
    out+='\\begin{longtable}{'+spec+'}\n'
    if caption:out+=r'\caption{'+tex(caption)+'}'+(('\\label{'+label+'}') if label else '')+r' \\'+'\n'
    hdr=' & '.join(r'\textbf{'+tex(v)+'}' for v in headers)+r' \\ \midrule'+'\n'
    out+='\\toprule\n'+hdr+'\\endfirsthead\n\\toprule\n'+hdr+'\\endhead\n'
    for row in rows:out+=' & '.join(tex(v) for v in row)+r' \\'+'\n'
    return out+'\\bottomrule\n\\end{longtable}\n\\endgroup\n'
def csvdata(p):
    with Path(p).open() as f:return list(csv.reader(f))
def clean(s,asn=True):
    s=s.replace('NO_MEDIDO','--').replace('? not_recorded','?').replace('[non_global]','[priv./esp.]').replace('[unknown]','[AS n/d]')
    if not asn:
        import re
        s=re.sub(r' \[[^\]]*\]','',s)
    return s.replace('; ','; ')
def csvtable(p,caption,label,asn=True,landscape=False):
    x=csvdata(p);n=len(x[0]);width=23.3 if landscape else 15.1
    widths=[.95]+[(width-.95)/(n-1)]*(n-1)
    return table(x[0],[[clean(c,asn) for c in row] for row in x[1:]],widths,caption,label)
def score(r):return (-r['median_unique_ips'],-r['median_coverage'],-(r['stability_jaccard'] if r.get('stability_jaccard') is not None else -1))
def graphpdf(cx,path):
    from reportlab.pdfgen import canvas
    from reportlab.lib.colors import HexColor
    d={k:v for a in cx for k,v in a.items()};w=842;pos={}
    first_rows=1+max(round(n.get('x',0)/160)//7 for n in d['nodes'] if n.get('y',0)==0)
    for n in d['nodes']:
        col=round(n.get('x',0)/160);row=col//7;cc=col%7
        if row%2:cc=6-cc
        line=0 if n.get('y',0)==0 else 1
        pos[n['id']]=(65+cc*118,560-row*55-line*(first_rows*55+40))
    ymin=min(y for x,y in pos.values());ymax=max(y for x,y in pos.values());c=canvas.Canvas(str(path),pagesize=(w,ymax-ymin+110),invariant=1);c.saveState();c.translate(0,-ymin+60)
    for e in d['edges']:
        a,b=pos[e['s']],pos[e['t']];color='#137C82' if e['v']['direction']=='ida' else '#CC641D';c.setStrokeColor(HexColor(color));c.setFillColor(HexColor(color));c.setLineWidth(1.4);dx=b[0]-a[0];dy=b[1]-a[1];dist=math.hypot(dx,dy) or 1;ux,uy=dx/dist,dy/dist;boundary=min(53/abs(ux) if ux else float('inf'),19/abs(uy) if uy else float('inf'));start=(a[0]+ux*(boundary+1),a[1]+uy*(boundary+1));end=(b[0]-ux*(boundary+3),b[1]-uy*(boundary+3));c.line(*start,*end);c.line(end[0],end[1],end[0]-ux*7+uy*3,end[1]-uy*7-ux*3);c.line(end[0],end[1],end[0]-ux*7-uy*3,end[1]-uy*7+ux*3)
    for n in d['nodes']:
        x,y=pos[n['id']];v=n['v'];kind=v['kind'];color={'ip_interface':'#DCEEF2','gap':'#E5E7EB','ambiguous_hop':'#FDE6AD'}[kind];c.setFillColor(HexColor(color));c.setStrokeColor(HexColor('#173D5C'));c.roundRect(x-53,y-19,106,38,5,fill=1,stroke=1);c.setFillColor(HexColor('#173D5C'));c.setFont('Helvetica',12)
        lines=v['label'].split('\n') if kind=='ip_interface' else [('Sin respuesta' if kind=='gap' else 'Respuesta multiple'),'TTL '+str(v.get('ttl',''))]
        for i,t in enumerate(lines):c.drawCentredString(x,y+5-i*11,t)
    c.restoreState();c.setFillColor(HexColor('#173D5C'));c.setFont('Helvetica',10);c.drawString(20,17,'Ida: verde | Vuelta: naranja | Gris: sin respuesta | Amarillo: capa ambigua');c.save()

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--analysis',required=True);ap.add_argument('--evidence',required=True);ap.add_argument('--output',default='informe/latex');ap.add_argument('--draft',action='store_true');a=ap.parse_args();analysis=Path(a.analysis).resolve();out=Path(a.output).resolve();ev=read(a.evidence);verify_manifest(analysis);summary=read(analysis/'summary.json');checks=delivery_checks(analysis)
    if not a.draft and not all(checks[k] for k in ('campaign_153_complete','three_current_graphs_public','fourteen_gui_methods_reviewed','selective_cases_corroborated')):raise ValueError('La edición final requiere 153 mediciones, tres grafos públicos, 14 revisiones GUI y casos selectivos corroborados')
    if not {ev[k] for k in ('patterns','payload','selective')} <= {x['path'] for x in ev['files']}:raise ValueError('Toda fuente seleccionada debe tener un hash explícito')
    for entry in ev['files']:
        p=(ROOT/entry['path']).resolve()
        if not p.is_relative_to(ROOT.resolve()):raise ValueError('Fuente fuera del proyecto')
        if sha256(p)!=entry['sha256']:raise ValueError('Evidencia alterada: '+entry['path'])
    for d in ('secciones','datos','figuras'): (out/d).mkdir(parents=True,exist_ok=True)
    runs=read(analysis/'runs.json');responses=read(analysis/'responses.json');rank=read(analysis/'rankings.json');adds=read(analysis/'tracelb_additional.json');sym=read(analysis/'symmetry.json');targets=summary['targets'];labels={t['ip']: {'Valparaiso':'Valparaíso','Habana':'La Habana'}.get(t['label'],t['label']) for t in targets};patterns=read(ROOT/ev['patterns']);payload=read(ROOT/ev['payload'])['cases'];selective=read(ROOT/ev['selective']);review=read(ROOT/'resultados/revision_wireshark_gui.json');exports=read(ROOT/'resultados/exportaciones_paquetes.json');pf=read(ROOT/'resultados/preflight_campana.json')
    sources={str(analysis.relative_to(ROOT))+'/manifest.json':sha256(analysis/'manifest.json')};
    for r in runs:
        m=ROOT/'datos/originales'/r['run_id']/'manifest.json';sources[str(m.relative_to(ROOT))]=sha256(m)
    for name in ('config/seleccion_revision.json','docs/MATRIZ_RUBRICA_ACTUALIZADA.md','datos/originales/enunciado_actualizado_20261026/enunciado.txt','datos/originales/enunciado_actualizado_20261026/rubrica.txt'):
        sources[name]=sha256(ROOT/name)
    sources.update({v['path']:v['sha256'] for v in ev['files']});captionmap={i['file']:i['caption'] for i in read(ROOT/'capturas/indice.json')};sources['scripts/generar_informe_latex.py']=sha256(Path(__file__));sources[str(Path(a.evidence).resolve().relative_to(ROOT))]=sha256(a.evidence)
    def asset(path):
        p=ROOT/path;dest=out/'figuras'/p.name;shutil.copyfile(p,dest);sources[str(p.relative_to(ROOT))]=sha256(p);return 'figuras/'+p.name
    publications={}
    for p in (ROOT/'grafos').glob('publication_*/publication.json'):
        v=read(p)
        if not v.get('public_read_verified') or v['target'] not in labels:continue
        proofpath=p.parent/'source.json'
        if not proofpath.exists():proofpath=p.parent/'attempt.json'
        proof=read(proofpath) if proofpath.exists() else {}
        graph=analysis/'grafos'/f"{v['target']}.cx2.json"
        sel=read(analysis/'grafos'/f"{v['target']}.selection.json")
        if proof.get('sha256')!=sha256(graph) or set(v['measurement_ids'])!=set(sel['ids']):continue
        publications[v['target']]=v;sources[str(p.relative_to(ROOT))]=sha256(p)
        for receiptname in ('source.json','summary.json','export.cx2.json'):
            q=p.parent/receiptname
            if q.exists():sources[str(q.relative_to(ROOT))]=sha256(q)
    def put(name,s): (out/'datos'/name).write_text(s)
    def ranktable(dest,tool,family,direction='ida'):
        g=sorted([v for v in rank if v['target']==dest and v['tool']==tool and v['family']==family and v['direction']==direction],key=score)
        rows=[[v['method'],v['median_unique_ips'],f"{v['median_coverage']*100:.1f}%",'n/d' if v.get('stability_jaccard') is None else f"{v['stability_jaccard']:.3f}",v.get('median_probes_sent') if v.get('median_probes_sent') is not None else 'n/d',v['destination_observed_runs']] for v in g]
        return table(['Método','IP únicas','Cobertura','Estabilidad','Sondas','Llegada / 3'],rows,[3.1,1.9,2.1,2.1,1.8,2.1]),g
    def packetrows(key,roundno):
        candidates=[r for r in runs if (r['tool'],r['family'],r['method'])==key and r['target']==targets[0]['ip'] and r['direction']=='ida' and r['round']==roundno];r=candidates[0];p=ROOT/exports[r['run_id']]/'emitted.tsv'
        with p.open() as f:return r,list(csv.DictReader(f,delimiter='\t'))
    def ficha(key):
        dest=targets[0]['ip'];r,packets=packetrows(key,1);r2,later=packetrows(key,2);items=[p for p in patterns if (p['tool'],p['family'],p['method'],p['target'])==(*key,dest) and '[byte ' not in p['field']];by={v['field']:v for v in items};fields=['ip.ttl','ip.id','ip.len','ip.proto']+(['udp.srcport','udp.dstport','udp.length','udp.checksum'] if key[2].lower().startswith('udp') else ['icmp.type','icmp.code','icmp.ident','icmp.seq','icmp.checksum'] if key[2].lower().startswith('icmp') else ['tcp.srcport','tcp.dstport','tcp.flags','tcp.seq_raw','tcp.ack_raw','tcp.len','tcp.checksum'])
        s=r'\Needspace{9\baselineskip}'+'\n'+heading(' / '.join(key),'subsubsection')+para('Ejemplo: '+labels[dest]+'. Entrenamiento: '+r['run_id']+'; contraste: rondas 2 y 3. Las reglas completas de los tres destinos están en el archivo de predicciones enlazado en el anexo.')
        rows=[]
        for field in fields:
            item=by.get(field)
            if not item:continue
            rule=item['rule'];kind=rule['kind'];desc={'constant':'constante '+str(rule.get('value','')),'step':'incremento '+str(rule.get('delta',''))+' por paquete','block_step':'incremento '+str(rule.get('delta',''))+' cada '+str(rule.get('block_size',''))+' paquetes','variable':'variable en la captura','insufficient':'muestras insuficientes'}[kind];val='; '.join('r'+n+': '+{'passed':'cumple','insufficient':'insuficiente','not_predictable':'no exacto','failed':'no cumple'}.get(v['status'],v['status']) for n,v in item['validation'].items());rows.append([field,desc,val])
        s+=table(['Campo','Regla en ronda 1','Contraste posterior'],rows,[3.1,5.8,5.1])
        c=next(v for v in payload if (v['tool'],v['family'],v['method'],v['target'])==(*key,dest));t=c['training'];s+=para('Payload: '+str(t['lengths_bytes'])+' bytes. '+('No hay datos de aplicación en las sondas TCP observadas.' if t['zero_payload'] else 'Hexadecimal inicial (offset 0):'))
        if t.get('first_hex'):s+=r'\begin{quote}\ttfamily\footnotesize\raggedright '+ ' '.join(t['first_hex'][i:i+4] for i in range(0,len(t['first_hex']),4))+r'\end{quote}'+'\n'
        for seg in t['constant_ascii_segments']:s+=para('Texto ASCII desde offset '+str(seg['offset'])+': '+seg['ascii'])
        constraint=t.get('word_constraint')
        if constraint and constraint.get('stable_within_run'):s+=para('La suma de '+', '.join(constraint['fields'])+' módulo 65535 se mantuvo constante. La base se aprende del primer paquete de cada ejecución; no se presume universal. Es compatible con compensación de checksum, sin probar la intención del emisor.')
        priority=['udp.dstport','udp.srcport','icmp.seq','icmp.ident','tcp.seq_raw','tcp.ack_raw','tcp.srcport','tcp.dstport','ip.ttl','ip.id']
        candidates=[v for v in items if v['rule']['kind'] in ('step','block_step','constant') and v['field'] in priority and len(later)>=4 and all(p.get(v['field']) for p in later[:4])]
        example=min(candidates,key=lambda v:(v['rule']['kind']=='constant',priority.index(v['field']))) if candidates else None
        if example:
            field=example['field'];rule=example['rule'];baseval=later[0][field];vals=[p[field] for p in later[1:4]];base=int(baseval,16) if baseval.startswith('0x') else int(baseval) if baseval.isdigit() else baseval;pred=[rule['value']]*3 if rule['kind']=='constant' else [base+(i//rule.get('block_size',1))*rule['delta'] for i in (1,2,3)];s+=para('Predicción concreta en ronda 2, campo '+field+': la primera solicitud tiene valor '+baseval+'. Con la regla aprendida y esa base cuando corresponde, se predicen las solicitudes 2 a 4 antes de contrastarlas con sus valores observados.')+table(['Solicitud / trama','Predicción','Observación'],[[str(i+2)+' / '+later[i+1]['frame.number'],pred[i],vals[i]] for i in range(3)],[3.2,5.1,5.1])
        s+=para('Alcance: '+str(len(packets))+' solicitudes en el ejemplo inicial. Una verificación de campo o byte no equivale a una medición independiente; los campos variables conservan sus restricciones y no reciben valores inventados.')
        return s
    intro=heading('Introducción','section','sec:intro')+para('Este trabajo caracteriza las rutas de Internet utilizadas desde una conexión de banda ancha fija domiciliaria y compara la información revelada por Scamper y RIPE Atlas. Las preguntas son qué método descubre más interfaces por destino, qué cambia al invertir el sentido y qué patrones permiten reconocer las sondas en una captura.')+para('El objetivo es documentar observaciones reproducibles y su alcance. Una IP de respuesta representa una interfaz observada; no equivale por sí sola a un router físico. Los ASN se obtienen de asociaciones IP-prefijo y no constituyen una ruta BGP medida.')
    intro+=heading('Conexión de origen','subsection')+table(['Dato','Valor'],[['Proveedor comercial','WOM, confirmado por el estudiante'],['Ubicación aproximada','Quilicura, Región Metropolitana de Chile'],['IPv4 pública',pf['public_ipv4']],['Prefijo',pf['prefix']],['ASN',','.join('AS'+str(x) for x in pf['asns'])],['Sonda local','1018487'],['Interfaz',pf['route']['dev']]],[4.2,10.3])+para('La asociación IP-prefijo-AS proviene de RIPEstat y sus respuestas conservadas. La consulta en BGP HE del 27 de octubre de 2026 confirma AS52341 (WOM S.A.) y muestra los anuncios 186.189.80.0/20 y 186.189.89.0/24; se usa el más específico. Su captura y transcripción se incluyen en los anexos y en el manifiesto de fuentes. Las direcciones privadas y 100.88.0.1 observadas son compatibles con NAT; sin comprobar la WAN del router no se confirma CGNAT.')
    intro+=heading('Destinos y motivación','subsection')+table(['Destino','IPv4','Sonda'],[[labels[t['ip']],t['ip'],t['probe_id']] for t in targets],[3,6,3])+para('Se usan las alternativas admitidas por el enunciado actualizado. Valparaíso, La Habana y Rusia son los casos propuestos por el curso para contrastar contextos de conectividad. Las referencias del enunciado a velocidad y censura motivan la selección, pero estos traceroutes no miden velocidad de acceso ni demuestran censura. El destino ruso anterior, 90.150.251.81 / 870, se conserva como antecedente y queda fuera del análisis vigente. Se consideran tres destinos; la referencia del punto 4 a sí mismo se interpreta como una referencia al proceso bidireccional del punto 3.')
    intro+=r'\noindent Fuentes para la conexión de origen: RIPEstat \cite{ref4} y BGP HE \cite{ref7}; la motivación y los destinos proceden del enunciado \cite{ref8}.'+'\n'
    put('introduccion.tex',intro)
    met=heading('Metodología','section','sec:metodo')+heading('Entorno y herramientas')+para('Equipo Linux CachyOS en la conexión WOM domiciliaria. Scamper 20260902, sus conversores y las herramientas de captura se ejecutaron con Docker Compose. La sonda RIPE Atlas usa red del host, identidad persistente y una imagen fijada por digest. La versión y la configuración efectiva se conservan por ejecución. Las capturas se inspeccionaron en Wireshark 4.6.6 y se exportaron con TShark.')+para('Antes y después de cada ejecución se verificó la IPv4 pública esperada. El piloto contrastó WARTS, JSON, puertos, solicitudes emitidas y citas ICMP. Las mediciones relacionadas se ejecutaron secuencialmente, sin campañas locales superpuestas.')
    met+=heading('Diseño de mediciones')+table(['Familia','Por ronda','Tres rondas'],[['Scamper trace: seis métodos x tres destinos',18,54],['Scamper tracelb: cinco modos x tres destinos',15,45],['RIPE ida: tres protocolos x tres destinos',9,27],['RIPE vuelta: tres protocolos x tres destinos',9,27],['Total',51,153]],[10,2,2])+para('Las rondas son repeticiones completas, distintas de los paquetes por salto. Las rondas rusas se separaron al menos 30 minutos desde el cierre anterior. Los dos primeros destinos pertenecen a una campaña anterior; no se presentan como una instantánea simultánea con Rusia. Tras un reinicio durante la primera ronda rusa, el intento incompleto y seis resultados previos se conservaron y se repitió esa ronda completa. Las comparaciones temporales se realizan dentro de cada destino.')
    met+=heading('Sondas, puertos y comandos')+para('Scamper se limitó a 20 paquetes por segundo. TCP utilizó puerto de destino 80 y UDP base 33435, validada contra el piloto RIPE. RIPE mantuvo el resto de sus parámetros predeterminados y seleccionó sondas por ID exacto: 1018487 en ida y la sonda de cada destino en vuelta. Cada vuelta apuntó a 186.189.89.115. El apéndice conserva los comandos efectivos y las definiciones RIPE completas.')+r'''\begin{lstlisting}[caption={Forma de los comandos Scamper; los valores efectivos están en cada metadata.json.}]
scamper -p 20 -w 1 -O warts -o - \
  -c "trace -P METODO -d PUERTO" -i DESTINO
scamper -p 20 -w 1 -O warts -o - \
  -c "tracelb -P MODO -d PUERTO" -i DESTINO
# ICMP no necesita puerto de destino.
\end{lstlisting}
'''+para('Métodos trace: UDP, ICMP, UDP-Paris, ICMP-Paris, TCP y TCP-ACK. Modos tracelb: UDP-dport, ICMP-echo, UDP-sport, TCP-sport y TCP-ack-sport. Las opciones específicas y los valores predeterminados son parte del procedimiento de cada algoritmo, no se asumen equivalentes por compartir protocolo.')
    met+=heading('Captura, normalización y métricas')+para('Dumpcap guardó PCAPNG con un filtro de captura que incluyó ICMP y el destino. TShark separó solicitudes exteriores de las cabeceras originales citadas dentro de ICMP; se excluyeron paquetes RST de control al contar sondas TCP. En vuelta, la captura domiciliaria es parcial y no permite observar todos los paquetes emitidos remotamente.')+para('La unidad normalizada es una respuesta por intento y TTL. Se preservan respuestas múltiples, errores y ausencias. En las tablas, * significa timeout registrado, ? significa que la herramienta no registró la respuesta y -- indica ausencia de registro para ese TTL en esa ejecución; no significa que no se haya ejecutado el método. [priv./esp.] indica dirección no global y [AS n/d] asociación no disponible. Un TTL 255 separado no se une artificialmente al salto anterior.')+table(['Métrica','Definición y uso'],[['IP únicas','Conjunto de direcciones de respuesta de cada ejecución; no es cantidad de routers físicos.'],['Cobertura','Proporción de TTL registrados con al menos una respuesta, según la normalización.'],['Estabilidad','Jaccard entre conjuntos de IP de rondas; conjuntos vacíos no prueban estabilidad perfecta.'],['Costo','Sondas informadas en WARTS y solicitudes observadas en PCAP; en RIPE inverso no se reconstruye emisión remota.'],['Elección','Mediana de IP únicas por destino; cobertura y estabilidad como desempates.']],[3,11.3])+para('Las tablas principales usan la ronda 2; las estadísticas usan las tres rondas. Se incluyen las rondas 1 y 3 en anexos. El descubrimiento con más paquetes se informa junto con ese costo, sin atribuir toda diferencia al algoritmo.')
    met+=heading('Construcción y publicación de grafos')+para('Se eligió un par de ida/vuelta del mismo destino, protocolo, ronda e IPv4 de sesión. El criterio lexicográfico maximiza la unión de IP, minimiza huecos y minimiza separación temporal. Los grafos dirigidos conservan las referencias RIPE y distinguen interfaz, hueco y capa ambigua. Las aristas indican adyacencia inferida u orden de capas; no se forman productos cartesianos de respuestas múltiples. La publicación NDEx se comprobó sin credenciales y se conservó la copia exportada.')
    met+=r'\noindent Bases documentales: Scamper \cite{ref1}; captura y exportación \cite{ref2}; mediciones RIPE \cite{ref3}; asociación de ASN \cite{ref4}; publicación y formato de grafos \cite{ref5,ref6}. Los detalles experimentales provienen de los originales locales.'+'\n'
    put('metodologia.tex',met)
    s=''
    resulthead=heading('Resultados y análisis','section','sec:resultados')+heading('Path Discovery con Scamper','subsection','sec:scamper')
    comparisons=''
    for t in targets:
        dest=t['ip'];s+=r'\begin{landscape}'+'\n'+(resulthead if dest==targets[0]['ip'] else '')+heading(labels[dest]+' - '+dest,'subsubsection');s+=csvtable(analysis/'tablas'/f'tabla1_{dest}_r2.csv','Ruta observada con los seis métodos Scamper; '+labels[dest]+', ronda 2.','tabla1:'+dest,False,True);s+=para('Las IP se muestran por TTL y método. Las ausencias al final de un método no extienden artificialmente su recorrido. Los ASN y las respuestas por intento se conservan en los originales y anexos.');s+=r'\end{landscape}'+'\n';rt,g=ranktable(dest,'scamper','trace');comparisons+=heading(labels[dest],'paragraph')+rt
        best=min(map(score,g));winners=[v['method'] for v in g if score(v)==best];comparisons+=para('Método(s) más informativo(s) según el criterio definido: '+', '.join(winners)+'. El orden de la tabla usa las tres rondas; llegada al destino y estabilidad contextualizan el resultado. Los ceros TCP se interpretan con el diagnóstico de recepción de la sección de respuesta selectiva.')
    s+=heading('Comparación de los tres destinos','subsubsection')+comparisons
    put('scamper.tex',s)
    s=heading('Análisis de tráfico de los seis métodos trace','subsection','sec:trace-patrones')+para('Las siguientes seis fichas usan Valparaíso como ejemplo homogéneo y conservan comprobaciones de los tres destinos en la evidencia digital. Los valores en hexadecimal son bytes de aplicación; los encabezados TCP/UDP/ICMP se analizan por separado.')
    for m in TRACE_METHODS:s+=ficha(('scamper','trace',m))
    put('trace_patrones.tex',s)
    s=heading('tracelb: descubrimiento adicional y patrones','subsection','sec:lb')
    for t in targets:
        dest=t['ip'];s+=heading(labels[dest],'subsubsection');g=[v for v in adds if v['target']==dest];s+=table(['Modo','IP adicionales r1 / r2 / r3','Mediana sondas'],[[m,' / '.join(str(len(next(v for v in g if v['round']==n and v['method']==m)['additional_ips'])) for n in (1,2,3)),statistics.median([v['probes_sent'] for v in g if v['method']==m])] for m in LB_METHODS],[3.2,8,3]);s+=para('La referencia es la unión de los seis trace de la misma ronda y destino. IP adicionales observadas: '+('; '.join(m+': '+(', '.join(sorted({ip for v in g if v['method']==m for ip in v['additional_ips']})) or 'ninguna') for m in LB_METHODS))+'. Un aumento de IP revela interfaces adicionales bajo mayor exploración; no acredita por sí solo un menor costo por descubrimiento.')
    for m in LB_METHODS:s+=ficha(('scamper','tracelb',m))
    put('tracelb.tex',s)
    s=heading('Path Discovery con RIPE Atlas','subsection','sec:ripe')
    for t in targets:
        dest=t['ip'];s+=heading(labels[dest]+' - IP y ASN por salto','subsubsection');s+=csvtable(analysis/'tablas'/f'ripe_ida_{dest}_r2.csv','RIPE de ida: IP y ASN por TTL, '+labels[dest]+', ronda 2.','ripe:'+dest);rt,g=ranktable(dest,'ripe','traceroute');s+=rt;best=min(map(score,g));s+=para('Protocolo(s) elegido(s): '+', '.join(v['method'] for v in g if score(v)==best)+'. Se compara información observada de infraestructura, sin convertirla en una medición de velocidad o censura.')
    for m in RIPE_METHODS:s+=ficha(('ripe','traceroute',m))
    put('ripe.tex',s)
    s=heading('Path way: comparación de ida y vuelta','subsection','sec:vuelta')+para('Cada tabla conserva la numeración TTL desde su propio origen: las filas de ida y vuelta no identifican automáticamente el mismo router. Para comparar el orden se invierte por separado la secuencia de vuelta. Direcciones diferentes no demuestran equipos diferentes y no se identificaron alias de interfaces mediante una prueba independiente.')
    for t in targets:
        dest=t['ip'];s+=heading(labels[dest],'subsubsection');ss=[v for v in sym if v['target']==dest];s+=table(['Protocolo','IP ida r2','IP vuelta r2','Jaccard r2','Orden igual','Ruta completa'],[[m,next(v for v in ss if v['protocol']==m and v['round']==2)['ida_unique_ips'],next(v for v in ss if v['protocol']==m and v['round']==2)['vuelta_unique_ips'],f"{next(v for v in ss if v['protocol']==m and v['round']==2)['ip_jaccard']:.3f}",'sí' if next(v for v in ss if v['protocol']==m and v['round']==2)['observed_ip_layer_order_equal'] else 'no','no' if next(v for v in ss if v['protocol']==m and v['round']==2)['incomplete'] else 'sí'] for m in RIPE_METHODS],[2.1,1.7,2,2,2.2,2.7])
        for m in RIPE_METHODS:s+=csvtable(analysis/'tablas'/f'tabla2_{dest}_{m}_r2.csv','Tabla tipo 2: '+labels[dest]+' / '+m+', ronda 2.','tabla2:'+dest+':'+m)
        s+=para('El contraste corresponde a las rutas efectivamente observadas. Los huecos impiden concluir simetría completa; una coincidencia de AS tampoco demuestra identidad de routers ni una ruta BGP. Las tres rondas y las respuestas múltiples se conservan en el anexo.')
    put('vuelta.tex',s)
    s=heading('IPs con respuesta selectiva y diagnóstico TCP','subsection','sec:selectiva')
    for c in selective['cases']:
        v=c.get('candidate');s+=heading(c['tool'].upper(),'subsubsection')
        if not v:s+=para(c.get('limitation','Sin caso corroborado.'));continue
        s+=para('IP '+v['ip']+', destino '+v['target']+'. Se observó con '+v['responds_method']+' y no se observó con '+v['not_observed_method']+' en las rondas y ventanas TTL comparables registradas. Resultado de repetición: '+c['status']+'.')+table(['Método','Repetición','IP observada','Run / ID RIPE'],[[r['method'],r['repeat'],'sí' if r['ip_observed'] else 'no',r['run_id']+(' / '+str(r['measurement_id']) if r.get('measurement_id') else '')] for r in c['additional_runs']],[1.5,1.8,2.2,8.7])+para('Hipótesis: comportamiento dependiente del protocolo, posible filtrado o política de respuesta. El protocolo con respuesta permite observar esa IP en este experimento. No se demostró una ACL concreta: otra ruta, balanceo o pérdida también pueden explicar la ausencia. Las pruebas corroboran el contraste observado, no una regla de firewall.')
    diag=read(ROOT/'resultados/correlacion_tcp_captura.json')['summary'];ch=read(ROOT/'resultados/checksums_tcp.json')['runs'];s+=heading('Discrepancia de recepción TCP','subsubsection')+para('En '+str(diag['reviewed_scamper_tcp_runs'])+' ejecuciones Scamper TCP se correlacionaron respuestas ICMP por direcciones, IPID, puertos y tiempo, pero no se incorporaron como saltos aceptados en WARTS. Se conserva el resultado de la herramienta separado de la captura. El control revisó '+str(sum(r['checked'] for r in ch))+' tramas TCP exteriores completas, incluidos RST de control, sin checksums TCP inválidos. Este conteo no equivale a sondas emitidas.')+para('El control adicional con ICMP-rxerr finalizó con stop_reason ERROR, mensaje de tipo no soportado y cero sondas. Se conserva como diagnóstico fallido y no cuenta como ruta válida. Su existencia no prueba filtrado ni corrige retrospectivamente los WARTS anteriores.')
    r,pk=packetrows(('scamper','trace','udp'),1)
    full=read(ROOT/exports[r['run_id']]/'packets_full.json')
    quoted=next(q['_source']['layers'] for q in full if q['_source']['layers'].get('icmp',{}).get('icmp.type')=='11' and q['_source']['layers']['icmp'].get('ip',{}).get('ip.dst')==targets[0]['ip'])
    ic=quoted['icmp'];inner=ic['ip'];udp=ic['udp']
    s+=heading('Lectura de la cabecera citada en ICMP','subsubsection')+para('Ejemplo trazable: '+r['run_id']+', trama '+quoted['frame']['frame.number']+'. La respuesta exterior procede de '+quoted['ip']['ip.src']+' y tiene tipo/código ICMP '+ic['icmp.type']+'/'+ic['icmp.code']+'. Dentro de ICMP se cita la solicitud original: destino '+inner['ip.dst']+', TTL '+inner['ip.ttl']+', IPID '+inner['ip.id']+', UDP '+udp['udp.srcport']+' a '+udp['udp.dstport']+'. El TTL exterior pertenece a la respuesta; no sustituye al TTL citado. La coincidencia se comprueba contra el paquete emitido, sus puertos, identificador y tiempo.')
    s+=para('En las fichas, ip.proto 1 identifica ICMP, 6 TCP y 17 UDP; ICMP 8/0 es Echo Request. Los flags TCP 0x0002 y 0x0010 corresponden respectivamente a SYN y ACK. Las secuencias se leen con valores absolutos, evitando confundir la numeración relativa de la interfaz gráfica con el valor transmitido.')
    put('selectiva.tex',s)
    s=''
    publichead=heading('Public Path: selección y publicación','subsection','sec:publicacion')
    for t in targets:
        dest=t['ip'];sel=read(analysis/'grafos'/f'{dest}.selection.json');pub=publications.get(dest);cx=read(analysis/'grafos'/f'{dest}.cx2.json');graphpdf(cx,out/'figuras'/f'grafo_{dest}.pdf');pair=[next(r for r in runs if r['run_id']==rid) for rid in sel['runs']];s+=r'\begin{landscape}'+'\n'+(publichead if dest==targets[0]['ip'] else '')+heading(labels[dest],'subsubsection')+para('Par elegido: '+pair[0]['method']+', ronda '+str(pair[0]['round'])+'. Unión de '+str(len(set(pair[0]['ips'])|set(pair[1]['ips'])))+' IP; '+str(pair[0]['missing_hops']+pair[1]['missing_hops'])+' TTL sin respuesta en conjunto. Ida '+str(sel['ids'][0])+'; vuelta '+str(sel['ids'][1])+'.')
        if pub:s+=para('UUID: '+pub['uuid'])+r'\noindent\url{'+pub['url']+r'}\par\medskip'+'\n'
        s+=r'\includegraphics[width=\linewidth,height=.62\textheight,keepaspectratio]{figuras/grafo_'+dest+r'.pdf}'+'\n'+r'\captionof{figure}{'+tex('Representación vectorial del mismo CX2 publicado, '+labels[dest]+'. Las flechas indican sentido; las aristas son inferidas. Las capturas reales de NDEx se incluyen en el anexo.')+'}\\label{grafo:'+dest+'}\n'+r'\end{landscape}'+'\n'
    put('publicacion.tex',s)
    s=heading('Conclusión','section','sec:conclusion')+para('Las tres rondas muestran que el método más informativo depende del destino y del criterio aplicado. La comparación se apoya en medianas de IP únicas, cobertura y estabilidad, y conserva el costo de exploración.')
    for t in targets:
        dest=t['ip'];parts=[]
        for tool,fam in (('scamper','trace'),('ripe','traceroute')):
            g=[v for v in rank if v['target']==dest and v['tool']==tool and v['family']==fam and v['direction']=='ida'];best=min(map(score,g));w=[v for v in g if score(v)==best];parts.append(tool+': '+', '.join(v['method'] for v in w)+' (mediana '+str(w[0]['median_unique_ips'])+' IP)')
        s+=para(labels[dest]+': '+'; '.join(parts)+'.')
    s+=para('tracelb permite revelar interfaces adicionales en algunos modos y destinos, con distinto costo en sondas. Las diferencias entre Chile, Cuba y Rusia describen las rutas y horarios medidos; no deben interpretarse como una clasificación de velocidades o de censura.')+para('Ida y vuelta no ofrecieron evidencia suficiente para afirmar simetría completa en las rutas incompletas. Las observaciones corresponden a interfaces; la identificación de routers físicos requiere corroboración adicional de alias. La respuesta selectiva sí se repitió en los casos documentados, pero no identifica por sí sola una regla de filtrado.')+para('El aprendizaje principal es que la calidad de Path Discovery depende tanto del método como de la captura, la recepción local y la trazabilidad. Para repetir el estudio conviene preservar originales, contrastar parámetros efectivos, verificar la continuidad de la sesión y comparar pares próximos temporalmente. El diagnóstico TCP demuestra por qué una ausencia en la salida de una herramienta debe contrastarse con los paquetes antes de atribuirla a la red.')
    put('conclusion.tex',s)
    s=heading('Anexos','section','sec:anexos')+heading('Imágenes de Wireshark y NDEx','subsection','anexo:imagenes')+para('Las siguientes capturas corresponden a la interfaz gráfica real. Cada una está vinculada a un original y a su hash en el inventario digital. Son evidencia complementaria; los valores legibles y las reglas se desarrollan en el cuerpo principal.')
    ids={r['run_id'] for r in runs}
    for entry in review['reviewed_runs']:
        if entry['run_id'] not in ids:continue
        path=asset(entry['screenshot']);s+=r'\begin{landscape}'+'\n'+r'\includegraphics[width=\linewidth,height=.83\textheight,keepaspectratio]{'+path+'}\n'+r'\captionof{figure}{'+tex('Wireshark: '+entry['method']+'. Original '+entry['run_id']+'. Encabezados y bytes observados; el contraste temporal se realiza con las rondas posteriores.')+'}\n'+r'\end{landscape}'+'\n'
    for name in ('capturas/bgp_he_origen.jpg','capturas/ndex_valparaiso_publico.jpg','capturas/ndex_habana_publico.jpg','capturas/ndex_rusia_publico.jpg','capturas/ndex_tres_grafos_publicos.jpg'):
        if (ROOT/name).exists():s+=r'\begin{landscape}'+'\n'+r'\includegraphics[width=\linewidth,height=.82\textheight,keepaspectratio]{'+asset(name)+'}\n'+r'\captionof{figure}{'+tex(captionmap.get(name,'NDEx: evidencia de visualización y publicación.'))+'}\n'+r'\end{landscape}'+'\n'
    s+=heading('Comandos completos, tablas y originales','subsection','anexo:originales')+para('Los WARTS, JSON y PCAPNG se entregan como archivos digitales para conservar la evidencia completa sin imprimir miles de registros. El manifiesto de fuentes enlaza cada tabla y figura con su archivo, versión y hash. Se conserva una respuesta por intento y TTL; las tablas siguientes compactan las respuestas múltiples por celda.')
    s+=heading('Comandos efectivos por método','subsubsection')
    used=set()
    for r in runs:
        k=(r['tool'],r['family'],r['method'],r['direction'])
        if k in used:continue
        used.add(k);m=read(ROOT/'datos/originales'/r['run_id']/'metadata.json');s+=r'\paragraph{'+tex(' / '.join(k))+'}\n'
        if r['tool']=='scamper':s+=r'\begin{lstlisting}'+'\n'+shlex.join(m['command'])+'\n'+r'\end{lstlisting}'+'\n'
        else:
            req=ROOT/'datos/originales'/r['run_id']/'request.json'
            if req.exists():s+=r'\begin{lstlisting}'+'\n'+json.dumps(read(req),ensure_ascii=False,indent=2)+'\n'+r'\end{lstlisting}'+'\n'
    s+=heading('Índice de las 153 ejecuciones','subsubsection')+table(['Destino','Ronda','Método / sentido','ID RIPE','Original'],[[labels[r['target']],r['round'],r['family']+' / '+r['method']+' / '+r['direction'],r.get('measurement_id') or '--',r['run_id']] for r in runs],[2,1.15,4.2,2.2,4.95])
    s+=heading('Tablas completas de las rondas 1 y 3','subsubsection')
    for t in targets:
        dest=t['ip']
        for n in (1,3):
            s+=r'\begin{landscape}'+'\n'+csvtable(analysis/'tablas'/f'tabla1_{dest}_r{n}.csv',labels[dest]+': seis métodos trace, ronda '+str(n)+'.','anexo:trace:'+dest+':'+str(n),False,True)+r'\end{landscape}'+'\n'
            s+=csvtable(analysis/'tablas'/f'ripe_ida_{dest}_r{n}.csv',labels[dest]+': RIPE ida, ronda '+str(n)+'.','anexo:ripe:'+dest+':'+str(n))
            for m in RIPE_METHODS:s+=csvtable(analysis/'tablas'/f'tabla2_{dest}_{m}_r{n}.csv',labels[dest]+': ida/vuelta '+m+', ronda '+str(n)+'.','anexo:vuelta:'+dest+':'+m+':'+str(n))
    s+=heading('Matriz de rúbrica y evidencia','subsubsection')
    criteria=[('1.1',6,'sec:scamper'),('1.2',6,'sec:scamper'),('1.3',18,'sec:trace-patrones'),('1.4',6,'sec:selectiva'),('1.5',5,'sec:lb'),('1.6',5,'sec:lb'),('1.7',15,'sec:lb'),('2.1',3,'sec:ripe'),('2.2',3,'sec:ripe'),('2.3',18,'sec:ripe'),('2.4',3,'sec:selectiva'),('3.1 interfaces',6,'sec:vuelta'),('3.1 comparación',6,'sec:vuelta'),('4.1',6,'sec:publicacion'),('4.2',4,'sec:publicacion'),('4.3',6,'sec:publicacion'),('5',4,'sec:intro')]
    s+=r'\begin{longtable}{p{3cm}p{2cm}p{9cm}}\toprule Criterio & Puntos & Localización \\ \midrule\endhead'+'\n'
    for c,points,label in criteria:s+=tex(c)+' & '+str(points)+r' & Sección \ref{'+label+r'}, página \pageref{'+label+r'}. \\'+'\n'
    s+=r'\bottomrule\end{longtable}'+'\n'+para('La matriz localiza evidencia, no asigna una calificación. La identidad de interfaces del mismo router y la existencia de una ACL concreta no se demostraron; se informa expresamente esa limitación. La evaluación del cumplimiento corresponde al docente.')
    s+=heading('Referencias','subsection','anexo:referencias')
    refs=[('CAIDA','Scamper y manual de la versión utilizada','https://www.caida.org/catalog/software/scamper/'),('Wireshark','Documentación y manual de TShark','https://www.wireshark.org/docs/man-pages/tshark.html'),('RIPE Atlas','Documentación de sondas y mediciones','https://atlas.ripe.net/docs/'),('RIPEstat','API network-info: asociación IP, prefijo y ASN','https://stat.ripe.net/docs/data-api/api-endpoints/network-info'),('NDEx','Documentación de la API','https://www.ndexbio.org/docs/using-the-ndex-api/'),('Cytoscape','Especificación CX2 y estilos visuales','https://cytoscape.org/cx/cx2/'),('BGP HE','BGP Toolkit: consulta de la IP de origen, 27 de octubre de 2026','https://bgp.he.net/ip/186.189.89.115')]
    s+=r'\renewcommand{\refname}{}\begin{thebibliography}{8}'+'\n'
    for i,(author,title,url) in enumerate(refs,1):s+=r'\bibitem{ref'+str(i)+'} '+tex(author+'. '+title+'. ')+r'\url{'+url+r'}.'+'\n'
    s+=r'\bibitem{ref8} '+tex('Enunciado actualizado y rúbrica de Tarea Individual, material suministrado por el curso, conservado con SHA-256. Webinar Medir para mejorar, material de clase proporcionado por el estudiante; referencia conceptual histórica de RIPE Atlas.')+'\n'+r'\end{thebibliography}'+'\n'
    put('anexos.tex',s)
    sections=['introduccion','metodologia','scamper','trace_patrones','tracelb','ripe','vuelta','selectiva','publicacion','conclusion','anexos']
    for name in sections:
        p=out/'secciones'/f'{name}.tex'
        if not p.exists():p.write_text('\\input{datos/'+name+'.tex}\n')
    main=r'''\documentclass[12pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[spanish,es-tabla]{babel}
\usepackage{lmodern,microtype,amsmath,amssymb,graphicx,booktabs,longtable,array,pdflscape,caption,xcolor,listings,fancyhdr,geometry,enumitem,needspace}
\geometry{left=2.5cm,right=2.5cm,top=2.4cm,bottom=2.4cm}
\usepackage[hidelinks]{hyperref}
\usepackage{xurl}
\setlength{\parindent}{0pt}
\setlength{\parskip}{5pt}
\emergencystretch=2em
\setlength{\headheight}{16pt}
\setlength{\tabcolsep}{3pt}
\renewcommand{\arraystretch}{1.08}
\definecolor{azul}{HTML}{173D5C}
\definecolor{backcolour}{rgb}{.95,.95,.92}
\definecolor{codegreen}{rgb}{0,.6,0}
\definecolor{codegray}{rgb}{.5,.5,.5}
\definecolor{codepurple}{rgb}{.58,0,.82}
\lstdefinestyle{mystyle}{backgroundcolor=\color{backcolour},commentstyle=\color{codegreen},keywordstyle=\color{magenta},numberstyle=\tiny\color{codegray},stringstyle=\color{codepurple},basicstyle=\ttfamily\footnotesize,breaklines=true,captionpos=b,keepspaces=true,numbers=left,numbersep=5pt,showstringspaces=false,tabsize=2,columns=fullflexible}
\lstset{style=mystyle}
\captionsetup{font=small,labelfont=bf}
\renewcommand{\refname}{}
\pagestyle{fancy}\fancyhf{}\lhead{\small Algoritmos de Ruteo}\rhead{\small Path Discovery}\cfoot{\thepage}
\hypersetup{pdftitle={Tarea individual: Path Discovery},pdfauthor={Diego Muñoz}}
\begin{document}
\begin{titlepage}\centering
\vspace*{2cm}
{\Large Algoritmos de Ruteo\par}\vspace{1.5cm}
{\Huge\bfseries\color{azul} Tarea individual\par}\vspace{.5cm}
{\LARGE Path Discovery\par}\vspace{.6cm}
{\large Comparación de Scamper y RIPE Atlas\par}
\vfill
{\large Integrante: Diego Muñoz\par}\vspace{.5cm}
{\large Profesor: Nicolas Boettcher\par}
\vfill
{\large 27 de octubre de 2026\par}
\vspace{.6cm}
{\small Banda ancha fija domiciliaria WOM, Quilicura, Chile\par}
\end{titlepage}
\pagenumbering{roman}\tableofcontents\clearpage
\pagenumbering{arabic}
'''
    for name in sections:
        if name in ('introduccion','metodologia','conclusion','anexos'):main+='\\clearpage\n'
        main+='\\input{secciones/'+name+'.tex}\n'
    main+='\\end{document}\n';(out/'main.tex').write_text(main)
    provenance={'generated_at':utc(),'analysis':str(analysis),'analysis_relative':str(analysis.relative_to(ROOT)),'analysis_manifest_sha256':sha256(analysis/'manifest.json'),'dataset_id':summary['dataset_id'],'campaign_status':{'completed':len(runs),'public_graphs':list(publications.values())},'files':sources,'generated_files':{str(p.relative_to(out)):sha256(p) for p in sorted(out.rglob('*')) if p.is_file() and p.suffix in ('.tex','.jpg','.pdf') and 'build' not in p.relative_to(out).parts and p.name!='informe.pdf'},'author':'Diego Muñoz','teacher':'Nicolas Boettcher','main_tables_round':2,'draft':a.draft,'limitations':['No se demostró alias de interfaces del mismo router.','Respuesta selectiva no demuestra ACL.','La asociación de ASN no es una ruta BGP observada.']};(out/'fuentes.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'project':str(out),'measurements':len(runs),'public_graphs':len(publications),'files':len(sources)},ensure_ascii=False))
if __name__=='__main__':main()
