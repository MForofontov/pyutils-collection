"""
Calculate SHA1 hash of a file.
"""

import hashlib
from pathlib import Path


def calculate_sha1_hash(
    file_path: str | Path,
    chunk_size: int = 8192,
) -> str:
    """
    Calculate SHA1 hash of a file.

    Parameters
    ----------
    file_path : str | Path
        Path to the file to hash.
    chunk_size : int, optional
        Size of chunks to read at a time in bytes (by default 8192).

    Returns
    -------
    str
        Hexadecimal SHA1 hash string.

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
    >>> calculate_sha1_hash("/path/to/file.txt")
    'da39a3ee5e6b4b0d3255bfef95601890afd80709'
    >>> calculate_sha1_hash("/path/to/file.txt", chunk_size=4096)
    'da39a3ee5e6b4b0d3255bfef95601890afd80709'

    Notes
    -----
    SHA1 is deprecated for cryptographic use but still useful for checksums.
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

    # Calculate SHA1 hash
    sha1_hash = hashlib.sha1(usedforsecurity=False)

    try:
        with open(path, "rb") as file:
            while chunk := file.read(chunk_size):
                sha1_hash.update(chunk)
    except OSError as e:
        raise OSError(f"Error reading file {file_path}: {e}") from e

    return sha1_hash.hexdigest()


__all__ = ["calculate_sha1_hash"]
