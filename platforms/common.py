"""
Shared utility functions for platform adapters.
"""

import os
import shutil
import subprocess
import tempfile
from typing import Tuple, List
from pathlib import Path


def run_command(cmd: List[str], timeout: int = 15) -> Tuple[int, str, str]:
    """
    Safely execute a system command with timeout and return (exit_code, stdout, stderr).
    """
    try:
        res = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            shell=False
        )
        return res.returncode, res.stdout.strip(), res.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", f"Command timed out after {timeout}s"
    except Exception as e:
        return -1, "", str(e)


def run_powershell(script: str, timeout: int = 15) -> Tuple[int, str, str]:
    """Execute a PowerShell command string on Windows."""
    cmd = ["powershell", "-NoProfile", "-NonInteractive", "-Command", script]
    return run_command(cmd, timeout=timeout)


def get_temp_directories() -> List[Path]:
    """Return standard system and user temporary directories."""
    dirs = []
    # Standard python tempdir
    dirs.append(Path(tempfile.gettempdir()))

    # Windows specific temp dirs
    if os.name == 'nt':
        win_temp = os.environ.get('WINDIR', 'C:\\Windows') + '\\Temp'
        if os.path.exists(win_temp):
            dirs.append(Path(win_temp))
        user_temp = os.environ.get('LOCALAPPDATA', '') + '\\Temp'
        if user_temp and os.path.exists(user_temp):
            dirs.append(Path(user_temp))
    else:
        # Linux / macOS
        for path_str in ['/tmp', '/var/tmp']:
            if os.path.exists(path_str):
                dirs.append(Path(path_str))
    
    # Deduplicate paths
    unique_dirs = []
    for d in dirs:
        resolved = d.resolve() if d.exists() else d
        if resolved not in unique_dirs:
            unique_dirs.append(resolved)
    return unique_dirs


def safe_remove_directory_contents(target_dir: Path) -> Tuple[int, int]:
    """
    Remove unlocked files and subdirectories inside target_dir.
    Returns (files_removed, bytes_freed).
    """
    removed_count = 0
    bytes_freed = 0

    if not target_dir.exists() or not target_dir.is_dir():
        return 0, 0

    for item in target_dir.glob('*'):
        try:
            if item.is_file() or item.is_symlink():
                size = item.stat().st_size
                item.unlink()
                removed_count += 1
                bytes_freed += size
            elif item.is_dir():
                # Try tree deletion or child deletion
                size = sum(f.stat().st_size for f in item.rglob('*') if f.is_file())
                shutil.rmtree(item, ignore_errors=True)
                removed_count += 1
                bytes_freed += size
        except Exception:
            # Locked files or permission errors are skipped safely
            continue

    return removed_count, bytes_freed
