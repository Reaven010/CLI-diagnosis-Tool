"""
Pure Standard Python 3 Menu-Driven CLI Interface for Adaptive System Diagnostics Tool.
"""

import sys
import os
import time
from pathlib import Path
from typing import Optional, List

from core.manager import SystemDiagnosticsManager
from modules.process import get_running_processes, kill_process, suspend_process, resume_process
from modules.services import list_services, manage_service
from modules.logs import fetch_system_logs
from modules.disk import analyze_downloads
from modules.report import save_report

manager = SystemDiagnosticsManager()


def clear_screen():
    """Clear terminal screen across OS platforms (Pure stdlib)."""
    os.system("cls" if os.name == "nt" else "clear")


def print_banner(title: str):
    """Print ASCII border banner."""
    width = 75
    print("=" * width)
    print(f" {title.center(width - 2)} ")
    print("=" * width)


def print_ascii_table(headers: List[str], rows: List[List[str]]):
    """Render a clean ASCII table using standard string formatting and operators."""
    if not rows:
        print("  (No records found)")
        return

    # Calculate max column widths
    col_widths = [len(h) for h in headers]
    for row in rows:
        for idx, cell in enumerate(row):
            col_widths[idx] = max(col_widths[idx], len(str(cell)))

    # Format divider and header
    header_str = " | ".join(f"{headers[i].ljust(col_widths[i])}" for i in range(len(headers)))
    divider = "-+-".join("-" * col_widths[i] for i in range(len(headers)))

    print(header_str)
    print(divider)
    for row in rows:
        row_str = " | ".join(f"{str(row[i]).ljust(col_widths[i])}" for i in range(len(headers)))
        print(row_str)


def show_info():
    """Option 1: Display System Hardware and OS Information."""
    print_banner("SYSTEM INFORMATION OVERVIEW")
    info = manager.get_system_info()

    headers = ["Property", "Value"]
    rows = [
        ["Operating System", f"{info.os_name} {info.os_version}"],
        ["Architecture", info.architecture],
        ["Kernel Version", info.kernel],
        ["Hostname", info.hostname],
        ["CPU Model", info.cpu_model],
        ["Total RAM", f"{info.total_ram_gb} GB"],
        ["Total Disk Space", f"{info.total_disk_gb} GB"],
        ["System Uptime", info.uptime_str],
        ["Primary IP Address", info.ip_address],
        ["Python Version", info.python_version],
    ]
    print_ascii_table(headers, rows)


def live_monitor(interval: float = 1.0, count: int = 5):
    """Option 2: Live Resource Monitor."""
    print_banner("LIVE RESOURCE MONITOR (Ctrl+C to Stop)")
    iterations = 0
    try:
        while True:
            cpu = manager.get_cpu_info(interval=0.2)
            mem = manager.get_memory_info()
            disk = manager.get_disk_info(scan_deep=False)
            net = manager.get_network_info(scan_ports=False)

            headers = ["Resource", "Usage Metrics", "Status Bar"]
            
            # Simple bar rendering
            cpu_bar = "[" + "#" * int(cpu.percent / 5) + "-" * (20 - int(cpu.percent / 5)) + f"] {cpu.percent}%"
            mem_bar = "[" + "#" * int(mem.percent / 5) + "-" * (20 - int(mem.percent / 5)) + f"] {mem.percent}%"
            disk_bar = "[" + "#" * int(disk.max_percent / 5) + "-" * (20 - int(disk.max_percent / 5)) + f"] {disk.max_percent}%"

            net_status = "ONLINE" if net.internet_ok else "OFFLINE"
            ping_str = f"{net.ping_ms} ms" if net.ping_ms else "N/A"

            rows = [
                ["CPU Load", f"{cpu.percent}% ({cpu.logical_cores} Cores)", cpu_bar],
                ["RAM Utilization", f"{mem.used_mb:.1f} MB / {mem.total_mb:.1f} MB", mem_bar],
                ["Max Disk Usage", f"{disk.max_percent}% Max Partition", disk_bar],
                ["Network", f"DNS: {'OK' if net.dns_ok else 'FAIL'} | Ping: {ping_str}", f"Status: {net_status}"],
            ]

            clear_screen()
            print_banner("LIVE RESOURCE MONITOR")
            print_ascii_table(headers, rows)

            iterations += 1
            if count > 0 and iterations >= count:
                break
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nMonitoring stopped.")


def list_procs(sort_by: str = "cpu", limit: int = 15):
    """Option 3: Process Manager."""
    print_banner(f"TOP {limit} PROCESSES (Sorted by {sort_by.upper()})")
    procs = get_running_processes(sort_by=sort_by, limit=limit)

    headers = ["PID", "Name", "CPU %", "Memory (MB)", "Memory %", "Status"]
    rows = []
    for p in procs:
        rows.append([
            str(p.pid),
            p.name[:25],
            f"{p.cpu_percent:.1f}%",
            f"{p.memory_mb:.1f}",
            f"{p.memory_percent:.1f}%",
            p.status
        ])
    print_ascii_table(headers, rows)


def analyze_disk(scan_deep: bool = False):
    """Option 4: Disk & Storage Analysis."""
    print_banner("DISK PARTITIONS & STORAGE ANALYSIS")
    disk_info = manager.get_disk_info(scan_deep=scan_deep)
    dl_count, dl_size_mb, dl_top = analyze_downloads()

    headers = ["Device", "Mountpoint", "Total (GB)", "Used (GB)", "Free (GB)", "Usage %"]
    rows = []
    for p in disk_info.partitions:
        rows.append([p.device, p.mountpoint, f"{p.total_gb:.1f}", f"{p.used_gb:.1f}", f"{p.free_gb:.1f}", f"{p.percent:.1f}%"])
    print_ascii_table(headers, rows)

    print("\n--- STORAGE CLEANLINESS SUMMARY ---")
    print(f"Temporary Files Accumulated: {disk_info.temp_size_mb:.1f} MB ({disk_info.temp_file_count} files)")
    print(f"Downloads Folder Contents  : {dl_count} files ({dl_size_mb:.1f} MB total)")

    if dl_top:
        print("\nTop Files in Downloads:")
        for fname, fsize in dl_top:
            print(f" - {fname} ({fsize:.1f} MB)")


def check_network(scan_ports: bool = False):
    """Option 5: Network Diagnostics & Port Scanner."""
    print_banner("NETWORK DIAGNOSTICS & INTERFACE CHECKS")
    net = manager.get_network_info(scan_ports=scan_ports)

    print(f"Internet Connectivity : {'PASS (Online)' if net.internet_ok else 'FAIL (Offline)'}")
    print(f"DNS Resolution       : {'PASS (Resolved)' if net.dns_ok else 'FAIL (Resolution Error)'}")
    print(f"Ping Latency         : {net.ping_ms or 'N/A'} ms\n")

    headers = ["Interface", "Status", "IP Address", "MAC Address"]
    rows = []
    for iface in net.interfaces:
        rows.append([iface.name, "UP" if iface.is_up else "DOWN", iface.ip_address or "N/A", iface.mac_address or "N/A"])
    print_ascii_table(headers, rows)

    if scan_ports:
        port_str = ", ".join(map(str, net.open_ports)) if net.open_ports else "None detected"
        print(f"\nOpen Local Service Ports: {port_str}")


def show_services(filter_status: str = "all"):
    """Option 6: System Service Manager."""
    print_banner(f"SYSTEM SERVICES ({manager.adapter.os_name.upper()}) - FILTER: {filter_status.upper()}")
    services = list_services(manager.adapter, filter_status=filter_status)

    headers = ["Service Name", "Display Name", "Status"]
    rows = []
    for s in services[:25]:
        rows.append([s.name[:25], s.display_name[:35], s.status.upper()])
    print_ascii_table(headers, rows)

    if len(services) > 25:
        print(f"\n... and {len(services) - 25} more services.")


def view_logs(lines: int = 30):
    """Option 7: System Log Inspector."""
    print_banner(f"RECENT {lines} SYSTEM LOG LINES ({manager.adapter.os_name.upper()})")
    log_lines = fetch_system_logs(manager.adapter, lines=lines)
    for line in log_lines:
        print(line)


def diagnose_system():
    """Option 8: System Health Diagnostics & Score."""
    print_banner("SYSTEM HEALTH DIAGNOSTICS SCAN")
    report = manager.run_diagnostics()

    print(f"OVERALL SYSTEM HEALTH SCORE: {report.health_score} / 100")
    print(f"TOTAL ACTIVE ISSUES FOUND  : {len(report.issues)}\n")

    if report.issues:
        headers = ["Severity", "Category", "Issue Title", "Description"]
        rows = []
        for issue in report.issues:
            rows.append([issue.severity.upper(), issue.category, issue.title, issue.description])
        print_ascii_table(headers, rows)
    else:
        print("[OK] No critical system issues detected. System is running healthy!")


def get_recommendations():
    """Option 9: Adaptive Recommendations Engine."""
    print_banner("ADAPTIVE SYSTEM RECOMMENDATIONS")
    report = manager.run_diagnostics()
    recs = report.recommendations

    if not recs:
        print("[OK] System parameters are within normal thresholds. No active recommendations.")
        return

    headers = ["Severity", "Title", "Recommendation", "Suggested Fix Action"]
    rows = []
    for r in recs:
        action_str = f"config action: {r.action_code.replace('_', '-')}" if r.action_code else "N/A"
        rows.append([r.severity.upper(), r.title, r.recommendation, action_str])
    print_ascii_table(headers, rows)


def export_report(fmt: str = "html"):
    """Option 10: Health Report Export."""
    print_banner(f"EXPORT SYSTEM HEALTH REPORT ({fmt.upper()})")
    filepath, _ = manager.generate_report(fmt=fmt)
    print(f"[OK] Health report successfully generated and saved to:")
    print(f"  --> {filepath}")


def config_assistant():
    """Option 11: Configuration & Maintenance Assistant."""
    print_banner("CONFIGURATION & MAINTENANCE ASSISTANT")
    print("Available Maintenance Actions:")
    print(" 1. Flush DNS Resolver Cache")
    print(" 2. Clear System Temporary Files")
    print(" 3. Restart Network Adapter")
    print(" 4. Change System Hostname")
    print(" 5. Cleanup Package Manager Caches")

    choice = input("\nSelect action number [1-5]: ").strip()
    act_map = {
        "1": "flush_dns",
        "2": "clear_temp_files",
        "3": "restart_network",
        "4": "change_hostname",
        "5": "cleanup_package_cache"
    }

    if choice not in act_map:
        print("Invalid action selected.")
        return

    action_name = act_map[choice]
    kwargs = {}
    if action_name == "change_hostname":
        new_name = input("Enter new computer hostname: ").strip()
        kwargs["new_hostname"] = new_name

    confirm = input(f"Confirm execution of '{action_name}'? (y/n): ").strip().lower()
    if confirm == "y":
        ok, msg = manager.execute_maintenance(action_name, **kwargs)
        status_str = "SUCCESS" if ok else "FAILED"
        print(f"[{status_str}] {msg}")
    else:
        print("Operation cancelled by user.")


def interactive_menu():
    """Main interactive menu-driven program loop using standard Python 3 input/print."""
    while True:
        clear_screen()
        print_banner("ADAPTIVE CLI SYSTEM HEALTH & DIAGNOSTICS TOOL")
        print("  1. System Information Overview")
        print("  2. Live Resource Monitor")
        print("  3. Process Manager (List & Control Processes)")
        print("  4. Disk & Storage Analysis")
        print("  5. Network Diagnostics & Open Port Scanner")
        print("  6. System Service Manager")
        print("  7. System Log Inspector")
        print("  8. Run Full System Health Diagnostics")
        print("  9. View Adaptive Recommendations")
        print(" 10. Export System Health Report (TXT / JSON / HTML)")
        print(" 11. Safe Configuration & Maintenance Assistant")
        print("  0. Exit Application")
        print("=" * 75)

        choice = input("\nSelect an option [0-11]: ").strip()

        # Demonstrating Control Flow & Relational Operators (==)
        if choice == "0":
            print("\nExiting Adaptive CLI. Goodbye!")
            break
        elif choice == "1":
            show_info()
        elif choice == "2":
            live_monitor(interval=1.0, count=5)
        elif choice == "3":
            print("\n--- PROCESS MANAGER ---")
            print("1. List Top CPU Processes")
            print("2. List Top Memory Processes")
            print("3. Kill Process by PID")
            sub = input("Select choice [1-3]: ").strip()
            if sub == "1":
                list_procs(sort_by="cpu", limit=15)
            elif sub == "2":
                list_procs(sort_by="memory", limit=15)
            elif sub == "3":
                pid_str = input("Enter PID to terminate: ").strip()
                if pid_str.isdigit():
                    pid_val = int(pid_str)
                    ok, msg = kill_process(pid_val)
                    print(f"[{'SUCCESS' if ok else 'FAILED'}] {msg}")
        elif choice == "4":
            deep_in = input("Perform deep scan for large subfolders (>500 MB)? (y/n): ").strip().lower()
            analyze_disk(scan_deep=(deep_in == "y"))
        elif choice == "5":
            ports_in = input("Perform local open port scan? (y/n): ").strip().lower()
            check_network(scan_ports=(ports_in == "y"))
        elif choice == "6":
            show_services(filter_status="all")
        elif choice == "7":
            lines_in = input("Number of log lines to view [default 30]: ").strip()
            num_lines = int(lines_in) if lines_in.isdigit() else 30
            view_logs(lines=num_lines)
        elif choice == "8":
            diagnose_system()
        elif choice == "9":
            get_recommendations()
        elif choice == "10":
            fmt_in = input("Select format (html/json/txt) [default html]: ").strip().lower()
            fmt_choice = fmt_in if fmt_in in ["html", "json", "txt"] else "html"
            export_report(fmt=fmt_choice)
        elif choice == "11":
            config_assistant()
        else:
            print("Invalid selection. Please enter a number between 0 and 11.")

        input("\nPress Enter to return to main menu...")


if __name__ == "__main__":
    interactive_menu()
