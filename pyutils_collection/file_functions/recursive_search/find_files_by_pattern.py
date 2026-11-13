"""
Find files by name pattern recursively in a directory.
"""

import fnmatch
import os
from pathlib import Path


def find_files_by_pattern(
    directory: str | Path,
    pattern: str,
    case_sensitive: bool = False,
) -> list[str]:
    """
    Find all files matching a name pattern recursively in a directory.

    Parameters
    ----------
    directory : str | Path
        The directory path to search in.
    pattern : str
        The filename pattern to match (supports wildcards * and ?).
    case_sensitive : bool, optional
        Whether the pattern matching should be case sensitive (by default False).
        Explicit case sensitivity is honored on every platform, including Windows.

    Returns
    -------
    list[str]
        List of absolute file paths matching the pattern.

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If directory doesn't exist or pattern is empty.
    OSError
        If there's an error accessing the directory.

    Examples
    --------
    >>> find_files_by_pattern("/path/to/dir", "*.py")
    ['/path/to/dir/script.py', '/path/to/dir/module.py']
    >>> find_files_by_pattern("/path/to/dir", "test_*", case_sensitive=True)
    ['/path/to/dir/test_module.py', '/path/to/dir/subdir/test_utils.py']

    Notes
    -----
    Supports Unix shell-style wildcards:
    - * matches everything
    - ? matches any single character
    - [seq] matches any character in seq
    - [!seq] matches any character not in seq

    Complexity
    ----------
    Time: O(n*m), Space: O(k) where n is total files, m is pattern length, k is matching files.
    """
    # Input validation
    if not isinstance(directory, (str, Path)):
        raise TypeError(
            f"directory must be a string or Path, got {type(directory).__name__}"
        )
    if not isinstance(pattern, str):
        raise TypeError(f"pattern must be a string, got {type(pattern).__name__}")
    if not isinstance(case_sensitive, bool):
        raise TypeError(
            f"case_sensitive must be a boolean, got {type(case_sensitive).__name__}"
        )

    # Convert to Path object
    dir_path = Path(directory)

    # Validate directory exists
    if not dir_path.exists():
        raise ValueError(f"Directory does not exist: {directory}")
    if not dir_path.is_dir():
        raise ValueError(f"Path is not a directory: {directory}")

    # Validate pattern
    if not pattern.strip():
        raise ValueError("Pattern cannot be empty")

    matching_files: list[str] = []
    seen_casefolded_paths: set[str] = set()

    try:
        for root, _, files in os.walk(dir_path):
            for file in files:
                # Apply case sensitivity
                if case_sensitive:
                    if fnmatch.fnmatchcase(file, pattern):
                        matching_files.append(str(Path(root) / file))
                else:
                    test_file = file.casefold()
                    test_pattern = pattern.casefold()

                    if fnmatch.fnmatchcase(test_file, test_pattern):
                        full_path = Path(root) / file
                        canonical_path = str(full_path).casefold()
                        if canonical_path not in seen_casefolded_paths:
                            seen_casefolded_paths.add(canonical_path)
                            matching_files.append(str(full_path))
    except OSError as e:
        raise OSError(f"Error accessing directory {directory}: {e}") from e

    return matching_files


__all__ = ["find_files_by_pattern"]
