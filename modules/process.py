"""
Process Manager module using Pure Standard Python 3 libraries.
"""

from typing import List, Tuple
from core.models import ProcessInfo
from core.detector import get_platform_adapter


def get_running_processes(sort_by: str = "cpu", limit: int = 25) -> List[ProcessInfo]:
    """Enumerate running processes via platform adapter."""
    adapter = get_platform_adapter()
    processes = adapter.get_process_list()

    if sort_by == "memory":
        processes.sort(key=lambda p: p.memory_mb, reverse=True)
    elif sort_by == "pid":
        processes.sort(key=lambda p: p.pid)
    else:  # cpu
        processes.sort(key=lambda p: p.cpu_percent, reverse=True)

    return processes[:limit]


def kill_process(pid: int) -> Tuple[bool, str]:
    """Terminate or kill a process by PID."""
    adapter = get_platform_adapter()
    return adapter.kill_process_by_pid(pid)


def suspend_process(pid: int) -> Tuple[bool, str]:
    """Suspend a process (stub for stdlib compatibility)."""
    return False, f"Suspend action is OS restricted for PID {pid}."


def resume_process(pid: int) -> Tuple[bool, str]:
    """Resume a process (stub for stdlib compatibility)."""
    return False, f"Resume action is OS restricted for PID {pid}."
