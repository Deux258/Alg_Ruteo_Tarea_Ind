#!/usr/bin/env python3
"""Regenerar y compilar el informe con Docker sin red y comparar los artefactos."""
import argparse,hashlib,json,subprocess
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(*args):subprocess.run(['docker','compose','-f','compose.latex.yaml','run','--rm',*args],cwd=ROOT,check=True)
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--analysis',required=True);ap.add_argument('--evidence',default='config/evidencia_informe.json');ap.add_argument('--reference',default='informe/latex');ap.add_argument('--output',default='informe/latex_reproduccion');a=ap.parse_args()
    paths=[(ROOT/p).resolve() for p in (a.analysis,a.evidence,a.reference,a.output)]
    if not all(p.is_relative_to(ROOT) for p in paths):raise ValueError('Las rutas deben pertenecer al proyecto')
    analysis,evidence,reference,out=paths
    if out==reference or not out.is_relative_to(ROOT/'informe'):raise ValueError('Usar una carpeta separada dentro de informe/')
    rel=lambda p:'/work/'+str(p.relative_to(ROOT))
    run('latex','python3','/work/scripts/generar_informe_latex.py','--analysis',rel(analysis),'--evidence',rel(evidence),'--output',rel(out))
    run('--workdir',rel(out),'latex')
    provenance=json.loads((reference/'fuentes.json').read_text());compared=[]
    for name,expected in provenance['generated_files'].items():
        if digest(reference/name)!=expected or digest(out/name)!=expected:raise ValueError('Artefacto diferente: '+name)
        compared.append(name)
    pdf=reference/'build/main.pdf';replay=out/'build/main.pdf'
    if digest(pdf)!=digest(replay):raise ValueError('El PDF regenerado no es idéntico; revisar imagen, fuentes y SOURCE_DATE_EPOCH')
    proof={'verified_at':datetime.now(timezone.utc).isoformat(),'analysis':str(analysis.relative_to(ROOT)),'reference':str(reference.relative_to(ROOT)),'generated_files_identical':compared,'pdf_byte_identical':True,'pdf_sha256':digest(pdf),'network_policy':'Generación y compilación con network_mode: none en Docker Compose','image_id':subprocess.check_output(['docker','image','inspect','path-discovery-latex:bookworm','--format','{{.Id}}'],text=True).strip()}
    target=ROOT/'resultados/reproduccion_informe_latex.json';target.write_text(json.dumps(proof,ensure_ascii=False,indent=2)+'\n');print(json.dumps({'proof':str(target),'identical_sources':len(compared),'pdf_byte_identical':True}))
if __name__=='__main__':main()
