"""Normalización sin completar rutas, métricas, tablas y grafos CX2."""
from __future__ import annotations

import ipaddress
import itertools
import json
import statistics
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from .common import (ROOT, TRACE_METHODS, RIPE_METHODS, config, csv_write, identifier,
                     json_write, records, request_json, save_manifest, utc, verify_manifest, sha256)

FIELDS = ["run_id", "tool", "family", "method", "round", "direction", "target", "source", "destination",
          "measurement_id", "probe_id", "timestamp", "ttl", "attempt", "reply_index", "ip", "rtt_ms",
          "status", "run_status", "pilot", "flow_id", "tx", "evidence_path", "asns", "prefix", "asn_status"]


def row_base(meta, run_id, obj):
    return {"run_id": run_id, **{k: meta.get(k) for k in ("tool", "family", "method", "round", "direction", "target", "destination", "measurement_id", "probe_id")},
            "source": obj.get("src_addr", obj.get("src", obj.get("from"))),
            "timestamp": obj.get("timestamp", obj.get("start", {}).get("sec")),
            "evidence_path": f"datos/originales/{run_id}", "ip": None, "ttl": None,
            "run_status": meta.get("status"), "pilot": meta.get("pilot", False),
            "attempt": None, "reply_index": None, "rtt_ms": None, "status": "unknown", "flow_id": None, "tx": None}


def normalize_ripe(obj, meta, run_id):
    base = row_base(meta, run_id, obj)
    if obj.get("prb_id") != meta.get("probe_id") or obj.get("msm_id") != meta.get("measurement_id"):
        raise ValueError("Resultado RIPE de otra sonda o measurement_id")
    if obj.get("dst_addr") != meta.get("destination"):
        raise ValueError("Destino RIPE inesperado")
    result = []
    for hop in obj.get("result", []):
        if "hop" not in hop:
            result.append({**base, "status": "error", "error": hop})
            continue
        replies = hop.get("result") or [{"error": hop.get("error", "sin intentos registrados")}]
        for attempt, reply in enumerate(replies, 1):
            ip = reply.get("from")
            status = "reply" if ip else "timeout" if "x" in reply else "error"
            result.append({**base, "ttl": hop["hop"], "attempt": attempt, "reply_index": attempt,
                           "ip": ip, "rtt_ms": reply.get("rtt"), "status": status,
                           "raw_reply": reply})
    if not result:
        result.append({**base, "status": "error", "error": obj.get("error", "sin saltos")})
    return result


def normalize_trace(obj, meta, run_id):
    base = row_base(meta, run_id, obj)
    rows = []
    for group, status in (("hops", "reply"), ("no_hops", "timeout")):
        for idx, reply in enumerate(obj.get(group, []), 1):
            rows.append({**base, "ttl": reply.get("probe_ttl"), "attempt": reply.get("probe_id"),
                         "reply_index": idx, "ip": reply.get("addr"), "rtt_ms": reply.get("rtt"),
                         "status": status, "tx": reply.get("tx"), "raw_reply": reply})
    seen = {r["ttl"] for r in rows}
    # Sin asumir que se enviaron todos los intentos máximos configurados.
    for ttl in range(obj.get("firsthop", 1), obj.get("hop_count", 0) + 1):
        if ttl not in seen:
            rows.append({**base, "ttl": ttl, "status": "not_recorded"})
    return rows or [{**base, "status": "error", "error": obj.get("errmsg", "sin saltos") }]


def normalize_lb(obj, meta, run_id):
    """El JSON de 20260902 contiene nodes[].links[][] con probes[].replies[]."""
    base = row_base(meta, run_id, obj)
    rows, seen = [], set()

    def walk(value, parent_addr=None):
        if isinstance(value, list):
            for item in value:
                walk(item, parent_addr)
        elif isinstance(value, dict):
            addr = value.get("addr", parent_addr)
            if "probes" in value:
                for probe in value["probes"]:
                    replies = probe.get("replies") or [None]
                    for reply_index, reply in enumerate(replies):
                        key = json.dumps([addr, probe.get("tx"), probe.get("ttl"), probe.get("flowid"), probe.get("attempt"), reply], sort_keys=True)
                        if key in seen:
                            continue
                        seen.add(key)
                        rows.append({**base, "ttl": probe.get("ttl"), "attempt": probe.get("attempt"),
                                     "reply_index": reply_index, "flow_id": probe.get("flowid"), "tx": probe.get("tx"),
                                     "ip": addr if reply and addr != "*" else None,
                                     "rtt_ms": reply.get("rtt") if reply else None,
                                     "status": "reply" if reply else "timeout", "raw_reply": reply})
            for key, val in value.items():
                if key not in ("probes", "replies") and isinstance(val, (dict, list)):
                    walk(val, addr)

    walk(obj.get("nodes", []))
    # Los nodos raíz pueden carecer de sondas en la exportación JSON. Se conservan
    # sin inventar TTL ni intento; WARTS sigue siendo la fuente completa.
    represented = {r["ip"] for r in rows}
    for node in obj.get("nodes", []):
        addr = node.get("addr")
        if addr and addr != "*" and addr not in represented:
            rows.append({**base, "ip": addr, "status": "node_only"})
            represented.add(addr)
    return rows or [{**base, "status": "error", "error": "sin nodos exportados"}]


def excluded_runs():
    """Exclusiones de calidad separadas de los parámetros de medición sellados."""
    excluded = set(config().get("excluded_runs", []))
    path = ROOT / "config/exclusiones_calidad.json"
    if path.exists():
        decision = json.loads(path.read_text())
        evidence = ROOT / decision["evidence_path"]
        verify_manifest(evidence)
        if sha256(evidence / "manifest.json") != decision["evidence_manifest_sha256"]:
            raise ValueError("Cambió la evidencia de exclusión de calidad")
        excluded.update(decision["excluded_runs"])
    return excluded


def collect(*, include_pilots=False, diagnostic_pilots=False):
    rows, runs, invalid = [], [], []
    excluded = excluded_runs()
    export_index = ROOT / "resultados/exportaciones_paquetes.json"
    exports = json.loads(export_index.read_text()) if export_index.exists() else {}
    for folder in sorted((ROOT / "datos/originales").glob("*")):
        if folder.name in excluded:
            continue
        if not (folder / "metadata.json").exists():
            continue
        try:
            verify_manifest(folder)
        except (OSError, ValueError, KeyError) as e:
            invalid.append({"run_id": folder.name, "reason": str(e)})
            continue
        meta = json.loads((folder / "metadata.json").read_text())
        if meta.get("kind") != "measurement" or (meta.get("pilot") and not include_pilots):
            continue
        diagnostic = diagnostic_pilots and meta.get("pilot") and meta.get("status") == "invalid_public_ip_changed"
        if meta.get("status") != "completed" and not diagnostic:
            invalid.append({"run_id": folder.name, "reason": meta.get("status")})
            continue
        path = folder / ("results.json" if meta["tool"] == "ripe" else "result.jsonl")
        raw = records(path)
        runrows, probes_sent = [], 0
        for obj in raw:
            if meta["tool"] == "ripe":
                if obj.get("prb_id") != meta["probe_id"]:
                    continue
                current = normalize_ripe(obj, meta, folder.name)
                probes_sent = None  # Contar desde captura; no inferir desde respuestas recibidas.
            elif obj.get("type") == "trace":
                current = normalize_trace(obj, meta, folder.name)
                probes_sent += obj.get("probe_count", 0)
            elif obj.get("type") == "tracelb":
                current = normalize_lb(obj, meta, folder.name)
                probes_sent += obj.get("probec", 0)
            else:
                continue
            runrows.extend(current)
        rows.extend(runrows)
        ips = sorted({r["ip"] for r in runrows if r.get("ip")})
        if meta["tool"] == "ripe" and meta["direction"] == "ida" and folder.name in exports:
            exported = ROOT / exports[folder.name]
            if not exported.resolve().is_relative_to(ROOT / "resultados/paquetes"):
                raise ValueError("Exportación fuera de resultados/paquetes")
            verify_manifest(exported)
            packet_meta = json.loads((exported / "metadata.json").read_text())
            if packet_meta.get("source_manifest_sha256") != sha256(folder / "manifest.json"):
                raise ValueError("La captura exportada no corresponde al original actual")
            probes_sent = packet_meta["candidate_emitted_packets"]
        ttl = {r["ttl"] for r in runrows if r["ttl"] is not None}
        replied = {r["ttl"] for r in runrows if r.get("ip") and r["ttl"] is not None}
        runs.append({**meta, "run_id": folder.name, "ips": ips, "unique_ips": len(ips),
                     "observed_hops": len(ttl), "responsive_hops": len(replied),
                     "coverage": len(replied)/len(ttl) if ttl else 0,
                     "missing_hops": len(ttl - replied), "probes_sent": probes_sent,
                     "elapsed_wall_seconds": (datetime.fromisoformat(meta["finished_at"]) - datetime.fromisoformat(meta["started_at"])).total_seconds() if meta.get("finished_at") and meta.get("started_at") else None,
                     "destination_observed": meta["destination"] in ips})
    return rows, runs, invalid


def enrich(rows, *, online=False):
    cache_dir = ROOT / "datos/originales/asn"
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache = {}
    for row in rows:
        ip = row.get("ip")
        if not ip:
            continue
        address = ipaddress.ip_address(ip)
        if not address.is_global:
            row.update(asns=[], prefix=None, asn_status="non_global")
            continue
        if ip not in cache:
            path = cache_dir / f"{ip}.json"
            if not path.exists() and online:
                data = request_json(f"https://stat.ripe.net/data/network-info/data.json?resource={ip}")
                json_write(path, {"queried_at": utc(), "response": data}, exclusive=True)
            cache[ip] = json.loads(path.read_text())["response"]["data"] if path.exists() else None
        data = cache[ip]
        row.update(asns=data.get("asns", []) if data else [], prefix=data.get("prefix") if data else None,
                   asn_status="mapped" if data and data.get("asns") else "unknown")
    return rows


def hop_cells(rows):
    hops = defaultdict(set)
    for r in rows:
        if r["ttl"] is None:
            continue
        ips = r.get("ip") or ("*" if r["status"] == "timeout" else "? " + r["status"])
        asns = r.get("asns")
        if r.get("ip"):
            ips += " [" + (",".join("AS" + str(a) for a in asns) if asns else r.get("asn_status", "unknown")) + "]"
        hops[r["ttl"]].add(ips)
    return {ttl: "; ".join(sorted(values)) for ttl, values in hops.items()}


def tables(rows, runs, out):
    for target in config()["targets"]:
        dest = target["ip"]
        for round_no in range(1, 4):
            rr = [r for r in rows if r["target"] == dest and r["round"] == round_no]
            for family, methods, name in (("trace", TRACE_METHODS, "tabla1"), ("traceroute", RIPE_METHODS, "ripe_ida")):
                cells = {m: hop_cells([r for r in rr if r["family"] == family and r["method"] == m and r["direction"] == "ida"]) for m in methods}
                ttls = sorted({t for c in cells.values() for t in c})
                csv_write(out / f"{name}_{dest}_r{round_no}.csv", [{"HOP": t, **{m: cells[m].get(t, "NO_MEDIDO") for m in methods}} for t in ttls], ["HOP", *methods])
            for protocol in RIPE_METHODS:
                cells = {d: hop_cells([r for r in rr if r["tool"] == "ripe" and r["method"] == protocol and r["direction"] == d]) for d in ("ida", "vuelta")}
                ttls = sorted(set(cells["ida"]) | set(cells["vuelta"]))
                csv_write(out / f"tabla2_{dest}_{protocol}_r{round_no}.csv", [{"HOP": t, "IP_IDA": cells["ida"].get(t, "NO_MEDIDO"), "IP_VUELTA": cells["vuelta"].get(t, "NO_MEDIDO")} for t in ttls], ["HOP", "IP_IDA", "IP_VUELTA"])


def method_rankings(runs):
    groups = defaultdict(list)
    for r in runs:
        groups[(r["target"], r["tool"], r["family"], r["direction"], r["method"])].append(r)
    result = []
    for (target, tool, family, direction, method), group in groups.items():
        # Una sola ejecución válida por celda; duplicados se resuelven antes de analizar.
        sets = [set(r["ips"]) for r in group]
        similarity = [len(a & b)/len(a | b) if a | b else 1 for a, b in itertools.combinations(sets, 2)]
        packet_counts = [r["probes_sent"] for r in group if r.get("probes_sent") is not None]
        elapsed = [r["elapsed_wall_seconds"] for r in group if r.get("elapsed_wall_seconds") is not None]
        result.append({"target": target, "tool": tool, "family": family, "direction": direction, "method": method,
                       "rounds": len({r["round"] for r in group}), "median_unique_ips": statistics.median(r["unique_ips"] for r in group),
                       "provisional": len({r["round"] for r in group}) < 3,
                       "median_coverage": statistics.median(r["coverage"] for r in group),
                       "stability_jaccard": statistics.mean(similarity) if similarity else None,
                       "median_probes_sent": statistics.median(packet_counts) if packet_counts else None,
                       "median_elapsed_wall_seconds": statistics.median(elapsed) if elapsed else None,
                       "destination_observed_runs": sum(r["destination_observed"] for r in group)})
    return sorted(result, key=lambda r: (r["target"], r["tool"], r["family"], r["direction"], -r["median_unique_ips"], -r["median_coverage"], -(r["stability_jaccard"] or 0), r["method"]))


def additional_ips(runs):
    result = []
    for r in runs:
        if r["family"] != "tracelb":
            continue
        reference = [a for a in runs if a["family"] == "trace" and a["target"] == r["target"] and a["round"] == r["round"]]
        union = set().union(*(set(a["ips"]) for a in reference))
        result.append({"run_id": r["run_id"], "target": r["target"], "round": r["round"], "method": r["method"],
                       "reference_methods": len(reference), "complete_reference": len({a["method"] for a in reference}) == 6,
                       "additional_ips": sorted(set(r["ips"]) - union), "probes_sent": r["probes_sent"],
                       "reference_probes_sent": sum(a["probes_sent"] or 0 for a in reference)})
    return result


def selective_candidates(rows, runs):
    groups = defaultdict(dict)
    for run in runs:
        if run["direction"] == "ida" and run["family"] != "tracelb":
            groups[(run["target"], run["tool"], run["round"])][run["method"]] = run
    candidates = []
    for (target, tool, round_no), group in groups.items():
        for a, b in itertools.permutations(group.values(), 2):
            for ip in sorted(set(a["ips"]) - set(b["ips"])):
                candidates.append({"target": target, "tool": tool, "round": round_no, "ip": ip,
                                   "responds_method": a["method"], "not_observed_method": b["method"],
                                   "responds_run": a["run_id"], "absent_run": b["run_id"],
                                   "status": "candidate_requires_targeted_validation_not_firewall_proof"})
    return candidates


def choose_pairs(runs):
    choices = defaultdict(list)
    for a in runs:
        if a["tool"] != "ripe" or a["direction"] != "ida":
            continue
        for b in runs:
            if b["tool"] != "ripe" or b["direction"] != "vuelta":
                continue
            if any(a[k] != b[k] for k in ("target", "method", "round", "public_ipv4")):
                continue
            delta = abs((datetime.fromisoformat(a["started_at"]) - datetime.fromisoformat(b["started_at"])).total_seconds())
            union = len(set(a["ips"]) | set(b["ips"]))
            choices[a["target"]].append(((-union, a["missing_hops"] + b["missing_hops"], delta, a["method"], a["run_id"], b["run_id"]), a, b))
    return {target: min(items, key=lambda x: x[0])[1:] for target, items in choices.items()}


def symmetry(rows, runs):
    result = []
    for a in runs:
        if a["tool"] != "ripe" or a["direction"] != "ida":
            continue
        for b in runs:
            if b["tool"] != "ripe" or b["direction"] != "vuelta" or any(a[k] != b[k] for k in ("target", "method", "round", "public_ipv4")):
                continue
            sequences, as_sequences = [], []
            incomplete = False
            endpoints = {a["target"], a["public_ipv4"]}
            for r in (a, b):
                layers = defaultdict(list)
                for row in rows:
                    if row["run_id"] == r["run_id"] and row["ttl"] is not None:
                        layers[row["ttl"]].append(row)
                sequence, as_sequence = [], []
                previous_ttl = 0
                for ttl, layer in sorted(layers.items()):
                    if ttl != previous_ttl + 1:
                        incomplete = True
                    previous_ttl = ttl
                    ips = {v["ip"] for v in layer if v.get("ip") and v["ip"] not in endpoints}
                    if not layer or any(not v.get("ip") for v in layer):
                        incomplete = True
                    # Saltos que contienen solo el extremo quedan fuera de la
                    # comparación de interfaces intermedias.
                    if ips or not any(v.get("ip") in endpoints for v in layer):
                        sequence.append(sorted(ips) if ips else ["*"])
                        asns = sorted({str(asn) for v in layer for asn in v.get("asns", []) if v.get("ip") not in endpoints})
                        token = asns or ["unknown"]
                        if not as_sequence or as_sequence[-1] != token:
                            as_sequence.append(token)
                sequences.append(sequence)
                as_sequences.append(as_sequence)
            ida, vuelta = sequences
            ai, av = as_sequences
            s1, s2 = set(a["ips"]) - endpoints, set(b["ips"]) - endpoints
            result.append({"target": a["target"], "protocol": a["method"], "round": a["round"],
                           "ida_id": a["measurement_id"], "vuelta_id": b["measurement_id"],
                           "ida_ip_layers": ida, "vuelta_reversed_ip_layers": vuelta[::-1],
                           "intermediate_ip_sets_equal": s1 == s2,
                           "observed_ip_layer_order_equal": ida == vuelta[::-1],
                           "observed_as_sequence_equal": ai == av[::-1],
                           "ida_as_sequence": ai, "vuelta_reversed_as_sequence": av[::-1],
                           "ip_jaccard": len(s1 & s2)/len(s1 | s2) if s1 | s2 else None,
                           "ida_unique_ips": a["unique_ips"], "vuelta_unique_ips": b["unique_ips"],
                           "incomplete": incomplete or not a["destination_observed"] or not b["destination_observed"],
                           "interpretation": "comparacion de observaciones; no prueba alias de routers ni ruta BGP"})
    return result


def cx2_graph(pair, rows):
    """Las capas de salto ambiguas no se expanden en enlaces IP cartesianos."""
    nodes, edges, ids = [], [], {}

    def node(label, attrs, x, y):
        key = label if attrs.get("kind") == "ip_interface" else attrs["key"]
        if key not in ids:
            nid = len(nodes)
            ids[key] = nid
            node_label = label
            if attrs.get("kind") == "ip_interface":
                asns = attrs.get("asns", "")
                node_label += "\n" + ("AS" + asns.replace(",", ", AS") if asns else "sin ASN disponible")
            else:
                node_label = ("Sin respuesta" if attrs.get("kind") == "gap" else "Respuesta múltiple") + f"\nTTL {attrs.get('ttl')}"
            nodes.append({"id": nid, "x": float(x), "y": float(y), "v": {"name": label, "label": node_label, **{k: v for k, v in attrs.items() if k != "key"}}})
        return ids[key]

    columns = max((len({r["ttl"] for r in rows if r["run_id"] == run["run_id"] and r["ttl"] is not None}) for run in pair), default=0)
    for line, run in enumerate(pair):
        rr = [r for r in rows if r["run_id"] == run["run_id"]]
        layers = defaultdict(list)
        source = next((r["source"] for r in rr if r.get("source")), None)
        previous = node(source, {"kind": "ip_interface", "asns": ""}, (0 if line == 0 else columns*160), line*230) if source else None
        for r in rr:
            if r["ttl"] is not None:
                layers[r["ttl"]].append(r)
        previous_ttl = 0
        for column, (ttl, layer) in enumerate(sorted(layers.items()), 1):
            # RIPE puede incluir TTL 255 tras un tramo interrumpido. No crear
            # cientos de saltos inexistentes ni afirmar adyacencia entre TTL separados.
            if ttl != previous_ttl + 1:
                previous = None
            addresses = sorted({r["ip"] for r in layer if r.get("ip")})
            mixed = any(not r.get("ip") for r in layer)
            if len(addresses) == 1 and not mixed:
                matching = [r for r in layer if r.get("ip") == addresses[0]][0]
                current = node(addresses[0], {"kind": "ip_interface", "asns": ",".join(map(str, matching.get("asns", [])))}, (column if line == 0 else columns-column)*160, line*230)
                evidence = "inferred_traceroute_adjacency"
            else:
                label = "*" if not addresses else " | ".join(addresses) + (" | *" if mixed else "")
                current = node(label, {"kind": "gap" if not addresses else "ambiguous_hop", "key": f"{run['run_id']}:{ttl}", "asns": "", "ttl": ttl}, (column if line == 0 else columns-column)*160, line*230)
                evidence = "hop_layer_order_only"
            if previous is not None and current != previous:
                edges.append({"id": len(edges), "s": previous, "t": current, "v": {"direction": run["direction"], "protocol": run["method"], "ttl": ttl, "measurement_id": str(run["measurement_id"]), "evidence": evidence}})
            previous = current
            previous_ttl = ttl
    a, b = pair
    description = f"Path Discovery {a['target']}. Ida msm_id={a['measurement_id']}; vuelta msm_id={b['measurement_id']}. {a['method']}, ronda {a['round']}. Ida azul/verde; vuelta naranja; flechas indican sentido. Huecos grises y capas ambiguas amarillas. Adyacencias inferidas; IPs no equivalen necesariamente a routers; huecos y saltos ambiguos explícitos. TTL no consecutivos sin enlace entre sí."
    return [{"CXVersion": "2.0", "hasFragments": False}, {"metaData": [{"name": "nodes", "elementCount": len(nodes)}, {"name": "edges", "elementCount": len(edges)}]},
            {"attributeDeclarations": [{"networkAttributes": {"name": {"d": "string"}, "description": {"d": "string"}}, "nodes": {"name": {"d": "string"}, "label": {"d": "string"}, "kind": {"d": "string"}, "asns": {"d": "string"}, "ttl": {"d": "integer"}}, "edges": {"direction": {"d": "string"}, "protocol": {"d": "string"}, "ttl": {"d": "integer"}, "measurement_id": {"d": "string"}, "evidence": {"d": "string"}}}]},
            {"networkAttributes": [{"name": "Path Discovery " + a["target"], "description": description}]},
            {"nodes": nodes}, {"edges": edges},
            {"visualProperties": [{"default": {
                "node": {"NODE_WIDTH": 135, "NODE_HEIGHT": 44, "NODE_SHAPE": "round-rectangle", "NODE_BACKGROUND_COLOR": "#DCEEF2", "NODE_BORDER_COLOR": "#173D5C", "NODE_BORDER_WIDTH": 1.2, "NODE_LABEL_COLOR": "#173D5C", "NODE_LABEL_FONT_SIZE": 10},
                "edge": {"EDGE_WIDTH": 2.0, "EDGE_LINE_COLOR": "#137C82", "EDGE_TARGET_ARROW_SHAPE": "triangle", "EDGE_TARGET_ARROW_COLOR": "#137C82", "EDGE_CURVE_STYLE": "bezier"}},
                "nodeMapping": {"NODE_LABEL": {"type": "PASSTHROUGH", "definition": {"attribute": "label"}}, "NODE_BACKGROUND_COLOR": {"type": "DISCRETE", "definition": {"attribute": "kind", "map": [{"v": "ip_interface", "vp": "#DCEEF2"}, {"v": "gap", "vp": "#E5E7EB"}, {"v": "ambiguous_hop", "vp": "#FDE6AD"}]}}},
                "edgeMapping": {prop: {"type": "DISCRETE", "definition": {"attribute": "direction", "map": [{"v": "ida", "vp": "#137C82"}, {"v": "vuelta", "vp": "#CC641D"}]}} for prop in ("EDGE_LINE_COLOR", "EDGE_TARGET_ARROW_COLOR")}}]},
            {"visualEditorProperties": [{"arrowColorMatchesEdge": True, "nodeSizeLocked": False}]},
            {"status": [{"success": True}]}]


def analyze(*, online=False, include_pilots=False, diagnostic_pilots=False):
    rows, runs, invalid = collect(include_pilots=include_pilots or diagnostic_pilots, diagnostic_pilots=diagnostic_pilots)
    cells = defaultdict(list)
    for r in runs:
        cells[tuple(r[k] for k in ("tool", "family", "method", "round", "direction", "target"))].append(r["run_id"])
    duplicates = [v for v in cells.values() if len(v) > 1]
    if duplicates:
        raise ValueError(f"Ejecuciones duplicadas; retirar explícitamente del análisis la repetición sustituida: {duplicates}")
    rows = enrich(rows, online=online)
    out = ROOT / "resultados" / ("analisis_" + identifier())
    out.mkdir(parents=True)
    json_write(out / "responses.json", rows)
    csv_write(out / "responses.csv", [{**r, "asns": ",".join(map(str, r.get("asns", [])))} for r in rows], FIELDS)
    json_write(out / "runs.json", runs)
    json_write(out / "invalid.json", invalid)
    json_write(out / "rankings.json", method_rankings(runs))
    json_write(out / "tracelb_additional.json", additional_ips(runs))
    json_write(out / "selective_candidates.json", selective_candidates(rows, runs))
    json_write(out / "symmetry.json", symmetry(rows, runs))
    tables(rows, runs, out / "tablas")
    pairs = choose_pairs(runs)
    for target, pair in pairs.items():
        json_write(out / "grafos" / f"{target}.cx2.json", cx2_graph(pair, rows))
        json_write(out / "grafos" / f"{target}.selection.json", {"ids": [p["measurement_id"] for p in pair], "runs": [p["run_id"] for p in pair], "criterion": "max IP union; min gaps; min temporal distance", "target": target})
    summary = {"created_at": utc(), "valid_measurements": sum(r.get("status") == "completed" and not r.get("pilot") for r in runs), "processed_runs": len(runs), "expected": 153,
               "includes_pilots": include_pilots or diagnostic_pilots, "diagnostic_pilots": diagnostic_pilots, "invalid": invalid, "graphs": list(pairs), "excluded_runs": sorted(excluded_runs()),
               "complete_campaign": len(runs) == 153 and not include_pilots and not diagnostic_pilots and not invalid}
    json_write(out / "summary.json", summary)
    save_manifest(out, {"kind": "analysis", **summary})
    return out, summary
