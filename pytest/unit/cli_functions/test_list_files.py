import os
import tempfile

import pytest

try:
    import psutil
    from pyutils_collection.cli_functions.list_files import list_files
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None  # type: ignore
    list_files = None  # type: ignore

pytestmark = [
    pytest.mark.unit,
    pytest.mark.cli_functions,
    pytest.mark.skipif(not PSUTIL_AVAILABLE, reason="psutil not installed"),
]


def test_list_files_valid_directory() -> None:
    """
    Test case 1: Test list_files function with a valid directory returns correct file list.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create some test files
        file1 = os.path.join(temp_dir, "file1.txt")
        file2 = os.path.join(temp_dir, "file2.py")
        hidden_file = os.path.join(temp_dir, ".hidden_file")

        for file_path in [file1, file2, hidden_file]:
            with open(file_path, "w") as f:
                f.write("test content")

        # Test without hidden files
        files = list_files(temp_dir, include_hidden=False)
        assert isinstance(files, list)
        assert "file1.txt" in files
        assert "file2.py" in files
        assert ".hidden_file" not in files
        assert len(files) == 2

        # Test with hidden files
        files_with_hidden = list_files(temp_dir, include_hidden=True)
        assert ".hidden_file" in files_with_hidden
        assert len(files_with_hidden) == 3


def test_list_files_empty_directory() -> None:
    """
    Test case 2: Test list_files function with an empty directory returns empty list.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        files = list_files(temp_dir)
        assert isinstance(files, list)
        assert len(files) == 0


def test_list_files_with_subdirectories() -> None:
    """
    Test case 3: Test list_files function ignores subdirectories and only returns files.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a file and a subdirectory
        file1 = os.path.join(temp_dir, "file1.txt")
        subdir = os.path.join(temp_dir, "subdir")

        with open(file1, "w") as f:
            f.write("test content")
        os.mkdir(subdir)

        files = list_files(temp_dir)
        assert "file1.txt" in files
        assert "subdir" not in files
        assert len(files) == 1


def test_list_files_nonexistent_directory_error() -> None:
    """
    Test case 4: Test list_files function with a nonexistent directory raises FileNotFoundError.
    """
    with pytest.raises(FileNotFoundError, match="Directory does not exist"):
        list_files("/nonexistent/directory")


def test_list_files_not_a_directory_error() -> None:
    """
    Test case 5: Test list_files function with a file instead of directory raises NotADirectoryError.
    """
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        try:
            with pytest.raises(NotADirectoryError, match="Path is not a directory"):
                list_files(temp_file.name)
        finally:
            temp_file.close()
            os.unlink(temp_file.name)


def test_list_files_invalid_type_error() -> None:
    """
    Test case 6: Test list_files function with invalid input type raises TypeError.
    """
    with pytest.raises(TypeError, match="directory_path must be a string"):
        list_files(123)

    with pytest.raises(TypeError):
        list_files(None)
