"""Informe de estado y resultados, con cobertura explícita de la campaña."""
import json
from pathlib import Path
from xml.sax.saxutils import escape

from .common import ROOT, config, identifier, json_write, utc


def generate_report(status):
    cfg = config()
    folder = ROOT / "informe" / ("reporte_" + identifier())
    folder.mkdir(parents=True)
    preflights = sorted((ROOT / "datos/originales").glob("preflight_*/preflight.json"))
    preflight = json.loads(preflights[-1].read_text()) if preflights else {}
    analyses = sorted((ROOT / "resultados").glob("analisis_*/summary.json"))
    analysis = analyses[-1].parent if analyses else None
    title = "Informe de Path Discovery" if status["scientific_results_complete"] else "Informe de avance de Path Discovery"
    sections = [(title, [f"Generado en UTC: {utc()}",
               f"Campaña principal: {status['completed']} de 153 combinaciones con evidencia válida. Pilotos válidos: {status['pilots']}.",
               "La tarea sigue abierta hasta completar las mediciones, el análisis de paquetes y las tres publicaciones públicas."])]
    if not cfg.get("baf_confirmed"):
        sections[0][1].append("El usuario confirmó que está conectado a la universidad. Las mediciones académicas están pendientes hasta conectarse a la banda ancha fija de casa; la sonda Docker fue detenida. El preflight inicial es diagnóstico de la red universitaria.")
    connection = [f"IPv4 pública observada: {preflight.get('public_ipv4', 'pendiente')}",
                  f"Prefijo: {preflight.get('prefix', 'pendiente')}. ASN: {preflight.get('asns', [])}.",
                  f"ISP comercial: {cfg.get('isp_comercial') or 'pendiente de confirmar por el usuario'}. NAT/CGNAT: {preflight.get('nat', 'pendiente')}.",
                  "Tres destinos y tres rondas. Scamper 20260902, seis métodos trace y cinco tracelb; RIPE UDP/ICMP/TCP en ambos sentidos.",
                  "Se conservan las IP del enunciado. Las referencias a cuatro IP y al punto 4 se interpretan como errores de edición; se requiere aclaración docente para sustituir sondas."]
    sections.append(("Entorno y metodología", connection))
    sections.append(("Dependencias pendientes", preflight.get("blockers", []) or ["No hay bloqueos detectados por preflight. La revisión manual sigue siendo necesaria."]))
    sections.append(("1 Path Discovery Scamper", ["Comparación prevista: IP únicas, cobertura de saltos, llegada al destino y estabilidad entre rondas. Las rutas incompletas se conservan.",
                    "Los pilotos y los intentos fallidos se identifican explícitamente y no se cuentan dentro de las 153 combinaciones."]))
    if analysis:
        info = json.loads((analysis / "summary.json").read_text())
        if info.get("includes_pilots"):
            sections[-1][1].append("El análisis más reciente contiene pilotos. Sus métricas no acreditan resultados de la campaña principal; la validez de la conexión y las exclusiones se conservan en la metadata de cada ejecución.")
        rankings = json.loads((analysis / "rankings.json").read_text())
        sections[-1][1].append(f"Análisis reproducible disponible en {analysis.relative_to(ROOT)}.")
        for r in rankings:
            sections[-1][1].append(f"{r['target']} {r['tool']} {r['family']} {r['method']} {r['direction']}: mediana IP únicas {r['median_unique_ips']}, cobertura {r['median_coverage']:.1%}, rondas {r['rounds']}.")
    else:
        sections[-1][1].append("Todavía no se ha generado un análisis; no se atribuye superioridad a ningún método.")
    sections.append(("2 Path Discovery RIPE", ["Requiere sonda local registrada, créditos, API key y sondas remotas consistentes con el enunciado.",
                    "Las solicitudes conservarán los parámetros predeterminados salvo protocolo, extremos y puerto TCP 80. Los ASN por IP se consultarán en RIPEstat con fecha y respuesta original."]))
    sections.append(("3 Path way RIPE", ["Se requieren nueve pares por ronda: tres destinos por tres protocolos. Cada par debe compartir IPv4 pública, ronda y protocolo.",
                    "Las tablas preservan TTL desde cada origen. Una diferencia entre IP de interfaces no prueba por sí sola que los routers sean diferentes.",
                    "La captura en el equipo local de una medición inversa es parcial; el resultado RIPE remoto es la evidencia del recorrido."]))
    sections.append(("4 Public Path", [f"Grafos públicos registrados: {len(status['public_graphs'])}.",
                    "Cada grafo debe citar los dos IDs RIPE de su par de ida y vuelta. Se preservarán los huecos y los saltos ambiguos; no se crearán conexiones físicas no observadas."]))
    for item in status["public_graphs"]:
        sections[-1][1].append(f"Destino {item['target']}: UUID {item['uuid']}; mediciones {item['measurement_ids']}; {item['url']}")
    sections.append(("Análisis de transporte y payload", ["Las exportaciones TShark conservan encabezados, bytes completos, payloads y citas ICMP. Las reglas constantes e incrementales aprendidas en ronda 1 se contrastan con las rondas 2 y 3.",
                    "Los candidatos de respuesta selectiva requieren pruebas dirigidas y revisión de PCAP. La ausencia de una IP en un traceroute no demuestra una regla de firewall.",
                    "La correlación de resultados y capturas está implementada. El análisis completo de catorce métodos permanece pendiente hasta disponer de sus mediciones."]))
    sections.append(("Referencias", ["Enunciado original conservado con hash en datos/originales/enunciado/.",
                    "https://www.caida.org/catalog/software/scamper/",
                    "https://atlas.ripe.net/docs/",
                    "https://stat.ripe.net/docs/data-api/api-endpoints/network-info",
                    "https://www.ndexbio.org/rest/swagger/index.html"]))
    text = "\n\n".join(("# " if i == 0 else "## ") + name + "\n\n" + "\n\n".join(paragraphs) for i, (name, paragraphs) in enumerate(sections)) + "\n"
    (folder / "informe.md").write_text(text)
    json_write(folder / "estado.json", status)
    pdf = None
    try:
        from reportlab.lib import colors
        from reportlab.lib.enums import TA_LEFT
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        font = Path("/usr/share/fonts/TTF/DejaVuSans.ttf")
        if not font.exists():
            font = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
        fontname = "Helvetica"
        if font.exists():
            pdfmetrics.registerFont(TTFont("PDDejaVu", str(font)))
            fontname = "PDDejaVu"
        styles = getSampleStyleSheet()
        for s in ("Title", "Heading2", "BodyText"):
            styles[s].fontName = fontname
            styles[s].textColor = colors.black
        styles["BodyText"].fontSize = 10
        styles["BodyText"].leading = 15
        styles["BodyText"].spaceAfter = 8
        styles["BodyText"].wordWrap = "CJK"
        story = []
        for i, (name, paragraphs) in enumerate(sections):
            story.append(Paragraph(escape(name), styles["Title" if i == 0 else "Heading2"]))
            for p in paragraphs:
                story.append(Paragraph(escape(p), styles["BodyText"]))
            story.append(Spacer(1, 8))
        pdf = folder / "informe.pdf"
        SimpleDocTemplate(str(pdf), pagesize=A4, leftMargin=48, rightMargin=48, topMargin=44, bottomMargin=44, title=title).build(story)
    except ImportError:
        pass
    return {"markdown": str(folder / "informe.md"), "pdf": str(pdf) if pdf else None, "campaign_complete": status["scientific_results_complete"]}
