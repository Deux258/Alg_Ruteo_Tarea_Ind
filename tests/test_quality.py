import json, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
from path_discovery.analysis import excluded_runs
from path_discovery.common import save_manifest, sha256


class QualityTests(unittest.TestCase):
    def test_sealed_quality_exclusions_and_tampering(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "config").mkdir()
            ev = root / "evidence"
            ev.mkdir()
            (ev / "decision.json").write_text("{}")
            save_manifest(ev, {"kind": "quality_adjudication"})
            decision = {
                "excluded_runs": ["interrupted"],
                "evidence_path": "evidence",
                "evidence_manifest_sha256": sha256(ev / "manifest.json"),
            }
            (root / "config/exclusiones_calidad.json").write_text(json.dumps(decision))
            with (
                patch("path_discovery.analysis.ROOT", root),
                patch(
                    "path_discovery.analysis.config",
                    return_value={"excluded_runs": ["pilot"]},
                ),
            ):
                self.assertEqual(excluded_runs(), {"interrupted", "pilot"})
                (ev / "decision.json").write_text('{"tampered":true}')
                with self.assertRaises(ValueError):
                    excluded_runs()

    def test_packet_patterns_ignore_excluded_and_diagnostic_exports(self):
        from path_discovery.packets import pattern_groups

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "resultados").mkdir()
            (root / "resultados/exportaciones_paquetes.json").write_text(
                json.dumps({"excluded": "missing", "diagnostic": "missing2"})
            )
            with (
                patch("path_discovery.packets.ROOT", root),
                patch("path_discovery.analysis.collect", return_value=([], [], [])),
            ):
                self.assertEqual(dict(pattern_groups()), {})

    def test_raw_tcp_is_explicit_diagnostic_option(self):
        from path_discovery.acquire import scamper_args
        from path_discovery.common import config

        cfg = config()
        regular = scamper_args(cfg, "trace", "tcp", "8.8.8.8", "-")
        self.assertNotIn("rawtcp", regular)
        cfg["diagnostic_raw_tcp"] = True
        self.assertIn("rawtcp", scamper_args(cfg, "trace", "tcp", "8.8.8.8", "-"))
        self.assertNotIn("rawtcp", scamper_args(cfg, "trace", "udp", "8.8.8.8", "-"))

    def test_selective_case_requires_repeated_presence_and_comparable_ttl(self):
        from scripts.validar_respuesta_selectiva import candidates

        runs = []
        rows = []
        for n in (1, 2, 3):
            for method, ips in [("udp", ["8.8.8.8"]), ("icmp", ["1.1.1.1"])]:
                rid = f"{method}{n}"
                runs.append(
                    {
                        "tool": "ripe",
                        "family": "traceroute",
                        "direction": "ida",
                        "target": "9.9.9.9",
                        "method": method,
                        "round": n,
                        "run_id": rid,
                        "ips": ips,
                    }
                )
                rows.append(
                    {"run_id": rid, "ip": ips[0], "ttl": 5 if method == "udp" else 2}
                )
        found = candidates(rows, runs, "ripe")
        self.assertFalse(any(c["ip"] == "8.8.8.8" for c in found))
        for r in rows:
            r["ttl"] = 5
        self.assertTrue(
            any(
                c["ip"] == "8.8.8.8" and len(c["responding_rounds"]) == 3
                for c in candidates(rows, runs, "ripe")
            )
        )

    def test_153_measurements_do_not_alone_make_delivery_complete(self):
        from path_discovery.delivery import delivery_checks

        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            analysis = root / "resultados/analysis"
            analysis.mkdir(parents=True)
            (analysis / "summary.json").write_text(
                json.dumps(
                    {
                        "complete_campaign": True,
                        "graphs": ["8.8.8.8", "1.1.1.1", "9.9.9.9"],
                    }
                )
            )
            with patch("path_discovery.delivery.ROOT", root):
                checks = delivery_checks(analysis)
            self.assertTrue(checks["campaign_153_complete"])
            self.assertFalse(checks["three_current_graphs_public"])
            self.assertFalse(all(checks.values()))

    def test_payload_checksum_constraint_handles_word_carry_and_failure(self):
        from scripts.estructura_payload import invariant

        rows = [
            {
                "data.data": "00010000",
                "icmp.checksum": "0x0001",
                "icmp.ident": "7",
                "icmp.seq": "65534",
            },
            {
                "data.data": "ffff0000",
                "icmp.checksum": "0x0001",
                "icmp.ident": "7",
                "icmp.seq": "0",
            },
        ]
        result = invariant(rows)
        self.assertTrue(result["stable_within_run"])
        self.assertEqual(result["checked_later_packets"], 1)
        rows[1]["data.data"] = "fffe0000"
        self.assertEqual(invariant(rows)["failed_later_packets"], 1)

    def test_ttl_repetition_rule_validates_new_round_without_hiding_failure(self):
        from path_discovery.packets import learn_rule, validate_rule

        rule = learn_rule(["1", "1", "1", "2", "2", "2", "3", "3", "3"])
        self.assertEqual(rule["kind"], "block_step")
        self.assertEqual(rule["block_size"], 3)
        self.assertEqual(
            validate_rule(rule, ["4", "4", "4", "5", "5", "5"])["status"], "passed"
        )
        self.assertEqual(
            validate_rule(rule, ["1", "1", "2", "2", "2", "2"])["status"], "failed"
        )
