"""
System Diagnostics module compiling hardware metrics using Relational, Logical, and Bitwise Operators.
"""

from datetime import datetime
from typing import List, Tuple
from core.models import HealthReport, Issue
from modules.system_info import get_system_info
from modules.cpu import get_cpu_info
from modules.memory import get_memory_info
from modules.disk import get_disk_info
from modules.network import get_network_info


def calculate_health_score_and_issues(
    cpu_percent: float,
    mem_percent: float,
    disk_max_percent: float,
    internet_ok: bool,
    dns_ok: bool,
    temp_mb: float
) -> Tuple[int, List[Issue]]:
    """
    Calculate health score (0-100) using Relational, Logical, and Bitwise operators.
    """
    score = 100
    issues: List[Issue] = []

    # Relational & Logical Operators Demonstration (>=, and, not)
    if cpu_percent >= 90.0:
        score -= 25
        issues.append(Issue(
            id="cpu_critical",
            title="CPU Usage Critical",
            severity="critical",
            category="CPU",
            description=f"CPU load is extremely high at {cpu_percent}%."
        ))
    elif cpu_percent >= 75.0 and cpu_percent < 90.0:
        score -= 10
        issues.append(Issue(
            id="cpu_high",
            title="CPU Usage High",
            severity="warning",
            category="CPU",
            description=f"CPU usage is elevated at {cpu_percent}%."
        ))

    # Memory check using relational operator (>=)
    if mem_percent >= 90.0:
        score -= 25
        issues.append(Issue(
            id="mem_critical",
            title="RAM Usage Critical",
            severity="critical",
            category="Memory",
            description=f"RAM utilization is critical at {mem_percent}%."
        ))
    elif mem_percent >= 75.0 and mem_percent < 90.0:
        score -= 10
        issues.append(Issue(
            id="mem_high",
            title="RAM Usage High",
            severity="warning",
            category="Memory",
            description=f"RAM utilization is high at {mem_percent}%."
        ))

    # Disk check
    if disk_max_percent >= 90.0:
        score -= 25
        issues.append(Issue(
            id="disk_critical",
            title="Disk Space Low",
            severity="critical",
            category="Disk",
            description=f"Primary partition space is critically low ({disk_max_percent}% full)."
        ))
    elif disk_max_percent >= 80.0 and disk_max_percent < 90.0:
        score -= 10
        issues.append(Issue(
            id="disk_warning",
            title="Disk Space Warning",
            severity="warning",
            category="Disk",
            description=f"Primary partition space usage is elevated ({disk_max_percent}% full)."
        ))

    # Network check using logical NOT and OR
    if not internet_ok or not dns_ok:
        if not internet_ok:
            score -= 30
            issues.append(Issue(
                id="net_offline",
                title="No Internet Connection",
                severity="critical",
                category="Network",
                description="System is unable to reach public network host."
            ))
        if not dns_ok and internet_ok:
            score -= 20
            issues.append(Issue(
                id="net_dns_fail",
                title="DNS Resolution Failure",
                severity="warning",
                category="Network",
                description="System cannot resolve domain names."
            ))

    # Bitwise Operator Demonstration (&) for flag validation
    flags = 0b101  # Bit 0: Check temp, Bit 2: Validated
    if (flags & 0b001) != 0 and temp_mb >= 2000.0:
        score -= 5
        issues.append(Issue(
            id="temp_accumulation",
            title="Temp Files Accumulated",
            severity="info",
            category="Disk",
            description=f"Temporary files occupy {round(temp_mb/1024, 1)} GB of space."
        ))

    final_score = max(0, min(100, score))
    return final_score, issues


def run_full_diagnostics() -> HealthReport:
    """Execute complete diagnostic scan across system subsystems."""
    sys_info = get_system_info()
    cpu_info = get_cpu_info(interval=0.2)
    mem_info = get_memory_info()
    disk_info = get_disk_info(scan_deep=False)
    net_info = get_network_info(scan_ports=False)

    score, issues = calculate_health_score_and_issues(
        cpu_percent=cpu_info.percent,
        mem_percent=mem_info.percent,
        disk_max_percent=disk_info.max_percent,
        internet_ok=net_info.internet_ok,
        dns_ok=net_info.dns_ok,
        temp_mb=disk_info.temp_size_mb
    )

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return HealthReport(
        timestamp=now_str,
        system_info=sys_info,
        cpu=cpu_info,
        memory=mem_info,
        disk=disk_info,
        network=net_info,
        health_score=score,
        issues=issues,
        recommendations=[]
    )
