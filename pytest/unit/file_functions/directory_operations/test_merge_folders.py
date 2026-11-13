import shutil
from pathlib import Path

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.file_functions]
from pyutils_collection.file_functions import merge_folders


def test_merge_folders_combines_structure(tmp_path: Path) -> None:
    """
    Test case 1: Merging two folders should combine their contents.
    """
    folder1: Path = tmp_path / "folder1"
    folder2: Path = tmp_path / "folder2"
    output: Path = tmp_path / "merged"
    folder1.mkdir()
    folder2.mkdir()
    (folder1 / "file1.txt").write_text("a")
    (folder2 / "file2.txt").write_text("b")
    merge_folders(str(folder1), str(folder2), str(output))
    assert (output / "file1.txt").read_text() == "a", "File from folder1 should exist"
    assert (output / "file2.txt").read_text() == "b", "File from folder2 should exist"


def test_merge_folders_conflicting_filenames(tmp_path: Path) -> None:
    """
    Test case 2: Conflicting filenames should produce files with a _copy suffix.
    """
    folder1: Path = tmp_path / "folder1"
    folder2: Path = tmp_path / "folder2"
    output: Path = tmp_path / "merged"
    folder1.mkdir()
    folder2.mkdir()
    (folder1 / "same.txt").write_text("one")
    (folder2 / "same.txt").write_text("two")
    merge_folders(str(folder1), str(folder2), str(output))
    assert (output / "same.txt").read_text() == "one", "Original file should be copied"
    assert (output / "same_copy.txt").read_text() == "two", (
        "Conflicting file should be renamed with _copy"
    )


def test_merge_folders_nested_directories(tmp_path: Path) -> None:
    """
    Test case 3: Nested directory structures should be preserved in the merge.
    """
    folder1: Path = tmp_path / "folder1"
    folder2: Path = tmp_path / "folder2"
    output: Path = tmp_path / "merged"
    (folder1 / "sub1").mkdir(parents=True)
    (folder2 / "sub2").mkdir(parents=True)
    (folder1 / "sub1" / "a.txt").write_text("a")
    (folder2 / "sub2" / "b.txt").write_text("b")
    merge_folders(str(folder1), str(folder2), str(output))
    assert (output / "sub1" / "a.txt").read_text() == "a", (
        "File in nested sub1 should be copied"
    )
    assert (output / "sub2" / "b.txt").read_text() == "b", (
        "File in nested sub2 should be copied"
    )


def test_merge_folders_missing_folder1(tmp_path: Path) -> None:
    """
    Test case 4: Missing folder1 should raise FileNotFoundError.
    """
    missing_folder1: Path = tmp_path / "missing1"
    folder2: Path = tmp_path / "folder2"
    output: Path = tmp_path / "merged"
    folder2.mkdir()
    (folder2 / "file2.txt").write_text("b")
    with pytest.raises(FileNotFoundError, match="Source folder not found"):
        merge_folders(str(missing_folder1), str(folder2), str(output))


def test_merge_folders_missing_folder2(tmp_path: Path) -> None:
    """
    Test case 5: Missing folder2 should raise FileNotFoundError.
    """
    folder1: Path = tmp_path / "folder1"
    missing_folder2: Path = tmp_path / "missing2"
    output: Path = tmp_path / "merged"
    folder1.mkdir()
    (folder1 / "file1.txt").write_text("a")
    with pytest.raises(FileNotFoundError, match="Source folder not found"):
        merge_folders(str(folder1), str(missing_folder2), str(output))


def test_merge_folders_read_only_output_dir(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """
    Test case 6: A read-only output directory should raise PermissionError.
    """
    folder1: Path = tmp_path / "folder1"
    folder2: Path = tmp_path / "folder2"
    output: Path = tmp_path / "merged"
    folder1.mkdir()
    folder2.mkdir()
    output.mkdir()
    (folder1 / "file1.txt").write_text("a")
    (folder2 / "file2.txt").write_text("b")

    def mock_copy2(src: str, dst: str, follow_symlinks: bool = True) -> None:
        raise PermissionError("Read-only directory")

    monkeypatch.setattr(shutil, "copy2", mock_copy2)
    with pytest.raises(PermissionError):
        merge_folders(str(folder1), str(folder2), str(output))


def test_merge_preserves_existing_conflicts(tmp_path: Path) -> None:
    first, second, output = (tmp_path / name for name in ("first", "second", "output"))
    for folder in (first, second, output):
        folder.mkdir()
    (first / "a.txt").write_text("first")
    (second / "a.txt").write_text("second")
    (output / "a.txt").write_text("existing")
    (output / "a_copy.txt").write_text("existing copy")
    merge_folders(str(first), str(second), str(output))
    assert (output / "a_copy.txt").read_text() == "existing copy"
    assert {p.read_text() for p in output.iterdir()} == {
        "first",
        "second",
        "existing",
        "existing copy",
    }


@pytest.mark.parametrize("nested", [False, True])
def test_folder_output_must_not_overlap_source(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, nested: bool
) -> None:
    import os

    first, second = tmp_path / "first", tmp_path / "second"
    first.mkdir()
    second.mkdir()
    output = first / "output" if nested else first

    def forbidden_walk(*args: object, **kwargs: object) -> None:
        pytest.fail("overlap must be rejected before traversal")

    monkeypatch.setattr(os, "walk", forbidden_walk)
    with pytest.raises(ValueError, match="overlap"):
        merge_folders(str(first), str(second), str(output))
    assert list(first.iterdir()) == []
