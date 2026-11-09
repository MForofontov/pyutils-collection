"""TAR archive decompression."""

import os
import stat
import tarfile


def decompress_file_tar(input_tar: str, output_dir: str) -> None:
    """
    Decompress a tar-compressed file.

    Parameters
    ----------
    input_tar : str
        The path to the input tar-compressed file.
    output_dir : str
        The path to the output directory to extract the decompressed files.

    Returns
    -------
    None
        This function does not return a value.

    Raises
    ------
    TypeError
        If input_tar or output_dir is not a string.
    FileNotFoundError
        If the input tar file does not exist.
    IOError
        If an I/O error occurs during decompression.

    Examples
    --------
    >>> decompress_file_tar('archive.tar.gz', 'output_folder')  # doctest: +SKIP
    """
    # Check if input_tar and output_dir are strings
    if not isinstance(input_tar, str):
        raise TypeError("input_tar must be a string")
    if not isinstance(output_dir, str):
        raise TypeError("output_dir must be a string")

    try:
        if not os.path.exists(input_tar):
            raise FileNotFoundError(f"The input tar file {input_tar} does not exist.")
        mode = os.stat(input_tar).st_mode
        if mode & (stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH) == 0:
            raise OSError("Input file is not readable")
        if os.path.exists(output_dir):
            dir_mode = os.stat(output_dir).st_mode
            if dir_mode & (stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH) == 0:
                raise OSError("Output location is not writable")
        else:
            parent = os.path.dirname(output_dir) or "."
            if os.path.exists(parent):
                parent_mode = os.stat(parent).st_mode
                if parent_mode & (stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH) == 0:
                    raise OSError("Output location is not writable")
        # Ensure the output directory exists
        os.makedirs(output_dir, exist_ok=True)

        # Open the input tar-compressed file in read mode with gzip compression
        with tarfile.open(input_tar, "r:gz") as tar:
            # Reject unsafe later members before writing any earlier members.
            for member in tar.getmembers():
                tarfile.data_filter(member, output_dir)
            # Extract all files to the specified output directory
            tar.extractall(path=output_dir, filter="data")
    except FileNotFoundError as exc:
        # Raise a FileNotFoundError if the input tar file does not exist
        raise FileNotFoundError(
            f"The input tar file {input_tar} does not exist."
        ) from exc
    except OSError as exc:
        # Raise an IOError if an I/O error occurs during decompression
        raise OSError(f"An I/O error occurred during decompression: {exc}") from exc


__all__ = ["decompress_file_tar"]
