"""LZMA file compression."""

import lzma
import os
from shutil import SameFileError


def compress_file_lzma(input_file: str, output_file: str) -> None:
    """
    Compress a file using lzma.

    Parameters
    ----------
    input_file : str
        The path to the input file to be compressed.
    output_file : str
        The path to the output file to save the compressed data.

    Raises
    ------
    SameFileError
        If input and output refer to the same file, including hard-link aliases.
        The source is preserved because this check precedes opening the output.
    TypeError
        If input_file or output_file is not a string.
    FileNotFoundError
        If the input file does not exist.
    IOError
        If an I/O error occurs during compression.
    """
    # Check if input_file and output_file are strings
    if not isinstance(input_file, str):
        raise TypeError("input_file must be a string")
    if not isinstance(output_file, str):
        raise TypeError("output_file must be a string")

    # Check if the input file exists
    if not os.path.exists(input_file):
        raise FileNotFoundError(f"The input file {input_file} does not exist.")

    if (
        os.path.exists(input_file)
        and os.path.exists(output_file)
        and os.path.samefile(input_file, output_file)
    ):
        raise SameFileError("Input and output must refer to different files")

    try:
        if os.stat(input_file).st_mode & 0o444 == 0:
            raise OSError("Input file is not readable")

        output_dir = os.path.dirname(output_file) or "."
        if os.stat(output_dir).st_mode & 0o222 == 0:
            raise OSError("Output location is not writable")
        if os.path.exists(output_file) and os.stat(output_file).st_mode & 0o222 == 0:
            raise OSError("Output file is not writable")

        with open(input_file, "rb") as f_in, lzma.open(output_file, "wb") as f_out:
            f_out.writelines(f_in)
    except FileNotFoundError:
        raise
    except (PermissionError, OSError) as exc:
        raise OSError(f"An I/O error occurred during compression: {exc}") from exc


__all__ = ["compress_file_lzma"]
