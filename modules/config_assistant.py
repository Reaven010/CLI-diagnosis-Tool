"""
Configuration Assistant module for safe maintenance and system configuration tasks.
"""

from typing import Tuple, Dict, Callable
from platforms.base import PlatformAdapter


class ConfigAssistant:
    def __init__(self, platform_adapter: PlatformAdapter):
        self.adapter = platform_adapter

    def flush_dns(self) -> Tuple[bool, str]:
        """Flush DNS Resolver Cache."""
        return self.adapter.flush_dns()

    def clear_temp_files(self) -> Tuple[bool, str]:
        """Clear user and system temporary files safely."""
        return self.adapter.clear_temp_files()

    def restart_network(self) -> Tuple[bool, str]:
        """Restart default network adapter / connection."""
        return self.adapter.restart_network()

    def change_hostname(self, new_hostname: str) -> Tuple[bool, str]:
        """Change system hostname."""
        if not new_hostname or len(new_hostname.strip()) == 0:
            return False, "Invalid hostname provided."
        return self.adapter.change_hostname(new_hostname.strip())

    def cleanup_package_cache(self) -> Tuple[bool, str]:
        """Clean package manager caches."""
        return self.adapter.cleanup_package_cache()

    def execute_action(self, action_name: str, **kwargs) -> Tuple[bool, str]:
        """Dispatch action execution by name."""
        actions: Dict[str, Callable[..., Tuple[bool, str]]] = {
            "flush_dns": self.flush_dns,
            "clear_temp_files": self.clear_temp_files,
            "restart_network": self.restart_network,
            "change_hostname": self.change_hostname,
            "cleanup_package_cache": self.cleanup_package_cache,
        }

        if action_name not in actions:
            return False, f"Unknown action: '{action_name}'."

        func = actions[action_name]
        try:
            return func(**kwargs)
        except Exception as e:
            return False, f"Execution error during '{action_name}': {str(e)}"
