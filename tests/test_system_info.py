"""
Unit tests for system_info module using Python standard library unittest.
"""

import unittest
from modules.system_info import get_system_info, format_uptime
from core.models import SystemInfo


class TestSystemInfo(unittest.TestCase):
    def test_format_uptime(self):
        self.assertEqual(format_uptime(45), "45 secs")
        self.assertEqual(format_uptime(120), "2 mins")
        self.assertEqual(format_uptime(3665), "1 hour, 1 min")
        self.assertEqual(format_uptime(90000), "1 day, 1 hour")
        self.assertEqual(format_uptime(0), "Unknown")

    def test_get_system_info(self):
        info = get_system_info()
        self.assertIsInstance(info, SystemInfo)
        self.assertNotEqual(info.os_name, "")
        self.assertNotEqual(info.hostname, "")
        self.assertGreaterEqual(info.total_ram_gb, 0.0)


if __name__ == "__main__":
    unittest.main()
