"""
Unit tests for Report Generator using unittest.
"""

import json
import tempfile
import unittest
from pathlib import Path
from modules.diagnostics import run_full_diagnostics
from modules.report import generate_txt_report, generate_html_report, save_report


class TestReport(unittest.TestCase):
    def test_generate_txt_report(self):
        report = run_full_diagnostics()
        txt = generate_txt_report(report)
        self.assertIn("ADAPTIVE CLI SYSTEM HEALTH REPORT", txt)
        self.assertIn(report.system_info.hostname, txt)

    def test_generate_html_report(self):
        report = run_full_diagnostics()
        html = generate_html_report(report)
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn(report.system_info.hostname, html)

    def test_save_report(self):
        report = run_full_diagnostics()
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)

            filepath_txt, content_txt = save_report(report, fmt="txt", output_dir=tmp_path)
            self.assertTrue(filepath_txt.exists())
            self.assertIn("ADAPTIVE CLI SYSTEM HEALTH REPORT", content_txt)

            filepath_json, content_json = save_report(report, fmt="json", output_dir=tmp_path)
            self.assertTrue(filepath_json.exists())
            data = json.loads(content_json)
            self.assertIn("health_score", data)

            filepath_html, content_html = save_report(report, fmt="html", output_dir=tmp_path)
            self.assertTrue(filepath_html.exists())
            self.assertIn("<!DOCTYPE html>", content_html)


if __name__ == "__main__":
    unittest.main()
