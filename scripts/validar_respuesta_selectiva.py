#!/usr/bin/env python3
"""Corroborar observaciones selectivas con repeticiones acotadas; no deduce ACL."""
import ipaddress, itertools, json, sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from path_discovery.common import (
    ROOT,
    config,
    load_credentials,
    campaign_lock,
    records,
    json_write,
    save_manifest,
    identifier,
    sha256,
    utc,
    verify_manifest,
)
from path_discovery.analysis import collect, load_dataset, normalize_trace, normalize_ripe
from path_discovery.acquire import measure_scamper, measure_ripe
from path_discovery.packets import export_packets


def candidates(rows, runs, tool):
    by_target = defaultdict(lambda: defaultdict(dict))
    ttls = defaultdict(list)
    for r in rows:
        if r.get("ip") and r.get("ttl") is not None:
            ttls[(r["run_id"], r["ip"])].append(r["ttl"])
    for r in runs:
        if (
            r["tool"] != tool
            or r["direction"] != "ida"
            or r["family"] != ("trace" if tool == "scamper" else "traceroute")
        ):
            continue
        if tool == "scamper" and r["method"].startswith("tcp"):
            continue
        by_target[r["target"]][r["method"]][r["round"]] = r
    result = []
    for target, methods in by_target.items():
        for a, b in itertools.permutations(sorted(methods), 2):
            ra, rb = methods[a], methods[b]
            if set(ra) != {1, 2, 3} or set(rb) != {1, 2, 3}:
                continue
            seen = defaultdict(list)
            for n, r in ra.items():
                for ip in r["ips"]:
                    if ipaddress.ip_address(ip).is_global:
                        seen[ip].append(n)
            absent_union = set().union(*(set(r["ips"]) for r in rb.values()))
            for ip, rounds in seen.items():
                if len(rounds) < 2 or ip in absent_union:
                    continue
                comparable = []
                for n in rounds:
                    ttl = min(ttls.get((ra[n]["run_id"], ip), [256]))
                    max_b = max(
                        (
                            r["ttl"]
                            for r in rows
                            if r["run_id"] == rb[n]["run_id"]
                            and r.get("ttl") is not None
                            and r["ttl"] < 255
                        ),
                        default=0,
                    )
                    if max_b >= ttl:
                        comparable.append(n)
                if len(comparable) < 2:
                    continue
                result.append(
                    {
                        "tool": tool,
                        "target": target,
                        "ip": ip,
                        "responds_method": a,
                        "not_observed_method": b,
                        "responding_rounds": rounds,
                        "comparable_ttl_rounds": comparable,
                        "evidence_runs": [ra[n]["run_id"] for n in sorted(ra)]
                        + [rb[n]["run_id"] for n in sorted(rb)],
                        "scope": "IP observada con un método y ausente con otro en ventanas TTL comparables. Puede reflejar diferencias de ruta; no prueba firewall.",
                    }
                )
    return sorted(
        result,
        key=lambda c: (
            -len(c["responding_rounds"]),
            -len(c["comparable_ttl_rounds"]),
            c["ip"] != c["target"],
            c["target"],
            c["responds_method"],
            c["not_observed_method"],
            c["ip"],
        ),
    )


def previous_cases(path, accepted_ids):
    """Reutiliza solo un contraste respaldado por originales íntegros vigentes."""
    if not path.exists():
        return {}, set()
    result = json.loads(path.read_text())
    if result.get("evidence"):
        verify_manifest(ROOT / result["evidence"])
    reusable, failed = {}, set()
    for case in result.get("cases", []):
        candidate = case.get("candidate") or {}
        key = tuple(candidate.get(k) for k in ("tool", "target", "ip", "not_observed_method"))
        if case.get("status") == "not_corroborated":
            failed.add(key)
        evidence = candidate.get("evidence_runs", [])
        if case.get("status") != "corroborated_observation" or not evidence or not set(evidence) <= accepted_ids:
            continue
        extra = case.get("additional_runs", [])
        if len(extra) < 4:
            continue
        for item in extra:
            path = ROOT / "datos/originales" / item["run_id"]
            verify_manifest(path)
            if sha256(path / "manifest.json") != item["manifest_sha256"]:
                raise ValueError("Manifiesto de validación previa modificado")
        reusable[case["tool"]] = {**case, "reused_from": str(pathlib_relative(result["evidence"]))}
    return reusable, failed


def pathlib_relative(value):
    """Valida la referencia de evidencia contenida en el proyecto."""
    path = (ROOT / value).resolve()
    if not path.is_relative_to(ROOT / "datos/originales"):
        raise ValueError("Evidencia previa fuera del proyecto")
    return path.relative_to(ROOT)


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset")
    args = parser.parse_args()
    selection = load_dataset(args.dataset) if args.dataset else None
    output = ROOT / ("resultados/respuesta_selectiva_revision.json" if selection else "resultados/respuesta_selectiva_validacion.json")
    if output.exists():
        print("Validación ya conservada; no se repite.")
        return
    if any((lambda intent: intent.get("session_id") == config().get("session_id") and intent.get("dataset_id") == (selection.get("dataset_id") if selection else None))(json.loads(p.read_text())) for p in (ROOT / "datos/originales").glob("validacion_selectiva_*/intent.json")):
        raise RuntimeError(
            "Hay validación iniciada sin cierre; revisar antes de repetir cualquier POST."
        )
    rows, runs, invalid = collect(dataset=args.dataset)
    if len(runs) != 153 or invalid:
        raise RuntimeError(
            "Completar y validar las 153 ejecuciones principales antes de estas pruebas adicionales."
        )
    load_credentials()
    cfg = config()
    if selection:
        cfg = {**cfg, "targets": selection["targets"]}
    folder = ROOT / "datos/originales" / ("validacion_selectiva_" + identifier())
    folder.mkdir()
    reusable, failed = previous_cases(ROOT / "resultados/respuesta_selectiva_validacion.json", {r["run_id"] for r in runs}) if selection else ({}, set())
    chosen = {}
    for tool in ("scamper", "ripe"):
        if tool in reusable:
            chosen[tool] = reusable[tool]["candidate"]
            continue
        eligible = [c for c in candidates(rows, runs, tool) if tuple(c.get(k) for k in ("tool", "target", "ip", "not_observed_method")) not in failed]
        chosen[tool] = (eligible or [None])[0]
    json_write(
        folder / "intent.json",
        {
            "session_id": cfg.get("session_id"),
            "dataset_id": selection.get("dataset_id") if selection else None,
            "started_at": utc(),
            "selected": chosen,
            "maximum_additional_runs": sum(4 for t, c in chosen.items() if c and t not in reusable),
            "ripe_credit_estimate": 0 if "ripe" in reusable or not chosen["ripe"] else 240,
            "reused_tools": sorted(reusable),
            "purpose": "Dos repeticiones por cada método de un caso Scamper y otro RIPE, sin superponer campaña.",
        },
        exclusive=True,
    )
    results = []
    with campaign_lock():
        for tool, candidate in chosen.items():
            if tool in reusable:
                results.append(reusable[tool])
                continue
            if candidate is None:
                results.append(
                    {
                        "tool": tool,
                        "status": "no_reproducible_case_found",
                        "limitation": "No se identificó una IP pública con contraste repetido y TTL comparable. No se fabrica un caso de filtrado.",
                    }
                )
                continue
            target = next(t for t in cfg["targets"] if t["ip"] == candidate["target"])
            extra = []
            for repeat in (1, 2):
                for method in (
                    candidate["responds_method"],
                    candidate["not_observed_method"],
                ):
                    if tool == "scamper":
                        original = measure_scamper(
                            cfg, target, "trace", method, 0, kind="targeted_validation"
                        )
                    else:
                        original = measure_ripe(
                            cfg, target, method, "ida", 0, kind="targeted_validation"
                        )
                    meta = json.loads((original / "metadata.json").read_text())
                    observations = []
                    for obj in records(
                        original
                        / ("result.jsonl" if tool == "scamper" else "results.json")
                    ):
                        if tool == "scamper" and obj.get("type") == "trace":
                            observations += normalize_trace(obj, meta, original.name)
                        elif tool == "ripe":
                            observations += normalize_ripe(obj, meta, original.name)
                    ips = {r["ip"] for r in observations if r.get("ip")}
                    export = export_packets(original)
                    extra.append(
                        {
                            "repeat": repeat,
                            "method": method,
                            "run_id": original.name,
                            "measurement_id": meta.get("measurement_id"),
                            "ip_observed": candidate["ip"] in ips,
                            "unique_ips": sorted(ips),
                            "export": str(export.relative_to(ROOT)),
                            "manifest_sha256": sha256(original / "manifest.json"),
                        }
                    )
                    json_write(folder / f"progress_{tool}.json", extra)
            a = [x for x in extra if x["method"] == candidate["responds_method"]]
            b = [x for x in extra if x["method"] == candidate["not_observed_method"]]
            confirmed = all(x["ip_observed"] for x in a) and not any(
                x["ip_observed"] for x in b
            )
            results.append(
                {
                    "tool": tool,
                    "candidate": candidate,
                    "additional_runs": extra,
                    "status": (
                        "corroborated_observation" if confirmed else "not_corroborated"
                    ),
                    "interpretation": "Corroboración del comportamiento observado, sin identificar una regla de firewall. No aparición también puede corresponder a otra ruta, pérdida, balanceo o recepción local.",
                }
            )
    result = {
        "session_id": cfg.get("session_id"),
        "dataset_id": selection.get("dataset_id") if selection else None,
        "session_public_ipv4": cfg.get("session_public_ipv4"),
        "performed_at": utc(),
        "evidence": str(folder.relative_to(ROOT)),
        "cases": results,
        "requirements_corroborated": all(
            r["status"] == "corroborated_observation" for r in results
        ),
        "scope": "Pruebas adicionales fuera de las 153 celdas y del entrenamiento de patrones.",
    }
    json_write(folder / "result.json", result, exclusive=True)
    save_manifest(folder, {"kind": "selective_response_validation"})
    json_write(output, result)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
