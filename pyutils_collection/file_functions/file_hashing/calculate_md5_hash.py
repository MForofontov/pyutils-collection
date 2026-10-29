"""
Calculate MD5 hash of a file.
"""

import hashlib
from pathlib import Path


def calculate_md5_hash(
    file_path: str | Path,
    chunk_size: int = 8192,
) -> str:
    """
    Calculate MD5 hash of a file.

    Parameters
    ----------
    file_path : str | Path
        Path to the file to hash.
    chunk_size : int, optional
        Size of chunks to read at a time in bytes (by default 8192).

    Returns
    -------
    str
        Hexadecimal MD5 hash string.

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If file doesn't exist or chunk_size is invalid.
    OSError
        If there's an error reading the file.

    Examples
    --------
    >>> calculate_md5_hash("/path/to/file.txt")
    'd41d8cd98f00b204e9800998ecf8427e'
    >>> calculate_md5_hash("/path/to/file.txt", chunk_size=4096)
    'd41d8cd98f00b204e9800998ecf8427e'

    Notes
    -----
    MD5 is not cryptographically secure but is useful for file integrity checks.
    The function reads the file in chunks to handle large files efficiently.

    Complexity
    ----------
    Time: O(n), Space: O(1) where n is file size.
    """
    # Input validation
    if not isinstance(file_path, (str, Path)):
        raise TypeError(
            f"file_path must be a string or Path, got {type(file_path).__name__}"
        )
    if not isinstance(chunk_size, int):
        raise TypeError(
            f"chunk_size must be an integer, got {type(chunk_size).__name__}"
        )

    # Convert to Path object
    path = Path(file_path)

    # Validate file exists and is a file
    if not path.exists():
        raise ValueError(f"File does not exist: {file_path}")
    if not path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")

    # Validate chunk_size
    if chunk_size <= 0:
        raise ValueError(f"chunk_size must be positive, got {chunk_size}")

    # Calculate MD5 hash
    md5_hash = hashlib.md5(usedforsecurity=False)

    try:
        with open(path, "rb") as file:
            while chunk := file.read(chunk_size):
                md5_hash.update(chunk)
    except OSError as e:
        raise OSError(f"Error reading file {file_path}: {e}") from e

    return md5_hash.hexdigest()


__all__ = ["calculate_md5_hash"]
