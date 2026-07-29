"""
Service Manager module integrating with platform adapters.
"""

from typing import List, Tuple
from core.models import ServiceInfo
from platforms.base import PlatformAdapter


def list_services(platform_adapter: PlatformAdapter, filter_status: str = "all") -> List[ServiceInfo]:
    """Retrieve system services, filtered by status ('all', 'running', 'stopped')."""
    services = platform_adapter.get_services()
    if filter_status.lower() == "running":
        return [s for s in services if s.status.lower() == "running"]
    elif filter_status.lower() == "stopped":
        return [s for s in services if s.status.lower() == "stopped"]
    return services


def manage_service(platform_adapter: PlatformAdapter, service_name: str, action: str) -> Tuple[bool, str]:
    """Start, stop, or restart a named system service via platform adapter."""
    return platform_adapter.control_service(service_name, action)
