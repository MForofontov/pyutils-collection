import os
from pathlib import Path

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.file_functions]
from pyutils_collection.file_functions import check_and_delete_file


def test_check_and_delete_file_existing_file(tmp_path: Path) -> None:
    """
    Test case 1: Test that deleting an existing file removes it from the filesystem.
    """
    file_path: Path = tmp_path / "temp.txt"
    file_path.write_text("data")
    check_and_delete_file(str(file_path))
    assert not file_path.exists(), "Existing file should be removed"


def test_check_and_delete_file_symlink(tmp_path: Path) -> None:
    """
    Test case 2: Test that deleting a symlink removes the link but not the target.
    """
    target: Path = tmp_path / "target.txt"
    target.write_text("content")
    link: Path = tmp_path / "link.txt"
    try:
        os.symlink(target, link)
    except OSError as exc:
        if getattr(exc, "winerror", None) == 1314:
            pytest.skip("Windows account lacks symlink creation privileges")
        raise
    check_and_delete_file(str(link))
    assert not link.exists(), "Symlink should be removed"
    assert target.exists(), "Target file should remain"


def test_check_and_delete_file_nonexistent_file(tmp_path: Path) -> None:
    """
    Test case 3: Test that calling the function with a missing file changes nothing.
    """
    sentinel: Path = tmp_path / "sentinel.txt"
    sentinel.write_text("a")
    before: set[str] = set(os.listdir(tmp_path))
    check_and_delete_file(str(tmp_path / "missing.txt"))
    after: set[str] = set(os.listdir(tmp_path))
    assert before == after, "Filesystem should remain unchanged"


def test_check_and_delete_file_directory_path(tmp_path: Path) -> None:
    """
    Test case 4: Test that supplying a directory path does not delete the directory.
    """
    dir_path: Path = tmp_path / "folder"
    dir_path.mkdir()
    check_and_delete_file(str(dir_path))
    assert dir_path.exists(), "Directory should not be removed"


def test_check_and_delete_file_permission_error(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    Test case 5: Test that attempting to delete a read-only file raises PermissionError.
    """
    file_path: Path = tmp_path / "readonly.txt"
    file_path.write_text("data")
    file_path.chmod(0o400)

    def mock_remove(path: str) -> None:
        raise PermissionError

    monkeypatch.setattr(os, "remove", mock_remove)
    with pytest.raises(PermissionError):
        check_and_delete_file(str(file_path))
    assert file_path.exists(), "File should remain when deletion is not permitted"
