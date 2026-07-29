"""
Unit tests for CLI functions using unittest.
"""

import unittest
import tempfile
from pathlib import Path
from cli import show_info, diagnose_system, get_recommendations, export_report


class TestCLI(unittest.TestCase):
    def test_cli_functions_execution(self):
        # Verify commands execute without throwing runtime errors
        show_info()
        diagnose_system()
        get_recommendations()

    def test_export_report_function(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            out_path = Path(tmp_dir)
            export_report(fmt="json")


if __name__ == "__main__":
    unittest.main()
