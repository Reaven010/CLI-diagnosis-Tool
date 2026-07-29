"""
macOS platform adapter implementation using 100% Pure Standard Python 3 libraries.
"""

import os
import sys
import signal
from typing import List, Tuple
from core.models import ServiceInfo, ProcessInfo
from platforms.base import PlatformAdapter
from platforms.common import run_command, get_temp_directories, safe_remove_directory_contents


class MacOSAdapter(PlatformAdapter):
    @property
    def os_name(self) -> str:
        return "macOS"

    def is_admin(self) -> bool:
        try:
            return os.geteuid() == 0
        except Exception:
            return False

    def get_memory_metrics(self) -> Tuple[float, float, float]:
        """Fetch macOS RAM stats via sysctl and vm_stat (Pure stdlib)."""
        total_mb = 8192.0
        c, out, _ = run_command(["sysctl", "-n", "hw.memsize"])
        if c == 0 and out:
            try:
                total_mb = float(out.strip()) / (1024 * 1024)
            except Exception:
                pass

        c2, out2, _ = run_command(["vm_stat"])
        used_mb = total_mb * 0.5
        if c2 == 0 and out2:
            try:
                page_size = 4096
                lines = out2.splitlines()
                pages_free = 0
                for line in lines:
                    if "Pages free:" in line:
                        pages_free = int(line.split(":")[1].replace(".", "").strip())
                free_mb = (pages_free * page_size) / (1024 * 1024)
                used_mb = max(0.0, total_mb - free_mb)
            except Exception:
                pass

        pct = (used_mb / total_mb) * 100 if total_mb > 0 else 50.0
        return round(total_mb, 1), round(used_mb, 1), round(pct, 1)

    def get_cpu_metrics(self) -> Tuple[float, int, int]:
        """Fetch macOS CPU load via sysctl (Pure stdlib)."""
        logical_cores = os.cpu_count() or 1
        physical_cores = max(1, logical_cores // 2)
        cpu_percent = 15.0

        c, out, _ = run_command(["sysctl", "-n", "vm.loadavg"])
        if c == 0 and out:
            try:
                # out format: { 1.50 1.20 1.10 }
                parts = out.replace("{", "").replace("}", "").strip().split()
                if parts:
                    load1 = float(parts[0])
                    cpu_percent = min(100.0, (load1 / logical_cores) * 100)
            except Exception:
                pass

        return round(cpu_percent, 1), physical_cores, logical_cores

    def get_process_list(self) -> List[ProcessInfo]:
        """Parse ps aux output (Pure stdlib)."""
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
        try:
            os.kill(pid, signal.SIGKILL)
            return True, f"Process PID {pid} killed."
        except Exception as e:
            return False, f"Failed to kill PID {pid}: {str(e)}"

    def get_services(self) -> List[ServiceInfo]:
        services = []
        code, out, _ = run_command(["launchctl", "list"])
        if code == 0 and out:
            lines = out.splitlines()
            for line in lines[1:]:
                parts = line.strip().split()
                if len(parts) >= 3:
                    pid_str, status_code, label = parts[0], parts[1], parts[2]
                    status = "running" if pid_str != "-" else "stopped"
                    services.append(ServiceInfo(
                        name=label,
                        display_name=label,
                        status=status
                    ))
        return services

    def control_service(self, service_name: str, action: str) -> Tuple[bool, str]:
        if action not in ["start", "stop", "restart"]:
            return False, f"Invalid action: {action}"

        if not self.is_admin():
            return False, "Root/sudo privileges are required to manage launchd services."

        if action == "start":
            code, out, err = run_command(["launchctl", "start", service_name])
        elif action == "stop":
            code, out, err = run_command(["launchctl", "stop", service_name])
        else:
            run_command(["launchctl", "stop", service_name])
            code, out, err = run_command(["launchctl", "start", service_name])

        if code == 0:
            return True, f"Service '{service_name}' {action}ed successfully."
        return False, f"Failed to {action} launchd service '{service_name}': {err or out}"

    def get_recent_logs(self, lines: int = 50) -> List[str]:
        code, out, err = run_command(["log", "show", "--style", "compact", "--last", "5m"])
        if code == 0 and out:
            all_lines = out.splitlines()
            return all_lines[-lines:]
        return [f"Unable to retrieve macOS logs: {err or 'Log command failed'}"]

    def flush_dns(self) -> Tuple[bool, str]:
        c1, o1, e1 = run_command(["dscacheutil", "-flushcache"])
        c2, o2, e2 = run_command(["killall", "-HUP", "mDNSResponder"])

        if c1 == 0 and c2 == 0:
            return True, "Flushed macOS DNS cache and restarted mDNSResponder."
        return False, f"DNS flush completed with errors: {e1 or e2}"

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
            return False, "Root privileges required to toggle network interfaces on macOS."

        code, out, err = run_command(["networksetup", "-setnetworkserviceenabled", "Wi-Fi", "off"])
        run_command(["networksetup", "-setnetworkserviceenabled", "Wi-Fi", "on"])
        if code == 0:
            return True, "Wi-Fi network interface toggled successfully."
        return False, f"Failed to restart Wi-Fi interface: {err or out}"

    def change_hostname(self, new_hostname: str) -> Tuple[bool, str]:
        if not self.is_admin():
            return False, "Root privileges required to change macOS hostname."

        run_command(["scutil", "--set", "ComputerName", new_hostname])
        run_command(["scutil", "--set", "LocalHostName", new_hostname])
        c, o, e = run_command(["scutil", "--set", "HostName", new_hostname])
        if c == 0:
            return True, f"macOS hostname updated to '{new_hostname}'."
        return False, f"Failed to update hostname: {e or o}"

    def cleanup_package_cache(self) -> Tuple[bool, str]:
        results = []
        if os.path.exists("/usr/local/bin/brew") or os.path.exists("/opt/homebrew/bin/brew"):
            c, _, _ = run_command(["brew", "cleanup"])
            if c == 0:
                results.append("Homebrew cleanup completed")

        c1, _, _ = run_command([sys.executable, "-m", "pip", "cache", "purge"])
        if c1 == 0:
            results.append("pip cache cleared")

        if results:
            return True, "Cleaned package caches: " + ", ".join(results)
        return True, "No package cache cleanup actions executed."
