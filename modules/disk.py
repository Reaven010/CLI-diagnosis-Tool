"""
Disk Analysis and Monitoring module using Pure Standard Python 3 libraries.
"""

import os
import shutil
import platform
from pathlib import Path
from typing import List, Tuple
from core.models import DiskInfo, PartitionInfo, LargeFolderInfo
from platforms.common import get_temp_directories


def get_disk_partitions_info() -> Tuple[List[PartitionInfo], float]:
    """Retrieve primary mounted partition stats using shutil.disk_usage."""
    partitions = []
    max_percent = 0.0

    target_paths = []
    if platform.system() == "Windows":
        for drive in ["C:", "D:", "E:"]:
            dp = f"{drive}\\"
            if os.path.exists(dp):
                target_paths.append(dp)
    else:
        target_paths.append("/")

    for path_str in target_paths:
        try:
            usage = shutil.disk_usage(path_str)
            total_gb = usage.total / (1024 ** 3)
            used_gb = usage.used / (1024 ** 3)
            free_gb = usage.free / (1024 ** 3)
            pct = (usage.used / usage.total) * 100 if usage.total > 0 else 0.0

            if pct > max_percent:
                max_percent = pct

            partitions.append(PartitionInfo(
                device=path_str,
                mountpoint=path_str,
                fstype="NTFS" if platform.system() == "Windows" else "ext4",
                total_gb=round(total_gb, 2),
                used_gb=round(used_gb, 2),
                free_gb=round(free_gb, 2),
                percent=round(pct, 1)
            ))
        except Exception:
            continue

    return partitions, round(max_percent, 1)


def scan_temp_files() -> Tuple[float, int]:
    """Scan system and user temp directories to compute total size (MB) and file count."""
    temp_dirs = get_temp_directories()
    total_bytes = 0
    file_count = 0

    for td in temp_dirs:
        if not td.exists() or not td.is_dir():
            continue
        for root, _, files in os.walk(td):
            for f in files:
                file_count += 1
                try:
                    fp = os.path.join(root, f)
                    total_bytes += os.path.getsize(fp)
                except Exception:
                    pass

    total_mb = total_bytes / (1024 * 1024)
    return round(total_mb, 1), file_count


def scan_large_folders(min_size_mb: float = 500.0) -> List[LargeFolderInfo]:
    """Scan user directories for subfolders exceeding min_size_mb."""
    large_folders = []
    user_home = Path.home()
    target_bases = [
        user_home / "Downloads",
        user_home / "Documents",
        user_home / "Desktop"
    ]

    for base in target_bases:
        if not base.exists() or not base.is_dir():
            continue

        try:
            for child in base.iterdir():
                if child.is_dir() and not child.name.startswith('.'):
                    dir_bytes = 0
                    try:
                        for root, _, files in os.walk(child):
                            for f in files:
                                try:
                                    dir_bytes += os.path.getsize(os.path.join(root, f))
                                except Exception:
                                    pass
                    except Exception:
                        pass

                    size_mb = dir_bytes / (1024 * 1024)
                    if size_mb >= min_size_mb:
                        large_folders.append(LargeFolderInfo(
                            path=str(child),
                            size_mb=round(size_mb, 1)
                        ))
        except Exception:
            continue

    large_folders.sort(key=lambda x: x.size_mb, reverse=True)
    return large_folders[:10]


def analyze_downloads() -> Tuple[int, float, List[Tuple[str, float]]]:
    """Analyze user's Downloads directory."""
    downloads_dir = Path.home() / "Downloads"
    if not downloads_dir.exists() or not downloads_dir.is_dir():
        return 0, 0.0, []

    files_list = []
    total_bytes = 0
    file_count = 0

    try:
        for f in downloads_dir.glob("*"):
            if f.is_file():
                file_count += 1
                try:
                    sz = f.stat().st_size
                    total_bytes += sz
                    files_list.append((f.name, sz / (1024 * 1024)))
                except Exception:
                    pass
    except Exception:
        pass

    files_list.sort(key=lambda x: x[1], reverse=True)
    top_5 = [(name, round(size, 1)) for name, size in files_list[:5]]
    total_mb = total_bytes / (1024 * 1024)

    return file_count, round(total_mb, 1), top_5


def get_disk_info(scan_deep: bool = False) -> DiskInfo:
    """Gather complete DiskInfo structure."""
    partitions, max_pct = get_disk_partitions_info()
    temp_mb, temp_count = scan_temp_files()

    large_folders = []
    if scan_deep:
        large_folders = scan_large_folders()

    return DiskInfo(
        partitions=partitions,
        max_percent=max_pct,
        temp_size_mb=temp_mb,
        temp_file_count=temp_count,
        large_folders=large_folders
    )
