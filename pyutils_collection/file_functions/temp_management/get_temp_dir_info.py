"""
Get information about system temporary directory.
"""

import os
import shutil
import stat
import tempfile
from pathlib import Path
from typing import Any


def get_temp_dir_info() -> dict[str, Any]:
    """
    Get information about the system temporary directory.

    Returns
    -------
    dict[str, Any]
        Dictionary containing temp directory information:
        - 'path': Path to temp directory
        - 'exists': Whether the directory exists
        - 'writable': Whether the directory is writable
        - 'total_files': Number of files in temp directory
        - 'total_size_bytes': Total size of all files in bytes
        - 'available_space_bytes': Available disk space in bytes

    Raises
    ------
    OSError
        If there's an error accessing the temporary directory.

    Examples
    --------
    >>> info = get_temp_dir_info()
    >>> info['path']
    '/tmp'
    >>> info['total_files']
    42
    >>> info['available_space_bytes']
    1073741824

    Notes
    -----
    The function scans all files in the temp directory which may be slow
    for directories with many files.
    Available space calculation may not be accurate on all systems.

    Complexity
    ----------
    Time: O(n), Space: O(1) where n is number of files in temp directory.
    """
    temp_dir_path = Path(tempfile.gettempdir())

    info: dict[str, Any] = {
        "path": str(temp_dir_path),
        "exists": False,
        "writable": False,
        "total_files": 0,
        "total_size_bytes": 0,
        "available_space_bytes": 0,
    }

    try:
        # Check if directory exists
        info["exists"] = temp_dir_path.exists() and temp_dir_path.is_dir()

        if info["exists"]:
            # Check if writable
            info["writable"] = os.access(temp_dir_path, os.W_OK)

            # Count files and calculate total size
            total_size = 0
            file_count = 0

            for item in temp_dir_path.rglob("*"):
                try:
                    file_info = item.stat()
                    if stat.S_ISREG(file_info.st_mode):
                        file_size = file_info.st_size
                        total_size += file_size
                        file_count += 1
                except OSError:
                    # Skip files that cannot be accessed
                    continue

            info["total_files"] = file_count
            info["total_size_bytes"] = total_size

            # Get available disk space
            try:
                statvfs_func = getattr(os, "statvfs", None)
                if statvfs_func is None:
                    raise AttributeError("statvfs is unavailable")
                statvfs = statvfs_func(temp_dir_path)
                available_bytes = statvfs.f_frsize * statvfs.f_bavail
                info["available_space_bytes"] = available_bytes
            except OSError, AttributeError:
                # Windows has no statvfs; disk_usage supports it natively.
                try:
                    info["available_space_bytes"] = shutil.disk_usage(
                        temp_dir_path
                    ).free
                except OSError, AttributeError:
                    info["available_space_bytes"] = 0

    except OSError as e:
        raise OSError(f"Error accessing temporary directory: {e}") from e

    return info


__all__ = ["get_temp_dir_info"]
