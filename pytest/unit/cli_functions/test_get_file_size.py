import os
import tempfile

import pytest

try:
    import psutil
    from pyutils_collection.cli_functions.get_file_size import get_file_size
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None  # type: ignore
    get_file_size = None  # type: ignore

pytestmark = [
    pytest.mark.unit,
    pytest.mark.cli_functions,
    pytest.mark.skipif(not PSUTIL_AVAILABLE, reason="psutil not installed"),
]


def test_get_file_size_valid_file() -> None:
    """
    Test case 1: Test get_file_size function with a valid file returns correct size.
    """
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        # Write some content to the file
        content = b"Hello, World!"
        temp_file.write(content)
        temp_file.flush()

        try:
            size = get_file_size(temp_file.name)
            assert size == len(content)
            assert isinstance(size, int)
        finally:
            temp_file.close()
            os.unlink(temp_file.name)


def test_get_file_size_empty_file() -> None:
    """
    Test case 2: Test get_file_size function with an empty file returns zero.
    """
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        try:
            size = get_file_size(temp_file.name)
            assert size == 0
        finally:
            temp_file.close()
            os.unlink(temp_file.name)


def test_get_file_size_nonexistent_file_error() -> None:
    """
    Test case 3: Test get_file_size function with a nonexistent file raises FileNotFoundError.
    """
    with pytest.raises(FileNotFoundError, match="File does not exist"):
        get_file_size("/nonexistent/file.txt")


def test_get_file_size_directory_error() -> None:
    """
    Test case 4: Test get_file_size function with a directory raises IsADirectoryError.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        with pytest.raises(IsADirectoryError, match="Path is a directory"):
            get_file_size(temp_dir)


def test_get_file_size_invalid_type_error() -> None:
    """
    Test case 5: Test get_file_size function with invalid input type raises TypeError.
    """
    with pytest.raises(TypeError, match="file_path must be a string"):
        get_file_size(123)

    with pytest.raises(TypeError):
        get_file_size(None)


def test_get_file_size_large_file() -> None:
    """
    Test case 6: Test get_file_size with larger file.
    """
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        # Write 1MB of data
        content = b"x" * (1024 * 1024)
        temp_file.write(content)
        temp_file.flush()

        try:
            size = get_file_size(temp_file.name)
            assert size == len(content)
            assert size == 1024 * 1024
        finally:
            temp_file.close()
            os.unlink(temp_file.name)
