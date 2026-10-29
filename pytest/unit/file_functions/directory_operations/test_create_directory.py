import os
from pathlib import Path

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.file_functions]
from pyutils_collection.file_functions import create_directory


def test_create_new_directory(tmp_path: Path) -> None:
    """
    Test case 1: Creating a new directory should return True and create the directory.
    """
    new_dir: Path = tmp_path / "new"
    result: bool = create_directory(str(new_dir))
    assert result is True, "Should return True for new directory"
    assert new_dir.exists(), "Directory should exist after creation"
    # Cleanup
    if new_dir.exists():
        new_dir.rmdir()


def test_existing_directory(tmp_path: Path) -> None:
    """
    Test case 2: Calling on an existing directory should return False.
    """
    existing_dir: Path = tmp_path / "existing"
    create_directory(str(existing_dir))
    result: bool = create_directory(str(existing_dir))
    assert result is False, "Should return False if directory already exists"
    # Cleanup
    if existing_dir.exists():
        existing_dir.rmdir()


def test_path_is_existing_file(tmp_path: Path) -> None:
    """
    Test case 3: Calling on a path that points to a file should return False and keep the file.
    """
    file_path: Path = tmp_path / "target"
    file_path.write_text("data")
    result: bool = create_directory(str(file_path))
    assert result is False, "Should return False if path already exists as a file"
    assert file_path.exists(), "Existing file should remain after call"
    # Cleanup
    if file_path.exists():
        file_path.unlink()


def test_nested_path_creation(tmp_path: Path) -> None:
    """
    Test case 4: Creating nested directories should succeed.
    """
    nested_dir: Path = tmp_path / "level1" / "level2" / "level3"
    result: bool = create_directory(str(nested_dir))
    assert result is True, "Should return True when creating nested path"
    assert nested_dir.exists(), "Nested directory should exist after creation"
    # Cleanup
    if nested_dir.exists():
        nested_dir.rmdir()
    parent2 = nested_dir.parent
    if parent2.exists():
        parent2.rmdir()
    parent1 = parent2.parent
    if parent1.exists():
        parent1.rmdir()


def test_permission_error_read_only_parent(tmp_path: Path) -> None:
    """
    Test case 5: Attempting to create a directory in a read-only parent should raise PermissionError.
    """
    pwd = pytest.importorskip("pwd", reason="Unix ownership test")
    parent_dir: Path = tmp_path / "parent"
    parent_dir.mkdir()
    parent_dir.chmod(0o555)
    child_dir: Path = parent_dir / "child"

    # Skip test if not running as root or if setegid/seteuid is not permitted
    if os.geteuid() != 0:
        pytest.skip(
            "Skipping test: requires root privileges to change effective UID/GID."
        )
    try:
        uid = pwd.getpwnam("nobody").pw_uid
        gid = pwd.getpwnam("nobody").pw_gid
        original_uid = os.geteuid()
        original_gid = os.getegid()
        os.setegid(gid)
        os.seteuid(uid)
        with pytest.raises(PermissionError):
            create_directory(str(child_dir))
    finally:
        try:
            os.seteuid(original_uid)
            os.setegid(original_gid)
        except Exception:
            pass
        parent_dir.chmod(0o755)
        # Cleanup
        if child_dir.exists():
            child_dir.rmdir()
        if parent_dir.exists():
            parent_dir.rmdir()
