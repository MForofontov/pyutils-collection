import os
import tempfile

import pytest

try:
    import psutil
    from pyutils_collection.cli_functions.list_directories import list_directories
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None  # type: ignore
    list_directories = None  # type: ignore

pytestmark = [
    pytest.mark.unit,
    pytest.mark.cli_functions,
    pytest.mark.skipif(not PSUTIL_AVAILABLE, reason="psutil not installed"),
]


def test_list_directories_valid_directory() -> None:
    """
    Test case 1: Test list_directories function with a valid directory returns correct directory list.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create some test directories
        dir1 = os.path.join(temp_dir, "dir1")
        dir2 = os.path.join(temp_dir, "dir2")
        hidden_dir = os.path.join(temp_dir, ".hidden_dir")

        for dir_path in [dir1, dir2, hidden_dir]:
            os.mkdir(dir_path)

        # Test without hidden directories
        directories = list_directories(temp_dir, include_hidden=False)
        assert isinstance(directories, list)
        assert "dir1" in directories
        assert "dir2" in directories
        assert ".hidden_dir" not in directories
        assert len(directories) == 2

        # Test with hidden directories
        dirs_with_hidden = list_directories(temp_dir, include_hidden=True)
        assert ".hidden_dir" in dirs_with_hidden
        assert len(dirs_with_hidden) == 3


def test_list_directories_empty_directory() -> None:
    """
    Test case 2: Test list_directories function with an empty directory returns empty list.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        directories = list_directories(temp_dir)
        assert isinstance(directories, list)
        assert len(directories) == 0


def test_list_directories_with_files() -> None:
    """
    Test case 3: Test list_directories function ignores files and only returns directories.
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create a directory and a file
        dir1 = os.path.join(temp_dir, "dir1")
        file1 = os.path.join(temp_dir, "file1.txt")

        os.mkdir(dir1)
        with open(file1, "w") as f:
            f.write("test content")

        directories = list_directories(temp_dir)
        assert "dir1" in directories
        assert "file1.txt" not in directories
        assert len(directories) == 1


def test_list_directories_nonexistent_directory_error() -> None:
    """
    Test case 4: Test list_directories function with a nonexistent directory raises FileNotFoundError.
    """
    with pytest.raises(FileNotFoundError, match="Directory does not exist"):
        list_directories("/nonexistent/directory")


def test_list_directories_not_a_directory_error() -> None:
    """
    Test case 5: Test list_directories function with a file instead of directory raises NotADirectoryError.
    """
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        try:
            with pytest.raises(NotADirectoryError, match="Path is not a directory"):
                list_directories(temp_file.name)
        finally:
            temp_file.close()
            os.unlink(temp_file.name)


def test_list_directories_invalid_type_error() -> None:
    """
    Test case 6: Test list_directories function with invalid input type raises TypeError.
    """
    with pytest.raises(TypeError, match="directory_path must be a string"):
        list_directories(123)

    with pytest.raises(TypeError):
        list_directories(None)
