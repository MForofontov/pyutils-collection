"""GZIP file decompression."""

import gzip
import os
import shutil
import stat
from shutil import SameFileError


def decompress_file_gzip(input_gzip: str, output_file: str) -> None:
    """
    Decompress a gzip-compressed file.

    Parameters
    ----------
    input_gzip : str
        The path to the input gzip-compressed file.
    output_file : str
        The path to the output file to save the decompressed data.

    Raises
    ------
    SameFileError
        If input and output refer to the same file, including hard-link aliases.
        The source is preserved because this check precedes opening the output.
    TypeError
        If input_gzip or output_file is not a string.
    FileNotFoundError
        If the input file does not exist.
    IOError
        If an I/O error occurs during decompression.
    """
    # Check if input_gzip and output_file are strings
    if not isinstance(input_gzip, str):
        raise TypeError("input_gzip must be a string")
    if not isinstance(output_file, str):
        raise TypeError("output_file must be a string")

    if (
        os.path.exists(input_gzip)
        and os.path.exists(output_file)
        and os.path.samefile(input_gzip, output_file)
    ):
        raise SameFileError("Input and output must refer to different files")

    try:
        if not os.path.exists(input_gzip):
            raise FileNotFoundError(f"The input file {input_gzip} does not exist.")
        mode = os.stat(input_gzip).st_mode
        if mode & (stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH) == 0:
            raise OSError("Input file is not readable")

        output_dir = os.path.dirname(output_file) or "."
        if os.path.exists(output_file):
            out_mode = os.stat(output_file).st_mode
            if out_mode & (stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH) == 0:
                raise OSError("Output location is not writable")
        dir_mode = os.stat(output_dir).st_mode
        if dir_mode & (stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH) == 0:
            raise OSError("Output location is not writable")
        # Open the input gzip-compressed file in binary read mode
        with gzip.open(input_gzip, "rb") as f_in:
            # Open the output file in binary write mode
            with open(output_file, "wb") as f_out:
                # Copy the contents of the input file to the output file
                shutil.copyfileobj(f_in, f_out)
    except FileNotFoundError as exc:
        # Raise a FileNotFoundError if the input file does not exist
        raise FileNotFoundError(f"The input file {input_gzip} does not exist.") from exc
    except OSError as exc:
        # Raise an IOError if an I/O error occurs during decompression
        raise OSError(f"An I/O error occurred during decompression: {exc}") from exc


__all__ = ["decompress_file_gzip"]
