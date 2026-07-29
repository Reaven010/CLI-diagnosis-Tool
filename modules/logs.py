"""
Log Analysis module integrating with platform log subsystems.
"""

from typing import List
from platforms.base import PlatformAdapter


def fetch_system_logs(platform_adapter: PlatformAdapter, lines: int = 50) -> List[str]:
    """Retrieve recent system logs from Windows Event Log / systemd journal / macOS Console."""
    return platform_adapter.get_recent_logs(lines=lines)
