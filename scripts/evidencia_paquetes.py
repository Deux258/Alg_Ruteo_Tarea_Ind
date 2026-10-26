#!/usr/bin/env python3
"""Exportar PCAP completos y generar fichas HTML verificables para capturas."""
import csv
import html
import io
import json
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from path_discovery.common import ROOT, sha256, json_write, verify_manifest
from path_discovery.packets import export_packets, PACKET_FIELDS


def build_page(original, export, out):
    m = json.loads((original / "metadata.json").read_text())
    packets = list(csv.DictReader((export / "emitted.tsv").open(), delimiter="\t"))
    full = json.loads((export / "packets_full.json").read_text())
    fields = [
        "frame.number",
        "ip.ttl",
        "ip.id",
        "ip.len",
        "ip.proto",
        "udp.srcport",
        "udp.dstport",
        "udp.checksum",
        "tcp.srcport",
        "tcp.dstport",
        "tcp.flags",
        "tcp.seq_raw",
        "tcp.ack_raw",
        "icmp.type",
        "icmp.code",
        "icmp.ident",
        "icmp.seq",
        "icmp.checksum",
    ]
    fields = [f for f in fields if any(p.get(f) for p in packets)]
    selected = packets[:4] + ([packets[-1]] if len(packets) > 4 else [])
    esc = lambda x: html.escape(str(x))
    heading = f"{m['tool']} {m['family']} / {m['method']}"
    body = f'<h1>{esc(heading)}</h1><p class="sub">Ronda {m["round"]} · {m["direction"]} · destino {m["target"]} · {esc(m["started_at"])}</p>'
    body += '<div class="note">Vista local de datos procesados con TShark (Wireshark). No es una captura de la interfaz gráfica de Wireshark.</div>'
    body += f'<p><b>Original:</b> {original.name}<br><b>PCAPNG SHA-256:</b> <code>{sha256(original/"capture.pcapng")}</code><br><b>ID RIPE:</b> {m.get("measurement_id") or "No corresponde"} · <b>Solicitudes observadas:</b> {len(packets)}</p>'
    body += (
        "<table><thead><tr><th>Campo</th>"
        + "".join(f'<th>Paquete {esc(p.get("frame.number"))}</th>' for p in selected)
        + "</tr></thead><tbody>"
    )
    for f in fields:
        body += (
            "<tr><td>"
            + esc(f)
            + "</td>"
            + "".join("<td>" + esc(p.get(f, "")) + "</td>" for p in selected)
            + "</tr>"
        )
    body += "</tbody></table><h2>Payload hexadecimal de las solicitudes</h2>"
    for p in selected[:2] + selected[-1:]:
        payload = next(
            (p.get(f) for f in ["udp.payload", "tcp.payload", "data.data"] if p.get(f)),
            None,
        )
        if payload is None:
            frame = next(
                (
                    v["_source"]["layers"]
                    for v in full
                    if v["_source"]["layers"].get("frame", {}).get("frame.number")
                    == p.get("frame.number")
                ),
                {},
            )
            raw = frame.get("data_raw")
            payload = (
                raw[0]
                if raw
                else "Sin payload de aplicación decodificado; consultar bytes completos del frame."
            )
        body += f'<p class="payload"><b>Frame {esc(p.get("frame.number"))}:</b> <code>{esc(payload)}</code></p>'
    quoted = []
    for v in full:
        layers = v["_source"]["layers"]
        icmp = layers.get("icmp", {})
        if icmp.get("ip", {}).get("ip.dst") == m["destination"]:
            quoted.append(
                (
                    layers.get("frame", {}).get("frame.number"),
                    layers.get("ip", {}).get("ip.src"),
                    icmp.get("icmp.type"),
                    icmp.get("icmp.code"),
                )
            )
    body += (
        "<p><b>Respuestas ICMP que citan el destino:</b> "
        + str(len(quoted))
        + " · Ejemplos (frame, origen, tipo, código): "
        + esc(quoted[:3])
        + "</p>"
    )
    body += '<p class="foot">Se muestran las primeras cuatro solicitudes y la última. Los TSV y JSON completos conservan todos los paquetes, encabezados citados y bytes. Esta muestra no acredita estabilidad entre rondas.</p>'
    css = "body{font:15px Arial,sans-serif;color:#182b42;background:#f6f8fb;margin:28px 36px;max-width:1240px}h1{font-size:26px;margin:0 0 8px}h2{font-size:18px;margin:16px 0 8px}.sub{color:#43556b}.note{padding:10px;border-left:4px solid #137c82;background:#e4f3f3}table{border-collapse:collapse;width:100%;font:13px monospace;background:white}th,td{padding:5px 9px;border:1px solid #d5dfe9;text-align:left;overflow-wrap:anywhere}th{background:#173d5c;color:white}p{line-height:1.5}.payload{font-size:12px;margin:6px 0;overflow-wrap:anywhere}.foot{font-size:12px;color:#43556b}code{font-size:12px;overflow-wrap:anywhere}"
    out.write_text(
        '<!doctype html><html lang="es"><meta charset="utf-8"><title>'
        + esc(heading)
        + "</title><style>"
        + css
        + "</style>"
        + body
        + "</html>"
    )


def main():
    index_path = ROOT / "resultados/exportaciones_paquetes.json"
    index = json.loads(index_path.read_text()) if index_path.exists() else {}
    state = json.loads((ROOT / ".state/campaign.json").read_text())
    runs = [
        j["run_id"]
        for rd in state["rounds"].values()
        for j in rd.get("jobs", {}).values()
        if j["status"] == "completed"
    ]
    examples = {}
    for rid in runs:
        original = ROOT / "datos/originales" / rid
        verify_manifest(original)
        outdated = (
            rid in index
            and json.loads((ROOT / index[rid] / "metadata.json").read_text()).get(
                "format_version", 1
            )
            < 2
        )
        if rid not in index or outdated:
            exported = export_packets(original)
            index[rid] = str(exported.relative_to(ROOT))
            json_write(index_path, index)
        m = json.loads((original / "metadata.json").read_text())
        if m["direction"] == "ida":
            examples.setdefault((m["tool"], m["family"], m["method"]), rid)
    output = ROOT / "resultados/fichas_paquetes"
    output.mkdir(exist_ok=True)
    for key, rid in examples.items():
        build_page(
            ROOT / "datos/originales" / rid,
            ROOT / index[rid],
            output / ("_".join(key) + ".html"),
        )
    json_write(
        output / "index.json",
        {
            "examples": {"_".join(k): v for k, v in examples.items()},
            "exported_runs": len(index),
            "view_type": "Datos locales procesados con TShark, no interfaz Wireshark",
        },
    )
    import subprocess

    subprocess.run(
        [sys.executable, str(ROOT / "scripts/estructura_payload.py")], check=True
    )
    print(
        json.dumps(
            {
                "exported_runs": len(index),
                "method_pages": len(examples),
                "folder": str(output),
            }
        )
    )


if __name__ == "__main__":
    main()
