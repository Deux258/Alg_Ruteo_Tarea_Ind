#!/usr/bin/env python3
"""Control adicional de recepción TCP; no modifica la campaña principal."""
import json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from path_discovery.common import (
    ROOT,
    config,
    records,
    json_write,
    campaign_lock,
    utc,
    sha256,
    save_manifest,
    identifier,
)
from path_discovery.acquire import measure_scamper
from path_discovery.packets import export_packets


def main():
    output = ROOT / "resultados/diagnostico_recepcion_tcp.json"
    if output.exists():
        print("Diagnóstico ya realizado; se conserva sin duplicarlo.")
        return
    if any(json.loads(p.read_text()).get("session_id") == config().get("session_id") for p in (ROOT / "datos/originales").glob("diagnostico_recepcion_tcp_*/intent.json")):
        raise RuntimeError(
            "Existe un diagnóstico incompleto; revisar sus originales antes de repetirlo."
        )
    cfg = config()
    target = cfg["targets"][0]
    results = []
    folder = ROOT / "datos/originales" / ("diagnostico_recepcion_tcp_" + identifier())
    folder.mkdir()
    json_write(
        folder / "intent.json",
        {
            "session_id": cfg.get("session_id"),
            "started_at": utc(),
            "target": target,
            "purpose": "Comparar envío TCP predeterminado por datalink y opción rawtcp oficial, con control de puerto origen. No cuenta para las 153 mediciones.",
        },
        exclusive=True,
    )
    with campaign_lock():
        for raw, sport in ((False, 32769), (True, 32769), (True, 20480)):
            local = {**cfg, "diagnostic_raw_tcp": raw, "tcp_source_port": sport}
            original = measure_scamper(
                local, target, "trace", "tcp", 0, kind="targeted_validation"
            )
            exported = export_packets(original)
            obj = next(
                o
                for o in records(original / "result.jsonl")
                if o.get("type") == "trace"
            )
            result = {
                "run_id": original.name,
                "rawtcp": raw,
                "source_port": sport,
                "unique_ips": sorted(
                    {h["addr"] for h in obj.get("hops", []) if h.get("addr")}
                ),
                "probe_count": obj.get("probe_count"),
                "stop_reason": obj.get("stop_reason"),
                "export": str(exported.relative_to(ROOT)),
                "manifest_sha256": sha256(original / "manifest.json"),
            }
            results.append(result)
            json_write(folder / "progress.json", results)
    result = {
        "session_id": cfg.get("session_id"),
        "performed_at": utc(),
        "target": target["ip"],
        "scope": "Diagnóstico adicional; excluido de la comparación principal y del entrenamiento de patrones. Una diferencia no identifica por sí sola la regla de firewall o causa local.",
        "runs": results,
        "evidence": str(folder.relative_to(ROOT)),
    }
    json_write(folder / "result.json", result, exclusive=True)
    save_manifest(folder, {"kind": "targeted_tcp_reception_validation"})
    json_write(output, result)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
