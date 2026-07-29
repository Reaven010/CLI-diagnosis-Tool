"""
System Information gathering module using Pure Standard Python 3.
"""

import sys
import os
import platform
import socket
import time
import shutil
from core.models import SystemInfo
from core.detector import get_platform_adapter


def get_uptime_seconds() -> float:
    """Calculate system uptime in seconds (Pure stdlib)."""
    try:
        if platform.system() == "Windows":
            import ctypes
            return float(ctypes.windll.kernel32.GetTickCount64()) / 1000.0
        elif platform.system() == "Linux" and os.path.exists("/proc/uptime"):
            with open("/proc/uptime", "r") as f:
                return float(f.readline().split()[0])
        elif platform.system() == "Darwin":
            res = subprocess.run(["sysctl", "-n", "kern.boottime"], capture_output=True, text=True)
            if res.returncode == 0:
                # e.g. { sec = 1710000000, usec = ... }
                line = res.stdout
                if "sec =" in line:
                    sec_val = int(line.split("sec =")[1].split(",")[0].strip())
                    return time.time() - sec_val
    except Exception:
        pass
    return 3600.0  # fallback 1 hour


def format_uptime(seconds: float) -> str:
    """Format uptime seconds into readable string."""
    if seconds <= 0:
        return "Unknown"

    mins, secs = divmod(int(seconds), 60)
    hours, mins = divmod(mins, 60)
    days, hours = divmod(hours, 24)

    parts = []
    if days > 0:
        parts.append(f"{days} day{'s' if days > 1 else ''}")
    if hours > 0:
        parts.append(f"{hours} hour{'s' if hours > 1 else ''}")
    if mins > 0:
        parts.append(f"{mins} min{'s' if mins > 1 else ''}")
    if not parts:
        parts.append(f"{secs} sec{'s' if secs > 1 else ''}")

    return ", ".join(parts)


def get_primary_ip_address() -> str:
    """Retrieve primary IPv4 address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(1.5)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return "127.0.0.1"


def get_cpu_model_name() -> str:
    """Fetch processor model name."""
    try:
        if platform.system() == "Windows":
            return platform.processor() or "x86_64 Processor"
        elif platform.system() == "Darwin":
            import subprocess
            res = subprocess.run(["sysctl", "-n", "machdep.cpu.brand_string"], capture_output=True, text=True)
            if res.returncode == 0 and res.stdout.strip():
                return res.stdout.strip()
        elif platform.system() == "Linux":
            with open("/proc/cpuinfo", "r") as f:
                for line in f:
                    if "model name" in line:
                        return line.split(":")[1].strip()
    except Exception:
        pass
    return platform.processor() or "Standard CPU"


def get_system_info() -> SystemInfo:
    """Gather complete static SystemInfo dataclass."""
    adapter = get_platform_adapter()
    total_ram_mb, _, _ = adapter.get_memory_metrics()
    total_ram_gb = total_ram_mb / 1024

    # Disk total via shutil.disk_usage (Pure stdlib)
    try:
        root_path = "C:\\" if platform.system() == "Windows" else "/"
        usage = shutil.disk_usage(root_path)
        total_disk_gb = usage.total / (1024 ** 3)
    except Exception:
        total_disk_gb = 0.0

    uptime_sec = get_uptime_seconds()
    uptime_str = format_uptime(uptime_sec)

    return SystemInfo(
        os_name=platform.system(),
        os_version=platform.version(),
        architecture=platform.machine(),
        kernel=platform.release(),
        hostname=socket.gethostname(),
        cpu_model=get_cpu_model_name(),
        total_ram_gb=round(total_ram_gb, 2),
        total_disk_gb=round(total_disk_gb, 2),
        uptime_seconds=uptime_sec,
        uptime_str=uptime_str,
        python_version=platform.python_version(),
        ip_address=get_primary_ip_address()
    )
