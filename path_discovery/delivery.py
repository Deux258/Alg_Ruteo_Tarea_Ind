"""Publicación NDEx y paquete de entrega libre de configuración privada."""
import base64
import json
import os
import re
import tarfile
import uuid
from pathlib import Path
from urllib.parse import urlencode

from .common import ROOT, identifier, json_write, request_json, sha256, utc, verify_manifest


def validate_cx2(cx):
    sections = {k: v for section in cx for k, v in section.items()}
    if sections.get("CXVersion") != "2.0":
        raise ValueError("No es CX2")
    ids = [n["id"] for n in sections["nodes"]]
    if len(ids) != len(set(ids)):
        raise ValueError("IDs de nodo duplicados")
    for edge in sections["edges"]:
        if edge["s"] not in ids or edge["t"] not in ids:
            raise ValueError("Enlace con nodo inexistente")
    return sections


def record_browser_publication(path, network_uuid):
    """Acreditar una importación hecha en la sesión del navegador, sin extraer credenciales."""
    path = Path(path).resolve()
    network_uuid = str(uuid.UUID(network_uuid))
    if not path.is_relative_to(ROOT / "resultados") or not path.name.endswith(".cx2.json"):
        raise ValueError("Seleccionar un CX2 del análisis local")
    verify_manifest(path.parent.parent)
    local = validate_cx2(json.loads(path.read_text()))
    summary = request_json(f"https://www.ndexbio.org/v3/networks/{network_uuid}/summary")
    if summary.get("visibility", "").upper() != "PUBLIC":
        raise ValueError("NDEx no acredita visibilidad PUBLIC")
    exported = request_json(f"https://www.ndexbio.org/v3/networks/{network_uuid}")
    remote = validate_cx2(exported)
    if len(local["nodes"]) != len(remote["nodes"]) or len(local["edges"]) != len(remote["edges"]):
        raise ValueError("El grafo público no tiene los nodos/enlaces esperados")
    selection = json.loads(path.with_name(path.name.replace(".cx2.json", ".selection.json")).read_text())
    description = str(remote.get("networkAttributes", []))
    if not all(re.search(r"\b" + str(mid) + r"\b", description) for mid in selection["ids"]):
        raise ValueError("El grafo público no conserva ambas referencias RIPE")
    receipt = ROOT / "grafos" / ("publication_" + identifier())
    receipt.mkdir(parents=True)
    json_write(receipt / "source.json", {"path": str(path.relative_to(ROOT)), "sha256": sha256(path), "method": "authenticated_browser_ui"}, exclusive=True)
    json_write(receipt / "summary.json", summary, exclusive=True)
    json_write(receipt / "export.cx2.json", exported, exclusive=True)
    result = {"uuid": network_uuid, "url": f"https://www.ndexbio.org/viewer/networks/{network_uuid}",
              "measurement_ids": selection["ids"], "target": selection["target"],
              "public_read_verified": True, "published_at": utc()}
    json_write(receipt / "publication.json", result, exclusive=True)
    return result


def publish(path):
    path = Path(path).resolve()
    if not path.is_relative_to(ROOT / "resultados") or not path.name.endswith(".cx2.json"):
        raise ValueError("Publicar solo grafos generados en resultados")
    verify_manifest(path.parent.parent)
    cx = json.loads(path.read_text())
    validate_cx2(cx)
    user, password = os.environ.get("NDEX_USERNAME"), os.environ.get("NDEX_PASSWORD")
    if not user or not password:
        raise RuntimeError("Configurar NDEX_USERNAME y NDEX_PASSWORD localmente")
    token = base64.b64encode((user + ":" + password).encode()).decode()
    headers = {"Authorization": "Basic " + token}
    # Intentos/publicaciones se registran fuera del análisis sellado. Un timeout
    # de POST exige revisar NDEx, sin duplicar la publicación automáticamente.
    receipt = ROOT / "grafos" / ("publication_" + identifier())
    receipt.mkdir(parents=True)
    selection = json.loads(path.with_name(path.name.replace(".cx2.json", ".selection.json")).read_text())
    json_write(receipt / "attempt.json", {"started_at": utc(), "source": str(path.relative_to(ROOT)), "sha256": sha256(path), "selection": selection}, exclusive=True)
    response = request_json("https://www.ndexbio.org/v3/networks?visibility=PUBLIC", cx, headers=headers)
    json_write(receipt / "response.json", response, exclusive=True)
    value = response.get("uuid", response.get("networkUUID")) if isinstance(response, dict) else response
    if not isinstance(value, str):
        raise RuntimeError("Respuesta NDEx sin UUID reconocible; revisar response.json antes de reintentar")
    value = str(uuid.UUID(value.rstrip("/").split("/")[-1]))
    # Configurar visibilidad explícitamente también en servidores que ignoran query.
    request_json(f"https://www.ndexbio.org/v2/network/{value}/systemproperty", {"visibility": "PUBLIC"}, headers=headers, method="PUT")
    summary = request_json(f"https://www.ndexbio.org/v2/network/{value}/summary")
    exported = request_json(f"https://www.ndexbio.org/v3/networks/{value}")
    validate_cx2(exported)
    json_write(receipt / "summary.json", summary, exclusive=True)
    json_write(receipt / "export.cx2.json", exported, exclusive=True)
    result = {"uuid": value, "url": f"https://www.ndexbio.org/viewer/networks/{value}", "measurement_ids": selection["ids"], "target": selection["target"], "public_read_verified": True, "published_at": utc()}
    json_write(receipt / "publication.json", result, exclusive=True)
    return result


def delivery_checks(analysis):
    analysis = Path(analysis)
    summary = json.loads((analysis / "summary.json").read_text())
    graph_targets = set(summary.get("graphs", []))
    published = set()
    for receipt in (ROOT / "grafos").glob("publication_*"):
        pubfile = receipt / "publication.json"
        if not pubfile.exists():
            continue
        publication = json.loads(pubfile.read_text())
        target = publication.get("target")
        selected = analysis / "grafos" / f"{target}.selection.json"
        graph = analysis / "grafos" / f"{target}.cx2.json"
        if not selected.exists() or not graph.exists():
            continue
        selection = json.loads(selected.read_text())
        source = next((receipt / n for n in ("source.json", "attempt.json") if (receipt / n).exists()), None)
        proof = json.loads(source.read_text()) if source else {}
        remote_summary = json.loads((receipt / "summary.json").read_text()) if (receipt / "summary.json").exists() else {}
        if publication.get("public_read_verified") and remote_summary.get("visibility", "").upper() == "PUBLIC" and set(publication.get("measurement_ids", [])) == set(selection["ids"]) and proof.get("sha256") == sha256(graph):
            published.add(target)
    gui = ROOT / "resultados/revision_wireshark_gui.json"
    review = json.loads(gui.read_text()) if gui.exists() else {}
    expected_methods = {"scamper_trace_" + m for m in ("udp", "icmp", "udp-paris", "icmp-paris", "tcp", "tcp-ack")} | {"scamper_tracelb_" + m for m in ("udp-dport", "icmp-echo", "udp-sport", "tcp-sport", "tcp-ack-sport")} | {"ripe_traceroute_" + m for m in ("UDP", "ICMP", "TCP")}
    current_runs_file = analysis / "runs.json"
    current_runs = {r["run_id"]: r for r in json.loads(current_runs_file.read_text())} if current_runs_file.exists() else {}
    reviewed_methods = set()
    for entry in review.get("reviewed_runs", []):
        run = current_runs.get(entry.get("run_id"))
        if not run or run.get("pilot"):
            continue
        expected_method = "_".join(run[k] for k in ("tool", "family", "method"))
        capture = ROOT / "datos/originales" / run["run_id"] / "capture.pcapng"
        shot = (ROOT / entry.get("screenshot", "")).resolve()
        if entry.get("method") == expected_method and capture.exists() and entry.get("sha256") == sha256(capture) and shot.is_relative_to(ROOT / "capturas") and shot.is_file() and entry.get("screenshot_sha256") == sha256(shot):
            reviewed_methods.add(expected_method)
    selective_path = ROOT / ("resultados/respuesta_selectiva_revision.json" if summary.get("dataset_id") and (ROOT / "resultados/respuesta_selectiva_revision.json").exists() else "resultados/respuesta_selectiva_validacion.json")
    selective = json.loads(selective_path.read_text()) if selective_path.exists() else {}
    valid_selective = set()
    for case in selective.get("cases", []):
        candidate = case.get("candidate") or {}
        evidence = candidate.get("evidence_runs", [])
        if (case.get("status") == "corroborated_observation" and evidence
                and set(evidence) <= set(current_runs)):
            valid_selective.add(case.get("tool"))
    report_path = ROOT / "informe/path_discovery/fuentes.json"
    report = json.loads(report_path.read_text()) if report_path.exists() else {}
    report_current = (report.get("analysis_relative") == str(analysis.resolve().relative_to(ROOT)) or report.get("analysis") == str(analysis.resolve())) and report.get("campaign_status", {}).get("completed") == 153 and len({p.get("target") for p in report.get("campaign_status", {}).get("public_graphs", [])}) == 3
    return {"campaign_153_complete": bool(summary.get("complete_campaign")), "three_current_graphs_public": len(graph_targets) == 3 and published == graph_targets, "fourteen_gui_methods_reviewed": expected_methods <= reviewed_methods, "selective_cases_corroborated": {"scamper", "ripe"} <= valid_selective, "report_uses_current_complete_evidence": report_current and (ROOT / "informe/path_discovery/informe.pdf").exists()}


def bundle(analysis):
    analysis = Path(analysis).resolve()
    if not analysis.is_relative_to(ROOT / "resultados"):
        raise ValueError("Seleccionar análisis dentro de resultados")
    verify_manifest(analysis)
    folder = ROOT / "entrega" / identifier()
    folder.mkdir(parents=True)
    roots = [ROOT / p for p in ("path_discovery", "config/campana.json", "config/campana_enunciado.json", "config/exclusiones_calidad.json", "config/reproduccion.json", "config/seleccion_revision.json", "config/wireshark-image.env.example", "scripts", "docs", "informe", "tests", "docker", "compose.yaml", "compose.wireshark.yaml", "compose.latex.yaml", "config/evidencia_informe.json", "README.md", "main", "pyproject.toml", ".env.example")]
    roots += [analysis, ROOT / "datos/originales", ROOT / "grafos", ROOT / "capturas", ROOT / "resultados/paquetes", ROOT / "resultados/registro_ripe_1018487"]
    roots += [ROOT / "resultados" / p for p in ("bgp_he_origen.txt", "revision_informe_latex.json", "reproduccion_informe_latex.json", "analisis_revision_final.json", "preflight_campana.json", "revision_wireshark_gui.json", "correlacion_tcp_captura.json", "estructura_payload.json", "auditoria_patrones_revision.json", "checksums_tcp.json", "diagnostico_recepcion_tcp.json", "diagnostico_tcp_rxerr_revision.json", "exportaciones_paquetes.json", "respuesta_selectiva_validacion.json", "respuesta_selectiva_revision.json", "fichas_paquetes/index.json", "revision_familias.json", "revision_pdf_sesion_activa.json", "revision_vuelta_domicilio.json")]
    roots += sorted((ROOT / "resultados").glob("reproduccion_ronda_*.json"))
    roots += sorted((ROOT / "resultados/fichas_paquetes").glob("progreso*.html"))
    roots += sorted((ROOT / "resultados").glob("revision_piloto_*"))
    roots += sorted((ROOT / "resultados").glob("analisis_*/summary.json"))  # summaries of historical sessions
    patterns = sorted((ROOT / "resultados").glob("patrones_*"))
    if patterns:
        roots.append(patterns[-1])
    files = sorted({p for base in roots for p in ([base] if base.is_file() else base.rglob("*")) if p.is_file()})
    def allowed_file(p):
        rel = p.relative_to(ROOT)
        # This archive contains only explicitly selected nonsecret state/config;
        # include them to keep its sealed manifest verifiable in the package.
        archived_public = len(rel.parts) >= 5 and rel.parts[:2] == ("datos", "originales") and rel.parts[2].startswith("cambio_sesion_") and str(Path(*rel.parts[3:])) in {
            "previous/.state/campaign.json", "previous/.state/pilot.json", "previous/.state/postprocessing.json", "previous/config/local.json"
        }
        # This exact sealed file is a public probe API response, not local config.
        public_probe_response = str(rel) == "datos/originales/seleccion_sondas_20261026T012504/local.json"
        blocked = any(x in ("__pycache__", ".env", ".state", ".tools", "local.json", "build", "qa", "latex_reproduccion") for x in rel.parts)
        return (not blocked or archived_public or public_probe_response) and not p.name.endswith((".pyc", ".key")) and "probe_key" not in p.name
    files = [p for p in files if allowed_file(p)]
    # Rechazar claves privadas accidentales en archivos pequeños, sin mostrarlas.
    for p in files:
        if p.stat().st_size < 1024 * 1024 and p.suffix not in (".pcapng", ".warts", ".pdf", ".docx"):
            data = p.read_bytes()
            if re.search(rb"-----BEGIN (?:OPENSSH |RSA |EC )?PRIVATE KEY-----", data):
                raise ValueError(f"Clave privada detectada en {p.name}")
            for name in ("RIPE_ATLAS_API_KEY", "NDEX_PASSWORD"):
                secret = os.environ.get(name, "")
                if len(secret) >= 8 and secret.encode() in data:
                    raise ValueError(f"Credencial detectada en {p.name}")
    manifest = {str(p.relative_to(ROOT)): sha256(p) for p in files}
    json_write(folder / "SHA256.json", manifest, exclusive=True)
    summary = json.loads((analysis / "summary.json").read_text())
    checks = delivery_checks(analysis)
    complete = all(checks.values())
    json_write(folder / "package_status.json", {"complete_campaign": bool(summary.get("complete_campaign")), "complete_delivery": complete, "checks": checks, "analysis": str(analysis.relative_to(ROOT)), "created_at": utc(), "warning": None if complete else "Paquete de avance: revisar checks; no es el cierre académico de la tarea"}, exclusive=True)
    with tarfile.open(folder / ("entrega.tar.gz" if complete else "paquete_preparacion.tar.gz"), "w:gz") as archive:
        for p in files:
            archive.add(p, arcname=str(p.relative_to(ROOT)))
        archive.add(folder / "SHA256.json", arcname="SHA256.json")
        archive.add(folder / "package_status.json", arcname="package_status.json")
    return folder
