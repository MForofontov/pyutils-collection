"""
Create temporary directory with automatic cleanup.
"""

import shutil
import tempfile
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def create_temp_directory(
    suffix: str = "",
    prefix: str = "tmp",
    dir: str | Path | None = None,
    delete: bool = True,
) -> Generator[str]:
    """
    Create a temporary directory with automatic cleanup.

    Parameters
    ----------
    suffix : str, optional
        Directory suffix (by default "").
    prefix : str, optional
        Directory prefix (by default "tmp").
    dir : str | Path | None, optional
        Parent directory to create temp dir in, None for system temp (by default None).
    delete : bool, optional
        Whether to delete directory when context exits (by default True).

    Yields
    ------
    str
        Path to the temporary directory.

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    OSError
        If there's an error creating or managing the temporary directory.

    Examples
    --------
    >>> with create_temp_directory(suffix="_test") as temp_dir:
    ...     file_path = Path(temp_dir) / "test.txt"
    ...     file_path.write_text("test content")
    ...     print(f"Temp dir: {temp_dir}")
    Temp dir: /tmp/tmpxyz123_test

    >>> with create_temp_directory(delete=False) as temp_dir:
    ...     print(f"Persistent temp dir: {temp_dir}")
    Persistent temp dir: /tmp/tmpxyz123

    Notes
    -----
    The directory is created immediately and the path is yielded.
    If delete=True, the directory and all its contents are automatically removed.
    The directory is created with secure permissions (accessible by owner only).

    Complexity
    ----------
    Time: O(n), Space: O(1) where n is number of files to delete.
    """
    # Input validation
    if not isinstance(suffix, str):
        raise TypeError(f"suffix must be a string, got {type(suffix).__name__}")
    if not isinstance(prefix, str):
        raise TypeError(f"prefix must be a string, got {type(prefix).__name__}")
    if dir is not None and not isinstance(dir, (str, Path)):
        raise TypeError(
            f"dir must be a string, Path, or None, got {type(dir).__name__}"
        )
    if not isinstance(delete, bool):
        raise TypeError(f"delete must be a boolean, got {type(delete).__name__}")

    # Convert dir to string if it's a Path
    temp_parent_dir = str(dir) if dir is not None else None

    temp_dir_path = None

    try:
        # Create temporary directory
        temp_dir_path = tempfile.mkdtemp(
            suffix=suffix, prefix=prefix, dir=temp_parent_dir
        )

        yield temp_dir_path

    except OSError as e:
        raise OSError(f"Error creating temporary directory: {e}") from e
    finally:
        # Cleanup
        if temp_dir_path and delete and Path(temp_dir_path).exists():
            try:
                shutil.rmtree(temp_dir_path)
            except OSError:
                # Directory might have been already deleted
                pass


__all__ = ["create_temp_directory"]
