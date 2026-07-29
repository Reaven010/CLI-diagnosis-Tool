"""
Unit tests for CPU, Memory, Disk, Network, Process, and Diagnostics modules using unittest.
"""

import unittest
from modules.cpu import get_cpu_info
from modules.memory import get_memory_info
from modules.disk import get_disk_info, analyze_downloads
from modules.network import get_network_info, ip_to_int, int_to_ip, calculate_network_broadcast
from modules.process import get_running_processes
from modules.diagnostics import calculate_health_score_and_issues, run_full_diagnostics
from core.models import CPUInfo, MemoryInfo, DiskInfo, NetworkInfo, HealthReport


class TestModules(unittest.TestCase):
    def test_cpu_module(self):
        cpu = get_cpu_info(interval=0.1)
        self.assertIsInstance(cpu, CPUInfo)
        self.assertTrue(0.0 <= cpu.percent <= 100.0)

    def test_memory_module(self):
        mem = get_memory_info()
        self.assertIsInstance(mem, MemoryInfo)
        self.assertGreater(mem.total_mb, 0)

    def test_disk_module(self):
        disk = get_disk_info(scan_deep=False)
        self.assertIsInstance(disk, DiskInfo)
        self.assertGreaterEqual(len(disk.partitions), 1)

        count, size, top = analyze_downloads()
        self.assertGreaterEqual(count, 0)

    def test_network_module_and_bitwise_operators(self):
        net = get_network_info(scan_ports=False)
        self.assertIsInstance(net, NetworkInfo)

        # Test Bitwise calculations
        ip_num = ip_to_int("192.168.1.10")
        self.assertIsInstance(ip_num, int)
        self.assertEqual(int_to_ip(ip_num), "192.168.1.10")

        net_addr, bcast_addr = calculate_network_broadcast("192.168.1.10", "255.255.255.0")
        self.assertEqual(net_addr, "192.168.1.0")
        self.assertEqual(bcast_addr, "192.168.1.255")

    def test_process_module(self):
        procs = get_running_processes(sort_by="cpu", limit=5)
        self.assertIsInstance(procs, list)
        if procs:
            self.assertGreaterEqual(procs[0].pid, 0)

    def test_diagnostics_health_score_calculation(self):
        score_healthy, issues_healthy = calculate_health_score_and_issues(
            cpu_percent=15.0,
            mem_percent=40.0,
            disk_max_percent=50.0,
            internet_ok=True,
            dns_ok=True,
            temp_mb=100.0
        )
        self.assertEqual(score_healthy, 100)

        score_unhealthy, issues_unhealthy = calculate_health_score_and_issues(
            cpu_percent=95.0,
            mem_percent=95.0,
            disk_max_percent=95.0,
            internet_ok=False,
            dns_ok=False,
            temp_mb=3000.0
        )
        self.assertLess(score_unhealthy, 50)

    def test_run_full_diagnostics(self):
        report = run_full_diagnostics()
        self.assertIsInstance(report, HealthReport)
        self.assertTrue(0 <= report.health_score <= 100)


if __name__ == "__main__":
    unittest.main()
