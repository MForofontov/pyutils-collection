"""ZIP archive decompression."""

import os
import stat
import zipfile
from pathlib import Path, PureWindowsPath


def decompress_file_zip(input_zip: str, output_dir: str) -> None:
    """
    Decompress a zip-compressed file.

    Parameters
    ----------
    input_zip : str
        The path to the input zip-compressed file.
    output_dir : str
        The path to the output directory to extract the decompressed files.

    Raises
    ------
    TypeError
        If input_zip or output_dir is not a string.
    FileNotFoundError
        If the input zip file does not exist.
    IOError
        If an I/O error occurs during decompression.
    """
    # Check if input_zip and output_dir are strings
    if not isinstance(input_zip, str):
        raise TypeError("input_zip must be a string")
    if not isinstance(output_dir, str):
        raise TypeError("output_dir must be a string")

    try:
        if not os.path.exists(input_zip):
            raise FileNotFoundError(f"The input zip file {input_zip} does not exist.")
        mode = os.stat(input_zip).st_mode
        if mode & (stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH) == 0:
            raise OSError("Input file is not readable")
        if os.path.exists(output_dir):
            dir_mode = os.stat(output_dir).st_mode
            if dir_mode & (stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH) == 0:
                raise OSError("Output location is not writable")
        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Open the input zip-compressed file in read mode
        with zipfile.ZipFile(input_zip, "r") as zipf:
            destination = Path(output_dir).resolve()
            # Validate the complete member list before creating any files.
            # ZIP's own name sanitization does not protect existing symlinks.
            for member in zipf.infolist():
                name = member.filename.replace("\\", "/")
                relative = Path(name)
                target = (destination / relative).resolve()
                if (
                    relative.is_absolute()
                    or PureWindowsPath(name).drive
                    or ".." in relative.parts
                    or not target.is_relative_to(destination)
                    or stat.S_ISLNK(member.external_attr >> 16)
                ):
                    raise ValueError(f"Unsafe ZIP member: {member.filename}")
            # Extract all files to the specified output directory
            zipf.extractall(output_dir)
    except FileNotFoundError as exc:
        # Raise a FileNotFoundError if the input zip file does not exist
        raise FileNotFoundError(
            f"The input zip file {input_zip} does not exist."
        ) from exc
    except OSError as exc:
        # Raise an IOError if an I/O error occurs during decompression
        raise OSError(f"An I/O error occurred during decompression: {exc}") from exc


__all__ = ["decompress_file_zip"]
