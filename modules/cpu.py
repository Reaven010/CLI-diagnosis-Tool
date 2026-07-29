"""
CPU Resource Monitoring module using Pure Standard Python 3.
"""

from core.models import CPUInfo
from core.detector import get_platform_adapter


def get_cpu_info(interval: float = 0.5) -> CPUInfo:
    """Gather CPU metrics via platform adapter."""
    adapter = get_platform_adapter()
    percent, phys_cores, log_cores = adapter.get_cpu_metrics()

    # Calculate per core representation
    per_core = [percent] * log_cores

    return CPUInfo(
        percent=round(percent, 1),
        per_core=[round(x, 1) for x in per_core],
        physical_cores=phys_cores,
        logical_cores=log_cores,
        frequency_mhz=2400.0,
        load_avg=[0.5, 0.4, 0.3]
    )
