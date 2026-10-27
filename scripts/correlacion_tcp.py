#!/usr/bin/env python3
"""Distinguir respuestas TCP/ICMP capturadas y respuestas aceptadas por Scamper."""
import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from path_discovery.common import (
    ROOT,
    json_write,
    verify_manifest,
    sha256,
    utc,
)


def main():
    from path_discovery.analysis import collect
    accepted = {r["run_id"]: r for r in collect()[1]}
    index = json.loads((ROOT / "resultados/exportaciones_paquetes.json").read_text())
    reviews = []
    for rid, export_rel in index.items():
        if rid not in accepted:
            continue
        original = ROOT / "datos/originales" / rid
        meta = json.loads((original / "metadata.json").read_text())
        if (
            meta.get("tool") != "scamper"
            or not meta.get("method", "").startswith("tcp")
            or meta.get("status") != "completed"
        ):
            continue
        verify_manifest(original)
        export = ROOT / export_rel
        verify_manifest(export)
        frames = json.loads((export / "packets_full.json").read_text())
        requests = {}
        quotes = []
        for p in frames:
            l = p["_source"]["layers"]
            ip = l.get("ip", {})
            tcp = l.get("tcp", {})
            icmp = l.get("icmp", {})
            frame = l.get("frame", {})
            if tcp and not icmp and ip.get("ip.dst") == meta["destination"]:
                flags = int(tcp.get("tcp.flags", "0"), 0)
                if flags not in (2, 16):
                    continue
                key = (
                    ip.get("ip.src"),
                    ip.get("ip.dst"),
                    ip.get("ip.id"),
                    tcp.get("tcp.srcport"),
                    tcp.get("tcp.dstport"),
                )
                requests.setdefault(key, []).append(
                    {
                        "frame": frame.get("frame.number"),
                        "time": float(frame["frame.time_epoch"]),
                        "ttl": ip.get("ip.ttl"),
                        "tcp_flags": tcp.get("tcp.flags"),
                    }
                )
            qi = icmp.get("ip", {})
            qt = icmp.get("tcp", {})
            if qi.get("ip.dst") == meta["destination"] and qt:
                key = (
                    qi.get("ip.src"),
                    qi.get("ip.dst"),
                    qi.get("ip.id"),
                    qt.get("tcp.srcport"),
                    qt.get("tcp.dstport"),
                )
                quotes.append(
                    (
                        key,
                        {
                            "frame": frame.get("frame.number"),
                            "time": float(frame["frame.time_epoch"]),
                            "from": ip.get("ip.src"),
                            "icmp_type": icmp.get("icmp.type"),
                            "icmp_code": icmp.get("icmp.code"),
                        },
                    )
                )
        matched = []
        unmatched = []
        for key, q in quotes:
            candidates = [r for r in requests.get(key, []) if r["time"] <= q["time"]]
            if candidates:
                r = max(candidates, key=lambda r: r["time"])
                matched.append(
                    {
                        **q,
                        "request": r,
                        "correlation": [
                            "ip.src",
                            "ip.dst",
                            "ip.id",
                            "tcp.srcport",
                            "tcp.dstport",
                            "temporal_order",
                        ],
                        "delta_ms": round((q["time"] - r["time"]) * 1000, 6),
                    }
                )
            else:
                unmatched.append(q)
        warts_ips = set(accepted[rid]["ips"])
        captured_ips = sorted({q["from"] for q in matched})
        reviews.append(
            {
                "run_id": rid,
                "method": meta["method"],
                "round": meta["round"],
                "target": meta["target"],
                "source_manifest_sha256": sha256(original / "manifest.json"),
                "export": export_rel,
                "matched_icmp_quotes": matched,
                "unmatched_tcp_quotes": unmatched,
                "captured_reply_ips": captured_ips,
                "warts_reply_ips": sorted(warts_ips),
                "captured_but_not_in_warts": sorted(set(captured_ips) - warts_ips),
            }
        )
    out = {
        "reviewed_at": utc(),
        "summary": {
            "reviewed_scamper_tcp_runs": len(reviews),
            "runs_with_matching_icmp_quotes": sum(
                bool(r["matched_icmp_quotes"]) for r in reviews
            ),
            "runs_with_pcap_warts_discrepancy": sum(
                bool(r["captured_but_not_in_warts"]) for r in reviews
            ),
            "interpretation": "Correlación estricta por direcciones, IPID, puertos y orden temporal. Presencia en PCAP no implica aceptación por Scamper. Causa de la diferencia no establecida; no demuestra bloqueo TCP de los routers.",
        },
        "runs": reviews,
    }
    json_write(ROOT / "resultados/correlacion_tcp_captura.json", out)
    print(json.dumps(out["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
