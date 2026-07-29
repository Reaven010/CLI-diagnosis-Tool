"""
Unit tests for platform detector and platform adapters using Python standard library unittest.
"""

import unittest
from core.detector import get_platform_adapter
from platforms.base import PlatformAdapter
from platforms.windows import WindowsAdapter
from platforms.linux import LinuxAdapter
from platforms.macos import MacOSAdapter


class TestDetectorAndPlatforms(unittest.TestCase):
    def test_get_platform_adapter(self):
        adapter = get_platform_adapter()
        self.assertIsInstance(adapter, PlatformAdapter)
        self.assertIn(adapter.os_name, ["Windows", "Linux", "macOS"])

    def test_platform_adapters_instantiation(self):
        win = WindowsAdapter()
        lin = LinuxAdapter()
        mac = MacOSAdapter()

        self.assertEqual(win.os_name, "Windows")
        self.assertEqual(lin.os_name, "Linux")
        self.assertEqual(mac.os_name, "macOS")

    def test_platform_methods_signature(self):
        adapter = get_platform_adapter()
        self.assertIsInstance(adapter.is_admin(), bool)
        self.assertIsInstance(adapter.get_services(), list)
        self.assertIsInstance(adapter.get_recent_logs(lines=5), list)


if __name__ == "__main__":
    unittest.main()
