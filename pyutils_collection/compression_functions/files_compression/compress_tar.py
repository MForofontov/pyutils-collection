"""TAR archive compression."""

import os
import tarfile
from shutil import SameFileError


def compress_tar(input_path: str, output_tar: str) -> None:
    """
    Compress a file or folder using tar with gzip compression.

    Parameters
    ----------
    input_path : str
        The path to the input file or folder to be compressed.
    output_tar : str
        The path to the output tar file to save the compressed data.

    Returns
    -------
    None
        This function does not return a value.

    Raises
    ------
    SameFileError
        If a file input and output refer to the same file, including hard links.
        The input is preserved because aliases are rejected before output opens.
    TypeError
        If input_path or output_tar is not a string.
    FileNotFoundError
        If the input path does not exist.
    IOError
        If an I/O error occurs during compression.

    Examples
    --------
    >>> compress_tar('my_folder', 'archive.tar.gz')  # doctest: +SKIP
    """
    # Check if input_path and output_tar are strings
    if not isinstance(input_path, str):
        raise TypeError("input_path must be a string")
    if not isinstance(output_tar, str):
        raise TypeError("output_tar must be a string")

    # Check if the input path exists
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"The input path {input_path} does not exist.")

    if os.path.exists(output_tar) and os.path.samefile(input_path, output_tar):
        raise SameFileError("Input and output must refer to different files")

    try:
        check_path = (
            input_path
            if os.path.isdir(input_path)
            else os.path.dirname(input_path) or "."
        )
        if os.path.isdir(input_path):
            if os.stat(check_path).st_mode & 0o444 == 0:
                raise OSError("Input path is not readable")
        else:
            if os.stat(input_path).st_mode & 0o444 == 0:
                raise OSError("Input path is not readable")

        output_dir = os.path.dirname(output_tar) or "."
        if os.stat(output_dir).st_mode & 0o222 == 0:
            raise OSError("Output location is not writable")
        if os.path.exists(output_tar) and os.stat(output_tar).st_mode & 0o222 == 0:
            raise OSError("Output file is not writable")

        with tarfile.open(output_tar, "w:gz") as tar:
            if os.path.isdir(input_path):
                tar.add(input_path, arcname=os.path.basename(input_path))
            else:
                tar.add(input_path, arcname=os.path.basename(input_path))
    except FileNotFoundError:
        raise
    except (PermissionError, OSError) as exc:
        raise OSError(f"An I/O error occurred during compression: {exc}") from exc


__all__ = ["compress_tar"]
