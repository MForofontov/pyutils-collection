import pytest

try:
    import bz2
    import os
    import snappy
    from pyutils_collection.compression_functions.files_compression.decompress_file_bz2 import decompress_file_bz2
    SNAPPY_AVAILABLE = True
except ImportError:
    SNAPPY_AVAILABLE = False
    bz2 = None  # type: ignore
    os = None  # type: ignore
    snappy = None  # type: ignore
    decompress_file_bz2 = None  # type: ignore

pytestmark = [
    pytest.mark.unit,
    pytest.mark.compression,
    pytest.mark.skipif(not SNAPPY_AVAILABLE, reason="python-snappy not installed"),
]



def test_decompress_file_bz2_basic(tmp_path) -> None:
    """
    Test case 1: Test the decompress_file_bz2 function with basic input.
    """
    compressed_file = tmp_path / "input.txt.bz2"
    output_file = tmp_path / "output.txt"
    data = b"hello world"

    # Create a compressed bz2 file
    with bz2.open(compressed_file, "wb") as f:
        f.write(data)

    decompress_file_bz2(str(compressed_file), str(output_file))

    # Check if the output file exists
    assert output_file.exists(), "Output file should exist"

    # Read the decompressed data to verify
    with open(output_file, "rb") as f:
        decompressed_data = f.read()

    assert decompressed_data == data, "Decompressed data should match the original data"


def test_decompress_file_bz2_empty_file(tmp_path) -> None:
    """
    Test case 2: Test the decompress_file_bz2 function with an empty file.
    """
    compressed_file = tmp_path / "input.txt.bz2"
    output_file = tmp_path / "output.txt"

    # Create an empty compressed bz2 file
    with bz2.open(compressed_file, "wb") as f:
        pass

    decompress_file_bz2(str(compressed_file), str(output_file))

    # Check if the output file exists
    assert output_file.exists(), "Output file should exist"

    # Read the decompressed data to verify
    with open(output_file, "rb") as f:
        decompressed_data = f.read()

    assert decompressed_data == b"", "Decompressed data should be empty"


def test_decompress_file_bz2_large_file(tmp_path) -> None:
    """
    Test case 3: Test the decompress_file_bz2 function with a large file.
    """
    compressed_file = tmp_path / "input.txt.bz2"
    output_file = tmp_path / "output.txt"
    data = b"a" * 1000000  # 1 MB of data

    # Create a compressed bz2 file
    with bz2.open(compressed_file, "wb") as f:
        f.write(data)

    decompress_file_bz2(str(compressed_file), str(output_file))

    # Check if the output file exists
    assert output_file.exists(), "Output file should exist"

    # Read the decompressed data to verify
    with open(output_file, "rb") as f:
        decompressed_data = f.read()

    assert decompressed_data == data, "Decompressed data should match the original data"


def test_decompress_file_bz2_invalid_input_type(tmp_path) -> None:
    """
    Test case 4: Test the decompress_file_bz2 function with invalid input file type.
    """
    output_file = tmp_path / "output.txt"

    with pytest.raises(TypeError):
        decompress_file_bz2(123, str(output_file))  # type: ignore


def test_decompress_file_bz2_invalid_output_type(tmp_path) -> None:
    """
    Test case 5: Test the decompress_file_bz2 function with invalid output file type.
    """
    compressed_file = tmp_path / "input.txt.bz2"
    data = b"hello world"

    # Create a compressed bz2 file
    with bz2.open(compressed_file, "wb") as f:
        f.write(data)

    with pytest.raises(TypeError):
        decompress_file_bz2(str(compressed_file), 123)  # type: ignore


def test_decompress_file_bz2_non_existent_input_file(tmp_path) -> None:
    """
    Test case 6: Test the decompress_file_bz2 function with a non-existent input file.
    """
    compressed_file = tmp_path / "non_existent.txt.bz2"
    output_file = tmp_path / "output.txt"

    with pytest.raises(FileNotFoundError):
        decompress_file_bz2(str(compressed_file), str(output_file))


def test_decompress_file_bz2_io_error_on_output_file(tmp_path) -> None:
    """
    Test case 7: Test the decompress_file_bz2 function handling of I/O errors on output file.
    """
    compressed_file = tmp_path / "input.txt.bz2"
    output_file = tmp_path / "output.txt"
    data = b"hello world"

    # Create a compressed bz2 file
    with bz2.open(compressed_file, "wb") as f:
        f.write(data)

    # Simulate an I/O error by making the output directory read-only
    os.chmod(tmp_path, 0o400)

    try:
        with pytest.raises(OSError):
            decompress_file_bz2(str(compressed_file), str(output_file))
    finally:
        # Restore permissions to delete the temporary directory
        os.chmod(tmp_path, 0o600)


def test_decompress_file_bz2_no_permission_on_input_file(tmp_path, deny_read_access) -> None:
    """
    Test case 8: Test the decompress_file_bz2 function with no permission on input file.
    """
    compressed_file = tmp_path / "input.txt.bz2"
    output_file = tmp_path / "output.txt"
    data = b"hello world"

    # Create a compressed bz2 file
    with bz2.open(compressed_file, "wb") as f:
        f.write(data)

    # Remove all permissions from the input file
    deny_read_access(compressed_file)

    try:
        with pytest.raises(OSError):
            decompress_file_bz2(str(compressed_file), str(output_file))
    finally:
        # Restore permissions to delete the temporary file
        os.chmod(compressed_file, 0o600)


def test_decompress_file_bz2_io_error_on_read_only_output_file(tmp_path) -> None:
    """
    Test case 9: Test the decompress_file_bz2 function with read-only output file.
    """
    compressed_file = tmp_path / "input.txt.bz2"
    output_file = tmp_path / "output.txt"
    data = b"hello world"

    # Create a compressed bz2 file
    with bz2.open(compressed_file, "wb") as f:
        f.write(data)

    with open(output_file, "wb") as f:
        pass

    # Simulate a read-only output file
    os.chmod(output_file, 0o400)

    try:
        with pytest.raises(OSError):
            decompress_file_bz2(str(compressed_file), str(output_file))
    finally:
        # Restore permissions to delete the temporary file
        os.chmod(output_file, 0o600)
