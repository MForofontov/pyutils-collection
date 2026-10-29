"""
Create temporary file with automatic cleanup.
"""

import os
import tempfile
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def create_temp_file(
    suffix: str = "",
    prefix: str = "tmp",
    dir: str | Path | None = None,
    text: bool = True,
    delete: bool = True,
) -> Generator[str]:
    """
    Create a temporary file with automatic cleanup.

    Parameters
    ----------
    suffix : str, optional
        File suffix/extension (by default "").
    prefix : str, optional
        File prefix (by default "tmp").
    dir : str | Path | None, optional
        Directory to create temp file in, None for system temp (by default None).
    text : bool, optional
        Whether to open in text mode (by default True).
    delete : bool, optional
        Whether to delete file when context exits (by default True).

    Yields
    ------
    str
        Path to the temporary file.

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    OSError
        If there's an error creating or managing the temporary file.

    Examples
    --------
    >>> with create_temp_file(suffix=".txt") as temp_path:
    ...     with open(temp_path, 'w') as f:
    ...         f.write("test content")
    ...     print(f"Temp file: {temp_path}")
    Temp file: /tmp/tmpxyz123.txt

    >>> with create_temp_file(delete=False) as temp_path:
    ...     print(f"Persistent temp file: {temp_path}")
    Persistent temp file: /tmp/tmpxyz123

    Notes
    -----
    The file is created immediately and the path is yielded.
    If delete=True, the file is automatically removed when exiting the context.
    The file is created with secure permissions (readable/writable by owner only).

    Complexity
    ----------
    Time: O(1), Space: O(1)
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
    if not isinstance(text, bool):
        raise TypeError(f"text must be a boolean, got {type(text).__name__}")
    if not isinstance(delete, bool):
        raise TypeError(f"delete must be a boolean, got {type(delete).__name__}")

    # Convert dir to string if it's a Path
    temp_dir = str(dir) if dir is not None else None

    temp_file = None
    temp_path = None

    try:
        # Create temporary file
        mode = "w+t" if text else "w+b"
        temp_file = tempfile.NamedTemporaryFile(
            mode=mode,
            suffix=suffix,
            prefix=prefix,
            dir=temp_dir,
            delete=False,  # We handle deletion manually
        )
        temp_path = temp_file.name
        temp_file.close()  # Close the file descriptor, keep the file

        yield temp_path

    except OSError as e:
        raise OSError(f"Error creating temporary file: {e}") from e
    finally:
        # Cleanup
        if temp_path and delete and os.path.exists(temp_path):
            try:
                os.unlink(temp_path)
            except OSError:
                # File might have been already deleted
                pass


__all__ = ["create_temp_file"]
