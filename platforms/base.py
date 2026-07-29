"""
Abstract base platform adapter defining OS-specific interfaces.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple
from core.models import ServiceInfo, ProcessInfo


class PlatformAdapter(ABC):
    @property
    @abstractmethod
    def os_name(self) -> str:
        """Returns normalized OS name ('Windows', 'Linux', 'macOS')."""
        pass

    @abstractmethod
    def is_admin(self) -> bool:
        """Check if application is running with administrative/root privileges."""
        pass

    @abstractmethod
    def get_memory_metrics(self) -> Tuple[float, float, float]:
        """Returns (total_mb, used_mb, percent)."""
        pass

    @abstractmethod
    def get_cpu_metrics(self) -> Tuple[float, int, int]:
        """Returns (cpu_percent, physical_cores, logical_cores)."""
        pass

    @abstractmethod
    def get_process_list(self) -> List[ProcessInfo]:
        """Fetch list of running processes."""
        pass

    @abstractmethod
    def kill_process_by_pid(self, pid: int) -> Tuple[bool, str]:
        """Terminate process by PID."""
        pass

    @abstractmethod
    def get_services(self) -> List[ServiceInfo]:
        """Fetch list of system services."""
        pass

    @abstractmethod
    def control_service(self, service_name: str, action: str) -> Tuple[bool, str]:
        """Start, stop, or restart a system service. Returns (success, output/error_message)."""
        pass

    @abstractmethod
    def get_recent_logs(self, lines: int = 50) -> List[str]:
        """Retrieve recent system log lines."""
        pass

    @abstractmethod
    def flush_dns(self) -> Tuple[bool, str]:
        """Flush local DNS resolver cache."""
        pass

    @abstractmethod
    def clear_temp_files(self) -> Tuple[bool, str]:
        """Clear user and system temporary files safely."""
        pass

    @abstractmethod
    def restart_network(self) -> Tuple[bool, str]:
        """Restart default network adapter / service."""
        pass

    @abstractmethod
    def change_hostname(self, new_hostname: str) -> Tuple[bool, str]:
        """Change system hostname."""
        pass

    @abstractmethod
    def cleanup_package_cache(self) -> Tuple[bool, str]:
        """Clean up OS package manager cache (e.g. apt, yum, brew, winget)."""
        pass
