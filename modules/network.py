"""
Network Diagnostics module demonstrating Bitwise, Relational, and Logical Operators using Pure Standard Python 3.
"""

import socket
import time
import platform
import subprocess
from typing import List, Optional, Tuple
from core.models import NetworkInfo, NetworkInterfaceInfo


def ip_to_int(ip_str: str) -> int:
    """
    Demonstrates Bitwise Left Shift (<<) and Bitwise OR (|) operators to convert IPv4 to 32-bit int.
    """
    try:
        octets = [int(x) for x in ip_str.split(".")]
        if len(octets) == 4:
            return (octets[0] << 24) | (octets[1] << 16) | (octets[2] << 8) | octets[3]
    except Exception:
        pass
    return 0


def int_to_ip(ip_int: int) -> str:
    """
    Demonstrates Bitwise Right Shift (>>) and Bitwise AND (&) operators to convert 32-bit int to IPv4.
    """
    o1 = (ip_int >> 24) & 0xFF
    o2 = (ip_int >> 16) & 0xFF
    o3 = (ip_int >> 8) & 0xFF
    o4 = ip_int & 0xFF
    return f"{o1}.{o2}.{o3}.{o4}"


def calculate_network_broadcast(ip_str: str, netmask_str: str = "255.255.255.0") -> Tuple[str, str]:
    """
    Demonstrates Bitwise AND (&), Bitwise NOT (~), and Bitwise OR (|) to compute network & broadcast address.
    """
    ip_num = ip_to_int(ip_str)
    mask_num = ip_to_int(netmask_str)

    network_num = ip_num & mask_num
    broadcast_num = network_num | (~mask_num & 0xFFFFFFFF)

    return int_to_ip(network_num), int_to_ip(broadcast_num)


def check_internet_connection(host: str = "8.8.8.8", port: int = 53, timeout: float = 2.0) -> Tuple[bool, Optional[float]]:
    """Check connectivity via TCP socket (Pure stdlib)."""
    start_time = time.time()
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, port))
        sock.close()
        elapsed_ms = (time.time() - start_time) * 1000
        return True, round(elapsed_ms, 1)
    except Exception:
        return False, None


def check_dns_resolution(domain: str = "google.com") -> bool:
    """Test DNS resolution using socket.gethostbyname."""
    try:
        socket.gethostbyname(domain)
        return True
    except Exception:
        return False


def scan_open_ports(target_host: str = "127.0.0.1", ports: List[int] = None) -> List[int]:
    """Scan local host for open ports using standard sockets."""
    if ports is None:
        ports = [21, 22, 25, 53, 80, 110, 143, 443, 3306, 8080]

    open_ports = []
    for port in ports:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.15)
            res = s.connect_ex((target_host, port))
            if res == 0:
                open_ports.append(port)
            s.close()
        except Exception:
            pass
    return open_ports


def get_network_interfaces() -> List[NetworkInterfaceInfo]:
    """Gather primary network interface information (Pure stdlib)."""
    interfaces = []
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        interfaces.append(NetworkInterfaceInfo(
            name="Primary Adapter",
            is_up=True,
            ip_address=local_ip,
            mac_address="00:00:00:00:00:00"
        ))
    except Exception:
        pass
    return interfaces


def get_network_info(scan_ports: bool = False) -> NetworkInfo:
    """Gather NetworkInfo data."""
    internet_ok, ping_ms = check_internet_connection()
    dns_ok = check_dns_resolution()
    interfaces = get_network_interfaces()
    open_ports = scan_open_ports() if scan_ports else []

    return NetworkInfo(
        interfaces=interfaces,
        internet_ok=internet_ok,
        dns_ok=dns_ok,
        ping_ms=ping_ms,
        bytes_sent_mb=0.0,
        bytes_recv_mb=0.0,
        open_ports=open_ports
    )
