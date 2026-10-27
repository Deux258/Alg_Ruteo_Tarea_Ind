#!/usr/bin/env python3
"""Formatos de payload observados y restricciones contrastables entre rondas."""
import csv, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from path_discovery.common import ROOT, json_write, utc, config
from path_discovery.packets import pattern_groups


def payload(row):
    value = next(
        (row.get(k) for k in ("udp.payload", "tcp.payload", "data.data") if row.get(k)),
        "",
    )
    return bytes.fromhex(value.replace(":", ""))


def number(value):
    return int(value, 16) if value.startswith("0x") else int(value)


def invariant(rows):
    if not rows or any(len(payload(r)) < 2 for r in rows):
        return None
    if len({payload(r)[2:] for r in rows}) != 1:
        return None
    if all(
        r.get("icmp.checksum") and r.get("icmp.ident") and r.get("icmp.seq")
        for r in rows
    ):
        fields = ("icmp.checksum", "icmp.ident", "icmp.seq")
    elif all(
        r.get("udp.checksum") and r.get("udp.srcport") and r.get("udp.dstport")
        for r in rows
    ):
        fields = ("udp.checksum", "udp.srcport", "udp.dstport")
    else:
        return None
    values = [
        (int.from_bytes(payload(r)[:2], "big") + sum(number(r[f]) for f in fields))
        % 65535
        for r in rows
    ]
    return {
        "fields": ["payload_word0_BE", *fields],
        "modulus": 65535,
        "stable_within_run": len(set(values)) == 1,
        "observed_bases": sorted(set(values)),
        "samples": len(values),
        "base_learned_from_first_packet": values[0],
        "checked_later_packets": len(values) - 1,
        "failed_later_packets": sum(v != values[0] for v in values[1:]),
        "base_is_execution_specific": True,
    }


def structure(rows):
    data = [payload(r) for r in rows]
    lengths = sorted({len(p) for p in data})
    segments = []
    variable = []
    if data and len(lengths) == 1 and lengths[0]:
        values = [set(p[i] for p in data) for i in range(lengths[0])]
        variable = [i for i, v in enumerate(values) if len(v) > 1]
        current = ""
        start = 0
        for i, v in enumerate(values + [set()]):
            if len(v) == 1 and 32 <= next(iter(v)) <= 126:
                if not current:
                    start = i
                current += chr(next(iter(v)))
            else:
                if len(current) >= 4:
                    segments.append({"offset": start, "ascii": current})
                current = ""
    return {
        "samples": len(data),
        "lengths_bytes": lengths,
        "first_hex": data[0].hex() if data else None,
        "within_run_variable_offsets": variable,
        "constant_ascii_segments": segments,
        "word_constraint": invariant(rows),
        "zero_payload": bool(data) and lengths == [0],
    }


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset")
    args = parser.parse_args()
    cases = []
    for key, rounds in sorted(pattern_groups(dataset=args.dataset).items()):
        if 1 not in rounds:
            continue
        training = structure(rounds[1][1])
        checks = {}
        for n, (_, rows) in rounds.items():
            if n == 1:
                continue
            actual = structure(rows)
            raw = [payload(r) for r in rows]
            segments_ok = all(
                all(
                    p[s["offset"] : s["offset"] + len(s["ascii"])]
                    == s["ascii"].encode()
                    for p in raw
                )
                for s in training["constant_ascii_segments"]
            )
            constraint = training["word_constraint"]
            candidate = actual["word_constraint"]
            checks[str(n)] = {
                "payload_lengths_match": actual["lengths_bytes"]
                == training["lengths_bytes"],
                "constant_ascii_segments_match": segments_ok,
                "samples": len(raw),
                "word_constraint_stable_in_new_execution": (
                    candidate["stable_within_run"] if constraint and candidate else None
                ),
                "new_execution_base": (
                    candidate["base_learned_from_first_packet"] if candidate else None
                ),
                "checked_later_packets": (
                    candidate["checked_later_packets"] if candidate else 0
                ),
                "failed_later_packets": (
                    candidate["failed_later_packets"] if candidate else None
                ),
            }
        cases.append(
            {
                "tool": key[0],
                "family": key[1],
                "method": key[2],
                "target": key[3],
                "training": training,
                "validation": checks,
                "scope": "Restricciones observadas, con offsets desde cero. El prefijo variable puede ser compatible con compensación de checksum; no se presume su valor exacto ni la intención del emisor. Las bases se contrastan dentro de cada ejecución, no se declaran universales.",
            }
        )
    json_write(
        ROOT / "resultados/estructura_payload.json",
        {"session_public_ipv4": config().get("session_public_ipv4"), "session_id": config().get("session_id"), "generated_at": utc(), "cases": cases},
    )
    print(
        json.dumps(
            {
                "payload_method_target_cases": len(cases),
                "contrasted_rounds": sorted(
                    {n for c in cases for n in c["validation"]}
                ),
            }
        )
    )


if __name__ == "__main__":
    main()
