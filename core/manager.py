"""
Central orchestrator managing platform adapters, diagnostics, rules engine, and configuration tasks.
"""

from typing import Tuple, Dict, Any, Optional
from core.detector import get_platform_adapter
from core.models import HealthReport, SystemInfo, CPUInfo, MemoryInfo, DiskInfo, NetworkInfo
from modules.system_info import get_system_info
from modules.cpu import get_cpu_info
from modules.memory import get_memory_info
from modules.disk import get_disk_info
from modules.network import get_network_info
from modules.diagnostics import run_full_diagnostics
from modules.recommendations import RecommendationEngine
from modules.config_assistant import ConfigAssistant
from modules.report import save_report


class SystemDiagnosticsManager:
    def __init__(self):
        self.adapter = get_platform_adapter()
        self.config_assistant = ConfigAssistant(self.adapter)
        self.recommendation_engine = RecommendationEngine()

    def get_system_info(self) -> SystemInfo:
        return get_system_info()

    def get_cpu_info(self, interval: float = 0.5) -> CPUInfo:
        return get_cpu_info(interval=interval)

    def get_memory_info(self) -> MemoryInfo:
        return get_memory_info()

    def get_disk_info(self, scan_deep: bool = False) -> DiskInfo:
        return get_disk_info(scan_deep=scan_deep)

    def get_network_info(self, scan_ports: bool = False) -> NetworkInfo:
        return get_network_info(scan_ports=scan_ports)

    def run_diagnostics(self) -> HealthReport:
        """Run full system diagnostics and attach active recommendations."""
        report = run_full_diagnostics()
        recs = self.recommendation_engine.evaluate(report)
        report.recommendations = recs
        return report

    def generate_report(self, fmt: str = "txt") -> Tuple[str, str]:
        """Generate and save report in specified format. Returns (file_path_str, report_content)."""
        report = self.run_diagnostics()
        filepath, content = save_report(report, fmt=fmt)
        return str(filepath), content

    def execute_maintenance(self, action_name: str, **kwargs) -> Tuple[bool, str]:
        """Safely execute system maintenance tasks."""
        return self.config_assistant.execute_action(action_name, **kwargs)
