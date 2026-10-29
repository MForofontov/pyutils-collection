"""
Create temporary file fixture for testing.
"""

import tempfile
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def create_temp_file_fixture(
    content: str = "",
    suffix: str = ".txt",
) -> Generator[Path]:
    """
    Create a temporary file fixture for testing.

    Parameters
    ----------
    content : str, optional
        Initial file content (by default "").
    suffix : str, optional
        File suffix (by default ".txt").

    Yields
    ------
    Path
        Path to temporary file.

    Raises
    ------
    TypeError
        If parameters are of wrong type.

    Examples
    --------
    >>> with create_temp_file_fixture("test content") as temp_file:
    ...     content = temp_file.read_text()
    ...     print(content)
    test content

    Notes
    -----
    File is automatically deleted after use.

    Complexity
    ----------
    Time: O(n), Space: O(n), where n is content length
    """
    if not isinstance(content, str):
        raise TypeError(f"content must be a string, got {type(content).__name__}")
    if not isinstance(suffix, str):
        raise TypeError(f"suffix must be a string, got {type(suffix).__name__}")

    with tempfile.NamedTemporaryFile(mode="w", suffix=suffix, delete=False) as f:
        f.write(content)
        temp_path = Path(f.name)

    try:
        yield temp_path
    finally:
        if temp_path.exists():
            temp_path.unlink()


__all__ = ["create_temp_file_fixture"]
