"""
Linux platform adapter implementation using 100% Pure Standard Python 3 libraries.
"""

import os
import sys
import signal
from typing import List, Tuple
from core.models import ServiceInfo, ProcessInfo
from platforms.base import PlatformAdapter
from platforms.common import run_command, get_temp_directories, safe_remove_directory_contents


class LinuxAdapter(PlatformAdapter):
    @property
    def os_name(self) -> str:
        return "Linux"

    def is_admin(self) -> bool:
        try:
            return os.geteuid() == 0
        except Exception:
            return False

    def get_memory_metrics(self) -> Tuple[float, float, float]:
        """Parse /proc/meminfo for memory stats (Pure stdlib)."""
        total_kb = 0.0
        free_kb = 0.0
        available_kb = 0.0

        if os.path.exists("/proc/meminfo"):
            try:
                with open("/proc/meminfo", "r") as f:
                    for line in f:
                        parts = line.split(":")
                        if len(parts) == 2:
                            key = parts[0].strip()
                            val = parts[1].strip().split()[0]
                            if key == "MemTotal":
                                total_kb = float(val)
                            elif key == "MemFree":
                                free_kb = float(val)
                            elif key == "MemAvailable":
                                available_kb = float(val)
            except Exception:
                pass

        if total_kb > 0:
            avail_final = available_kb if available_kb > 0 else free_kb
            total_mb = total_kb / 1024
            used_mb = (total_kb - avail_final) / 1024
            pct = ((total_kb - avail_final) / total_kb) * 100
            return round(total_mb, 1), round(used_mb, 1), round(pct, 1)

        return 8000.0, 4000.0, 50.0

    def get_cpu_metrics(self) -> Tuple[float, int, int]:
        """Parse /proc/stat for CPU load (Pure stdlib)."""
        logical_cores = os.cpu_count() or 1
        physical_cores = max(1, logical_cores // 2)
        cpu_percent = 15.0

        if os.path.exists("/proc/stat"):
            try:
                with open("/proc/stat", "r") as f:
                    line = f.readline()
                    if line.startswith("cpu "):
                        parts = [float(x) for x in line.split()[1:]]
                        idle = parts[3]
                        total = sum(parts)
                        if total > 0:
                            cpu_percent = ((total - idle) / total) * 100
            except Exception:
                pass

        return round(cpu_percent, 1), physical_cores, logical_cores

    def get_process_list(self) -> List[ProcessInfo]:
        """Parse ps aux output for running processes (Pure stdlib)."""
        processes = []
        code, out, _ = run_command(["ps", "aux"])
        if code == 0 and out:
            lines = out.splitlines()
            for line in lines[1:]:
                parts = line.split(None, 10)
                if len(parts) >= 11:
                    user, pid_str, cpu_str, mem_str, vsz, rss, tty, stat, start, time_str, cmd = parts
                    try:
                        pid = int(pid_str)
                        cpu_p = float(cpu_str)
                        mem_p = float(mem_str)
                        mem_mb = float(rss) / 1024
                    except ValueError:
                        continue

                    processes.append(ProcessInfo(
                        pid=pid,
                        name=cmd.split()[0] if cmd else "unknown",
                        cpu_percent=cpu_p,
                        memory_percent=mem_p,
                        memory_mb=round(mem_mb, 1),
                        status="running",
                        username=user
                    ))
        return processes

    def kill_process_by_pid(self, pid: int) -> Tuple[bool, str]:
        """Kill process via os.kill SIGKILL (Pure stdlib)."""
        try:
            os.kill(pid, signal.SIGKILL)
            return True, f"Process PID {pid} was killed."
        except Exception as e:
            return False, f"Failed to kill PID {pid}: {str(e)}"

    def get_services(self) -> List[ServiceInfo]:
        services = []
        code, out, _ = run_command(["systemctl", "list-units", "--type=service", "--all", "--no-legend", "--no-pager"])
        if code == 0 and out:
            for line in out.splitlines():
                parts = line.strip().split(None, 4)
                if len(parts) >= 4:
                    name = parts[0].replace(".service", "")
                    active = parts[2]
                    status = "running" if active == "active" else "stopped"
                    desc = parts[4] if len(parts) > 4 else ""
                    services.append(ServiceInfo(
                        name=name,
                        display_name=name,
                        status=status,
                        description=desc
                    ))
        return services

    def control_service(self, service_name: str, action: str) -> Tuple[bool, str]:
        if action not in ["start", "stop", "restart"]:
            return False, f"Invalid action: {action}"

        if not self.is_admin():
            return False, "Root/sudo privileges are required to manage systemd services."

        full_service = service_name if service_name.endswith(".service") else f"{service_name}.service"
        code, out, err = run_command(["systemctl", action, full_service])
        if code == 0:
            return True, f"Service '{service_name}' {action}ed successfully."
        return False, f"Failed to {action} service '{service_name}': {err or out}"

    def get_recent_logs(self, lines: int = 50) -> List[str]:
        code, out, err = run_command(["journalctl", "-n", str(lines), "--no-pager"])
        if code == 0 and out:
            return out.splitlines()

        if os.path.exists("/var/log/syslog"):
            try:
                with open("/var/log/syslog", "r", encoding="utf-8", errors="ignore") as f:
                    log_lines = f.readlines()
                    return [l.strip() for l in log_lines[-lines:]]
            except Exception:
                pass

        return [f"Unable to retrieve Linux system logs: {err or 'journalctl unavailable'}"]

    def flush_dns(self) -> Tuple[bool, str]:
        code, out, err = run_command(["resolvectl", "flush-caches"])
        if code == 0:
            return True, "Flushed DNS cache via resolvectl."
        return False, "Failed to flush DNS cache (resolvectl not found or permission denied)."

    def clear_temp_files(self) -> Tuple[bool, str]:
        temp_dirs = get_temp_directories()
        total_files = 0
        total_bytes = 0
        for td in temp_dirs:
            count, size = safe_remove_directory_contents(td)
            total_files += count
            total_bytes += size

        mb_freed = round(total_bytes / (1024 * 1024), 2)
        return True, f"Cleared {total_files} temp files, freeing {mb_freed} MB of disk space."

    def restart_network(self) -> Tuple[bool, str]:
        if not self.is_admin():
            return False, "Root privileges are required to restart network service."

        code, out, err = run_command(["systemctl", "restart", "NetworkManager"])
        if code == 0:
            return True, "Restarted NetworkManager service successfully."
        return False, f"Failed to restart network manager: {err or out}"

    def change_hostname(self, new_hostname: str) -> Tuple[bool, str]:
        if not self.is_admin():
            return False, "Root privileges are required to change system hostname."

        code, out, err = run_command(["hostnamectl", "set-hostname", new_hostname])
        if code == 0:
            return True, f"Hostname changed to '{new_hostname}'."
        return False, f"Failed to change hostname: {err or out}"

    def cleanup_package_cache(self) -> Tuple[bool, str]:
        results = []
        if os.path.exists("/usr/bin/apt-get"):
            c, _, _ = run_command(["apt-get", "clean"])
            if c == 0:
                results.append("apt cache cleaned")

        c1, _, _ = run_command([sys.executable, "-m", "pip", "cache", "purge"])
        if c1 == 0:
            results.append("pip cache cleared")

        if results:
            return True, "Cleaned package caches: " + ", ".join(results)
        return True, "No package cache cleanup actions succeeded or required."
