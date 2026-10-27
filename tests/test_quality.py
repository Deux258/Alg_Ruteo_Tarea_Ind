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


class SessionTests(unittest.TestCase):
    def test_changed_session_blocks_before_capture_and_post(self):
        from path_discovery.acquire import measure_ripe, measure_scamper
        from path_discovery.common import config
        cfg = {**config(), "session_public_ipv4": "1.1.1.1"}
        with tempfile.TemporaryDirectory() as td, patch("path_discovery.acquire.ROOT", Path(td)), patch("path_discovery.acquire.public_ip", return_value="9.9.9.9"), patch("path_discovery.acquire.Capture") as capture, patch("path_discovery.acquire.request_json") as post, patch.dict("os.environ", {"RIPE_ATLAS_API_KEY": "test-only"}):
            with self.assertRaises(RuntimeError):
                measure_scamper(cfg, cfg["targets"][0], "trace", "udp", 1)
            with self.assertRaises(RuntimeError):
                measure_ripe(cfg, cfg["targets"][0], "UDP", "ida", 1)
            capture.assert_not_called()
            post.assert_not_called()

    def test_collect_selects_active_session_and_explicit_history(self):
        from path_discovery.analysis import collect
        from path_discovery.common import json_write
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for label, ip in (("old", "1.1.1.1"), ("new", "9.9.9.9")):
                folder = root / "datos/originales" / label
                folder.mkdir(parents=True)
                json_write(folder / "metadata.json", {"kind": "measurement", "tool": "scamper", "family": "trace", "method": "udp", "round": 1, "direction": "ida", "target": "8.8.8.8", "destination": "8.8.8.8", "public_ipv4": ip, "status": "completed"})
                json_write(folder / "result.jsonl", {"type": "trace", "dst": "8.8.8.8", "hop_count": 1, "probe_count": 1, "hops": [{"probe_ttl": 1, "addr": "8.8.8.8"}]})
                save_manifest(folder, {})
            with patch("path_discovery.analysis.ROOT", root), patch("path_discovery.analysis.config", return_value={"session_public_ipv4": "9.9.9.9"}):
                self.assertEqual([r["run_id"] for r in collect()[1]], ["new"])
                self.assertEqual([r["run_id"] for r in collect(session_ip="1.1.1.1")[1]], ["old"])


class DeliverySessionTests(unittest.TestCase):
    def test_historical_gui_methods_do_not_satisfy_current_review(self):
        from path_discovery.delivery import delivery_checks
        from path_discovery.common import json_write, TRACE_METHODS, LB_METHODS, RIPE_METHODS
        with tempfile.TemporaryDirectory() as td:
            root = Path(td);analysis = root / "resultados/analysis";analysis.mkdir(parents=True)
            json_write(analysis / "summary.json", {"complete_campaign": True, "graphs": []})
            json_write(analysis / "runs.json", [])
            names = ["scamper_trace_" + m for m in TRACE_METHODS] + ["scamper_tracelb_" + m for m in LB_METHODS] + ["ripe_traceroute_" + m for m in RIPE_METHODS]
            json_write(root / "resultados/revision_wireshark_gui.json", {"reviewed_runs": [{"method": m, "run_id": "historical"} for m in names]})
            with patch("path_discovery.delivery.ROOT", root):
                self.assertFalse(delivery_checks(analysis)["fourteen_gui_methods_reviewed"])


    def test_bundle_preserves_sealed_public_archive_without_live_credentials(self):
        import tarfile
        from path_discovery.delivery import bundle
        from path_discovery.common import json_write, verify_manifest
        with tempfile.TemporaryDirectory() as td:
            root = Path(td);analysis = root / "resultados/analysis";analysis.mkdir(parents=True)
            json_write(analysis / "summary.json", {"complete_campaign": False, "graphs": []})
            save_manifest(analysis, {"kind": "analysis"})
            archive = root / "datos/originales/cambio_sesion_test"
            for rel in ("previous/.state/campaign.json", "previous/.state/pilot.json", "previous/.state/postprocessing.json", "previous/config/local.json"):
                json_write(archive / rel, {"public_metadata": True})
            save_manifest(archive, {"kind": "session_change"})
            selection = root / "datos/originales/seleccion_sondas_20261026T012504"
            json_write(selection / "local.json", {"url": "https://atlas.ripe.net/api/v2/probes/1018487/", "response": {"id": 1018487}})
            save_manifest(selection, {"kind": "target_substitution"})
            (root / "config").mkdir();json_write(root / "config/local.json", {"private_local": True})
            (root / ".env").write_text("EXAMPLE=not-for-package")
            with patch("path_discovery.delivery.ROOT", root):
                output = bundle(analysis)
            with tarfile.open(output / "paquete_preparacion.tar.gz") as tar:
                names = set(tar.getnames())
                self.assertNotIn("config/local.json", names)
                self.assertNotIn(".env", names)
                for rel in ("previous/.state/campaign.json", "previous/.state/pilot.json", "previous/.state/postprocessing.json", "previous/config/local.json"):
                    self.assertIn("datos/originales/cambio_sesion_test/" + rel, names)
                extracted = root / "extracted";tar.extractall(extracted, filter="data")
            verify_manifest(extracted / "datos/originales/cambio_sesion_test")
            verify_manifest(extracted / "datos/originales/seleccion_sondas_20261026T012504")


class ContinuityTests(unittest.TestCase):
    def test_suspend_cannot_be_accepted_as_continuous_measurement(self):
        from path_discovery.acquire import validate_measurement_continuity
        meta = {"status": "completed", "clock_start": {"monotonic": 10, "boottime": 100, "boot_id": "a"}}
        with patch("path_discovery.acquire.measurement_clocks", return_value={"monotonic": 30, "boottime": 190, "boot_id": "a"}):
            validate_measurement_continuity(meta)
        self.assertEqual(meta["status"], "invalid_session_interruption")
        self.assertEqual(meta["clock_check"]["suspend_gap_seconds"], 70)

    def test_awake_and_historical_measurements_preserve_status(self):
        from path_discovery.acquire import validate_measurement_continuity
        meta = {"status": "completed", "clock_start": {"monotonic": 10, "boottime": 100, "boot_id": "a"}}
        with patch("path_discovery.acquire.measurement_clocks", return_value={"monotonic": 30, "boottime": 120, "boot_id": "a"}):
            validate_measurement_continuity(meta)
        self.assertEqual(meta["status"], "completed")
        old = {"status": "completed"}
        validate_measurement_continuity(old)
        self.assertEqual(old, {"status": "completed"})


class StatusSessionTests(unittest.TestCase):
    def test_historical_graphs_do_not_count_for_active_session(self):
        from path_discovery.cli import status
        from path_discovery.common import json_write
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            json_write(root / "grafos/publication_old/publication.json", {"measurement_ids": [1, 2], "target": "8.8.8.8", "public_read_verified": True})
            with patch("path_discovery.cli.ROOT", root), patch("path_discovery.cli.collect", return_value=([], [], [])), patch("path_discovery.cli.plan_jobs", return_value=[]):
                self.assertEqual(status()["public_graphs"], [])


class ProbeProtocolIsolationTests(unittest.TestCase):
    def test_background_protocols_and_quotes_are_not_mixed_with_probes(self):
        from path_discovery.packets import is_probe_request
        udp = {"ip.proto": "17", "udp.srcport": "20480", "udp.dstport": "33435"}
        echo = {"ip.proto": "1", "icmp.type": "8"}
        syn = {"ip.proto": "6", "tcp.flags": "0x0002"}
        quote = {**udp, "ip.proto": "1", "icmp.type": "11"}
        for method, expected in (("UDP", udp), ("udp-sport", udp), ("ICMP", echo), ("icmp-paris", echo), ("TCP", syn)):
            accepted = [p for p in (udp, echo, syn, quote) if is_probe_request(p, method)]
            self.assertEqual(accepted, [expected])

    def test_unknown_protocol_is_not_silently_counted(self):
        from path_discovery.packets import is_probe_request
        with self.assertRaises(ValueError):
            is_probe_request({"ip.proto": "17", "udp.srcport": "1", "udp.dstport": "2"}, "unknown")


class ProbeCostSourceTests(unittest.TestCase):
    def test_counter_capture_difference_remains_explicit_without_discarding_route(self):
        from path_discovery.analysis import collect
        from path_discovery.common import json_write
        with tempfile.TemporaryDirectory() as td:
            root = Path(td);original=root / "datos/originales/scamper_fixture";original.mkdir(parents=True)
            json_write(original / "metadata.json", {"kind":"measurement", "tool":"scamper", "family":"trace", "method":"udp-paris", "round":1, "direction":"ida", "target":"8.8.8.8", "destination":"8.8.8.8", "public_ipv4":"1.1.1.1", "status":"completed"})
            json_write(original / "result.jsonl", {"type":"trace", "probe_count":2, "hop_count":1, "hops":[{"addr":"8.8.8.8", "probe_ttl":1}]})
            save_manifest(original, {})
            exported=root / "resultados/paquetes/fixture";exported.mkdir(parents=True)
            json_write(exported / "metadata.json", {"probe_classifier_revision":2, "candidate_emitted_packets":1, "source_manifest_sha256":sha256(original / "manifest.json")})
            save_manifest(exported,{})
            json_write(root / "resultados/exportaciones_paquetes.json", {"scamper_fixture":"resultados/paquetes/fixture"})
            with patch("path_discovery.analysis.ROOT",root),patch("path_discovery.analysis.config",return_value={}):
                _,runs,invalid=collect()
            self.assertEqual(invalid,[])
            self.assertEqual(runs[0]["probes_sent"],2)
            self.assertEqual(runs[0]["pcap_observed_probes"],1)
            self.assertTrue(runs[0]["packet_count_mismatch"])
            self.assertTrue(runs[0]["destination_observed"])


class SourceAsnTests(unittest.TestCase):
    def test_source_asn_is_resolved_even_when_no_hop_replies(self):
        from path_discovery.analysis import enrich
        with tempfile.TemporaryDirectory() as td:
            rows=[{"ip":None,"source":"8.8.8.8"},{"ip":"8.8.8.8","source":"10.0.0.1"}]
            with patch("path_discovery.analysis.ROOT",Path(td)),patch("path_discovery.analysis.request_json",return_value={"data":{"asns":[64500],"prefix":"8.8.8.0/24"}}) as request:
                enrich(rows,online=True)
            self.assertEqual(request.call_count,1)
            self.assertEqual(rows[0]["source_asns"],[64500])
            self.assertEqual(rows[1]["asns"],[64500])
            self.assertEqual(rows[1]["source_asn_status"],"non_global")

    def test_graph_public_origin_keeps_its_asn(self):
        from path_discovery.analysis import cx2_graph
        a={"run_id":"ida","method":"UDP","direction":"ida","target":"8.8.8.8","round":1,"measurement_id":1}
        b={**a,"run_id":"vuelta","direction":"vuelta","measurement_id":2}
        rows=[{"run_id":"ida","source":"1.1.1.1","source_asns":[13335],"ttl":1,"ip":"8.8.8.8","asns":[15169]}, {"run_id":"vuelta","source":"8.8.8.8","source_asns":[15169],"ttl":1,"ip":"1.1.1.1","asns":[13335]}]
        nodes=next(x["nodes"] for x in cx2_graph((a,b),rows) if "nodes" in x)
        self.assertEqual(next(n for n in nodes if n["v"]["name"]=="1.1.1.1")["v"]["asns"],"13335")


class GraphGapEvidenceTests(unittest.TestCase):
    def test_edge_after_gap_does_not_claim_interface_adjacency(self):
        from path_discovery.analysis import cx2_graph
        a={"run_id":"ida","method":"UDP","direction":"ida","target":"8.8.8.8","round":1,"measurement_id":1};b={**a,"run_id":"vuelta","direction":"vuelta","measurement_id":2}
        rows=[{"run_id":"ida","source":"1.1.1.1","ttl":n,"ip":ip,"asns":[]} for n,ip in [(1,"8.8.4.4"),(2,None),(3,"8.8.8.8")]]
        graph={k:v for part in cx2_graph((a,b),rows) for k,v in part.items()}
        kinds={n["id"]:n["v"]["kind"] for n in graph['nodes']}
        gap_edges=[e for e in graph['edges'] if kinds[e['s']]!='ip_interface' or kinds[e['t']]!='ip_interface']
        self.assertEqual(len(gap_edges),2)
        self.assertTrue(all(e['v']['evidence']=='hop_layer_order_only' for e in gap_edges))
