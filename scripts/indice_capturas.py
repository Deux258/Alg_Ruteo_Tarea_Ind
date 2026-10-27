#!/usr/bin/env python3
"""Actualizar el índice de las imágenes conservadas para el informe."""
from pathlib import Path
import hashlib
import json
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
folder = ROOT / "capturas"
examples_file = ROOT / "resultados/fichas_paquetes/index.json"
examples = (
    json.loads(examples_file.read_text())["examples"] if examples_file.exists() else {}
)
old_index = folder / "indice.json"
previous = {i["file"]: i for i in json.loads(old_index.read_text())} if old_index.exists() else {}
items = []
for p in sorted(
    p for p in folder.iterdir() if p.suffix.lower() in (".png", ".jpg", ".jpeg")
):
    key = p.stem.removesuffix("_r1")
    if p.name.startswith("campana_"):
        source = (
            "Vista local de progreso verificado; no corresponde al panel RIPE ni NDEx"
        )
    elif p.name.startswith("wireshark_"):
        source = "Wireshark gráfico real en contenedor local, manejado por navegador"
    elif key in examples:
        source = "Vista local de datos procesados con TShark; no es interfaz gráfica de Wireshark"
    else:
        source = (
            "Captura del navegador RIPE Atlas o NDEx; la leyenda determina su contexto"
        )
    item = {
        "file": str(p.relative_to(ROOT)),
        "caption": p.stem.replace("_", " "),
        "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
        "source": source,
        "actual_encoding": (
            "JPEG"
            if p.read_bytes().startswith(b"\xff\xd8")
            else "PNG" if p.read_bytes().startswith(b"\x89PNG") else "unknown"
        ),
        "file_mtime_utc": datetime.fromtimestamp(
            p.stat().st_mtime, timezone.utc
        ).isoformat(),
    }
    method_key = key.removeprefix("wireshark_")
    if str(p.relative_to(ROOT)) not in previous and method_key in examples:
        item["source_run"] = examples[method_key]
        item["source_pcap"] = (
            "datos/originales/" + examples[method_key] + "/capture.pcapng"
        )
    if str(p.relative_to(ROOT)) not in previous and p.name == "wireshark_cita_icmp_tcp_scamper_r1.png":
        item["source_run"] = examples.get("scamper_trace_tcp")
        item["source_pcap"] = (
            "datos/originales/" + item["source_run"] + "/capture.pcapng"
        )
    if p.name.startswith("ripe_") and p.stem.split("_")[-1].isdigit():
        item["measurement_url"] = (
            "https://atlas.ripe.net/measurements/" + p.stem.split("_")[-1] + "/results"
        )
    old = previous.get(item["file"], {})
    for field in ("source_run", "source_pcap", "session_public_ipv4", "historical_session", "historical_setup", "caption_override", "superseded_progress_snapshot"):
        if field in old:
            item[field] = old[field]
    if item.get("source_run"):
        m = ROOT / "datos/originales" / item["source_run"] / "metadata.json"
        if m.exists():
            item["session_public_ipv4"] = json.loads(m.read_text()).get("public_ipv4")
    gui_path = ROOT / "resultados/revision_wireshark_gui.json"
    gui_entries = json.loads(gui_path.read_text()).get("reviewed_runs", []) if gui_path.exists() else []
    gui_entry = next((r for r in gui_entries if r.get("screenshot") == item["file"]), None)
    if gui_entry:
        item.update(source_run=gui_entry["run_id"], source_pcap=gui_entry["source"], session_public_ipv4=gui_entry.get("session_public_ipv4"), historical_session=False)
    if item.get("caption_override"):
        item["caption"] = item["caption_override"]
    elif gui_entry:
        item["caption"] = "Wireshark: " + gui_entry["method"].replace("_", " / ") + " | sesión " + str(gui_entry.get("session_public_ipv4"))
    items.append(item)
(folder / "indice.json").write_text(
    json.dumps(items, ensure_ascii=False, indent=2) + "\n"
)
lines = [
    "# Índice de capturas",
    "Cada imagen complementa WARTS/JSON/PCAP; su alcance no sustituye la evidencia original. Las vistas procesadas y la GUI real se identifican separadamente.",
]
for item in items:
    lines += [
        "## " + item["caption"],
        item["source"],
        (
            "Run: "
            + item.get("source_run", "Registro o evidencia indicada en la imagen")
        ),
        item["file"],
        "SHA-256: " + item["sha256"],
    ]
(folder / "indice.md").write_text("\n\n".join(lines) + "\n")
print(json.dumps({"images": len(items), "index": str(folder / "indice.json")}))
