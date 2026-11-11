import tempfile
from pathlib import Path

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.file_functions]
from pyutils_collection.file_functions.file_operations.copy_file import copy_file


def test_copy_file_basic_copy() -> None:
    """
    Test case 1: Copy file successfully.
    """
    # Arrange
    with tempfile.TemporaryDirectory() as temp_dir:
        source = Path(temp_dir) / "source.txt"
        destination = Path(temp_dir) / "destination.txt"
        source.write_text("test content")

        # Act
        copy_file(str(source), str(destination))

        # Assert
        assert destination.exists()
        assert destination.read_text() == "test content"


def test_copy_file_overwrites_existing() -> None:
    """
    Test case 2: Copy file overwrites existing destination.
    """
    # Arrange
    with tempfile.TemporaryDirectory() as temp_dir:
        source = Path(temp_dir) / "source.txt"
        destination = Path(temp_dir) / "destination.txt"
        source.write_text("new content")
        destination.write_text("old content")

        # Act
        copy_file(str(source), str(destination))

        # Assert
        assert destination.read_text() == "new content"


def test_copy_file_creates_destination_directory() -> None:
    """
    Test case 3: Creates destination directory if it doesn't exist.
    """
    # Arrange
    with tempfile.TemporaryDirectory() as temp_dir:
        source = Path(temp_dir) / "source.txt"
        destination = Path(temp_dir) / "new_dir" / "destination.txt"
        source.write_text("content")

        # Act
        copy_file(str(source), str(destination))

        # Assert
        assert destination.exists()
        assert destination.read_text() == "content"


def test_copy_file_large_file() -> None:
    """
    Test case 4: Copy large file successfully.
    """
    # Arrange
    with tempfile.TemporaryDirectory() as temp_dir:
        source = Path(temp_dir) / "large_file.txt"
        destination = Path(temp_dir) / "dest_large_file.txt"
        large_content = "x" * 100000  # 100KB
        source.write_text(large_content)

        # Act
        copy_file(str(source), str(destination))

        # Assert
        assert destination.exists()
        assert len(destination.read_text()) == 100000


def test_copy_file_preserves_content() -> None:
    """
    Test case 5: Verify file content is preserved exactly.
    """
    # Arrange
    with tempfile.TemporaryDirectory() as temp_dir:
        source = Path(temp_dir) / "source.txt"
        destination = Path(temp_dir) / "destination.txt"
        content = "Special chars: <>&\"' 世界\n\tTabbed line"
        source.write_text(content, encoding="utf-8")

        # Act
        copy_file(str(source), str(destination))

        # Assert
        assert destination.read_text(encoding="utf-8") == content


def test_copy_file_different_extension() -> None:
    """
    Test case 6: Copy file with different extension.
    """
    # Arrange
    with tempfile.TemporaryDirectory() as temp_dir:
        source = Path(temp_dir) / "source.txt"
        destination = Path(temp_dir) / "destination.dat"
        source.write_text("content")

        # Act
        copy_file(str(source), str(destination))

        # Assert
        assert destination.exists()
        assert destination.read_text() == "content"


def test_copy_file_type_error_non_string_source() -> None:
    """
    Test case 7: TypeError when source is not a string.
    """
    # Act & Assert
    with pytest.raises(TypeError, match="source must be a string"):
        copy_file(123, "destination.txt")  # type: ignore


def test_copy_file_type_error_non_string_destination() -> None:
    """
    Test case 8: TypeError when destination is not a string.
    """
    # Act & Assert
    with pytest.raises(TypeError, match="destination must be a string"):
        copy_file("source.txt", 456)  # type: ignore


def test_copy_file_value_error_empty_source() -> None:
    """
    Test case 9: ValueError when source path is empty.
    """
    # Act & Assert
    with pytest.raises(ValueError, match="source path cannot be empty"):
        copy_file("", "destination.txt")


def test_copy_file_value_error_empty_destination() -> None:
    """
    Test case 10: ValueError when destination path is empty.
    """
    # Act & Assert
    with pytest.raises(ValueError, match="destination path cannot be empty"):
        copy_file("source.txt", "")


def test_copy_file_file_not_found_error() -> None:
    """
    Test case 11: FileNotFoundError when source doesn't exist.
    """
    # Arrange
    non_existent = "/path/that/does/not/exist/file.txt"

    # Act & Assert
    with pytest.raises(FileNotFoundError, match="Source file not found"):
        copy_file(non_existent, "destination.txt")


def test_copy_file_value_error_source_is_directory() -> None:
    """
    Test case 12: ValueError when source is a directory.
    """
    # Arrange
    with tempfile.TemporaryDirectory() as temp_dir:
        source_dir = Path(temp_dir) / "source_dir"
        source_dir.mkdir()

        # Act & Assert
        with pytest.raises(ValueError, match="Source is not a file"):
            copy_file(str(source_dir), "destination.txt")
