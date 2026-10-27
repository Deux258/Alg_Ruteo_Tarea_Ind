"""Exportación completa de paquetes y predicciones entre rondas."""
import csv
import io
import json
import subprocess
import itertools
from collections import defaultdict
from pathlib import Path

from .common import ROOT, command, csv_write, identifier, json_write, tool_command, verify_manifest, work_path, sha256, save_manifest, utc


def inspect_udp_export(export, meta):
    """Inspeccionar cabeceras exteriores y citas ICMP sin confundirlas con emisiones."""
    export = Path(export)
    packets = json.loads((export / "packets_full.json").read_text())
    requests, quotes = [], []
    for packet in packets:
        layers = packet["_source"]["layers"]
        ip, udp, icmp = (layers.get(k, {}) for k in ("ip", "udp", "icmp"))
        frame = layers.get("frame", {})
        if not icmp and udp and ip.get("ip.dst") == meta["destination"]:
            requests.append({"frame": frame.get("frame.number"), "time": frame.get("frame.time_epoch"),
                             **{k: ip.get(k) for k in ("ip.src", "ip.dst", "ip.ttl", "ip.id", "ip.len", "ip.proto")},
                             **{k: udp.get(k) for k in ("udp.srcport", "udp.dstport", "udp.length", "udp.checksum", "udp.payload")}})
        quoted_ip, quoted_udp = icmp.get("ip", {}), icmp.get("udp", {})
        if quoted_ip.get("ip.dst") == meta["destination"] and quoted_udp:
            quotes.append({"frame": frame.get("frame.number"), "from": ip.get("ip.src"),
                           "type": icmp.get("icmp.type"), "code": icmp.get("icmp.code"),
                           **{k: quoted_ip.get(k) for k in ("ip.dst", "ip.id")},
                           **{k: quoted_udp.get(k) for k in ("udp.srcport", "udp.dstport", "udp.checksum")}})
    fields = ("ip.dst", "ip.id", "udp.srcport", "udp.dstport")
    signatures = {tuple(r.get(k) for k in fields) for r in requests}
    for q in quotes:
        q["matches_local_request"] = tuple(q.get(k) for k in fields) in signatures
    outgoing = meta["direction"] == "ida"
    matching = sum(q["matches_local_request"] for q in quotes)
    if outgoing and (not requests or not matching):
        raise ValueError("Captura de ida sin solicitudes UDP y citas ICMP correlacionables")
    return {"run_id": export.name, "requests_count": len(requests), "icmp_quotes_count": len(quotes),
            "matched_quotes": matching, "requests": requests, "icmp_quotes": quotes,
            "reverse_capture_is_partial": not outgoing,
            "udp_ports": sorted({int(r["udp.dstport"]) for r in requests}),
            "limitations": "Correlación por destino, IPID y puertos; NAT puede modificar campos. Una captura inversa local puede no observar sondas remotas."}


def review_udp_pilots(runs):
    """Revisión reproducible con TShark; no afirma revisión de la interfaz gráfica."""
    out = ROOT / "resultados" / ("revision_piloto_" + identifier())
    out.mkdir(parents=True)
    reviews = []
    for run in runs:
        original = ROOT / "datos/originales" / run["run_id"]
        export = export_packets(original)
        review = inspect_udp_export(export, run)
        review.update(run_id=run["run_id"], export=str(export.relative_to(ROOT)),
                      source_manifest_sha256=sha256(original / "manifest.json"))
        json_write(out / (run["run_id"] + ".json"), review)
        reviews.append(review)
    evidence = {"reviewed_at": utc(), "mode": "tshark_decoded_headers_and_bytes", "manual_wireshark_review": False,
                "runs": [r["run_id"] for r in runs], "reviews": reviews}
    json_write(out / "review.json", evidence)
    paragraphs = ["# Revisión de pilotos UDP con TShark", "Se analizaron las cabeceras exteriores, los payloads y las citas ICMP. No se realizó revisión de la interfaz gráfica."]
    for r in reviews:
        paragraphs += [f"## {r['run_id']}", f"Solicitudes locales: {r['requests_count']}. Citas ICMP: {r['icmp_quotes_count']}; correlacionadas: {r['matched_quotes']}. Puertos: {r['udp_ports']}.",
                       f"Datos completos y bytes: `{r['export']}`. Captura inversa parcial: {r['reverse_capture_is_partial']}.", r["limitations"]]
    (out / "revision.md").write_text("\n\n".join(paragraphs) + "\n")
    save_manifest(out, {"kind": "packet_review", "runs": evidence["runs"]})
    return out

PACKET_FIELDS = ("frame.number", "frame.time_epoch", "frame.len", "ip.src", "ip.dst", "ip.ttl", "ip.id", "ip.len", "ip.proto", "ip.checksum",
                 "udp.srcport", "udp.dstport", "udp.length", "udp.checksum", "tcp.srcport", "tcp.dstport", "tcp.flags", "tcp.seq_raw", "tcp.ack_raw", "tcp.len", "tcp.checksum",
                 "icmp.type", "icmp.code", "icmp.ident", "icmp.seq", "icmp.checksum", "udp.payload", "tcp.payload", "data.data")


def is_probe_request(row, method):
    """Solo solicitudes del protocolo pedido; excluir citas ICMP y RST del host."""
    lower = method.lower()
    proto = row.get("ip.proto")
    if lower.startswith("udp"):
        return bool(row.get("udp.srcport") and row.get("udp.dstport")) and not row.get("icmp.type") and proto in (None, "", "17")
    if lower.startswith("icmp"):
        return row.get("icmp.type") == "8" and proto in (None, "", "1")
    if not lower.startswith("tcp"):
        raise ValueError("Método no reconocido para clasificar solicitudes")
    if not row.get("tcp.flags") or row.get("icmp.type") or proto not in (None, "", "6"):
        return False
    flags = int(row["tcp.flags"], 0)
    if "ack" in method.lower():
        return bool(flags & 0x10) and not bool(flags & 0x07)
    return bool(flags & 0x02) and not bool(flags & 0x15)


def export_packets(folder):
    verify_manifest(folder)
    meta = json.loads((folder / "metadata.json").read_text())
    capture = folder / "capture.pcapng"
    if not capture.is_file():
        raise ValueError("Falta captura real PCAPNG")
    out = ROOT / "resultados/paquetes" / (folder.name + "_" + identifier())
    out.mkdir(parents=True)
    args = ["-r", work_path(capture), "-n", "-T", "json", "-x"]
    raw = command(tool_command("tshark", args), timeout=180)
    (out / "packets_full.json").write_text(raw.stdout)
    args = ["-r", work_path(capture), "-n", "-T", "fields", "-E", "header=y", "-E", "separator=/t", "-E", "quote=d", "-E", "occurrence=a", "-E", "aggregator=|"]
    for field in PACKET_FIELDS:
        args += ["-e", field]
    exported = command(tool_command("tshark", args), timeout=180)
    (out / "packets.tsv").write_text(exported.stdout)
    allrows = list(csv.DictReader(io.StringIO(exported.stdout), delimiter="\t"))
    # Datos de predicción: solo solicitudes emitidas, excluyendo ICMP con citas
    # y tráfico de administración/background de la sonda.
    args = ["-r", work_path(capture), "-n", "-Y",
            f"ip.dst == {meta['destination']} && (udp || tcp || icmp.type == 8) && !(icmp.type == 3 || icmp.type == 11)",
            "-T", "fields", "-E", "header=y", "-E", "separator=/t", "-E", "quote=d", "-E", "occurrence=f"]
    for field in PACKET_FIELDS:
        args += ["-e", field]
    emitted = command(tool_command("tshark", args), timeout=180)
    (out / "outbound.tsv").write_text(emitted.stdout)
    outbound = list(csv.DictReader(io.StringIO(emitted.stdout), delimiter="\t"))
    emittedrows = [r for r in outbound if is_probe_request(r, meta["method"])]
    with (out / "emitted.tsv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=PACKET_FIELDS, delimiter="\t")
        writer.writeheader()
        writer.writerows(emittedrows)
    json_write(out / "metadata.json", {"format_version": 2, "probe_classifier_revision": 2, "run_id": folder.name, "tool": meta["tool"], "method": meta["method"], "family": meta["family"], "target": meta["target"], "direction": meta["direction"], "round": meta["round"], "pilot": meta["pilot"], "packets_captured": len(allrows), "candidate_emitted_packets": len(emittedrows), "outbound_transport_packets": len(outbound), "outbound_nonprobe_packets": len(outbound)-len(emittedrows), "reverse_capture_is_partial": meta["direction"] == "vuelta", "source_manifest": str(folder / "manifest.json"), "source_manifest_sha256": sha256(folder / "manifest.json")})
    save_manifest(out, {"kind": "packet_export", "source_run": folder.name})
    return out


def learn_rule(values):
    values = [v for v in values if v != ""]
    if len(values) < 3:
        return {"kind": "insufficient", "samples": len(values)}
    if len(set(values)) == 1:
        return {"kind": "constant", "value": values[0], "samples": len(values)}
    try:
        numbers = [int(v, 16) if v.startswith("0x") else int(v) for v in values]
    except ValueError:
        return {"kind": "variable", "samples": len(values), "lengths": sorted({len(v.replace(":", "")) // 2 for v in values})}
    diffs = [b-a for a, b in zip(numbers, numbers[1:])]
    if len(set(diffs)) == 1:
        return {"kind": "step", "delta": diffs[0], "base_per_execution": True, "samples": len(values)}
    blocks = [(value, len(list(group))) for value, group in itertools.groupby(numbers)]
    if len(blocks) >= 3:
        width = blocks[0][1]
        deltas = [b[0]-a[0] for a,b in zip(blocks,blocks[1:])]
        if width > 1 and all(count == width for _,count in blocks[:-1]) and blocks[-1][1] <= width and len(set(deltas)) == 1:
            return {"kind": "block_step", "block_size": width, "delta": deltas[0], "base_per_execution": True, "samples": len(values)}
    return {"kind": "variable", "samples": len(values), "min_observed": min(numbers), "max_observed": max(numbers)}


def validate_rule(rule, values):
    values = [v for v in values if v != ""]
    if len(values) < 2:
        return {"status": "insufficient", "checked": len(values)}
    if rule["kind"] == "constant":
        failures = sum(v != rule["value"] for v in values)
    elif rule["kind"] == "step":
        try:
            numbers = [int(v, 16) if v.startswith("0x") else int(v) for v in values]
        except ValueError:
            return {"status": "failed_non_numeric", "checked": len(values)}
        failures = sum(b-a != rule["delta"] for a, b in zip(numbers, numbers[1:]))
        return {"status": "passed" if failures == 0 else "failed", "checked": len(values)-1, "failures": failures}
    elif rule["kind"] == "block_step":
        try:
            numbers = [int(v, 16) if v.startswith("0x") else int(v) for v in values]
        except ValueError:
            return {"status": "failed_non_numeric", "checked": len(values)}
        failures = sum(value != numbers[0] + (i // rule["block_size"]) * rule["delta"] for i,value in enumerate(numbers[1:],1))
        return {"status": "passed" if failures == 0 else "failed", "checked": len(values)-1, "failures": failures}
    else:
        return {"status": "not_predictable", "checked": len(values)}
    return {"status": "passed" if failures == 0 else "failed", "checked": len(values), "failures": failures}


def pattern_groups():
    from .analysis import collect
    accepted = {r["run_id"] for r in collect()[1]}
    path = ROOT / "resultados/exportaciones_paquetes.json"
    index = json.loads(path.read_text()) if path.exists() else {}
    groups = defaultdict(dict)
    for run_id, relative in sorted(index.items()):
        if run_id not in accepted:
            continue
        folder = ROOT / relative
        verify_manifest(folder)
        meta = json.loads((folder / "metadata.json").read_text())
        if meta["pilot"] or meta["direction"] != "ida":
            continue
        source = ROOT / "datos/originales" / run_id
        if meta.get("format_version", 1) < 2 or meta.get("probe_classifier_revision", 1) < 2 or meta.get("source_manifest_sha256") != sha256(source / "manifest.json"):
            raise ValueError("Reexportar paquetes antes de generar patrones: " + run_id)
        key = (meta["tool"], meta["family"], meta["method"], meta["target"])
        if meta["round"] in groups[key]:
            raise ValueError("Más de una ejecución principal para método, destino y ronda")
        with (folder / "emitted.tsv").open() as stream:
            groups[key][meta["round"]] = (folder, list(csv.DictReader(stream, delimiter="\t")))
    return groups


def patterns():
    groups = pattern_groups()
    out = ROOT / "resultados" / ("patrones_" + identifier())
    out.mkdir(parents=True)
    allrules = []
    for key, rounds in sorted(groups.items()):
        if 1 not in rounds:
            continue
        for field in PACKET_FIELDS:
            if field in ("frame.number", "frame.time_epoch"):
                continue
            rule = learn_rule([r[field] for r in rounds[1][1]])
            checks = {str(n): validate_rule(rule, [r[field] for r in rows]) for n, (_, rows) in rounds.items() if n > 1}
            allrules.append({"tool": key[0], "family": key[1], "method": key[2], "target": key[3], "field": field,
                             "rule": rule, "validation": checks,
                             "training": str(rounds[1][0].relative_to(ROOT)),
                             "warning": "Constancia o incremento son hipótesis de esta captura; solo validación en otra ronda aporta corroboración."})
            if field in ("udp.payload", "tcp.payload", "data.data"):
                def payload_bytes(rows):
                    return [bytes.fromhex(r[field].replace(":", "")) for r in rows if r.get(field)]
                training = payload_bytes(rounds[1][1])
                if training and len({len(v) for v in training}) == 1:
                    for offset in range(len(training[0])):
                        byte_rule = learn_rule([str(v[offset]) for v in training])
                        byte_checks = {}
                        for n, (_, rows) in rounds.items():
                            if n > 1:
                                values = payload_bytes(rows)
                                byte_checks[str(n)] = validate_rule(byte_rule, [str(v[offset]) for v in values if len(v) > offset])
                        allrules.append({"tool": key[0], "family": key[1], "method": key[2], "target": key[3],
                                         "field": field + f"[byte {offset}]", "rule": byte_rule, "validation": byte_checks,
                                         "training": str(rounds[1][0].relative_to(ROOT)),
                                         "warning": "Offset desde cero; regla local contrastada entre rondas, sin garantizar bases ni datos aleatorios."})
    json_write(out / "predictions.json", allrules)
    save_manifest(out, {"kind": "cross_round_packet_patterns", "training_rule_count": len(allrules)})
    return out
