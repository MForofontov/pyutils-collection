import pytest

try:
    import os
    import zipfile
    import snappy
    from pyutils_collection.compression_functions.files_compression.decompress_file_zip import decompress_file_zip
    SNAPPY_AVAILABLE = True
except ImportError:
    SNAPPY_AVAILABLE = False
    os = None  # type: ignore
    zipfile = None  # type: ignore
    snappy = None  # type: ignore
    decompress_file_zip = None  # type: ignore

pytestmark = [
    pytest.mark.unit,
    pytest.mark.compression,
    pytest.mark.skipif(not SNAPPY_AVAILABLE, reason="python-snappy not installed"),
]



def test_decompress_file_zip_basic(tmp_path) -> None:
    """
    Test case 1: Test the decompress_file_zip function with basic input.
    """
    compressed_file = tmp_path / "input.zip"
    output_dir = tmp_path / "output"
    data = b"hello world"

    # Create a zip-compressed file
    os.makedirs(output_dir)
    input_file = tmp_path / "input.txt"
    with open(input_file, "wb") as f:
        f.write(data)

    with zipfile.ZipFile(compressed_file, "w") as zipf:
        zipf.write(input_file, arcname="input.txt")

    decompress_file_zip(str(compressed_file), str(output_dir))

    # Check if the output file exists
    extracted_file = output_dir / "input.txt"
    assert extracted_file.exists(), "Extracted file should exist"

    # Read the decompressed data to verify
    with open(extracted_file, "rb") as f:
        decompressed_data = f.read()

    assert decompressed_data == data, "Decompressed data should match the original data"


def test_decompress_file_zip_empty_file(tmp_path) -> None:
    """
    Test case 2: Test the decompress_file_zip function with an empty file.
    """
    compressed_file = tmp_path / "input.zip"
    output_dir = tmp_path / "output"

    # Create an empty zip-compressed file
    with zipfile.ZipFile(compressed_file, "w"):
        pass

    decompress_file_zip(str(compressed_file), str(output_dir))

    # Check if the output directory exists and is empty
    assert os.path.exists(output_dir), "Output directory should exist"
    assert os.listdir(output_dir) == [], "Output directory should be empty"


def test_decompress_file_zip_large_file(tmp_path) -> None:
    """
    Test case 3: Test the decompress_file_zip function with a large file.
    """
    compressed_file = tmp_path / "input.zip"
    output_dir = tmp_path / "output"
    data = b"a" * 1000000  # 1 MB of data

    # Create a zip-compressed file
    os.makedirs(output_dir)
    input_file = tmp_path / "input.txt"
    with open(input_file, "wb") as f:
        f.write(data)

    with zipfile.ZipFile(compressed_file, "w") as zipf:
        zipf.write(input_file, arcname="input.txt")

    decompress_file_zip(str(compressed_file), str(output_dir))

    # Check if the output file exists
    extracted_file = output_dir / "input.txt"
    assert extracted_file.exists(), "Extracted file should exist"

    # Read the decompressed data to verify
    with open(extracted_file, "rb") as f:
        decompressed_data = f.read()

    assert decompressed_data == data, "Decompressed data should match the original data"


def test_decompress_file_zip_invalid_input_type(tmp_path) -> None:
    """
    Test case 4: Test the decompress_file_zip function with invalid input file type.
    """
    output_dir = tmp_path / "output"

    with pytest.raises(TypeError):
        decompress_file_zip(123, str(output_dir))  # type: ignore


def test_decompress_file_zip_invalid_output_type(tmp_path) -> None:
    """
    Test case 5: Test the decompress_file_zip function with invalid output directory type.
    """
    compressed_file = tmp_path / "input.zip"
    data = b"hello world"

    # Create a zip-compressed file
    input_file = tmp_path / "input.txt"
    with open(input_file, "wb") as f:
        f.write(data)

    with zipfile.ZipFile(compressed_file, "w") as zipf:
        zipf.write(input_file, arcname="input.txt")

    with pytest.raises(TypeError):
        decompress_file_zip(str(compressed_file), 123)  # type: ignore


def test_decompress_file_zip_non_existent_input_file(tmp_path) -> None:
    """
    Test case 6: Test the decompress_file_zip function with a non-existent input file.
    """
    compressed_file = tmp_path / "non_existent.zip"
    output_dir = tmp_path / "output"

    with pytest.raises(FileNotFoundError):
        decompress_file_zip(str(compressed_file), str(output_dir))


def test_decompress_file_zip_io_error_on_output_dir(tmp_path) -> None:
    """
    Test case 7: Test the decompress_file_zip function handling of I/O errors on output directory.
    """
    compressed_file = tmp_path / "input.zip"
    output_dir = tmp_path / "output"
    data = b"hello world"

    # Create a zip-compressed file
    input_file = tmp_path / "input.txt"
    with open(input_file, "wb") as f:
        f.write(data)

    with zipfile.ZipFile(compressed_file, "w") as zipf:
        zipf.write(input_file, arcname="input.txt")

    # Simulate an I/O error by making the output directory read-only
    os.makedirs(output_dir)
    os.chmod(output_dir, 0o400)

    try:
        with pytest.raises(OSError):
            decompress_file_zip(str(compressed_file), str(output_dir))
    finally:
        # Restore permissions to delete the temporary directory
        os.chmod(output_dir, 0o600)


def test_decompress_file_zip_no_permission_on_input_file(tmp_path, deny_read_access) -> None:
    """
    Test case 8: Test the decompress_file_zip function with no permission on input file.
    """
    compressed_file = tmp_path / "input.zip"
    output_dir = tmp_path / "output"
    data = b"hello world"

    # Create a zip-compressed file
    input_file = tmp_path / "input.txt"
    with open(input_file, "wb") as f:
        f.write(data)

    with zipfile.ZipFile(compressed_file, "w") as zipf:
        zipf.write(input_file, arcname="input.txt")

    # Remove all permissions from the input file
    deny_read_access(compressed_file)

    try:
        with pytest.raises(OSError):
            decompress_file_zip(str(compressed_file), str(output_dir))
    finally:
        # Restore permissions to delete the temporary file
        os.chmod(compressed_file, 0o600)


def test_decompress_file_zip_io_error_on_read_only_output_dir(tmp_path) -> None:
    """
    Test case 9: Test the decompress_file_zip function with read-only output directory.
    """
    compressed_file = tmp_path / "input.zip"
    output_dir = tmp_path / "output"
    data = b"hello world"

    # Create a zip-compressed file
    input_file = tmp_path / "input.txt"
    with open(input_file, "wb") as f:
        f.write(data)

    with zipfile.ZipFile(compressed_file, "w") as zipf:
        zipf.write(input_file, arcname="input.txt")

    os.makedirs(output_dir)

    # Simulate a read-only output directory
    os.chmod(output_dir, 0o400)

    try:
        with pytest.raises(OSError):
            decompress_file_zip(str(compressed_file), str(output_dir))
    finally:
        # Restore permissions to delete the temporary directory
        os.chmod(output_dir, 0o600)
