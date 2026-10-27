"""Fixtures sintéticos de validación; nunca se cuentan como mediciones reales."""

import copy
import json
import tempfile
import os
import unittest
from urllib.error import HTTPError
from pathlib import Path
from unittest.mock import patch

from path_discovery.acquire import plan_jobs, probe_issues, ripe_body, scamper_args
from path_discovery.analysis import (
    additional_ips,
    choose_pairs,
    cx2_graph,
    method_rankings,
    normalize_lb,
    normalize_ripe,
    normalize_trace,
    symmetry,
    collect,
)
from path_discovery.common import (
    config,
    json_write,
    save_manifest,
    verify_manifest,
    request_json,
    public_ip,
)
from path_discovery.delivery import validate_cx2, record_browser_publication
from path_discovery.packets import (
    learn_rule,
    validate_rule,
    inspect_udp_export,
    is_probe_request,
)
from path_discovery.common import tool_command, load_credentials


def metadata(**updates):
    base = {
        "kind": "measurement",
        "tool": "ripe",
        "family": "traceroute",
        "method": "UDP",
        "round": 1,
        "direction": "ida",
        "target": "8.8.8.8",
        "destination": "8.8.8.8",
        "measurement_id": 123,
        "probe_id": 7,
        "public_ipv4": "1.1.1.1",
        "started_at": "2026-10-23T10:00:00+00:00",
        "status": "completed",
        "pilot": False,
    }
    return {**base, **updates}


class CampaignTests(unittest.TestCase):
    def setUp(self):
        self.cfg = config()
        self.cfg["local_probe_id"] = 7

    def test_exact_153_unique_cells(self):
        jobs = plan_jobs(self.cfg)
        self.assertEqual(len(jobs), 153)
        self.assertEqual(len({tuple(j.values()) for j in jobs}), 153)
        self.assertEqual(sum(j["tool"] == "ripe" for j in jobs), 54)
        self.assertEqual(sum(j["family"] == "trace" for j in jobs), 54)
        self.assertEqual(sum(j["family"] == "tracelb" for j in jobs), 45)

    def test_ripe_does_not_override_defaults(self):
        body = ripe_body(self.cfg, self.cfg["targets"][0], "UDP", "ida", "1.1.1.1")
        self.assertEqual(
            body["probes"], [{"requested": 1, "type": "probes", "value": "7"}]
        )
        self.assertTrue(body["is_oneoff"])
        self.assertNotIn("packets", body["definitions"][0])
        self.assertNotIn("paris", body["definitions"][0])
        self.assertNotIn("port", body["definitions"][0])

    def test_reverse_targets_public_ip_from_exact_remote(self):
        t = self.cfg["targets"][0]
        body = ripe_body(self.cfg, t, "TCP", "vuelta", "1.1.1.1")
        self.assertEqual(body["probes"][0]["value"], str(t["probe_id"]))
        self.assertEqual(body["definitions"][0]["target"], "1.1.1.1")
        self.assertEqual(body["definitions"][0]["port"], 80)

    def test_unknown_protocol_rejected(self):
        with self.assertRaises(ValueError):
            ripe_body(self.cfg, self.cfg["targets"][0], "HTTP", "ida", "1.1.1.1")

    def test_probe_discrepancies_preserved(self):
        t = self.cfg["targets"][0]
        original_ip = t["ip"]
        issues = probe_issues(
            {"targets": [t]},
            {
                str(t["probe_id"]): {
                    "address_v4": "9.9.9.9",
                    "status": {"id": 3, "name": "Abandoned"},
                }
            },
        )
        self.assertEqual(len(issues), 2)
        self.assertEqual(t["ip"], original_ip)

    def test_scamper_command_no_shell_and_pps(self):
        with patch("path_discovery.acquire.work_path", return_value="/work/test.warts"):
            args = scamper_args(self.cfg, "trace", "tcp", "8.8.8.8", Path("test.warts"))
        self.assertIn("trace -P tcp -d 80", args)
        self.assertEqual(args[args.index("-p") + 1], "20")

    def test_explicit_diagnostic_source_port_does_not_change_default(self):
        baseline = scamper_args(self.cfg, "trace", "tcp", "8.8.8.8", "-")
        diagnostic = scamper_args(
            {**self.cfg, "tcp_source_port": 20480}, "trace", "tcp", "8.8.8.8", "-"
        )
        self.assertNotIn("-s 20480", baseline)
        self.assertIn("trace -P tcp -d 80 -s 20480", diagnostic)
        with self.assertRaises(ValueError):
            scamper_args(
                {**self.cfg, "tcp_source_port": 70000}, "trace", "tcp", "8.8.8.8", "-"
            )


class NormalizationTests(unittest.TestCase):
    def test_ripe_preserves_multiple_responses_timeout_and_error(self):
        obj = {
            "msm_id": 123,
            "prb_id": 7,
            "dst_addr": "8.8.8.8",
            "result": [
                {
                    "hop": 1,
                    "result": [
                        {"from": "10.0.0.1", "rtt": 2},
                        {"from": "10.0.0.2", "rtt": 3},
                        {"x": "*"},
                    ],
                },
                {"hop": 2, "error": "unreachable"},
            ],
        }
        rows = normalize_ripe(obj, metadata(), "test")
        self.assertEqual(len(rows), 4)
        self.assertEqual(
            [r["status"] for r in rows], ["reply", "reply", "timeout", "error"]
        )

    def test_wrong_ripe_source_or_destination_rejected(self):
        for updates in ({"prb_id": 99}, {"dst_addr": "9.9.9.9"}, {"msm_id": 124}):
            obj = {"msm_id": 123, "prb_id": 7, "dst_addr": "8.8.8.8", **updates}
            with self.assertRaises(ValueError):
                normalize_ripe(obj, metadata(), "test")

    def test_ripe_top_level_error_recorded(self):
        obj = {
            "msm_id": 123,
            "prb_id": 7,
            "dst_addr": "8.8.8.8",
            "error": "cannot route",
        }
        self.assertEqual(normalize_ripe(obj, metadata(), "t")[0]["status"], "error")

    def test_trace_20260902_no_hops_no_invented_attempts(self):
        obj = {
            "firsthop": 1,
            "hop_count": 3,
            "hops": [{"probe_ttl": 1, "probe_id": 0, "addr": "10.0.0.1", "rtt": 2}],
            "no_hops": [{"probe_ttl": 2, "probe_id": 0}],
        }
        rows = normalize_trace(obj, metadata(tool="scamper", family="trace"), "test")
        self.assertEqual(
            [r["status"] for r in rows], ["reply", "timeout", "not_recorded"]
        )
        self.assertEqual(len(rows), 3)

    def test_tracelb_nested_links_deduplicates_probe_representations(self):
        branch = {
            "addr": "8.8.8.8",
            "probes": [
                {
                    "ttl": 2,
                    "flowid": 4,
                    "attempt": 0,
                    "tx": {"sec": 1},
                    "replies": [{"rtt": 1}],
                }
            ],
        }
        obj = {
            "nodes": [
                {
                    "addr": "10.0.0.1",
                    "links": [
                        [
                            branch,
                            branch,
                            {"addr": "*", "probes": [{"ttl": 3, "attempt": 1}]},
                        ]
                    ],
                }
            ]
        }
        rows = normalize_lb(obj, metadata(tool="scamper", family="tracelb"), "test")
        self.assertEqual(sum(r["status"] == "reply" for r in rows), 1)
        self.assertEqual(sum(r["status"] == "timeout" for r in rows), 1)
        self.assertEqual(sum(r["status"] == "node_only" for r in rows), 1)

    def test_tracelb_reply_ttl_not_confused_with_probe_distance(self):
        obj = {
            "nodes": [
                {
                    "addr": "10.0.0.1",
                    "links": [
                        [
                            {
                                "addr": "8.8.8.8",
                                "probes": [
                                    {"ttl": 4, "replies": [{"ttl": 248, "rtt": 1}]}
                                ],
                            }
                        ]
                    ],
                }
            ]
        }
        rows = normalize_lb(obj, metadata(), "t")
        self.assertEqual(rows[0]["ttl"], 4)


def run(name, **updates):
    return {
        **metadata(),
        "run_id": name,
        "ips": ["10.0.0.1", "8.8.8.8"],
        "unique_ips": 2,
        "coverage": 1,
        "missing_hops": 0,
        "probes_sent": 3,
        "destination_observed": True,
        **updates,
    }


class AnalysisTests(unittest.TestCase):
    def test_pair_same_protocol_round_and_public_ip(self):
        a = run("a")
        b = run("b", direction="vuelta", measurement_id=124)
        self.assertEqual(choose_pairs([a, b])["8.8.8.8"][1]["measurement_id"], 124)
        for change in ({"method": "TCP"}, {"round": 2}, {"public_ipv4": "9.9.9.9"}):
            self.assertEqual(choose_pairs([a, {**b, **change}]), {})

    def test_pair_selects_union_then_gaps(self):
        pair = [
            run("a"),
            run("b", direction="vuelta", measurement_id=124),
            run("c", method="TCP", ips=["9.9.9.9"], unique_ips=1),
            run(
                "d",
                method="TCP",
                direction="vuelta",
                measurement_id=125,
                ips=["4.4.4.4", "5.5.5.5"],
                unique_ips=2,
            ),
        ]
        self.assertEqual(choose_pairs(pair)["8.8.8.8"][0]["method"], "TCP")

    def test_graph_no_cartesian_links_and_gap_is_explicit(self):
        a, b = run("a"), run("b", direction="vuelta", measurement_id=124)
        rows = [
            {"run_id": "a", "source": "1.1.1.1", "ttl": ttl, "ip": ip, "asns": []}
            for ttl, ip in [(1, "10.0.0.1"), (1, "10.0.0.2"), (2, None), (3, "8.8.8.8")]
        ]
        cx = validate_cx2(cx2_graph((a, b), rows))
        self.assertEqual(sum(n["v"]["kind"] == "ambiguous_hop" for n in cx["nodes"]), 1)
        self.assertEqual(sum(n["v"]["kind"] == "gap" for n in cx["nodes"]), 1)
        self.assertEqual(len(cx["edges"]), 3)
        self.assertIn("123", cx["networkAttributes"][0]["description"])
        self.assertIn("124", cx["networkAttributes"][0]["description"])

    def test_graph_nonconsecutive_ttl_does_not_invent_path(self):
        a, b = run("a"), run("b", direction="vuelta", measurement_id=124)
        rows = [
            {"run_id": "a", "source": "1.1.1.1", "ttl": ttl, "ip": ip, "asns": []}
            for ttl, ip in [(1, "10.0.0.1"), (2, None), (255, None)]
        ]
        cx = validate_cx2(cx2_graph((a, b), rows))
        self.assertEqual(len(cx["nodes"]), 4)
        self.assertTrue(any(n["v"].get("ttl") == 255 for n in cx["nodes"]))
        self.assertEqual([e["v"]["ttl"] for e in cx["edges"]], [1, 2])
        self.assertLess(max(n["x"] for n in cx["nodes"]), 500)

    def test_symmetry_keeps_recorded_ttl_255_without_fabricated_layers(self):
        a, b = run("a"), run("b", direction="vuelta", measurement_id=124)
        rows = [
            {"run_id": name, "ttl": ttl, "ip": ip, "asns": []}
            for name in ("a", "b")
            for ttl, ip in [(1, "10.0.0.1"), (255, None)]
        ]
        result = symmetry(rows, [a, b])[0]
        self.assertEqual(len(result["ida_ip_layers"]), 2)
        self.assertTrue(result["incomplete"])

    def test_additional_ips_uses_union_of_all_trace_methods(self):
        base = [
            run("a", tool="scamper", family="trace", ips=["1.1.1.1"]),
            run("b", tool="scamper", family="trace", method="icmp", ips=["9.9.9.9"]),
        ]
        result = additional_ips(
            base + [run("lb", family="tracelb", ips=["9.9.9.9", "8.8.8.8"])]
        )[0]
        self.assertEqual(result["additional_ips"], ["8.8.8.8"])
        self.assertFalse(result["complete_reference"])

    def test_stability_does_not_treat_two_empty_paths_as_perfect_match(self):
        empty = [run("a", round=1, ips=[], unique_ips=0), run("b", round=2, ips=[], unique_ips=0)]
        self.assertIsNone(method_rankings(empty)[0]["stability_jaccard"])
        empty.append(run("c", round=3, ips=["1.1.1.1"], unique_ips=1))
        self.assertEqual(method_rankings(empty)[0]["stability_jaccard"], 0.0)

    def test_rank_uses_median_not_most_favorable_run(self):
        runs = [
            run("a", round=1, unique_ips=100),
            run("b", round=2, unique_ips=1),
            run("c", round=3, unique_ips=1),
            run("d", method="TCP", unique_ips=3),
        ]
        self.assertEqual(method_rankings(runs)[0]["method"], "TCP")


class PublicationReceiptTests(unittest.TestCase):
    def fixture(self, root):
        analysis = root / "resultados/analysis"
        graph = analysis / "grafos/target.cx2.json"
        graph.parent.mkdir(parents=True)
        cx = [
            {"CXVersion": "2.0"},
            {"nodes": [{"id": 0}]},
            {"edges": []},
            {
                "networkAttributes": [
                    {"description": "Ida msm_id=123; vuelta msm_id=124"}
                ]
            },
        ]
        graph.write_text(json.dumps(cx))
        graph.with_name("target.selection.json").write_text(
            json.dumps({"ids": [123, 124], "target": "8.8.8.8"})
        )
        save_manifest(analysis, {})
        return graph, cx

    def test_public_export_and_both_measurement_ids_required(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            graph, cx = self.fixture(root)
            with (
                patch("path_discovery.delivery.ROOT", root),
                patch(
                    "path_discovery.delivery.request_json",
                    side_effect=[{"visibility": "PUBLIC"}, cx],
                ) as fetch,
            ):
                result = record_browser_publication(
                    graph, "00000000-0000-4000-8000-000000000001"
                )
            self.assertTrue(result["public_read_verified"])
            self.assertEqual(result["measurement_ids"], [123, 124])
            self.assertTrue(all(not c.kwargs for c in fetch.call_args_list))

    def test_readable_but_unlisted_graph_is_not_called_public(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            graph, cx = self.fixture(root)
            with (
                patch("path_discovery.delivery.ROOT", root),
                patch(
                    "path_discovery.delivery.request_json",
                    return_value={"visibility": "UNLISTED"},
                ),
            ):
                with self.assertRaises(ValueError):
                    record_browser_publication(
                        graph, "00000000-0000-4000-8000-000000000001"
                    )

    def test_missing_measurement_reference_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            graph, cx = self.fixture(root)
            cx[-1]["networkAttributes"][0]["description"] = "Only 123"
            with (
                patch("path_discovery.delivery.ROOT", root),
                patch(
                    "path_discovery.delivery.request_json",
                    side_effect=[{"visibility": "PUBLIC"}, cx],
                ),
            ):
                with self.assertRaises(ValueError):
                    record_browser_publication(
                        graph, "00000000-0000-4000-8000-000000000001"
                    )


class PacketReviewTests(unittest.TestCase):
    def test_tcp_reset_control_packets_are_not_counted_as_probes(self):
        self.assertTrue(is_probe_request({"tcp.flags": "0x0002"}, "TCP"))
        self.assertFalse(is_probe_request({"tcp.flags": "0x0004"}, "TCP"))
        self.assertFalse(is_probe_request({"tcp.flags": "0x0014"}, "TCP"))
        self.assertTrue(is_probe_request({"tcp.flags": "0x0010"}, "tcp-ack-sport"))
        self.assertFalse(is_probe_request({"tcp.flags": "0x0014"}, "tcp-ack-sport"))

    def test_icmp_quoted_udp_is_not_counted_as_emitted_request(self):
        ip = {"ip.dst": "8.8.8.8", "ip.id": "0x10", "ip.ttl": "1"}
        udp = {"udp.srcport": "20000", "udp.dstport": "33435", "udp.checksum": "0x01"}
        packets = [
            {
                "_source": {
                    "layers": {"ip": ip, "udp": udp, "frame": {"frame.number": "1"}}
                }
            },
            {
                "_source": {
                    "layers": {
                        "ip": {"ip.src": "10.0.0.1"},
                        "frame": {"frame.number": "2"},
                        "icmp": {
                            "icmp.type": "11",
                            "icmp.code": "0",
                            "ip": ip,
                            "udp": udp,
                        },
                    }
                }
            },
        ]
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)
            (path / "packets_full.json").write_text(json.dumps(packets))
            evidence = inspect_udp_export(path, metadata())
        self.assertEqual(evidence["requests_count"], 1)
        self.assertEqual(evidence["matched_quotes"], 1)
        self.assertEqual(evidence["udp_ports"], [33435])

    def test_outgoing_capture_without_correlated_reply_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)
            (path / "packets_full.json").write_text("[]")
            with self.assertRaises(ValueError):
                inspect_udp_export(path, metadata())
            evidence = inspect_udp_export(path, metadata(direction="vuelta"))
            self.assertTrue(evidence["reverse_capture_is_partial"])
            self.assertEqual(evidence["requests_count"], 0)


class IntegrityTests(unittest.TestCase):
    def test_manifest_detects_tampering_and_missing_files(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td)
            (path / "test.txt").write_text("original")
            save_manifest(path, {"kind": "fixture"})
            verify_manifest(path)
            (path / "test.txt").write_text("alterado")
            with self.assertRaises(ValueError):
                verify_manifest(path)
            (path / "test.txt").unlink()
            with self.assertRaises(ValueError):
                verify_manifest(path)

    def test_sealed_manifest_not_overwritten(self):
        with tempfile.TemporaryDirectory() as td:
            save_manifest(td, {})
            with self.assertRaises(FileExistsError):
                save_manifest(td, {})

    def test_cx2_invalid_edges_rejected(self):
        with self.assertRaises(ValueError):
            validate_cx2(
                [
                    {"CXVersion": "2.0"},
                    {"nodes": [{"id": 1}]},
                    {"edges": [{"s": 1, "t": 9}]},
                ]
            )

    def test_post_is_never_retried_and_secret_not_in_error(self):
        error = HTTPError(
            "https://example.invalid/?key=SECRET", 503, "unavailable", {}, None
        )
        with patch("path_discovery.common.urlopen", side_effect=error) as call:
            with self.assertRaises(RuntimeError) as exc:
                request_json("https://example.invalid/?key=SECRET", {"definitions": []})
            self.assertEqual(call.call_count, 1)
            self.assertNotIn("SECRET", str(exc.exception))

    def test_public_ip_disagreement_blocks_measurement(self):
        with self.assertRaises(RuntimeError):
            public_ip({"one": "1.1.1.1", "two": "9.9.9.9"})
        self.assertEqual(public_ip({"one": "1.1.1.1", "two": "1.1.1.1"}), "1.1.1.1")

    def test_private_ip_cannot_be_used_as_public_endpoint(self):
        with self.assertRaises(ValueError):
            public_ip({"one": "10.0.0.1", "two": "10.0.0.1"})

    def test_campaign_without_pilot_does_not_measure(self):
        from path_discovery.cli import run_campaign

        with (
            tempfile.TemporaryDirectory() as td,
            patch("path_discovery.cli.ROOT", Path(td)),
            patch("path_discovery.cli.measure_scamper") as measure,
        ):
            with self.assertRaises(ValueError):
                run_campaign(1)
            measure.assert_not_called()

    def test_invalid_university_pilot_is_excluded_from_campaign(self):
        with tempfile.TemporaryDirectory() as td:
            folder = Path(td) / "datos/originales/scamper_fixture"
            folder.mkdir(parents=True)
            meta = metadata(
                tool="scamper",
                family="trace",
                method="udp",
                round=0,
                pilot=True,
                status="invalid_public_ip_changed",
            )
            json_write(folder / "metadata.json", meta)
            json_write(
                folder / "result.jsonl",
                {
                    "type": "trace",
                    "firsthop": 1,
                    "hop_count": 1,
                    "hops": [{"probe_ttl": 1, "addr": "10.0.0.1", "probe_id": 1}],
                    "probe_count": 1,
                },
            )
            save_manifest(folder, {})
            with (
                patch("path_discovery.analysis.ROOT", Path(td)),
                patch("path_discovery.analysis.config", return_value={}),
            ):
                self.assertEqual(len(collect()[1]), 0)
                self.assertEqual(len(collect(include_pilots=True)[1]), 0)
                rows, runs, _ = collect(include_pilots=True, diagnostic_pilots=True)
                self.assertEqual(len(runs), 1)
                self.assertTrue(rows[0]["pilot"])
                self.assertEqual(rows[0]["run_status"], "invalid_public_ip_changed")

    def test_symmetry_preserves_gaps_and_does_not_claim_physical_path(self):
        a = run("a")
        b = run("b", direction="vuelta", measurement_id=124)
        rows = [
            {"run_id": name, "ttl": ttl, "ip": ip, "asns": []}
            for name in ("a", "b")
            for ttl, ip in ((1, "10.0.0.1"), (2, None))
        ]
        result = symmetry(rows, [a, b])[0]
        self.assertTrue(result["incomplete"])
        self.assertIn("no prueba", result["interpretation"])


class ComposeAndCredentialsTests(unittest.TestCase):
    def test_compose_tool_does_not_start_atlas_or_allocate_tty(self):
        with patch.dict(os.environ, {}, clear=True):
            args = tool_command(
                "dumpcap", ["-w", "-"], cfg=config(), name="capture-test"
            )
        self.assertIn("compose", args)
        self.assertIn("--no-deps", args)
        self.assertIn("-T", args)
        self.assertIn("--interactive=false", args)
        self.assertEqual(args[-4:], ["tools", "dumpcap", "-w", "-"])
        self.assertNotIn("atlas", args)
        self.assertIn("capture-test", args)

    def test_local_credentials_are_loaded_without_overriding_environment(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / ".env").write_text(
                "RIPE_ATLAS_API_KEY='local-value'\nNDEX_PASSWORD='password with spaces'\nHOME=/wrong\n"
            )
            with (
                patch("path_discovery.common.ROOT", root),
                patch.dict(
                    os.environ,
                    {"RIPE_ATLAS_API_KEY": "existing-value", "HOME": "/original"},
                    clear=True,
                ),
            ):
                load_credentials()
                self.assertEqual(os.environ["RIPE_ATLAS_API_KEY"], "existing-value")
                self.assertEqual(os.environ["NDEX_PASSWORD"], "password with spaces")
                self.assertEqual(os.environ["HOME"], "/original")

    def test_dotenv_never_executes_command_substitution(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / ".env").write_text(
                "NDEX_PASSWORD='$(touch /tmp/should-not-be-created)'\n"
            )
            with (
                patch("path_discovery.common.ROOT", root),
                patch.dict(os.environ, {}, clear=True),
            ):
                load_credentials()
                self.assertEqual(
                    os.environ["NDEX_PASSWORD"], "$(touch /tmp/should-not-be-created)"
                )

    def test_malformed_credential_error_does_not_include_value(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / ".env").write_text("NDEX_PASSWORD='PRIVATEVALUE\n")
            with patch("path_discovery.common.ROOT", root):
                with self.assertRaises(ValueError) as exc:
                    load_credentials()
                self.assertNotIn("PRIVATEVALUE", str(exc.exception))


class PredictionTests(unittest.TestCase):
    def test_constant_verified_in_separate_round(self):
        rule = learn_rule(["80", "80", "80"])
        self.assertEqual(validate_rule(rule, ["80", "81"])["status"], "failed")

    def test_step_predicts_after_execution_base(self):
        rule = learn_rule(["33434", "33435", "33436"])
        self.assertEqual(rule["kind"], "step")
        self.assertEqual(
            validate_rule(rule, ["50000", "50001", "50002"])["status"], "passed"
        )

    def test_variable_is_not_claimed_predictable(self):
        rule = learn_rule(["1", "9", "4"])
        self.assertEqual(validate_rule(rule, ["5", "9"])["status"], "not_predictable")

    def test_insufficient_samples(self):
        self.assertEqual(learn_rule(["1"])["kind"], "insufficient")


if __name__ == "__main__":
    unittest.main()
