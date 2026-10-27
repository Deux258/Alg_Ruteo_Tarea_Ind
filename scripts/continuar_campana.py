#!/usr/bin/env python3
"""Completar rondas autorizadas sin repetir resultados ni POST inciertos."""
import fcntl, json, os, signal, subprocess, sys, time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PDF_PYTHON = "/home/diego/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"
child = None
SESSION = json.loads((ROOT / "config/local.json").read_text()).get("session_id", "legacy")


def log_path(name):
    return ROOT / "resultados" / (SESSION + "_" + name)


def stop(signum, frame):
    if child and child.poll() is None:
        child.send_signal(signal.SIGINT)
    raise SystemExit(128 + signum)


signal.signal(signal.SIGTERM, stop)
signal.signal(signal.SIGINT, stop)


def read_state():
    p = ROOT / ".state/campaign.json"
    return json.loads(p.read_text()) if p.exists() else {"rounds": {}}


def save_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def run_command(args, logname):
    global child
    with log_path(logname).open("a") as log:
        child = subprocess.Popen(args, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
        result = child.wait()
    child = None
    if result:
        raise RuntimeError(
            f"Comando detenido con código {result}; revisar resultados/{logname}. No se reintentó."
        )


def last_json(path):
    text = path.read_text()
    decoder = json.JSONDecoder()
    found = []
    for line_start in [0] + [i + 1 for i, c in enumerate(text) if c == "\n"]:
        if text[line_start : line_start + 1] == "{":
            try:
                found.append(decoder.raw_decode(text[line_start:])[0])
            except json.JSONDecodeError:
                pass
    if not found:
        raise RuntimeError("Log sin resultado JSON: " + str(path))
    return found[-1]


def render_report(analysis, n):
    run_command(
        [PDF_PYTHON, "scripts/informe_academico.py", analysis], f"informe_ronda_{n}.log"
    )


def process_round(n, checkpoints):
    run_command(
        [sys.executable, "scripts/evidencia_paquetes.py"],
        f"procesamiento_ronda_{n}.log",
    )
    run_command(["./main", "analyze", "--online-asn"], f"analisis_ronda_{n}.log")
    result = last_json(log_path(f"analisis_ronda_{n}.log"))
    run_command(
        [sys.executable, "scripts/correlacion_tcp.py"], f"correlacion_ronda_{n}.log"
    )
    run_command(
        [sys.executable, "scripts/verificar_checksums.py"], f"checksums_ronda_{n}.log"
    )
    run_command(["./main", "patterns"], f"patrones_ronda_{n}.log")
    run_command(
        [sys.executable, "scripts/vista_progreso.py"], f"progreso_ronda_{n}.log"
    )
    render_report(result["folder"], n)
    checkpoints[str(n)] = {
        "analysis": result["folder"],
        "processed_at": datetime.now(timezone.utc).isoformat(),
    }
    save_json(ROOT / ".state/postprocessing.json", checkpoints)
    save_json(ROOT / "resultados/ultimo_analisis_campana.json", result)


def main():
    with (ROOT / ".state/coordinator.lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError("Ya hay un coordinador activo.")
        (ROOT / ".state/continuacion.pid").write_text(str(os.getpid()) + "\n")
        cp = ROOT / ".state/postprocessing.json"
        checkpoints = json.loads(cp.read_text()) if cp.exists() else {}
        for n in (1, 2, 3):
            rd = read_state()["rounds"].get(str(n), {})
            if any(
                j["status"] in ("running", "needs_review")
                for j in rd.get("jobs", {}).values()
            ):
                raise RuntimeError(
                    f"Ronda {n} tiene un trabajo activo o incierto; revisar antes de reenviar."
                )
            if not rd.get("finished_at"):
                if n > 1:
                    previous = read_state()["rounds"][str(n - 1)]
                    deadline = (
                        datetime.fromisoformat(previous["finished_at"]).timestamp()
                        + 1800
                    )
                    print(
                        f"Esperando separación de ronda {n}: hasta {datetime.fromtimestamp(deadline,timezone.utc).isoformat()} UTC.",
                        flush=True,
                    )
                    while time.time() < deadline:
                        time.sleep(min(30, max(0.1, deadline - time.time())))
                print(f"Iniciando ronda {n}.", flush=True)
                run_command(
                    ["./main", "campaign", "--round", str(n)], f"campana_ronda_{n}.log"
                )
            if str(n) not in checkpoints:
                print(
                    f"Ronda {n} terminada. Exportando paquetes, análisis e informe de avance.",
                    flush=True,
                )
                process_round(n, checkpoints)
            if n == 1:
                print("Comprobando control adicional de recepción TCP.", flush=True)
                run_command(
                    [sys.executable, "scripts/diagnostico_tcp.py"],
                    "diagnostico_recepcion_tcp.log",
                )
        run_command(
            [sys.executable, "scripts/validar_respuesta_selectiva.py"],
            "respuesta_selectiva_validacion.log",
        )
        run_command(["./main", "verify"], "verificacion_campana.log")
        render_report(checkpoints["3"]["analysis"], 3)
        print(
            "Tres rondas procesadas. Pendientes: revisión visual final del PDF, publicación de tres grafos en NDEx, capturas y paquete de entrega.",
            flush=True,
        )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(str(e), file=sys.stderr, flush=True)
        sys.exit(1)
