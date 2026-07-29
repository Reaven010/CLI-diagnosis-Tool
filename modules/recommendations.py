"""
Adaptive Recommendation Engine evaluating system metrics against JSON rules.
"""

import json
import operator
from pathlib import Path
from typing import List, Dict, Any, Optional
from core.models import HealthReport, Recommendation


DEFAULT_RULES = [
    {
        "id": "cpu_high_usage",
        "category": "CPU",
        "metric": "cpu.percent",
        "operator": ">",
        "threshold": 85.0,
        "severity": "critical",
        "title": "High CPU Usage Detected",
        "description": "Total CPU usage exceeds 85%.",
        "recommendation": "Identify and close heavy background applications.",
        "action_code": "kill_heavy_proc"
    },
    {
        "id": "memory_high_usage",
        "category": "Memory",
        "metric": "memory.percent",
        "operator": ">",
        "threshold": 90.0,
        "severity": "critical",
        "title": "Critically High RAM Usage",
        "description": "Memory utilization is over 90%.",
        "recommendation": "Close unused memory-intensive programs.",
        "action_code": "kill_heavy_proc"
    },
    {
        "id": "disk_space_critical",
        "category": "Disk",
        "metric": "disk.max_percent",
        "operator": ">",
        "threshold": 90.0,
        "severity": "critical",
        "title": "Critical Low Disk Space",
        "description": "Disk space usage exceeds 90%.",
        "recommendation": "Clean system temporary files and package caches.",
        "action_code": "clear_temp_files"
    },
    {
        "id": "dns_resolution_failure",
        "category": "Network",
        "metric": "network.dns_ok",
        "operator": "==",
        "threshold": False,
        "severity": "critical",
        "title": "DNS Resolution Failed",
        "description": "Domain name resolution failed.",
        "recommendation": "Flush the DNS cache or verify DNS resolver settings.",
        "action_code": "flush_dns"
    },
    {
        "id": "internet_offline",
        "category": "Network",
        "metric": "network.internet_ok",
        "operator": "==",
        "threshold": False,
        "severity": "warning",
        "title": "No Internet Connectivity",
        "description": "Public ping checks failed.",
        "recommendation": "Restart your network adapter or check Wi-Fi connection.",
        "action_code": "restart_network"
    },
    {
        "id": "temp_files_accumulated",
        "category": "Disk",
        "metric": "disk.temp_files_mb",
        "operator": ">",
        "threshold": 1000.0,
        "severity": "warning",
        "title": "Accumulation of Temp Files",
        "description": "Over 1 GB of temp files found.",
        "recommendation": "Safely purge temporary directory contents.",
        "action_code": "clear_temp_files"
    }
]


OPERATORS = {
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le,
    "==": operator.eq,
    "!=": operator.ne,
}


class RecommendationEngine:
    def __init__(self, rules_file_path: Optional[Path] = None):
        self.rules = self.load_rules(rules_file_path)

    def load_rules(self, rules_file_path: Optional[Path]) -> List[Dict[str, Any]]:
        """Load rules from JSON configuration file."""
        if rules_file_path is None:
            rules_file_path = Path(__file__).parent.parent / "configs" / "rules.json"

        if rules_file_path.exists():
            try:
                with open(rules_file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return data.get("rules", DEFAULT_RULES)
            except Exception:
                pass
        return DEFAULT_RULES

    def extract_metric_value(self, report: HealthReport, metric_key: str) -> Any:
        """Extract value corresponding to dotted metric key e.g. 'cpu.percent'."""
        mapping = {
            "cpu.percent": report.cpu.percent,
            "memory.percent": report.memory.percent,
            "disk.max_percent": report.disk.max_percent,
            "disk.temp_files_mb": report.disk.temp_size_mb,
            "network.internet_ok": report.network.internet_ok,
            "network.dns_ok": report.network.dns_ok,
            "network.ping_ms": report.network.ping_ms,
        }
        return mapping.get(metric_key)

    def evaluate(self, report: HealthReport) -> List[Recommendation]:
        """Evaluate all rules against report metrics and return active recommendations."""
        recs: List[Recommendation] = []

        for rule in self.rules:
            rule_id = rule.get("id")
            metric_key = rule.get("metric")
            op_str = rule.get("operator")
            threshold = rule.get("threshold")

            val = self.extract_metric_value(report, metric_key)
            if val is None:
                continue

            op_func = OPERATORS.get(op_str)
            if not op_func:
                continue

            try:
                if op_func(val, threshold):
                    recs.append(Recommendation(
                        rule_id=rule_id,
                        title=rule.get("title", "Recommendation"),
                        description=rule.get("description", ""),
                        recommendation=rule.get("recommendation", ""),
                        severity=rule.get("severity", "warning"),
                        action_code=rule.get("action_code")
                    ))
            except Exception:
                continue

        # Sort recommendations by severity (critical > warning > info)
        severity_order = {"critical": 0, "warning": 1, "info": 2}
        recs.sort(key=lambda r: severity_order.get(r.severity, 3))

        return recs
