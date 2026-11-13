"""File concatenation utilities."""

import os
import shutil


def concat_files(source_file: str, destination_file: str) -> None:
    """
    Concatenates the source file to the destination file.

    Parameters
    ----------
    source_file : str
        The path to the source file.
    destination_file : str
        The path to the destination file.

    Returns
    -------
    None

    Raises
    ------
    shutil.SameFileError
        If source and destination refer to the same file, including aliases.
    FileNotFoundError
        If the source does not exist. A missing source does not create output.
    """
    if os.path.exists(destination_file) and os.path.samefile(
        source_file, destination_file
    ):
        raise shutil.SameFileError("Source and destination must be different files")
    with open(source_file) as infile, open(destination_file, "a") as outfile:
        shutil.copyfileobj(infile, outfile)


__all__ = ["concat_files"]
