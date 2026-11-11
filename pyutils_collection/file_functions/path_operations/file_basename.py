"""File basename extraction."""

import os


def file_basename(file_path: str, file_extension: bool = True) -> str:
    """
    Get the file name from a file path.

    Parameters
    ----------
    file_path : str
        The path to the file.
    file_extension : bool, optional
        Whether to include the file extension in the returned name (default is True).

    Returns
    -------
    str
        The file name extracted from the file path.

    Raises
    ------
    ValueError
        If ``file_path`` is an empty string.
    """
    if not file_path:
        raise ValueError("file_path must not be empty")

    normalized_path: str = file_path.rstrip(os.sep + (os.altsep or ""))
    base_name: str = os.path.basename(normalized_path)

    if not file_extension:
        base_name = os.path.splitext(base_name)[0]

    return base_name


__all__ = ["file_basename"]
