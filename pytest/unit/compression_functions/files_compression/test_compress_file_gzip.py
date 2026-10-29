import pytest

try:
    import gzip
    import os
    import snappy
    from pyutils_collection.compression_functions.files_compression.compress_file_gzip import compress_file_gzip
    SNAPPY_AVAILABLE = True
except ImportError:
    SNAPPY_AVAILABLE = False
    gzip = None  # type: ignore
    os = None  # type: ignore
    snappy = None  # type: ignore
    compress_file_gzip = None  # type: ignore

pytestmark = [
    pytest.mark.unit,
    pytest.mark.compression,
    pytest.mark.skipif(not SNAPPY_AVAILABLE, reason="python-snappy not installed"),
]


def test_compress_file_gzip_basic_compression(tmp_path) -> None:
    """
    Test case 1: Test the compress_file_gzip function with basic input.
    """
    input_file = tmp_path / "input.txt"
    output_file = tmp_path / "output.gz"
    data = b"hello world"

    with open(input_file, "wb") as f:
        f.write(data)

    compress_file_gzip(str(input_file), str(output_file))

    # Check if the output file exists
    assert output_file.exists(), "Output file should exist"

    # Decompress the data to verify
    with gzip.open(output_file, "rb") as f:
        decompressed_data = f.read()

    assert decompressed_data == data, "Decompressed data should match the original data"


def test_compress_file_gzip_empty_file_compression_and_verification(tmp_path) -> None:
    """
    Test case 2: Test the compress_file_gzip function with an empty file.
    """
    input_file = tmp_path / "input.txt"
    output_file = tmp_path / "output.gz"

    with open(input_file, "wb") as f:
        pass

    compress_file_gzip(str(input_file), str(output_file))

    # Check if the output file exists
    assert output_file.exists(), "Output file should exist"

    # Decompress the data to verify
    with gzip.open(output_file, "rb") as f:
        decompressed_data = f.read()

    assert decompressed_data == b"", "Decompressed data should match the original data"


def test_compress_file_gzip_large_file_compression_and_verification(tmp_path) -> None:
    """
    Test case 3: Test the compress_file_gzip function with a large file.
    """
    input_file = tmp_path / "input.txt"
    output_file = tmp_path / "output.gz"
    data = b"a" * 1000000  # 1 MB of data

    with open(input_file, "wb") as f:
        f.write(data)

    compress_file_gzip(str(input_file), str(output_file))

    # Check if the output file exists
    assert output_file.exists(), "Output file should exist"

    # Check if the compressed file is smaller than the original file
    assert output_file.stat().st_size < input_file.stat().st_size, (
        "Compressed file should be smaller than the original file"
    )

    # Decompress the data to verify
    with gzip.open(output_file, "rb") as f:
        decompressed_data = f.read()

    assert decompressed_data == data, "Decompressed data should match the original data"


def test_compress_file_gzip_invalid_input_file_type(tmp_path) -> None:
    """
    Test case 4: Test the compress_file_gzip function with invalid input file type.
    """
    output_file = tmp_path / "output.gz"

    with pytest.raises(TypeError):
        compress_file_gzip(123, str(output_file))  # type: ignore


def test_compress_file_gzip_invalid_output_file_type(tmp_path) -> None:
    """
    Test case 5: Test the compress_file_gzip function with invalid output file type.
    """
    input_file = tmp_path / "input.txt"
    data = b"hello world"

    with open(input_file, "wb") as f:
        f.write(data)

    with pytest.raises(TypeError):
        compress_file_gzip(str(input_file), 123)  # type: ignore


def test_compress_file_gzip_non_existent_input_file(tmp_path) -> None:
    """
    Test case 6: Test the compress_file_gzip function with a non-existent input file.
    """
    input_file = tmp_path / "non_existent.txt"
    output_file = tmp_path / "output.gz"

    with pytest.raises(FileNotFoundError):
        compress_file_gzip(str(input_file), str(output_file))


def test_compress_file_gzip_io_error_on_output_file(tmp_path) -> None:
    """
    Test case 7: Test the compress_file_gzip function handling of I/O errors on output file.
    """
    input_file = tmp_path / "input.txt"
    output_file = tmp_path / "output.gz"
    data = b"hello world"

    with open(input_file, "wb") as f:
        f.write(data)

    # Simulate an I/O error by making the output directory read-only
    os.chmod(tmp_path, 0o400)

    try:
        with pytest.raises(OSError):
            compress_file_gzip(str(input_file), str(output_file))
    finally:
        # Restore permissions to delete the temporary directory
        os.chmod(tmp_path, 0o600)


def test_compress_file_gzip_no_permission_on_input_file(tmp_path, deny_read_access) -> None:
    """
    Test case 8: Test the compress_file_gzip function with no permission on input file.
    """
    input_file = tmp_path / "input.txt"
    output_file = tmp_path / "output.gz"
    data = b"hello world"

    with open(input_file, "wb") as f:
        f.write(data)

    # Remove all permissions from the input file
    deny_read_access(input_file)

    try:
        with pytest.raises(OSError):
            compress_file_gzip(str(input_file), str(output_file))
    finally:
        # Restore permissions to delete the temporary file
        os.chmod(input_file, 0o600)


def test_compress_file_gzip_io_error_on_read_only_output_file(tmp_path) -> None:
    """
    Test case 9: Test the compress_file_gzip function with read-only output file.
    """
    input_file = tmp_path / "input.txt"
    output_file = tmp_path / "output.gz"
    data = b"hello world"

    with open(input_file, "wb") as f:
        f.write(data)

    with open(output_file, "wb") as f:
        pass

    # Simulate a read-only output file
    os.chmod(output_file, 0o400)

    try:
        with pytest.raises(OSError):
            compress_file_gzip(str(input_file), str(output_file))
    finally:
        # Restore permissions to delete the temporary file
        os.chmod(output_file, 0o600)


def test_compress_file_gzip_read_only_output_directory(tmp_path) -> None:
    """
    Test case 10: Test the compress_file_gzip function with read-only output directory.
    """
    input_file = tmp_path / "input.txt"
    output_dir = tmp_path / "output_dir"
    output_dir.mkdir()
    output_file = output_dir / "output.gz"
    data = b"hello world"

    with open(input_file, "wb") as f:
        f.write(data)

    # Make output directory read-only
    os.chmod(output_dir, 0o444)

    try:
        with pytest.raises(OSError, match="Output location is not writable"):
            compress_file_gzip(str(input_file), str(output_file))
    finally:
        # Restore permissions to delete the directory
        os.chmod(output_dir, 0o755)
