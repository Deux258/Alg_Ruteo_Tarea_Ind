#!/usr/bin/env python3
"""Comprobar checksum IPv4 y TCP de las solicitudes capturadas, sin emitir tráfico."""
from pathlib import Path
import json, struct

ROOT = Path(__file__).resolve().parents[1]


def folded(data):
    if len(data) % 2:
        data += b"\0"
    value = sum(struct.unpack("!" + str(len(data) // 2) + "H", data))
    while value >> 16:
        value = (value & 65535) + (value >> 16)
    return value


index = json.loads((ROOT / "resultados/exportaciones_paquetes.json").read_text())
records = []
for rid, export in index.items():
    original = ROOT / "datos/originales" / rid
    m = json.loads((original / "metadata.json").read_text())
    if m["direction"] != "ida":
        continue
    packets = json.loads((ROOT / export / "packets_full.json").read_text())
    checked = []
    for p in packets:
        l = p["_source"]["layers"]
        ip = l.get("ip", {})
        if "tcp" not in l or ip.get("ip.dst") != m["destination"]:
            continue
        raw = bytes.fromhex(l["frame_raw"][0])
        start = l["ip_raw"][1]
        header = int(ip["ip.hdr_len"])
        size = int(ip["ip.len"])
        segment = raw[start : start + size]
        if len(segment) != size:
            continue
        pseudo = segment[12:20] + bytes([0, 6]) + struct.pack("!H", size - header)
        checked.append(
            {
                "frame": l["frame"]["frame.number"],
                "ip_valid": folded(segment[:header]) == 65535,
                "tcp_valid": folded(pseudo + segment[header:]) == 65535,
            }
        )
    if checked:
        records.append(
            {
                "run_id": rid,
                "method": m["method"],
                "round": m["round"],
                "checked": len(checked),
                "ipv4_valid": sum(p["ip_valid"] for p in checked),
                "tcp_valid": sum(p["tcp_valid"] for p in checked),
                "frames": checked,
            }
        )
(ROOT / "resultados/checksums_tcp.json").write_text(
    json.dumps(
        {
            "scope": "Solicitudes exteriores completas de las exportaciones actuales; la ausencia de respuestas no se atribuye a checksum sin evidencia.",
            "runs": records,
        },
        indent=2,
    )
    + "\n"
)
print(
    json.dumps(
        {
            "runs": len(records),
            "tcp_requests_checked": sum(r["checked"] for r in records),
            "invalid_tcp": sum(r["checked"] - r["tcp_valid"] for r in records),
        }
    )
)
