"""
Platform detector factory.
"""

import sys
import platform
from platforms.base import PlatformAdapter
from platforms.windows import WindowsAdapter
from platforms.linux import LinuxAdapter
from platforms.macos import MacOSAdapter


def get_platform_adapter() -> PlatformAdapter:
    """
    Detect the running operating system and return the appropriate PlatformAdapter instance.
    """
    sys_platform = sys.platform.lower()
    os_type = platform.system().lower()

    if sys_platform.startswith("win") or os_type == "windows":
        return WindowsAdapter()
    elif sys_platform.startswith("darwin") or os_type == "darwin":
        return MacOSAdapter()
    elif sys_platform.startswith("linux") or os_type == "linux":
        return LinuxAdapter()
    else:
        # Default fallback to Linux interface for general POSIX
        return LinuxAdapter()
