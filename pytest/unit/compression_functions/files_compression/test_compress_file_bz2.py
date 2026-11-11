import bz2
import os

import pytest

try:
    import snappy
    from pyutils_collection.compression_functions.files_compression.compress_file_bz2 import compress_file_bz2
    SNAPPY_AVAILABLE = True
except ImportError:
    SNAPPY_AVAILABLE = False
    snappy = None  # type: ignore
    compress_file_bz2 = None  # type: ignore

pytestmark = [
    pytest.mark.unit,
    pytest.mark.compression,
    pytest.mark.skipif(not SNAPPY_AVAILABLE, reason="python-snappy not installed"),
]


def test_compress_file_bz2_basic(tmp_path) -> None:
    """
    Test case 1: Test the compress_file_bz2 function with basic input.
    """
    input_file = tmp_path / "input.txt"
    output_file = tmp_path / "output.bz2"
    data = b"hello world"

    with open(input_file, "wb") as f:
        f.write(data)

    compress_file_bz2(str(input_file), str(output_file))

    # Check if the output file exists
    assert output_file.exists(), "Output file should exist"

    # Decompress the data to verify
    with bz2.open(output_file, "rb") as f:
        decompressed_data = f.read()

    assert decompressed_data == data, "Decompressed data should match the original data"


def test_compress_file_bz2_empty_file_compression_and_verification(tmp_path) -> None:
    """
    Test case 2: Test the compress_file_bz2 function with an empty file.
    """
    input_file = tmp_path / "input.txt"
    output_file = tmp_path / "output.bz2"

    with open(input_file, "wb") as f:
        pass

    compress_file_bz2(str(input_file), str(output_file))

    # Check if the output file exists
    assert output_file.exists(), "Output file should exist"

    # Decompress the data to verify
    with bz2.open(output_file, "rb") as f:
        decompressed_data = f.read()

    assert decompressed_data == b"", "Decompressed data should match the original data"


def test_compress_file_bz2_large_file_compression_and_verification(tmp_path) -> None:
    """
    Test case 3: Test the compress_file_bz2 function with a large file.
    """
    input_file = tmp_path / "input.txt"
    output_file = tmp_path / "output.bz2"
    data = b"a" * 1000000  # 1 MB of data

    with open(input_file, "wb") as f:
        f.write(data)

    compress_file_bz2(str(input_file), str(output_file))

    # Check if the output file exists
    assert output_file.exists(), "Output file should exist"

    # Check if the compressed file is smaller than the original file
    assert output_file.stat().st_size < input_file.stat().st_size, (
        "Compressed file should be smaller than the original file"
    )

    # Decompress the data to verify
    with bz2.open(output_file, "rb") as f:
        decompressed_data = f.read()

    assert decompressed_data == data, "Decompressed data should match the original data"


def test_compress_file_bz2_invalid_input_type(tmp_path) -> None:
    """
    Test case 4: Test the compress_file_bz2 function with invalid input file type.
    """
    output_file = tmp_path / "output.bz2"

    with pytest.raises(TypeError):
        compress_file_bz2(123, str(output_file))  # type: ignore


def test_compress_file_bz2_invalid_output_type(tmp_path) -> None:
    """
    Test case 5: Test the compress_file_bz2 function with invalid output file type.
    """
    input_file = tmp_path / "input.txt"
    data = b"hello world"

    with open(input_file, "wb") as f:
        f.write(data)

    with pytest.raises(TypeError):
        compress_file_bz2(str(input_file), 123)  # type: ignore


def test_compress_file_bz2_file_not_found(tmp_path) -> None:
    """
    Test case 6: Test the compress_file_bz2 function with a non-existent input file.
    """
    input_file = tmp_path / "non_existent.txt"
    output_file = tmp_path / "output.bz2"

    with pytest.raises(FileNotFoundError):
        compress_file_bz2(str(input_file), str(output_file))


def test_compress_file_bz2_io_error_on_read_only_output_directory(tmp_path) -> None:
    """
    Test case 7: Test the compress_file_bz2 function handling of I/O errors on read-only output directory.
    """
    input_file = tmp_path / "input.txt"
    output_file = tmp_path / "output.bz2"
    data = b"hello world"

    with open(input_file, "wb") as f:
        f.write(data)

    # Simulate an I/O error by making the output directory read-only
    os.chmod(tmp_path, 0o400)

    try:
        with pytest.raises(OSError):
            compress_file_bz2(str(input_file), str(output_file))
    finally:
        # Restore permissions to delete the temporary directory
        os.chmod(tmp_path, 0o600)


def test_compress_file_bz2_no_permission_on_input_file(tmp_path, deny_read_access) -> None:
    """
    Test case 8: Test the compress_file_bz2 function with no permission on input file.
    """
    input_file = tmp_path / "input.txt"
    output_file = tmp_path / "output.bz2"
    data = b"hello world"

    with open(input_file, "wb") as f:
        f.write(data)

    # Remove all permissions from the input file
    deny_read_access(input_file)

    try:
        with pytest.raises(OSError):
            compress_file_bz2(str(input_file), str(output_file))
    finally:
        # Restore permissions to delete the temporary file
        os.chmod(input_file, 0o600)


def test_compress_file_bz2_io_error_on_read_only_output_file(tmp_path) -> None:
    """
    Test case 9: Test the compress_file_bz2 function with read-only output file.
    """
    input_file = tmp_path / "input.txt"
    output_file = tmp_path / "output.bz2"
    data = b"hello world"

    with open(input_file, "wb") as f:
        f.write(data)

    with open(output_file, "wb") as f:
        pass

    # Simulate a read-only output file
    os.chmod(output_file, 0o400)

    try:
        with pytest.raises(OSError):
            compress_file_bz2(str(input_file), str(output_file))
    finally:
        # Restore permissions to delete the temporary file
        os.chmod(output_file, 0o600)


def test_compress_file_bz2_read_only_output_directory(tmp_path) -> None:
    """
    Test case 10: Test the compress_file_bz2 function with read-only output directory.
    """
    input_file = tmp_path / "input.txt"
    output_dir = tmp_path / "output_dir"
    output_dir.mkdir()
    output_file = output_dir / "output.bz2"
    data = b"hello world"

    with open(input_file, "wb") as f:
        f.write(data)

    # Make output directory read-only
    os.chmod(output_dir, 0o444)

    try:
        with pytest.raises(OSError, match="Output location is not writable"):
            compress_file_bz2(str(input_file), str(output_file))
    finally:
        # Restore permissions to delete the directory
        os.chmod(output_dir, 0o755)
