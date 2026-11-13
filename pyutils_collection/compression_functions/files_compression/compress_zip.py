"""ZIP archive compression."""

import os
import zipfile
from shutil import SameFileError


def compress_zip(input_path: str, output_zip: str) -> None:
    """
    Compress a file or folder using zip.

    Parameters
    ----------
    input_path : str
        The path to the input file or folder to be compressed.
    output_zip : str
        The path to the output zip file to save the compressed data.

    Raises
    ------
    SameFileError
        If a file input and output refer to the same file, including hard links.
        The input is preserved because aliases are rejected before output opens.
    TypeError
        If input_path or output_zip is not a string.
    FileNotFoundError
        If the input path does not exist.
    IOError
        If an I/O error occurs during compression.
    """
    # Check if input_path and output_zip are strings
    if not isinstance(input_path, str):
        raise TypeError("input_path must be a string")
    if not isinstance(output_zip, str):
        raise TypeError("output_zip must be a string")

    # Check if the input path exists
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"The input path {input_path} does not exist.")

    if os.path.exists(output_zip) and os.path.samefile(input_path, output_zip):
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

        output_dir = os.path.dirname(output_zip) or "."
        if os.stat(output_dir).st_mode & 0o222 == 0:
            raise OSError("Output location is not writable")
        if os.path.exists(output_zip) and os.stat(output_zip).st_mode & 0o222 == 0:
            raise OSError("Output file is not writable")

        with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
            if os.path.isdir(input_path):
                for root, _dirs, files in os.walk(input_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, start=input_path)
                        zipf.write(file_path, arcname=arcname)
            else:
                zipf.write(input_path, arcname=os.path.basename(input_path))
    except FileNotFoundError:
        raise
    except (PermissionError, OSError) as exc:
        raise OSError(f"An I/O error occurred during compression: {exc}") from exc


__all__ = ["compress_zip"]
