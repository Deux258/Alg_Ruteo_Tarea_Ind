from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from .acquire import (fetch_ripe, init_probe, measure_ripe, measure_scamper,
                      plan_jobs, preflight)
from .analysis import analyze, collect, load_dataset
from .common import (ROOT, TRACE_METHODS, LB_METHODS, RIPE_METHODS, campaign_lock,
                     clone_sources, command, config, identifier, json_write,
                     public_ip, save_manifest, sha256, utc, verify_manifest)
from .common import load_credentials
from .delivery import bundle, publish, record_browser_publication
from .packets import export_packets, patterns, review_udp_pilots


def resolve_run(name):
    path = (ROOT / "datos/originales" / name).resolve()
    if not path.is_relative_to(ROOT / "datos/originales") or not path.is_dir():
        raise ValueError("Run inexistente o fuera de datos/originales")
    return path


def fingerprint(cfg):
    return hashlib.sha256(json.dumps(cfg, sort_keys=True).encode()).hexdigest()


def selected_udp_pilots(target):
    rows, runs, invalid = collect(include_pilots=True)
    pilots = [r for r in runs if r.get("pilot") and r["target"] == target]
    local = [r for r in pilots if r["tool"] == "scamper" and r["family"] == "trace" and r["method"] == "udp"]
    ida = [r for r in pilots if r["tool"] == "ripe" and r["direction"] == "ida" and r["method"] == "UDP"]
    vuelta = [r for r in pilots if r["tool"] == "ripe" and r["direction"] == "vuelta" and r["method"] == "UDP"]
    if not local or not ida or not vuelta:
        raise ValueError("Piloto incompleto: requiere Scamper UDP y RIPE UDP ida/vuelta")
    return [local[-1], ida[-1], vuelta[-1]]


def accept_pilot(args):
    cfg = config()
    chosen = selected_udp_pilots(args.target)
    packet_review = None
    if args.packet_review:
        path = Path(args.packet_review).resolve()
        if not path.is_relative_to(ROOT / "resultados"):
            raise ValueError("La revisión debe estar dentro de resultados")
        verify_manifest(path)
        packet_review = json.loads((path / "review.json").read_text())
        if packet_review.get("mode") != "tshark_decoded_headers_and_bytes" or set(packet_review.get("runs", [])) != {r["run_id"] for r in chosen}:
            raise ValueError("Revisión TShark incompatible con los pilotos seleccionados")
        for r in chosen:
            evidence = next((e for e in packet_review.get("reviews", []) if e.get("run_id") == r["run_id"]), {})
            if evidence.get("source_manifest_sha256") != sha256(resolve_run(r["run_id"]) / "manifest.json"):
                raise ValueError("Cambió el original revisado")
            if r["direction"] == "ida" and (not evidence.get("requests_count") or not evidence.get("matched_quotes")):
                raise ValueError("La revisión de ida carece de solicitudes y respuestas correlacionadas")
    if not args.wireshark_reviewed and packet_review is None:
        raise ValueError("Revisar PCAP en Wireshark o generar pilot-review y proporcionar --packet-review")
    if cfg["udp_base_port"] is None:
        raise ValueError("Configurar udp_base_port a partir del PCAP piloto RIPE UDP")
    if cfg.get("session_public_ipv4") and any(r["public_ipv4"] != cfg["session_public_ipv4"] for r in chosen):
        raise ValueError("Piloto de otra sesión pública")
    if len({r["public_ipv4"] for r in chosen}) != 1:
        raise ValueError("Los pilotos no comparten IPv4 pública")
    import csv
    exports = []
    for run in chosen:
        folder = resolve_run(run["run_id"])
        exports.append(export_packets(folder))
    with (exports[1] / "emitted.tsv").open() as f:
        packets = list(csv.DictReader(f, delimiter="\t"))
    udp = [int(p["udp.dstport"]) for p in packets if p.get("udp.dstport")]
    if not udp or cfg["udp_base_port"] != min(udp):
        raise ValueError("udp_base_port no coincide con la base observada en el piloto RIPE UDP")
    value = {"accepted_at": utc(), "config_fingerprint": fingerprint(cfg), "public_ipv4": chosen[0]["public_ipv4"],
             "runs": [r["run_id"] for r in chosen], "manual_wireshark_review": args.wireshark_reviewed,
             "packet_review": str(path.relative_to(ROOT)) if packet_review is not None else None,
             "packet_review_manifest": sha256(path / "manifest.json") if packet_review is not None else None,
             "manifests": {r["run_id"]: sha256(resolve_run(r["run_id"]) / "manifest.json") for r in chosen}}
    json_write(ROOT / ".state/pilot.json", value)
    return value


def run_campaign(round_no):
    cfg = config()
    path = ROOT / ".state/pilot.json"
    if not path.exists():
        raise ValueError("Completar y aceptar el piloto antes de lanzar la campaña")
    pilot = json.loads(path.read_text())
    if pilot["config_fingerprint"] != fingerprint(cfg):
        raise ValueError("Configuración modificada después del piloto; volver a validarlo")
    for name, digest in pilot["manifests"].items():
        verify_manifest(resolve_run(name))
        if sha256(resolve_run(name) / "manifest.json") != digest:
            raise ValueError("Cambió la evidencia del piloto")
    if pilot.get("packet_review"):
        review = ROOT / pilot["packet_review"]
        verify_manifest(review)
        if sha256(review / "manifest.json") != pilot["packet_review_manifest"]:
            raise ValueError("Cambió la revisión de paquetes del piloto")
    _, checks = preflight()
    if checks["blockers"]:
        raise ValueError("Preflight bloquea campaña: " + "; ".join(checks["blockers"]))
    statefile = ROOT / ".state/campaign.json"
    state = json.loads(statefile.read_text()) if statefile.exists() else {"fingerprint": fingerprint(cfg), "public_ipv4": public_ip(), "rounds": {}}
    if state["fingerprint"] != fingerprint(cfg) or state["public_ipv4"] != public_ip():
        raise ValueError("Cambió la configuración o IPv4 pública; conservar sesión y preparar una nueva explícitamente")
    previous = state["rounds"].get(str(round_no-1))
    if round_no > 1:
        if not previous or not previous.get("finished_at"):
            raise ValueError("Completar la ronda anterior primero")
        elapsed = (datetime.now(timezone.utc) - datetime.fromisoformat(previous["finished_at"])).total_seconds()
        if elapsed < cfg["round_gap_seconds"]:
            raise ValueError(f"Separar rondas: faltan {int(cfg['round_gap_seconds'] - elapsed)} segundos")
    rd = state["rounds"].setdefault(str(round_no), {"started_at": utc(), "jobs": {}})
    for job in [j for j in plan_jobs(cfg) if j["round"] == round_no]:
        key = "|".join(str(job[k]) for k in ("target", "tool", "family", "method", "direction"))
        old = rd["jobs"].get(key)
        if old:
            # Un trabajo en curso o fallido no se reenvía; exige inspección explícita.
            if old.get("status") != "completed":
                raise ValueError(f"Trabajo pendiente de revisar: {key}. No se repetirá automáticamente.")
            verify_manifest(resolve_run(old["run_id"]))
            continue
        rd["jobs"][key] = {"status": "running", "started_at": utc()}
        json_write(statefile, state)
        t = next(t for t in cfg["targets"] if t["ip"] == job["target"])
        print(f"Midiendo {key}", flush=True)
        try:
            if job["tool"] == "scamper":
                folder = measure_scamper(cfg, t, job["family"], job["method"], round_no)
            else:
                folder = measure_ripe(cfg, t, job["method"], job["direction"], round_no)
            meta = json.loads((folder / "metadata.json").read_text())
            if meta["status"] != "completed":
                raise RuntimeError("Resultado no válido")
            rd["jobs"][key] = {"status": "completed", "run_id": folder.name}
        except BaseException:
            rd["jobs"][key]["status"] = "needs_review"
            json_write(statefile, state)
            raise
        json_write(statefile, state)
    rd["finished_at"] = utc()
    json_write(statefile, state)
    return rd


def recover_ripe(name):
    import shutil
    old = resolve_run(name)
    verify_manifest(old)
    if (old / "metadata.json").exists():
        raise ValueError("El run ya tiene resultado final; no sobrescribir")
    new = ROOT / "datos/originales" / ("ripe_recovery_" + identifier())
    new.mkdir()
    for item in ("pending.json", "request.json", "created.json", "capture.pcapng", "capture.log"):
        if (old / item).exists():
            shutil.copyfile(old / item, new / item)
    meta = json.loads((new / "pending.json").read_text())
    meta["recovered_from"] = old.name
    json_write(new / "pending.json", meta)
    try:
        result = fetch_ripe(new)
    finally:
        save_manifest(new, {"kind": "recovery", "source": old.name})
    return {"run_id": new.name, "status": result["status"]}


def status(dataset=None):
    rows, runs, invalid = collect(dataset=dataset)
    pilots, rr, _ = collect(include_pilots=True)
    missing = []
    keys = {tuple(r[k] for k in ("round", "target", "tool", "family", "method", "direction")) for r in runs}
    cfg = config()
    if dataset:
        cfg = {**cfg, "targets": load_dataset(dataset)["targets"]}
    jobs = plan_jobs(cfg)
    expected_keys = {tuple(job[k] for k in ("round", "target", "tool", "family", "method", "direction")) for job in jobs}
    for job in jobs:
        if tuple(job[k] for k in ("round", "target", "tool", "family", "method", "direction")) not in keys:
            missing.append(job)
    publications = []
    current_ripe_ids = {r["measurement_id"] for r in runs if r.get("measurement_id")}
    for p in (ROOT / "grafos").glob("publication_*/publication.json"):
        publication = json.loads(p.read_text())
        ids = set(publication.get("measurement_ids", []))
        if len(ids) == 2 and ids <= current_ripe_ids:
            publications.append(publication)
    return {"expected": 153, "completed": len(keys), "valid_runs": len(runs), "pilots": sum(r.get("pilot", False) for r in rr), "missing": missing, "invalid": invalid,
            "public_graphs": publications, "scientific_results_complete": not invalid and keys == expected_keys and len(runs) == len(expected_keys) and len({p["target"] for p in publications}) == len(cfg["targets"])}


def build_parser():
    parser = argparse.ArgumentParser(description="Tarea Path Discovery — mediciones, originales y análisis reproducible")
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name in ("plan", "preflight", "probe-init", "sources", "report", "verify"):
        sub.add_parser(name)
    for name in ("status", "patterns"):
        sub.add_parser(name).add_argument("--dataset")
    p = sub.add_parser("pilot")
    p.add_argument("--target", default="200.14.48.134")
    p.add_argument("--tool", choices=("scamper", "ripe"), default="scamper")
    p.add_argument("--family", choices=("trace", "tracelb"), default="trace")
    p.add_argument("--method", default="udp")
    p.add_argument("--direction", choices=("ida", "vuelta"), default="ida")
    p = sub.add_parser("pilot-accept")
    p.add_argument("--target", default="200.14.48.134")
    p.add_argument("--wireshark-reviewed", action="store_true")
    p.add_argument("--packet-review", help="Directorio sellado generado por pilot-review (TShark)")
    p = sub.add_parser("pilot-review")
    p.add_argument("--target", default="200.14.48.134")
    p = sub.add_parser("campaign")
    p.add_argument("--round", type=int, choices=(1, 2, 3), required=True)
    for name in ("ripe-fetch", "packet-export"):
        sub.add_parser(name).add_argument("run")
    p = sub.add_parser("analyze")
    p.add_argument("--online-asn", action="store_true")
    p.add_argument("--session-ip", help="Analizar explícitamente una sesión IPv4 histórica")
    p.add_argument("--dataset", help="Selección explícita de originales aceptados dentro de config")
    p.add_argument("--include-pilots", action="store_true")
    p.add_argument("--diagnostic-pilots", action="store_true")
    sub.add_parser("publish").add_argument("cx2")
    p = sub.add_parser("publish-receipt")
    p.add_argument("cx2")
    p.add_argument("uuid")
    sub.add_parser("bundle").add_argument("analysis")
    return parser


def execute(args):
    cfg = config()
    if args.cmd == "sources":
        return clone_sources()
    if args.cmd == "plan":
        jobs = plan_jobs(cfg)
        json_write(ROOT / "resultados/plan_153.json", jobs)
        return {"total": len(jobs), "ripe_oneoff_estimated_credits": 3240, "jobs_file": "resultados/plan_153.json"}
    if args.cmd == "preflight":
        folder, result = preflight()
        return {"folder": str(folder), **result}
    if args.cmd == "probe-init":
        return init_probe()
    if args.cmd == "pilot":
        t = next((t for t in cfg["targets"] if t["ip"] == args.target), None)
        if not t:
            raise ValueError("Usar exclusivamente un destino de config/campana.json")
        with campaign_lock():
            if args.tool == "scamper":
                folder = measure_scamper(cfg, t, args.family, args.method.lower(), 0, pilot=True)
            else:
                folder = measure_ripe(cfg, t, args.method.upper(), args.direction, 0, pilot=True)
        return {"run_id": folder.name}
    if args.cmd == "pilot-accept":
        return accept_pilot(args)
    if args.cmd == "pilot-review":
        return {"folder": str(review_udp_pilots(selected_udp_pilots(args.target)))}
    if args.cmd == "campaign":
        with campaign_lock():
            return run_campaign(args.round)
    if args.cmd == "ripe-fetch":
        with campaign_lock():
            return recover_ripe(args.run)
    if args.cmd == "analyze":
        folder, result = analyze(online=args.online_asn, include_pilots=args.include_pilots, diagnostic_pilots=args.diagnostic_pilots, session_ip=args.session_ip, dataset=args.dataset)
        return {"folder": str(folder), **result}
    if args.cmd == "packet-export":
        return {"folder": str(export_packets(resolve_run(args.run)))}
    if args.cmd == "patterns":
        return {"folder": str(patterns(dataset=args.dataset))}
    if args.cmd == "publish":
        return publish(args.cx2)
    if args.cmd == "publish-receipt":
        return record_browser_publication(args.cx2, args.uuid)
    if args.cmd == "bundle":
        return {"folder": str(bundle(args.analysis))}
    if args.cmd == "verify":
        folders = [p.parent for p in (ROOT / "datos/originales").rglob("manifest.json")]
        for folder in folders:
            verify_manifest(folder)
        return {"verified_manifests": len(folders)}
    if args.cmd == "report":
        from .report import generate_report
        return generate_report(status())
    return status(dataset=getattr(args, "dataset", None))


def main():
    try:
        load_credentials()
        args = build_parser().parse_args()
        print(json.dumps(execute(args), ensure_ascii=False, indent=2, default=str))
    except (ValueError, RuntimeError, OSError, subprocess.SubprocessError) as e:
        # Los errores de subprocess pueden contener comandos privados: mostrar solo
        # tipo para errores externos; nunca encabezados/API keys.
        message = str(e) if isinstance(e, (ValueError, RuntimeError)) else type(e).__name__ + ": revisar los logs locales"
        print("ERROR: " + message, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
