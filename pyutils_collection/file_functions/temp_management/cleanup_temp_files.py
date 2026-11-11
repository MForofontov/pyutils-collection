"""
Cleanup temporary files and directories by age or pattern.
"""

import math
import stat
import time
from pathlib import Path


def cleanup_temp_files(
    temp_dir: str | Path | None = None,
    max_age_hours: float = 24.0,
    pattern: str = "*",
    dry_run: bool = False,
) -> list[str]:
    """
    Clean up temporary files older than specified age.

    Parameters
    ----------
    temp_dir : str | Path | None, optional
        Directory to clean, None for system temp directory (by default None).
    max_age_hours : float, optional
        Maximum age in hours before files are deleted (by default 24.0).
    pattern : str, optional
        Relative filename pattern to match for deletion (by default "*").
        Absolute patterns and parent-directory traversal are rejected.
    dry_run : bool, optional
        If True, return list of files that would be deleted without deleting (by default False).

    Returns
    -------
    list[str]
        List of files that were deleted (or would be deleted in dry run).

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If directory doesn't exist or max_age_hours is invalid.
    OSError
        If there's an error accessing or deleting files.

    Examples
    --------
    >>> cleanup_temp_files(max_age_hours=1.0)
    ['/tmp/old_file1.tmp', '/tmp/old_file2.tmp']
    >>> cleanup_temp_files(pattern="*.log", dry_run=True)
    ['/tmp/old_app.log', '/tmp/old_debug.log']

    Notes
    -----
    Only files (not directories) are deleted by default.
    The function uses modification time to determine file age.
    Be careful with the pattern to avoid deleting system files.

    Complexity
    ----------
    Time: O(n), Space: O(m) where n is total files and m is matching files.
    """
    # Input validation
    if temp_dir is not None and not isinstance(temp_dir, (str, Path)):
        raise TypeError(
            f"temp_dir must be a string, Path, or None, got {type(temp_dir).__name__}"
        )
    if not isinstance(max_age_hours, (int, float)) or isinstance(max_age_hours, bool):
        raise TypeError(
            f"max_age_hours must be a number, got {type(max_age_hours).__name__}"
        )
    if not isinstance(pattern, str):
        raise TypeError(f"pattern must be a string, got {type(pattern).__name__}")
    if not isinstance(dry_run, bool):
        raise TypeError(f"dry_run must be a boolean, got {type(dry_run).__name__}")
    if not pattern or Path(pattern).anchor or ".." in Path(pattern).parts:
        raise ValueError("pattern must be a nonempty relative path without '..'")
    if not math.isfinite(max_age_hours) or max_age_hours <= 0:
        raise ValueError(
            f"max_age_hours must be positive and finite, got {max_age_hours}"
        )

    # Use system temp directory if none specified
    if temp_dir is None:
        import tempfile

        temp_dir = tempfile.gettempdir()

    # Convert to Path object
    dir_path = Path(temp_dir)

    # Validate directory exists
    if not dir_path.exists():
        raise ValueError(f"Directory does not exist: {temp_dir}")
    if not dir_path.is_dir():
        raise ValueError(f"Path is not a directory: {temp_dir}")

    # Calculate cutoff time
    current_time = time.time()
    cutoff_time = current_time - (max_age_hours * 3600)  # Convert hours to seconds

    deleted_files: list[str] = []

    try:
        # Find matching files
        for file_path in dir_path.glob(pattern):
            try:
                file_info = file_path.stat()
                if stat.S_ISREG(file_info.st_mode):
                    file_mtime = file_info.st_mtime

                    if file_mtime < cutoff_time:
                        if dry_run:
                            deleted_files.append(str(file_path))
                        else:
                            file_path.unlink()
                            deleted_files.append(str(file_path))

            except OSError:
                # Skip files that cannot be accessed or deleted
                continue

    except OSError as e:
        raise OSError(f"Error accessing directory {temp_dir}: {e}") from e

    return deleted_files


__all__ = ["cleanup_temp_files"]
