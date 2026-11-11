"""Directory listing utilities."""

import os


def list_directories(directory_path: str, include_hidden: bool = False) -> list[str]:
    """
    List all directories in a given path.

    Parameters
    ----------
    directory_path : str
        Path to the parent directory.
    include_hidden : bool, optional
        Include hidden directories (starting with .) (by default False).

    Returns
    -------
    list[str]
        List of directory names.

    Raises
    ------
    TypeError
        If directory_path is not a string.
    FileNotFoundError
        If directory does not exist.
    NotADirectoryError
        If path is not a directory.

    Examples
    --------
    >>> dirs = list_directories('/tmp')
    >>> isinstance(dirs, list)
    True
    """
    if not isinstance(directory_path, str):
        raise TypeError("directory_path must be a string")

    if not os.path.exists(directory_path):
        raise FileNotFoundError(f"Directory does not exist: {directory_path}")

    if not os.path.isdir(directory_path):
        raise NotADirectoryError(f"Path is not a directory: {directory_path}")

    with os.scandir(directory_path) as entries:
        return sorted(
            entry.name
            for entry in entries
            if (include_hidden or not entry.name.startswith(".")) and entry.is_dir()
        )


__all__ = ["list_directories"]
