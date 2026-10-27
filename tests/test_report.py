"""Barreras de integridad del informe y conservación de respuestas múltiples."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from scripts import generar_informe_latex as report

class ReportTests(unittest.TestCase):
    def attempt(self, root, evidence, checks):
        analysis=root/'resultados/final';analysis.mkdir(parents=True)
        (analysis/'summary.json').write_text(json.dumps({'complete_campaign':True}))
        ev=root/'evidence.json';ev.write_text(json.dumps(evidence))
        argv=['report','--analysis',str(analysis),'--evidence',str(ev),'--output',str(root/'out')]
        with patch.object(report,'ROOT',root),patch.object(report,'verify_manifest'),patch.object(report,'delivery_checks',return_value=checks),patch('sys.argv',argv):report.main()

    def test_tampered_evidence_stops_before_document_creation(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'proof.json').write_text('{}')
            ev={'patterns':'proof.json','payload':'proof.json','selective':'proof.json','files':[{'path':'proof.json','sha256':'0'*64}]}
            checks={k:True for k in ('campaign_153_complete','three_current_graphs_public','fourteen_gui_methods_reviewed','selective_cases_corroborated')}
            with self.assertRaisesRegex(ValueError,'Evidencia alterada'):self.attempt(root,ev,checks)
            self.assertFalse((root/'out').exists())

    def test_incomplete_publication_prevents_final_report(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);checks={'campaign_153_complete':True,'three_current_graphs_public':False}
            with self.assertRaisesRegex(ValueError,'edición final'):self.attempt(root,{},checks)
            self.assertFalse((root/'out').exists())

    def test_selected_source_without_hash_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);ev={'patterns':'missing.json','payload':'missing.json','selective':'missing.json','files':[]}
            checks={k:True for k in ('campaign_153_complete','three_current_graphs_public','fourteen_gui_methods_reviewed','selective_cases_corroborated')}
            with self.assertRaisesRegex(ValueError,'hash explícito'):self.attempt(root,ev,checks)

    def test_zero_stability_beats_unknown_on_equal_information(self):
        base={'median_unique_ips':8,'median_coverage':.8}
        self.assertLess(report.score(dict(base,stability_jaccard=0)),report.score(dict(base,stability_jaccard=None)))

    def test_multiple_responses_and_non_global_labels_survive_formatting(self):
        text=report.clean('1.1.1.1 [AS13335]; 10.0.0.1 [non_global]; *; NO_MEDIDO')
        self.assertIn('1.1.1.1 [AS13335]',text)
        self.assertIn('10.0.0.1 [priv./esp.]',text)
        self.assertIn('*; --',text)

if __name__=='__main__':unittest.main()
