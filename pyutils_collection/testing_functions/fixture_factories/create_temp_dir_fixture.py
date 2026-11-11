"""
Create temporary directory fixture for testing.
"""

import tempfile
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def create_temp_dir_fixture(
    files: dict[str, str] | None = None,
) -> Generator[Path]:
    """
    Create a temporary directory fixture with optional files.

    Parameters
    ----------
    files : dict[str, str] | None, optional
        Dictionary mapping filenames to contents (by default None).

    Yields
    ------
    Path
        Path to temporary directory.

    Raises
    ------
    TypeError
        If files is not a dict or None.

    Examples
    --------
    >>> files = {"test.txt": "content"}
    >>> with create_temp_dir_fixture(files) as temp_dir:
    ...     file_path = temp_dir / "test.txt"
    ...     print(file_path.exists())
    True

    Notes
    -----
    Directory and all contents are deleted after use.

    Complexity
    ----------
    Time: O(n * m), Space: O(n * m), where n is number of files and m is average content size
    """
    if files is not None and not isinstance(files, dict):
        raise TypeError(f"files must be a dict or None, got {type(files).__name__}")

    temp_dir = Path(tempfile.mkdtemp())

    try:
        if files:
            for filename, content in files.items():
                file_path = temp_dir / filename
                file_path.parent.mkdir(parents=True, exist_ok=True)
                file_path.write_text(content)

        yield temp_dir
    finally:
        # Clean up directory and all contents
        if temp_dir.exists():
            for item in temp_dir.rglob("*"):
                if item.is_file():
                    item.unlink()
            for item in sorted(temp_dir.rglob("*"), reverse=True):
                if item.is_dir():
                    item.rmdir()
            temp_dir.rmdir()


__all__ = ["create_temp_dir_fixture"]
