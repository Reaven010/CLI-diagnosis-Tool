"""
Report Generator module for exporting TXT, JSON, and HTML health reports.
"""

import json
from pathlib import Path
from typing import Tuple, Optional
from core.models import HealthReport


def generate_txt_report(report: HealthReport) -> str:
    """Generate human-readable text report."""
    lines = [
        "=" * 60,
        "          ADAPTIVE CLI SYSTEM HEALTH REPORT          ",
        "=" * 60,
        f"Timestamp    : {report.timestamp}",
        f"Health Score : {report.health_score} / 100",
        "-" * 60,
        "HARDWARE & SYSTEM INFORMATION",
        "-" * 60,
        f"OS           : {report.system_info.os_name} {report.system_info.os_version} ({report.system_info.architecture})",
        f"Hostname     : {report.system_info.hostname}",
        f"Kernel       : {report.system_info.kernel}",
        f"CPU Model    : {report.system_info.cpu_model}",
        f"Total RAM    : {report.system_info.total_ram_gb} GB",
        f"Total Disk   : {report.system_info.total_disk_gb} GB",
        f"Uptime       : {report.system_info.uptime_str}",
        f"Primary IP   : {report.system_info.ip_address}",
        f"Python Ver   : {report.system_info.python_version}",
        "-" * 60,
        "RESOURCE METRICS",
        "-" * 60,
        f"CPU Usage    : {report.cpu.percent}% ({report.cpu.logical_cores} Cores)",
        f"RAM Usage    : {report.memory.percent}% ({report.memory.used_mb} MB / {report.memory.total_mb} MB)",
        f"Max Disk Pct : {report.disk.max_percent}%",
        f"Temp Files   : {report.disk.temp_size_mb} MB ({report.disk.temp_file_count} files)",
        f"Internet OK  : {'Yes' if report.network.internet_ok else 'No'}",
        f"DNS OK       : {'Yes' if report.network.dns_ok else 'No'}",
        f"Ping Latency : {report.network.ping_ms} ms" if report.network.ping_ms else "Ping Latency : N/A",
        "-" * 60,
        f"PROBLEMS FOUND ({len(report.issues)})",
        "-" * 60,
    ]

    if report.issues:
        for i in report.issues:
            lines.append(f"[{i.severity.upper()}] [{i.category}] {i.title}: {i.description}")
    else:
        lines.append("No critical system issues detected.")

    lines.extend([
        "-" * 60,
        f"ADAPTIVE RECOMMENDATIONS ({len(report.recommendations)})",
        "-" * 60,
    ])

    if report.recommendations:
        for r in report.recommendations:
            lines.append(f"- [{r.severity.upper()}] {r.title}")
            lines.append(f"  Action : {r.recommendation}")
            if r.action_code:
                lines.append(f"  Fix Cmd: adaptive-cli config --action {r.action_code.replace('_', '-')}")
    else:
        lines.append("System running optimally. No recommendations required.")

    lines.append("=" * 60)
    return "\n".join(lines)


def generate_html_report(report: HealthReport) -> str:
    """Generate modern, styled HTML dashboard report."""
    score_color = "#10B981" if report.health_score >= 80 else ("#F59E0B" if report.health_score >= 60 else "#EF4444")
    
    issues_html = ""
    if report.issues:
        for issue in report.issues:
            badge_cls = "bg-danger" if issue.severity == "critical" else ("bg-warning" if issue.severity == "warning" else "bg-info")
            issues_html += f"""
            <tr class="border-b border-gray-700">
                <td class="py-3 px-4"><span class="badge {badge_cls}">{issue.severity.upper()}</span></td>
                <td class="py-3 px-4 text-gray-300 font-semibold">{issue.category}</td>
                <td class="py-3 px-4 text-white font-bold">{issue.title}</td>
                <td class="py-3 px-4 text-gray-300">{issue.description}</td>
            </tr>
            """
    else:
        issues_html = '<tr><td colspan="4" class="py-4 px-4 text-center text-emerald-400 font-semibold">No issues detected. System healthy!</td></tr>'

    recs_html = ""
    if report.recommendations:
        for rec in report.recommendations:
            badge_cls = "bg-danger" if rec.severity == "critical" else "bg-warning"
            action_btn = ""
            if rec.action_code:
                action_btn = f'<div class="mt-2 text-xs font-mono text-cyan-400 bg-gray-900 p-2 rounded">adaptive-cli config --action {rec.action_code.replace("_", "-")}</div>'
            recs_html += f"""
            <div class="bg-gray-800 p-4 rounded-xl border border-gray-700">
                <div class="flex items-center justify-between mb-2">
                    <span class="font-bold text-white text-lg">{rec.title}</span>
                    <span class="badge {badge_cls}">{rec.severity.upper()}</span>
                </div>
                <p class="text-gray-300 text-sm">{rec.recommendation}</p>
                {action_btn}
            </div>
            """
    else:
        recs_html = '<div class="p-4 bg-gray-800 rounded-xl text-center text-emerald-400">All rules passed. No active recommendations.</div>'

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>System Health Report - {report.system_info.hostname}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        body {{ background-color: #0F172A; color: #F8FAFC; font-family: system-ui, -apple-system, sans-serif; }}
        .badge {{ padding: 0.25rem 0.6rem; border-radius: 9999px; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; }}
        .bg-danger {{ background-color: #EF4444; color: white; }}
        .bg-warning {{ background-color: #F59E0B; color: black; }}
        .bg-info {{ background-color: #3B82F6; color: white; }}
        .metric-card {{ background: #1E293B; border: 1px solid #334155; border-radius: 0.75rem; padding: 1.25rem; }}
    </style>
</head>
<body class="p-6 md:p-12">
    <div class="max-w-6xl mx-auto space-y-8">
        <!-- Header -->
        <div class="flex flex-col md:flex-row justify-between items-start md:items-center bg-gray-800 p-6 rounded-2xl border border-gray-700 shadow-xl">
            <div>
                <h1 class="text-3xl font-extrabold tracking-tight text-white">System Diagnostics Report</h1>
                <p class="text-gray-400 text-sm mt-1">Generated: {report.timestamp} | Host: <span class="text-cyan-400">{report.system_info.hostname}</span></p>
            </div>
            <div class="mt-4 md:mt-0 flex items-center gap-4">
                <div class="text-right">
                    <div class="text-xs uppercase text-gray-400 font-bold">Health Score</div>
                    <div class="text-4xl font-black" style="color: {score_color};">{report.health_score}<span class="text-xl text-gray-500">/100</span></div>
                </div>
            </div>
        </div>

        <!-- Metrics Grid -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div class="metric-card">
                <div class="text-xs font-bold text-gray-400 uppercase">CPU Usage</div>
                <div class="text-3xl font-bold text-white mt-1">{report.cpu.percent}%</div>
                <div class="text-xs text-gray-400 mt-2">{report.cpu.logical_cores} Cores | {report.system_info.cpu_model[:25]}</div>
            </div>
            <div class="metric-card">
                <div class="text-xs font-bold text-gray-400 uppercase">RAM Utilization</div>
                <div class="text-3xl font-bold text-white mt-1">{report.memory.percent}%</div>
                <div class="text-xs text-gray-400 mt-2">{report.memory.used_mb} MB / {report.memory.total_mb} MB</div>
            </div>
            <div class="metric-card">
                <div class="text-xs font-bold text-gray-400 uppercase">Max Disk Usage</div>
                <div class="text-3xl font-bold text-white mt-1">{report.disk.max_percent}%</div>
                <div class="text-xs text-gray-400 mt-2">Temp: {report.disk.temp_size_mb} MB ({report.disk.temp_file_count} files)</div>
            </div>
            <div class="metric-card">
                <div class="text-xs font-bold text-gray-400 uppercase">Network Status</div>
                <div class="text-3xl font-bold text-emerald-400 mt-1">{"ONLINE" if report.network.internet_ok else "OFFLINE"}</div>
                <div class="text-xs text-gray-400 mt-2">DNS: {"OK" if report.network.dns_ok else "FAIL"} | Ping: {report.network.ping_ms or "N/A"} ms</div>
            </div>
        </div>

        <!-- System Details Card -->
        <div class="bg-gray-800 p-6 rounded-2xl border border-gray-700">
            <h2 class="text-xl font-bold text-white mb-4">Hardware & OS Specifications</h2>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                <div><span class="text-gray-400">OS Name:</span> <span class="font-semibold text-white">{report.system_info.os_name}</span></div>
                <div><span class="text-gray-400">OS Version:</span> <span class="font-semibold text-white">{report.system_info.os_version[:20]}</span></div>
                <div><span class="text-gray-400">Architecture:</span> <span class="font-semibold text-white">{report.system_info.architecture}</span></div>
                <div><span class="text-gray-400">Kernel:</span> <span class="font-semibold text-white">{report.system_info.kernel}</span></div>
                <div><span class="text-gray-400">Uptime:</span> <span class="font-semibold text-white">{report.system_info.uptime_str}</span></div>
                <div><span class="text-gray-400">Primary IP:</span> <span class="font-semibold text-cyan-400">{report.system_info.ip_address}</span></div>
                <div><span class="text-gray-400">Total RAM:</span> <span class="font-semibold text-white">{report.system_info.total_ram_gb} GB</span></div>
                <div><span class="text-gray-400">Python:</span> <span class="font-semibold text-white">{report.system_info.python_version}</span></div>
            </div>
        </div>

        <!-- Problems Found Table -->
        <div class="bg-gray-800 rounded-2xl border border-gray-700 overflow-hidden">
            <div class="p-6 border-b border-gray-700">
                <h2 class="text-xl font-bold text-white">Detected Issues</h2>
            </div>
            <div class="overflow-x-auto">
                <table class="w-full text-left text-sm">
                    <thead class="bg-gray-900 text-gray-400 uppercase text-xs">
                        <tr>
                            <th class="py-3 px-4">Severity</th>
                            <th class="py-3 px-4">Category</th>
                            <th class="py-3 px-4">Issue</th>
                            <th class="py-3 px-4">Description</th>
                        </tr>
                    </thead>
                    <tbody>
                        {issues_html}
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Recommendations -->
        <div class="bg-gray-800 p-6 rounded-2xl border border-gray-700 space-y-4">
            <h2 class="text-xl font-bold text-white">Adaptive Recommendations</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                {recs_html}
            </div>
        </div>
    </div>
</body>
</html>
"""
    return html


def save_report(report: HealthReport, fmt: str = "txt", output_dir: Optional[Path] = None) -> Tuple[Path, str]:
    """Save report to specified format ('txt', 'json', 'html') in reports directory."""
    if output_dir is None:
        output_dir = Path(__file__).parent.parent / "reports"

    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp_clean = report.timestamp.replace(":", "-").replace(" ", "_")
    filename = f"health_report_{timestamp_clean}.{fmt.lower()}"
    filepath = output_dir / filename

    fmt_lower = fmt.lower()
    if fmt_lower == "json":
        content = json.dumps(report.to_dict(), indent=2)
    elif fmt_lower == "html":
        content = generate_html_report(report)
    else:
        content = generate_txt_report(report)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return filepath, content
