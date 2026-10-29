import os
import tarfile

import pytest

try:
    import snappy
    from pyutils_collection.compression_functions.files_compression.compress_tar import compress_tar
    SNAPPY_AVAILABLE = True
except ImportError:
    SNAPPY_AVAILABLE = False
    snappy = None  # type: ignore
    compress_tar = None  # type: ignore

pytestmark = [
    pytest.mark.unit,
    pytest.mark.compression,
    pytest.mark.skipif(not SNAPPY_AVAILABLE, reason="python-snappy not installed"),
]


def test_compress_tar_basic_file_compression(tmp_path) -> None:
    """
    Test case 1: Test the compress_tar function with a single file.
    """
    input_file = tmp_path / "input.txt"
    output_tar = tmp_path / "output.tar.gz"
    data = b"hello world"

    with open(input_file, "wb") as f:
        f.write(data)

    compress_tar(str(input_file), str(output_tar))

    # Check if the output tar file exists
    assert output_tar.exists(), "Output tar file should exist"

    # Extract the tar file to verify
    with tarfile.open(output_tar, "r:gz") as tar:
        tar.extractall(path=tmp_path, filter="data")

    extracted_file = tmp_path / "input.txt"
    with open(extracted_file, "rb") as f:
        extracted_data = f.read()

    assert extracted_data == data, "Extracted data should match the original data"


def test_compress_tar_empty_directory_compression(tmp_path) -> None:
    """
    Test case 2: Test the compress_tar function with an empty directory.
    """
    input_dir = tmp_path / "empty_dir"
    output_tar = tmp_path / "output.tar.gz"

    os.makedirs(input_dir)

    compress_tar(str(input_dir), str(output_tar))

    # Check if the output tar file exists
    assert output_tar.exists(), "Output tar file should exist"

    # Extract the tar file to verify
    with tarfile.open(output_tar, "r:gz") as tar:
        tar.extractall(path=tmp_path, filter="data")

    extracted_dir = tmp_path / "empty_dir"
    assert extracted_dir.exists() and extracted_dir.is_dir(), (
        "Extracted directory should exist and be empty"
    )


def test_compress_tar_directory_with_files_compression(tmp_path) -> None:
    """
    Test case 3: Test the compress_tar function with a directory containing files.
    """
    input_dir = tmp_path / "dir_with_files"
    output_tar = tmp_path / "output.tar.gz"
    data = b"hello world"

    os.makedirs(input_dir)
    file1 = input_dir / "file1.txt"
    file2 = input_dir / "file2.txt"

    with open(file1, "wb") as f:
        f.write(data)
    with open(file2, "wb") as f:
        f.write(data)

    compress_tar(str(input_dir), str(output_tar))

    # Check if the output tar file exists
    assert output_tar.exists(), "Output tar file should exist"

    # Extract the tar file to verify
    with tarfile.open(output_tar, "r:gz") as tar:
        tar.extractall(path=tmp_path, filter="data")

    extracted_file1 = tmp_path / "dir_with_files" / "file1.txt"
    extracted_file2 = tmp_path / "dir_with_files" / "file2.txt"

    with open(extracted_file1, "rb") as f:
        extracted_data1 = f.read()
    with open(extracted_file2, "rb") as f:
        extracted_data2 = f.read()

    assert extracted_data1 == data, (
        "Extracted data from file1 should match the original data"
    )
    assert extracted_data2 == data, (
        "Extracted data from file2 should match the original data"
    )


def test_compress_tar_invalid_input_path_type(tmp_path) -> None:
    """
    Test case 4: Test the compress_tar function with invalid input path type.
    """
    output_tar = tmp_path / "output.tar.gz"

    with pytest.raises(TypeError):
        compress_tar(123, str(output_tar))  # type: ignore


def test_compress_tar_invalid_output_path_type(tmp_path) -> None:
    """
    Test case 5: Test the compress_tar function with invalid output path type.
    """
    input_file = tmp_path / "input.txt"
    data = b"hello world"

    with open(input_file, "wb") as f:
        f.write(data)

    with pytest.raises(TypeError):
        compress_tar(str(input_file), 123)  # type: ignore


def test_compress_tar_non_existent_input_path(tmp_path) -> None:
    """
    Test case 6: Test the compress_tar function with a non-existent input path.
    """
    input_path = tmp_path / "non_existent"
    output_tar = tmp_path / "output.tar.gz"

    with pytest.raises(FileNotFoundError):
        compress_tar(str(input_path), str(output_tar))


def test_compress_tar_io_error_on_output_file(tmp_path) -> None:
    """
    Test case 7: Test the compress_tar function handling of I/O errors on output file.
    """
    input_file = tmp_path / "input.txt"
    output_tar = tmp_path / "output.tar.gz"
    data = b"hello world"

    with open(input_file, "wb") as f:
        f.write(data)

    # Simulate an I/O error by making the output directory read-only
    os.chmod(tmp_path, 0o400)

    try:
        with pytest.raises(OSError):
            compress_tar(str(input_file), str(output_tar))
    finally:
        # Restore permissions to delete the temporary directory
        os.chmod(tmp_path, 0o600)


def test_compress_tar_no_permission_on_input_file(tmp_path, deny_read_access) -> None:
    """
    Test case 8: Test the compress_tar function with no permission on input file.
    """
    input_file = tmp_path / "input.txt"
    output_tar = tmp_path / "output.tar.gz"
    data = b"hello world"

    with open(input_file, "wb") as f:
        f.write(data)

    # Remove all permissions from the input file
    deny_read_access(input_file)

    try:
        with pytest.raises(OSError):
            compress_tar(str(input_file), str(output_tar))
    finally:
        # Restore permissions to delete the temporary file
        os.chmod(input_file, 0o600)


def test_compress_tar_io_error_on_read_only_output_file(tmp_path) -> None:
    """
    Test case 9: Test the compress_tar function with read-only output file.
    """
    input_file = tmp_path / "input.txt"
    output_tar = tmp_path / "output.tar.gz"
    data = b"hello world"

    with open(input_file, "wb") as f:
        f.write(data)

    with open(output_tar, "wb") as f:
        pass

    # Simulate a read-only output file
    os.chmod(output_tar, 0o400)

    try:
        with pytest.raises(OSError):
            compress_tar(str(input_file), str(output_tar))
    finally:
        # Restore permissions to delete the temporary file
        os.chmod(output_tar, 0o600)


def test_compress_tar_read_only_output_directory(tmp_path) -> None:
    """
    Test case 10: Test the compress_tar function with read-only output directory.
    """
    input_file = tmp_path / "input.txt"
    output_dir = tmp_path / "output_dir"
    output_dir.mkdir()
    output_tar = output_dir / "output.tar.gz"
    data = b"hello world"

    with open(input_file, "wb") as f:
        f.write(data)

    # Make output directory read-only
    os.chmod(output_dir, 0o444)

    try:
        with pytest.raises(OSError, match="Output location is not writable"):
            compress_tar(str(input_file), str(output_tar))
    finally:
        # Restore permissions to delete the directory
        os.chmod(output_dir, 0o755)


def test_compress_tar_read_only_input_directory(tmp_path, deny_read_access) -> None:
    """
    Test case 11: Test the compress_tar function with read-only input directory.
    """
    input_dir = tmp_path / "input_dir"
    input_dir.mkdir()
    (input_dir / "file.txt").write_text("test data")
    output_tar = tmp_path / "output.tar.gz"

    # Make input directory read-only
    deny_read_access(input_dir)

    try:
        with pytest.raises(OSError, match="Input path is not readable"):
            compress_tar(str(input_dir), str(output_tar))
    finally:
        # Restore permissions to delete the directory
        os.chmod(input_dir, 0o755)
