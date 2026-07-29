"""
Unit tests for Adaptive Recommendation Engine using unittest.
"""

import unittest
from modules.recommendations import RecommendationEngine
from modules.diagnostics import run_full_diagnostics


class TestRecommendations(unittest.TestCase):
    def test_recommendation_engine_evaluation(self):
        engine = RecommendationEngine()
        report = run_full_diagnostics()

        report.cpu.percent = 95.0
        report.memory.percent = 95.0
        report.disk.max_percent = 95.0
        report.network.dns_ok = False

        recs = engine.evaluate(report)
        self.assertGreaterEqual(len(recs), 3)

        rule_ids = [r.rule_id for r in recs]
        self.assertIn("cpu_high_usage", rule_ids)
        self.assertIn("memory_high_usage", rule_ids)
        self.assertIn("disk_space_critical", rule_ids)
        self.assertIn("dns_resolution_failure", rule_ids)


if __name__ == "__main__":
    unittest.main()
