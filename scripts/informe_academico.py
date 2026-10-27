#!/usr/bin/env python3
"""Generar el informe desde evidencia real; los huecos se declaran como pendientes."""
import argparse
import csv
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path
from xml.sax.saxutils import escape

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from path_discovery.common import ROOT, config, utc, verify_manifest
from path_discovery.cli import status


def image_caption(path):
    index_path = ROOT / "capturas/indice.json"
    index = json.loads(index_path.read_text()) if index_path.exists() else []
    relative = str(Path(path).relative_to(ROOT))
    item = next((i for i in index if i["file"] == relative), {})
    return item.get("caption", Path(path).stem.replace("_", " "))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("analysis")
    args = parser.parse_args()
    analysis = Path(args.analysis).resolve()
    verify_manifest(analysis)
    summary = json.loads((analysis / "summary.json").read_text())
    if summary.get("includes_pilots"):
        raise ValueError(
            "El informe académico requiere análisis de campaña sin pilotos"
        )
    runs = json.loads((analysis / "runs.json").read_text())
    rank = json.loads((analysis / "rankings.json").read_text())
    additions = json.loads((analysis / "tracelb_additional.json").read_text())
    symmetry = json.loads((analysis / "symmetry.json").read_text())
    cfg = config()
    if cfg.get("session_public_ipv4") and any(r.get("public_ipv4") != cfg["session_public_ipv4"] for r in runs):
        raise ValueError("El análisis pertenece a otra sesión; no combinar con el entorno y las capturas actuales")
    state = status()
    out = ROOT / "informe/path_discovery"
    out.mkdir(parents=True, exist_ok=True)
    blocks = []

    def heading(text):
        blocks.append(("heading", text))

    def para(text):
        blocks.append(("paragraph", text))

    def table(headers, rows):
        blocks.append(("table", [headers, *[[str(v) for v in row] for row in rows]]))

    def csvtable(path):
        if not path.exists():
            para("Pendiente de medir en esta sesión; tabla aún sin evidencia.")
            return
        with path.open() as f:
            rows = list(csv.reader(f))
        if len(rows) > 1:
            blocks.append(("table", rows))
        else:
            para("Sin resultados disponibles para esta tabla.")

    title = "Path Discovery: comparación de Scamper y RIPE Atlas"
    heading(title)
    para(
        "Tarea individual - Algoritmos de Ruteo. Fuente del enunciado: Tarea Individual.docx, conservada con hash. Fecha de elaboración en UTC: "
        + utc()
        + "."
    )
    para(
        f"Estado de campaña al generar: {state['completed']}/153; esta edición analiza {len(runs)} ejecuciones principales válidas; {state['pilots']} pilotos conservados y separados; {len(state['public_graphs'])}/3 grafos públicos registrados. El documento es de avance mientras queden evidencias pendientes."
    )
    heading("Entorno, adaptación de destinos y trazabilidad")
    pf = json.loads((ROOT / "resultados/preflight_campana.json").read_text())
    para(
        f"Banda ancha fija domiciliaria en Quilicura, proveedor comercial WOM confirmado por el estudiante. IPv4 pública {pf['public_ipv4']}; prefijo {pf['prefix']}; ASN {', '.join('AS'+str(a) for a in pf['asns'])}. La salida se contrastó con dos servicios y se verificó antes y después de cada ejecución. Interfaz {pf['route']['dev']}; sincronización horaria {pf['clock_synced']}."
    )
    para(
        "La presencia de 100.88.0.1 y direcciones privadas en el recorrido es compatible con NAT del operador. No se verificó la dirección WAN del router y no se confirma CGNAT. La falta de respuesta inversa no permite atribuir una causa por sí sola."
    )
    table(
        ["Caso", "IP del enunciado / sonda", "IP activa / sonda"],
        [
            ["Valparaíso", "138.204.228.2 / 31416", "138.204.230.242 / 6652"],
            ["Habana", "200.14.48.134 / 12734", "200.14.48.134 / 12734"],
            [
                "Rusia",
                "37.79.153.66 / 870",
                next(t["ip"] for t in cfg["targets"] if t["probe_id"] == 870)
                + " / 870",
            ],
        ],
    )
    para(
        "El estudiante autorizó reemplazar 31416, cuyo estado público es Abandoned desde 2025-12-14. Se eligió 6652, conectada y del mismo AS61506, con ubicación declarada en Valparaíso a aproximadamente 0,29 km de la original. Cambia el extremo y el prefijo; no se afirma que sean el mismo equipo o edificio. No se atribuye esta decisión al docente ni se interpreta la indisponibilidad como un fallo de RIPE o del ISP."
    )
    para(
        "Para Rusia se autorizó actualizar la IPv4 de la misma sonda 870. La API se consulta antes de medir para evitar pares incoherentes. Los cambios están documentados en docs/CAMBIOS_DESTINOS.md y la configuración original permanece en config/campana_enunciado.json."
    )
    para(
        "Se trabajan tres destinos, conforme a la tabla del enunciado. Las menciones a cuatro IP y al punto 4 como origen de los pares se interpretan como errores de edición. Las motivaciones sobre velocidad y censura no son hipótesis demostradas por estos traceroutes."
    )
    gui_review = ROOT / "resultados/revision_wireshark_gui.json"
    if gui_review.exists():
        reviewed = json.loads(gui_review.read_text())
        para(
            "Revisión gráfica adicional de la campaña: "
            + str(len(reviewed.get("reviewed_runs", [])))
            + " PCAP inspeccionados en Wireshark gráfico real, con capturas y procedencia en resultados/revision_wireshark_gui.json."
        )
    heading("Diseño de la campaña y controles")
    para(
        "El diseño prevé tres rondas completas, separadas por al menos treinta minutos desde el cierre de la anterior. Cada ronda: 18 trace, 15 tracelb, 9 RIPE de ida y 9 de vuelta. Las duraciones informadas son tiempos de ejecución de pared, incluyendo espera y procesamiento; el envío remoto no se reconstruye desde una captura local inversa. Se ejecuta una sola medición local por vez; Scamper tiene límite global de 20 paquetes/s. TCP usa puerto 80; UDP usa base 33435. RIPE conserva los demás parámetros predeterminados y selecciona IDs exactos de sonda."
    )
    incident = ROOT / "docs/INCIDENTES_CAMPANA.md"
    if incident.exists():
        for line in incident.read_text().splitlines():
            if not line.strip():
                continue
            if line.startswith("#"):
                heading(line.lstrip("# ").strip())
            else:
                para(line.replace("`", ""))
    para(
        "Scamper 20260902 se construyó con verificación SHA-256. Las herramientas y la sonda se gestionan con Docker Compose; la imagen de la sonda está fijada por digest, con red del host e identidad persistente. La sonda local es 1018487. Se habilitaron créditos y una API key de permiso limitado, almacenada fuera de Git y de la entrega."
    )
    para(
        "La validación del piloto incluyó WARTS, JSON, PCAPNG, puertos, citas ICMP y correlación temporal. La inspección reproducible se realizó con TShark, componente de Wireshark; no se declaró revisión de su interfaz gráfica. Se conservan los intentos fallidos e inválidos y no cuentan como campaña."
    )
    for round_no in range(1, 4):
        group = [r for r in runs if r["round"] == round_no]
        para(
            f"Ronda {round_no}: {len(group)}/51 ejecuciones válidas. Inicio observado: {min((r['started_at'] for r in group),default='pendiente')}; cierre observado: {max((r['finished_at'] for r in group),default='pendiente')}."
        )
    para(
        "La unidad normalizada es una respuesta por intento y TTL. Se preservan respuestas múltiples, errores y timeouts. Un TTL 255 separado de los anteriores se conserva como registro, sin inventar los TTL intermedios ni enlaces entre capas no consecutivas. Los ASN son asociaciones IP-prefijo obtenidas con RIPEstat y no una ruta BGP observada."
    )
    para("El costo de Scamper se informa con su contador WARTS y el de RIPE de ida con solicitudes clasificadas en PCAP. Se conservan ambos conteos cuando están disponibles. Una diferencia entre contador y captura se documenta sin atribuir automáticamente pérdida, fallo de envío o filtrado. Las capturas inversas locales no permiten contar toda la emisión remota.")
    mismatches = [r for r in runs if r.get("packet_count_mismatch")]
    if mismatches:
        table(["Destino", "Método", "Ronda", "Contador WARTS", "Solicitudes PCAP"], [[r["target"], r["family"] + " / " + r["method"], r["round"], r["tool_reported_probes"], r["pcap_observed_probes"]] for r in mismatches])
    family_path = ROOT / "resultados/revision_familias.json"
    if family_path.exists():
        family_review = json.loads(family_path.read_text())
        if all(r["run_id"] in {v["run_id"] for v in runs} for r in family_review.get("families", [])):
            para("Se contrastó una ejecución representativa de trace, tracelb y RIPE con sus originales, capturas y revisión GUI real. La evidencia y sus hashes están en " + family_review["evidence"] + ". Este control verifica la normalización y la asociación de archivos; el contraste temporal requiere las tres rondas.")
    heading("1. Path Discovery Scamper")
    for target in cfg["targets"]:
        dest = target["ip"]
        heading(target["label"] + " - " + dest)
        group = [
            r
            for r in rank
            if r["target"] == dest and r["tool"] == "scamper" and r["family"] == "trace"
        ]
        table(
            [
                "Método",
                "Rondas",
                "Mediana IP únicas",
                "Cobertura",
                "Jaccard entre rondas",
                "Mediana sondas WARTS",
                "Mediana duración (s)",
                "IP destino observada",
            ],
            [
                [
                    r["method"],
                    r["rounds"],
                    r["median_unique_ips"],
                    f"{r['median_coverage']:.1%}",
                    (
                        f"{r['stability_jaccard']:.3f}"
                        if r["stability_jaccard"] is not None
                        else ("Sin IP observadas" if r["rounds"] >= 2 else "No contrastado")
                    ),
                    (
                        r.get("median_probes_sent")
                        if r.get("median_probes_sent") is not None
                        else "No observable"
                    ),
                    round(r.get("median_elapsed_wall_seconds") or 0, 1),
                    r["destination_observed_runs"],
                ]
                for r in group
            ],
        )
        if group:
            best = group[0]
            ties = best_ties(group)
            para(
                "Métodos con mayor información según mediana de IP únicas, cobertura y estabilidad: "
                + ", ".join(ties)
                + (". Empate en estos criterios." if len(ties) > 1 else ".")
                + (
                    " Selección provisional: faltan rondas."
                    if best["provisional"]
                    else " Comparación basada en tres rondas."
                )
                + " La ausencia de llegada se conserva y no invalida automáticamente una medición."
            )
        para(
            "Tabla tipo 1, ronda 1. Las rondas 2 y 3 y todos los intentos están en los anexos CSV de este análisis. Se conserva más de una IP por TTL cuando corresponde."
        )
        csvtable(analysis / "tablas" / f"tabla1_{dest}_r1.csv")
        extra = [r for r in additions if r["target"] == dest]
        table(
            [
                "tracelb",
                "Ronda",
                "IP adicionales frente a unión de 6 trace",
                "Sondas tracelb",
                "Sondas de referencia",
            ],
            [
                [
                    r["method"],
                    r["round"],
                    ", ".join(r["additional_ips"]) or "Ninguna",
                    r["probes_sent"],
                    r["reference_probes_sent"],
                ]
                for r in extra
            ],
        )
        para(
            "Las IP adicionales se comparan contra la unión de los seis trace de la misma ronda. Más IP con más paquetes se interpreta como una relación entre cobertura y costo, sin atribuir superioridad independiente del presupuesto de sondas."
        )
    heading("2. Path Discovery RIPE")
    para(
        "La definición efectiva, la solicitud, el ID, la sonda participante y los tiempos reales se conservan para cada medición. La aceptación de una solicitud no se contó como ejecución: se esperó un resultado con el ID y sonda correctos. Las capturas locales de ida permiten contar solicitudes; las de vuelta son parciales y no permiten reconstruir todo el tráfico remoto."
    )
    for target in cfg["targets"]:
        dest = target["ip"]
        heading(target["label"] + " - protocolos RIPE de ida")
        group = [
            r
            for r in rank
            if r["target"] == dest and r["tool"] == "ripe" and r["direction"] == "ida"
        ]
        table(
            [
                "Protocolo",
                "Rondas",
                "Mediana IP únicas",
                "Cobertura",
                "Jaccard",
                "Mediana sondas PCAP",
                "Mediana duración (s)",
                "IP destino observada",
            ],
            [
                [
                    r["method"],
                    r["rounds"],
                    r["median_unique_ips"],
                    f"{r['median_coverage']:.1%}",
                    (
                        f"{r['stability_jaccard']:.3f}"
                        if r["stability_jaccard"] is not None
                        else ("Sin IP observadas" if r["rounds"] >= 2 else "No contrastado")
                    ),
                    (
                        r.get("median_probes_sent")
                        if r.get("median_probes_sent") is not None
                        else "No observable"
                    ),
                    round(r.get("median_elapsed_wall_seconds") or 0, 1),
                    r["destination_observed_runs"],
                ]
                for r in group
            ],
        )
        if group:
            ties = best_ties(group)
            para(
                "Protocolos con mayor información en la comparación disponible: "
                + ", ".join(ties)
                + (". Empate en estos criterios." if len(ties) > 1 else ".")
                + (
                    " Resultado provisional."
                    if group[0]["provisional"]
                    else " Comparación de las tres rondas."
                )
            )
        csvtable(analysis / "tablas" / f"ripe_ida_{dest}_r1.csv")
    heading("Transporte, payload y respuesta selectiva")
    para(
        "Se inspeccionan seis métodos trace, cinco tracelb y tres protocolos RIPE. Las fichas conservan TTL, tamaño, IPID, protocolo, puertos, flags TCP, secuencia/ACK, campos ICMP, checksums, payload hexadecimal y encabezados originales citados. Los campos no presentes en un protocolo se consideran no aplicables."
    )
    patterns = sorted((ROOT / "resultados").glob("patrones_*/predictions.json"))
    current_ids = {r["run_id"] for r in runs}
    rules = []
    for candidate in reversed(patterns):
        candidate_rules = json.loads(candidate.read_text())
        training = {r["training"] for r in candidate_rules}
        if candidate_rules and all(json.loads((ROOT / t / "metadata.json").read_text()).get("run_id") in current_ids for t in training):
            verify_manifest(candidate.parent)
            rules = candidate_rules
            break
    method_groups = defaultdict(list)
    for r in rules:
        method_groups[(r["tool"], r["family"], r["method"])].append(r)
    payload_path = ROOT / "resultados/estructura_payload.json"
    payload_info = json.loads(payload_path.read_text()) if payload_path.exists() else {}
    payload_cases = payload_info.get("cases", []) if payload_info.get("session_public_ipv4") == cfg.get("session_public_ipv4") else []
    for key, items in sorted(method_groups.items()):
        heading(" / ".join(key))
        example_target = sorted({r["target"] for r in items})[0]
        regular = [
            r
            for r in items
            if "[byte " not in r["field"]
            and r["target"] == example_target
            and r["rule"].get("samples", 0) > 0
        ]
        para(
            "Ficha ilustrada para "
            + example_target
            + ". Los demás destinos y el detalle por byte se conservan en predictions.json, sin mezclar ejecuciones."
        )
        table(
            ["Campo", "Regla observada en ronda 1", "Contraste rondas 2 y 3"],
            [
                [r["field"], rule_text(r["rule"]), validation_text(r["validation"])]
                for r in regular
            ],
        )
        payload_case = next(
            (
                c
                for c in payload_cases
                if (c["tool"], c["family"], c["method"]) == key
                and c["target"] == example_target
            ),
            None,
        )
        if payload_case:
            payload_info = payload_case["training"]
            para(
                "Payload observado: "
                + str(payload_info["lengths_bytes"])
                + " bytes. "
                + (
                    "Sin payload de aplicación en estas sondas."
                    if payload_info["zero_payload"]
                    else "Bytes iniciales: "
                    + str(payload_info["first_hex"])
                    + ". Offsets que cambiaron dentro de la ejecución: "
                    + str(payload_info["within_run_variable_offsets"])
                    + "."
                )
            )
            for segment in payload_info["constant_ascii_segments"]:
                para(
                    f"Segmento ASCII constante desde offset {segment['offset']}: {segment['ascii']}"
                )
            constraint = payload_info["word_constraint"]
            if constraint and constraint["stable_within_run"]:
                para(
                    "Restricción observada: la suma de "
                    + ", ".join(constraint["fields"])
                    + " módulo 65535 se mantuvo constante dentro de la ejecución. Su base depende de la ejecución. Es compatible con compensación de checksum; se conserva como hipótesis contrastable, sin atribuir una intención no comprobada."
                )
            if payload_case["validation"]:
                for round_no, validation in sorted(payload_case["validation"].items()):
                    lengths = "coinciden" if validation.get("payload_lengths_match") else "no coinciden"
                    segments = "coinciden" if validation.get("constant_ascii_segments_match") else "no coinciden"
                    detail = (f"Ronda {round_no}: las longitudes {lengths} y los segmentos ASCII constantes {segments}; "
                              f"se examinaron {validation.get('samples', 0)} paquetes.")
                    if validation.get("word_constraint_stable_in_new_execution") is not None:
                        stable = "se mantuvo" if validation["word_constraint_stable_in_new_execution"] else "no se mantuvo"
                        detail += (f" La restricción de la suma {stable} en esa ejecución: "
                                   f"{validation.get('checked_later_packets', 0)} paquetes posteriores contrastados y "
                                   f"{validation.get('failed_later_packets', 0)} discrepancias.")
                    para(detail)
        para(
            "El archivo predictions.json incluye el contraste por offset de los bytes del payload. Las constancias e incrementos se tratan como hipótesis de captura; una validación fallida se conserva y las bases dependientes de ejecución no se presentan como constantes universales. Los valores variables o dependientes del estado no se predicen exactamente sin evidencia."
        )
    if not method_groups:
        para(
            "Pendiente generar y contrastar las fichas completas de los catorce métodos; no se presentan predicciones como comprobadas."
        )
    tcp_review = ROOT / "resultados/correlacion_tcp_captura.json"
    if tcp_review.exists():
        tcp_summary = json.loads(tcp_review.read_text()).get("summary", {})
        para(
            f"Control de recepción TCP: se revisaron {tcp_summary.get('reviewed_scamper_tcp_runs', 0)} ejecuciones de Scamper; "
            f"{tcp_summary.get('runs_with_matching_icmp_quotes', 0)} contienen respuestas ICMP correlacionadas con solicitudes "
            f"y {tcp_summary.get('runs_with_pcap_warts_discrepancy', 0)} presentan diferencias entre PCAP y WARTS. "
            "La correlación usa direcciones, IPID, puertos y orden temporal; la causa de las diferencias no está establecida. "
            "Una respuesta presente en PCAP no implica que Scamper la haya aceptado y no prueba filtrado de red. "
            "Detalle reproducible en resultados/correlacion_tcp_captura.json."
        )
    candidates = json.loads((analysis / "selective_candidates.json").read_text())
    para(
        f"Candidatos de respuesta selectiva detectados: {len(candidates)}. La ausencia de una IP en un método no demuestra una regla de firewall: puede deberse a carga, balanceo, pérdida o rutas diferentes. Se requiere corroboración entre rondas y pruebas dirigidas acotadas para cada herramienta."
    )
    validation = ROOT / "resultados/respuesta_selectiva_validacion.json"
    if validation.exists():
        validation_result = json.loads(validation.read_text())
        for case in validation_result.get("cases", []):
            heading("Corroboración adicional - " + case["tool"])
            candidate = case.get("candidate")
            if not candidate:
                para(case.get("limitation", "Sin caso reproducible disponible."))
                continue
            para(
                f"IP {candidate['ip']}, destino {candidate['target']}: observada con {candidate['responds_method']} y ausente con {candidate['not_observed_method']}; rondas con presencia: {candidate['responding_rounds']}; rondas con TTL comparable: {candidate['comparable_ttl_rounds']}."
            )
            table(
                ["Método", "Repetición", "Run / ID RIPE", "IP observada"],
                [
                    [
                        r["method"],
                        r["repeat"],
                        r["run_id"]
                        + " / "
                        + str(r.get("measurement_id") or "No corresponde"),
                        "Sí" if r["ip_observed"] else "No",
                    ]
                    for r in case["additional_runs"]
                ],
            )
            if case["status"] == "corroborated_observation":
                para("Resultado: el contraste se repitió en las pruebas adicionales. La ausencia puede deberse a otra ruta, pérdida, balanceo o recepción local; no identifica por sí sola una regla de firewall.")
            elif case["status"] == "not_corroborated":
                para("Resultado: el contraste no se corroboró en las pruebas adicionales. Se conservan las observaciones que contradicen el candidato inicial; no se atribuye una regla de firewall.")
            else:
                para("Resultado: " + case["status"] + ". " + case.get("interpretation", ""))
    else:
        para(
            "Pruebas dirigidas de respuesta selectiva pendientes. Este requisito no se da por cerrado por la mera lista de candidatos."
        )
    diagnostic = ROOT / "resultados/diagnostico_recepcion_tcp.json"
    if diagnostic.exists():
        check = json.loads(diagnostic.read_text())
        heading("Control adicional de recepción TCP")
        para(
            "Prueba fuera de las 153 celdas. Se compara el envío predeterminado y la opción oficial rawtcp, conservando o cambiando explícitamente el puerto de origen. Los resultados principales mantienen sus parámetros originales."
        )
        table(
            ["rawtcp", "Puerto origen", "IP únicas", "Sondas", "Parada", "Run"],
            [
                [
                    r["rawtcp"],
                    r["source_port"],
                    len(r["unique_ips"]),
                    r["probe_count"],
                    r["stop_reason"],
                    r["run_id"],
                ]
                for r in check["runs"]
            ],
        )
        para(check["scope"])

    heading("3. Path way RIPE: ida y vuelta")
    para("Las respuestas desde la IPv4 pública domiciliaria acreditan la observación de esa dirección. Identificar al equipo que respondió requiere correlación con la captura local y conocimiento del NAT.")
    reverse_note = ROOT / "resultados/revision_vuelta_domicilio.json"
    if reverse_note.exists():
        note = json.loads(reverse_note.read_text())
        if note.get("run_id") in {r["run_id"] for r in runs}:
            para(f"La vuelta {note['protocol']} {note['measurement_id']} observó respuestas desde la IP pública de destino. La captura local contiene {len(note['local_frames_with_remote_probe_outer_ip'])} paquetes con la IP de esa sonda en el encabezado IPv4 exterior; la identidad del respondiente queda sin establecer. Evidencia: {note['evidence']}.")
    para(
        "Cada comparación conserva la numeración desde cada origen y también compara el orden inverso de la vuelta. Las IP corresponden a interfaces observadas; direcciones distintas no demuestran routers distintos ni se asume alias entre interfaces. Las secuencias AS tampoco prueban una ruta BGP."
    )
    for target in cfg["targets"]:
        dest = target["ip"]
        heading(target["label"] + " - comparación de sentidos")
        group = [s for s in symmetry if s["target"] == dest]
        table(
            [
                "Protocolo",
                "Ronda",
                "IDs ida / vuelta",
                "IP únicas ida / vuelta",
                "Jaccard IP intermedias",
                "Observación incompleta",
            ],
            [
                [
                    s["protocol"],
                    s["round"],
                    f"{s['ida_id']} / {s['vuelta_id']}",
                    f"{s['ida_unique_ips']} / {s['vuelta_unique_ips']}",
                    (
                        f"{s['ip_jaccard']:.3f}"
                        if s["ip_jaccard"] is not None
                        else "Sin IP"
                    ),
                    s["incomplete"],
                ]
                for s in group
            ],
        )
        for protocol in ["UDP", "ICMP", "TCP"]:
            para(
                f"Tabla tipo 2: {protocol}, ronda 1. Las otras rondas permanecen en CSV."
            )
            csvtable(analysis / "tablas" / f"tabla2_{dest}_{protocol}_r1.csv")
        for s in group:
            para(
                f"{s['protocol']}, ronda {s['round']}: AS de ida {s['ida_as_sequence']}; AS de vuelta invertida {s['vuelta_reversed_as_sequence']}. Coincidencia del orden observado de IP: {s['observed_ip_layer_order_equal']}; de secuencia AS: {s['observed_as_sequence_equal']}. {'No permite afirmar simetría completa por observaciones incompletas.' if s['incomplete'] else 'La comparación se limita a las interfaces y sondas utilizadas.'}"
            )
    heading("4. Public Path")
    para(
        "Por destino se selecciona un par RIPE del mismo protocolo, ronda e IPv4 pública. Se maximiza la unión de IP, luego se minimizan saltos sin respuesta y separación temporal. El grafo es dirigido; las adyacencias son inferidas por traceroute, los huecos son explícitos y no se crean enlaces cartesianos entre respuestas múltiples."
    )
    for p in sorted((analysis / "grafos").glob("*.selection.json")):
        selected = json.loads(p.read_text())
        publication = next(
            (p for p in state["public_graphs"] if p["target"] == selected["target"]),
            None,
        )
        para(
            f"Destino {selected['target']}: mediciones seleccionadas {selected['ids']}. "
            + (
                f"UUID {publication['uuid']}; URL {publication['url']}; lectura pública verificada: {publication['public_read_verified']}."
                if publication
                else "Publicación y UUID público pendientes."
            )
        )
    heading("Reproducción, integridad y limitaciones")
    para(
        "Análisis utilizado: "
        + str(analysis.relative_to(ROOT))
        + ". Regenerar con ./main analyze después de conservar las consultas ASN; ./main verify comprueba los manifiestos. Exportar PCAP con ./main packet-export y contrastar patrones con ./main patterns. El código, configuración activa y original, capturas, tablas, grafos y originales se reúnen con ./main bundle, excluyendo credenciales y claves privadas."
    )
    reproduction = sorted((ROOT / "resultados").glob("reproduccion_ronda_*.json"))
    if reproduction:
        proof = json.loads(reproduction[-1].read_text())
        para(
            "Reproducción local acreditada en "
            + reproduction[-1].name
            + ": "
            + str(proof["offline_valid_measurements"])
            + " ejecuciones regeneradas sin nuevas mediciones ni consultas ASN, con tablas, métricas y tres CX2 idénticos. Se verificaron "
            + str(proof["verified_package_files"])
            + " archivos del paquete. El alcance corresponde a las ejecuciones incluidas en esa constancia; la publicación de grafos se verifica por separado."
        )
    para(
        "Las mediciones describen las rutas observadas en estos horarios y bajo estos protocolos. No cuantifican por sí solas velocidad de acceso, congestión sostenida, censura o reglas de filtrado. Los timeouts y las rutas incompletas se conservan como resultados con sus límites de interpretación."
    )
    heading("Referencias")
    for url in [
        "https://www.caida.org/catalog/software/scamper/",
        "https://www.wireshark.org/docs/man-pages/tshark.html",
        "https://atlas.ripe.net/docs/",
        "https://stat.ripe.net/docs/data-api/api-endpoints/network-info",
        "https://www.ndexbio.org/docs/using-the-ndex-api/",
        "https://cytoscape.org/cx/cx2/cx2-visual-styles/",
    ]:
        para(url)
    images = sorted(
        p
        for p in (ROOT / "capturas").iterdir()
        if p.suffix.lower() in (".png", ".jpg", ".jpeg")
    )
    index_path = ROOT / "capturas/indice.json"
    image_index = {i["file"]: i for i in json.loads(index_path.read_text())} if index_path.exists() else {}
    session_ip = cfg.get("session_public_ipv4")
    images = [p for p in images if not session_ip or not (
        image_index.get(str(p.relative_to(ROOT)), {}).get("historical_session") or
        image_index.get(str(p.relative_to(ROOT)), {}).get("superseded_progress_snapshot") or
        image_index.get(str(p.relative_to(ROOT)), {}).get("session_public_ipv4") not in (None, session_ip)
    )]
    gui_available = any(p.name.startswith("wireshark_") for p in images)
    for image in images:
        if image.stem in ("ndex_acceso_inicial", "propuesta_api_key"):
            continue
        if gui_available and image.name.startswith(("scamper_", "ripe_traceroute_")):
            continue
        blocks.append(("image", str(image)))
    md = []
    md_images = False
    for kind, item in blocks:
        if kind == "heading":
            md.append("## " + item)
        elif kind == "paragraph":
            md.append(item)
        elif kind == "table":
            md.append(
                "\n".join(
                    ["| " + " | ".join(row) + " |" for row in item[:1]]
                    + ["| " + " | ".join(["---"] * len(item[0])) + " |"]
                    + [
                        "| "
                        + " | ".join(
                            v.replace("|", " / ").replace("\n", " ") for v in row
                        )
                        + " |"
                        for row in item[1:]
                    ]
                )
            )
        else:
            if not md_images:
                md.append("## Anexo de capturas")
                md_images = True
            md.append(
                "!["
                + image_caption(item)
                + "](../../"
                + str(Path(item).relative_to(ROOT))
                + ")"
            )
    (out / "informe.md").write_text("\n\n".join(md) + "\n")
    (out / "fuentes.json").write_text(
        json.dumps(
            {
                "analysis": str(analysis),
                "generated_at": utc(),
                "campaign_status": state,
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n"
    )
    render_pdf(blocks, out / "informe.pdf", title)
    print(
        json.dumps(
            {
                "markdown": str(out / "informe.md"),
                "pdf": str(out / "informe.pdf"),
                "completed": state["completed"],
                "graphs": len(state["public_graphs"]),
            }
        )
    )


def best_ties(group):
    score = lambda r: (
        r["median_unique_ips"],
        r["median_coverage"],
        r["stability_jaccard"],
    )
    return [r["method"] for r in group if score(r) == score(group[0])]


def rule_text(rule):
    n = rule.get("samples", 0)
    kind = rule["kind"]
    if kind == "constant":
        return "Constante: " + str(rule["value"]) + f"; n={n}"
    if kind == "step":
        return f"Incremento {rule['delta']} por sonda; base propia de cada ejecución; n={n}"
    if kind == "block_step":
        return f"Incremento {rule['delta']} cada {rule['block_size']} sondas; base propia de cada ejecución; n={n}"
    if kind == "variable":
        if "min_observed" in rule:
            return f"Variable; rango observado {rule['min_observed']} a {rule['max_observed']}; n={n}. No se predice valor exacto."
        return f"Variable; longitudes observadas {rule.get('lengths',[])} bytes; n={n}. No se predice valor exacto."
    return f"Muestras insuficientes: n={n}"


def validation_text(checks):
    if not checks:
        return "Pendiente: aún no hay otra ronda contrastada"
    labels = {
        "passed": "regla corroborada",
        "failed": "regla no corroborada",
        "failed_non_numeric": "contraste fallido: formato no numérico",
        "not_predictable": "sin regla exacta contrastable",
        "insufficient": "muestras insuficientes",
    }
    return "; ".join(
        f"Ronda {n}: {labels.get(v['status'],v['status'])}; comprobaciones={v.get('checked',0)}"
        + (f"; fallos={v['failures']}" if "failures" in v else "")
        for n, v in sorted(checks.items())
    )


def render_pdf(blocks, path, title):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import (
        BaseDocTemplate,
        Frame,
        PageTemplate,
        Paragraph,
        Spacer,
        LongTable,
        TableStyle,
        PageBreak,
        NextPageTemplate,
        Image,
        KeepTogether,
    )
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    font = next(
        (
            p
            for p in [
                Path("/usr/share/fonts/TTF/DejaVuSans.ttf"),
                Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
            ]
            if p.exists()
        ),
        None,
    )
    name = "Helvetica"
    if font:
        pdfmetrics.registerFont(TTFont("PDReport", str(font)))
        name = "PDReport"
    styles = getSampleStyleSheet()
    body = ParagraphStyle("PDbody", fontName=name, fontSize=9, leading=13, spaceAfter=7)
    heading = ParagraphStyle(
        "PDheading",
        fontName=name,
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#173d5c"),
        spaceBefore=12,
        spaceAfter=8,
        keepWithNext=True,
    )
    cell = ParagraphStyle(
        "PDcell", fontName=name, fontSize=6.7, leading=9, wordWrap="CJK"
    )
    header = ParagraphStyle("PDheader", parent=cell, textColor=colors.white)
    width, height = A4
    margin = 38
    doc = BaseDocTemplate(
        str(path),
        pagesize=A4,
        leftMargin=margin,
        rightMargin=margin,
        topMargin=45,
        bottomMargin=40,
        title=title,
        author="Diego",
    )

    def footer(canvas, document):
        w, h = canvas._pagesize
        canvas.saveState()
        canvas.setFont(name, 7)
        canvas.setFillColor(colors.HexColor("#43556b"))
        canvas.drawString(38, 22, "Path Discovery | Evidencia de mediciones reales")
        canvas.drawRightString(w - 38, 22, str(document.page))
        canvas.restoreState()

    doc.addPageTemplates(
        [
            PageTemplate(
                id="Portrait",
                frames=[Frame(margin, 40, width - 2 * margin, height - 85, id="p")],
                pagesize=A4,
                onPage=footer,
            ),
            PageTemplate(
                id="Landscape",
                frames=[
                    Frame(38, 35, landscape(A4)[0] - 76, landscape(A4)[1] - 70, id="l")
                ],
                pagesize=landscape(A4),
                onPage=footer,
            ),
        ]
    )
    story = []
    images = False
    for kind, item in blocks:
        if kind == "heading":
            story.append(Paragraph(escape(item), heading))
        elif kind == "paragraph":
            story.append(Paragraph(escape(item), body))
        elif kind == "table":
            n = len(item[0])
            available = width - 2 * margin - 12
            widths = [available / n] * n
            if n >= 4:
                widths = [available * 0.12] + [available * 0.88 / (n - 1)] * (n - 1)
            data = [
                [
                    Paragraph(
                        escape(str(v)).replace("; ", ";<br/>"),
                        header if row == 0 else cell,
                    )
                    for v in values
                ]
                for row, values in enumerate(item)
            ]
            t = LongTable(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
            t.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#173d5c")),
                        (
                            "ROWBACKGROUNDS",
                            (0, 1),
                            (-1, -1),
                            [colors.white, colors.HexColor("#edf3f7")],
                        ),
                        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#ccd7e0")),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ("LEFTPADDING", (0, 0), (-1, -1), 4),
                        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                        ("TOPPADDING", (0, 0), (-1, -1), 4),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                    ]
                )
            )
            story += [t, Spacer(1, 9)]
        else:
            first_image = not images
            if first_image:
                story.append(NextPageTemplate("Landscape"))
                images = True
            story.append(PageBreak())
            if first_image:
                story.append(Paragraph("Anexo de capturas", heading))
                story.append(
                    Paragraph(
                        "Evidencia visual complementaria. Las imágenes Wireshark muestran la interfaz gráfica real. El índice capturas/indice.json conserva procedencia y hashes.",
                        body,
                    )
                )
            story.append(Paragraph(escape(image_caption(item)), heading))
            image = Image(item)
            factor = min(
                (landscape(A4)[0] - 95) / image.imageWidth,
                (landscape(A4)[1] - (200 if first_image else 130)) / image.imageHeight,
            )
            image.drawWidth = image.imageWidth * factor
            image.drawHeight = image.imageHeight * factor
            story.append(image)
    doc.build(story)


if __name__ == "__main__":
    main()
