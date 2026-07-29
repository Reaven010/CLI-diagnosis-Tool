"""
Data models for Adaptive CLI System Health & Diagnostics Tool.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class SystemInfo:
    os_name: str
    os_version: str
    architecture: str
    kernel: str
    hostname: str
    cpu_model: str
    total_ram_gb: float
    total_disk_gb: float
    uptime_seconds: float
    uptime_str: str
    python_version: str
    ip_address: str


@dataclass
class CPUInfo:
    percent: float
    per_core: List[float]
    physical_cores: int
    logical_cores: int
    frequency_mhz: Optional[float]
    load_avg: List[float]


@dataclass
class MemoryInfo:
    total_mb: float
    used_mb: float
    available_mb: float
    percent: float
    swap_total_mb: float
    swap_used_mb: float
    swap_percent: float


@dataclass
class PartitionInfo:
    device: str
    mountpoint: str
    fstype: str
    total_gb: float
    used_gb: float
    free_gb: float
    percent: float


@dataclass
class LargeFolderInfo:
    path: str
    size_mb: float


@dataclass
class DiskInfo:
    partitions: List[PartitionInfo]
    max_percent: float
    temp_size_mb: float
    temp_file_count: int
    large_folders: List[LargeFolderInfo] = field(default_factory=list)


@dataclass
class NetworkInterfaceInfo:
    name: str
    is_up: bool
    ip_address: Optional[str]
    mac_address: Optional[str]


@dataclass
class NetworkInfo:
    interfaces: List[NetworkInterfaceInfo]
    internet_ok: bool
    dns_ok: bool
    ping_ms: Optional[float]
    bytes_sent_mb: float
    bytes_recv_mb: float
    open_ports: List[int] = field(default_factory=list)


@dataclass
class ProcessInfo:
    pid: int
    name: str
    cpu_percent: float
    memory_percent: float
    memory_mb: float
    status: str
    username: Optional[str] = None


@dataclass
class ServiceInfo:
    name: str
    display_name: str
    status: str  # 'running', 'stopped', 'unknown'
    description: Optional[str] = None


@dataclass
class Issue:
    id: str
    title: str
    severity: str  # 'info', 'warning', 'critical'
    category: str
    description: str


@dataclass
class Recommendation:
    rule_id: str
    title: str
    description: str
    recommendation: str
    severity: str
    action_code: Optional[str] = None


@dataclass
class HealthReport:
    timestamp: str
    system_info: SystemInfo
    cpu: CPUInfo
    memory: MemoryInfo
    disk: DiskInfo
    network: NetworkInfo
    health_score: int  # 0 to 100
    issues: List[Issue] = field(default_factory=list)
    recommendations: List[Recommendation] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert health report to a nested dictionary suitable for JSON serialization."""
        return {
            "timestamp": self.timestamp,
            "health_score": self.health_score,
            "system_info": {
                "os_name": self.system_info.os_name,
                "os_version": self.system_info.os_version,
                "architecture": self.system_info.architecture,
                "kernel": self.system_info.kernel,
                "hostname": self.system_info.hostname,
                "cpu_model": self.system_info.cpu_model,
                "total_ram_gb": round(self.system_info.total_ram_gb, 2),
                "total_disk_gb": round(self.system_info.total_disk_gb, 2),
                "uptime_str": self.system_info.uptime_str,
                "python_version": self.system_info.python_version,
                "ip_address": self.system_info.ip_address,
            },
            "metrics": {
                "cpu_percent": self.cpu.percent,
                "cpu_cores": self.cpu.logical_cores,
                "memory_percent": self.memory.percent,
                "memory_used_mb": round(self.memory.used_mb, 1),
                "memory_total_mb": round(self.memory.total_mb, 1),
                "disk_max_percent": self.disk.max_percent,
                "temp_size_mb": round(self.disk.temp_size_mb, 1),
                "internet_ok": self.network.internet_ok,
                "dns_ok": self.network.dns_ok,
                "ping_ms": self.network.ping_ms,
            },
            "issues": [
                {
                    "id": i.id,
                    "title": i.title,
                    "severity": i.severity,
                    "category": i.category,
                    "description": i.description,
                }
                for i in self.issues
            ],
            "recommendations": [
                {
                    "rule_id": r.rule_id,
                    "title": r.title,
                    "severity": r.severity,
                    "recommendation": r.recommendation,
                    "action_code": r.action_code,
                }
                for r in self.recommendations
            ],
        }
