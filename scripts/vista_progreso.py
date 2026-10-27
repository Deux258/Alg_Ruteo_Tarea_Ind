#!/usr/bin/env python3
"""Vista local de un estado verificado; no es evidencia de una plataforma externa."""
import html, json, sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from path_discovery.common import ROOT, utc, config
from path_discovery.analysis import collect


def main():
    rows, runs, invalid = collect()
    cfg = config()
    statefile = ROOT / ".state/campaign.json"
    state = json.loads(statefile.read_text()) if statefile.exists() else {"rounds": {}}
    counts = Counter(r["round"] for r in runs)
    out = ROOT / "resultados/fichas_paquetes"
    out.mkdir(exist_ok=True)
    body = (
        "<h1>Path Discovery · estado verificado de campaña</h1><p>"
        + html.escape(utc())
        + " UTC · conexión domiciliaria WOM · sonda RIPE 1018487</p>"
    )
    body += "<p>Sesión: " + html.escape(cfg.get("session_id", "histórica")) + " · IPv4: " + html.escape(cfg.get("session_public_ipv4", "no fijada")) + "</p>"
    body += f'<div class="count">{len(runs)} / 153 <span>ejecuciones principales con originales y manifiesto</span></div>'
    body += '<p class="note">Vista local generada desde WARTS/JSON y metadatos; no es una captura del panel RIPE. Pilotos, diagnósticos y ejecuciones descartadas no cuentan. La sesión anterior se conserva aparte; sus 60 resultados no se suman a esta campaña.</p>'
    body += "<table><tr><th>Ronda</th><th>trace / 18</th><th>tracelb / 15</th><th>RIPE ida / 9</th><th>RIPE vuelta / 9</th><th>Total / 51</th><th>Cierre UTC</th></tr>"
    for n in (1, 2, 3):
        rr = [r for r in runs if r["round"] == n]
        c = [
            sum(r["family"] == "trace" for r in rr),
            sum(r["family"] == "tracelb" for r in rr),
            sum(r["tool"] == "ripe" and r["direction"] == "ida" for r in rr),
            sum(r["tool"] == "ripe" and r["direction"] == "vuelta" for r in rr),
        ]
        finished = state["rounds"].get(str(n), {}).get("finished_at", "Pendiente")
        body += (
            "<tr>"
            + "".join(
                "<td>" + html.escape(str(v)) + "</td>"
                for v in [n, *c, len(rr), finished]
            )
            + "</tr>"
        )
    body += "</table><h2>Destinos activos y evidencia</h2><table><tr><th>Destino</th><th>IPv4</th><th>Sonda RIPE</th><th>Ejecuciones / 51</th></tr>"
    for t in cfg["targets"]:
        body += (
            "<tr>"
            + "".join(
                "<td>" + html.escape(str(v)) + "</td>"
                for v in [
                    t["label"],
                    t["ip"],
                    t["probe_id"],
                    sum(r["target"] == t["ip"] for r in runs),
                ]
            )
            + "</tr>"
        )
    body += "</table><p>Configuración original y cambios autorizados: docs/CAMBIOS_DESTINOS.md. Decisiones de calidad: config/exclusiones_calidad.json. Evidencia visual: capturas/indice.json.</p>"
    css = "body{font:16px Arial,sans-serif;color:#173d5c;background:#f6f8fb;margin:32px;max-width:1240px}h1{font-size:28px}h2{font-size:20px}.count{font-size:42px;font-weight:bold;padding:18px;background:#dceef2}.count span{font-size:18px;font-weight:normal}.note{padding:12px;background:#fff3d7;border-left:4px solid #cc641d}table{border-collapse:collapse;width:100%;background:white;margin:18px 0}td,th{padding:12px;border:1px solid #ccd7e0;text-align:left}th{background:#173d5c;color:white}p{line-height:1.5;font-size:14px}"
    page = (
        '<!doctype html><html lang="es"><meta charset="utf-8"><title>Path Discovery · progreso</title><style>'
        + css
        + "</style>"
        + body
        + "</html>"
    )
    (out / "progreso.html").write_text(page)
    closed = [
        n for n in (1, 2, 3) if state["rounds"].get(str(n), {}).get("finished_at")
    ]
    if closed:
        n = max(closed)
        snapshot = out / f"progreso_ronda_{n}.html"
        if not snapshot.exists() and len(runs) == n * 51:
            snapshot.write_text(page)
    print(
        json.dumps(
            {
                "completed": len(runs),
                "invalid": invalid,
                "page": str(out / "progreso.html"),
            }
        )
    )


if __name__ == "__main__":
    main()
