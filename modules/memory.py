"""
Memory Resource Monitoring module using Pure Standard Python 3.
"""

from core.models import MemoryInfo
from core.detector import get_platform_adapter


def get_memory_info() -> MemoryInfo:
    """Gather Virtual Memory stats via platform adapter."""
    adapter = get_platform_adapter()
    total_mb, used_mb, pct = adapter.get_memory_metrics()
    avail_mb = max(0.0, total_mb - used_mb)

    return MemoryInfo(
        total_mb=round(total_mb, 1),
        used_mb=round(used_mb, 1),
        available_mb=round(avail_mb, 1),
        percent=round(pct, 1),
        swap_total_mb=0.0,
        swap_used_mb=0.0,
        swap_percent=0.0
    )
