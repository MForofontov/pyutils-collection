"""Directory merging utilities."""

import os
import shutil
from pathlib import Path


def merge_folders(folder1: str, folder2: str, output_folder: str) -> None:
    """
    Merge the contents of two folders into an output folder.

    Parameters
    ----------
    folder1 : str
        Path to the first folder to merge.
    folder2 : str
        Path to the second folder to merge.
    output_folder : str
        Path to the output folder where the merged contents will be stored.

    Returns
    -------
    None

    Raises
    ------
    FileNotFoundError
        If either source is not a directory.
    ValueError
        If the output and either source overlap.

    Notes
    -----
    - If the output folder does not exist, it will be created.
    - Conflicts use "_copy", then "_copy2", "_copy3", and so on without
      overwriting existing entries. Concurrent destination writers are unsupported.
    - Source and output directories must not contain one another.
    - The function ensures that all intermediate directories are created as needed.
    """

    if not os.path.isdir(folder1):
        raise FileNotFoundError(f"Source folder not found: {folder1}")
    if not os.path.isdir(folder2):
        raise FileNotFoundError(f"Source folder not found: {folder2}")

    destination = Path(output_folder).resolve()
    for folder in (folder1, folder2):
        source = Path(folder).resolve()
        if destination.is_relative_to(source) or source.is_relative_to(destination):
            raise ValueError("Source and output folders must not overlap")

    def copy_files(src_folder: str) -> None:
        """
        Copy files from the source folder to the output folder.

        Parameters
        ----------
        src_folder : str
            Path to the source folder from which files will be copied.

        Returns
        -------
        None
        """
        for root, _, files in os.walk(src_folder):
            for file in files:
                src_file_path: str = os.path.join(root, file)
                relative_path: str = os.path.relpath(src_file_path, src_folder)
                dest_file_path: str = os.path.join(output_folder, relative_path)

                os.makedirs(os.path.dirname(dest_file_path), exist_ok=True)

                if os.path.lexists(dest_file_path):
                    base, ext = os.path.splitext(dest_file_path)
                    dest_file_path = f"{base}_copy{ext}"
                    suffix = 2
                    while os.path.lexists(dest_file_path):
                        dest_file_path = f"{base}_copy{suffix}{ext}"
                        suffix += 1

                shutil.copy2(src_file_path, dest_file_path)

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    copy_files(folder1)
    copy_files(folder2)


__all__ = ["merge_folders"]
