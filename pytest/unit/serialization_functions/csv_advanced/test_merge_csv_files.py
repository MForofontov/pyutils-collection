"""
Unit tests for merge_csv_files function.
"""

import csv
import tempfile
from pathlib import Path

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.serialization]

try:
    from pyutils_collection.serialization_functions.csv_advanced.merge_csv_files import (
        merge_csv_files,
    )

    IMPORT_SUCCESS = True
except ImportError:
    IMPORT_SUCCESS = False
    merge_csv_files = None  # type: ignore

pytestmark = [
    pytest.mark.skipif(not IMPORT_SUCCESS, reason="dependencies not installed"),
    *pytestmark,
]


def test_merge_csv_files_basic_merge() -> None:
    """
    Test basic merge of multiple CSV files with headers.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test CSV files
        file1 = Path(tmpdir) / "data1.csv"
        file2 = Path(tmpdir) / "data2.csv"
        output = Path(tmpdir) / "merged.csv"

        # Write test data
        with open(file1, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["name", "age"])
            writer.writerow(["Alice", "30"])
            writer.writerow(["Bob", "25"])

        with open(file2, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["name", "age"])
            writer.writerow(["Charlie", "35"])

        # Merge files
        rows = merge_csv_files([file1, file2], output)

        assert rows == 3
        assert output.exists()

        # Verify merged content
        with open(output, newline="") as f:
            reader = csv.reader(f)
            data = list(reader)
            assert len(data) == 4  # header + 3 rows
            assert data[0] == ["name", "age"]
            assert data[1] == ["Alice", "30"]
            assert data[2] == ["Bob", "25"]
            assert data[3] == ["Charlie", "35"]


def test_merge_csv_files_three_files() -> None:
    """
    Test merging three files successfully.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        files = [Path(tmpdir) / f"data{i}.csv" for i in range(3)]
        output = Path(tmpdir) / "merged.csv"

        for idx, file_path in enumerate(files):
            with open(file_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["id", "value"])
                writer.writerow([str(idx), f"value{idx}"])

        rows = merge_csv_files(files, output)

        assert rows == 3
        with open(output, newline="") as f:
            reader = csv.reader(f)
            data = list(reader)
            assert len(data) == 4  # header + 3 rows


def test_merge_csv_files_skip_duplicates() -> None:
    """
    Test merge with duplicate row detection.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        file1 = Path(tmpdir) / "data1.csv"
        file2 = Path(tmpdir) / "data2.csv"
        output = Path(tmpdir) / "merged.csv"

        with open(file1, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "value"])
            writer.writerow(["1", "A"])
            writer.writerow(["2", "B"])

        with open(file2, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "value"])
            writer.writerow(["2", "B"])  # Duplicate
            writer.writerow(["3", "C"])

        rows = merge_csv_files([file1, file2], output, skip_duplicates=True)

        assert rows == 3  # Only unique rows
        with open(output, newline="") as f:
            reader = csv.reader(f)
            data = list(reader)
            assert len(data) == 4  # header + 3 unique rows


def test_merge_csv_files_no_header() -> None:
    """
    Test merge files without headers.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        file1 = Path(tmpdir) / "data1.csv"
        file2 = Path(tmpdir) / "data2.csv"
        output = Path(tmpdir) / "merged.csv"

        with open(file1, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Alice", "30"])
            writer.writerow(["Bob", "25"])

        with open(file2, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Charlie", "35"])

        rows = merge_csv_files([file1, file2], output, has_header=False)

        assert rows == 3
        with open(output, newline="") as f:
            reader = csv.reader(f)
            data = list(reader)
            assert len(data) == 3  # No header, just data


def test_merge_csv_files_empty_file_skipped() -> None:
    """
    Test that empty files are skipped during merge.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        file1 = Path(tmpdir) / "data1.csv"
        file2 = Path(tmpdir) / "data2.csv"
        file3 = Path(tmpdir) / "empty.csv"
        output = Path(tmpdir) / "merged.csv"

        with open(file1, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "value"])
            writer.writerow(["1", "A"])

        with open(file2, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "value"])
            writer.writerow(["2", "B"])

        # Create empty file
        with open(file3, "w", newline="") as f:
            pass

        rows = merge_csv_files([file1, file2, file3], output)

        assert rows == 2


def test_merge_csv_files_invalid_type_input_files() -> None:
    """
    Test TypeError for invalid input_files type.
    """
    with pytest.raises(TypeError, match="input_files must be a sequence"):
        merge_csv_files("not_a_list", "output.csv")  # type: ignore


def test_merge_csv_files_invalid_type_output_file() -> None:
    """
    Test TypeError for invalid output_file type.
    """
    with pytest.raises(TypeError, match="output_file must be str or Path"):
        merge_csv_files(["/some/file.csv"], 123)  # type: ignore


def test_merge_csv_files_empty_input_error() -> None:
    """
    Test ValueError for empty input list.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        output = Path(tmpdir) / "merged.csv"

        with pytest.raises(ValueError, match="input_files cannot be empty"):
            merge_csv_files([], output)


def test_merge_csv_files_file_not_found() -> None:
    """
    Test FileNotFoundError for non-existent file.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        output = Path(tmpdir) / "merged.csv"

        with pytest.raises(FileNotFoundError, match="Input file not found"):
            merge_csv_files(["/nonexistent/file.csv"], output)


def test_merge_csv_files_header_mismatch_error() -> None:
    """
    Test ValueError for mismatched headers.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        file1 = Path(tmpdir) / "data1.csv"
        file2 = Path(tmpdir) / "data2.csv"
        output = Path(tmpdir) / "merged.csv"

        with open(file1, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["name", "age"])
            writer.writerow(["Alice", "30"])

        with open(file2, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "value"])  # Different header
            writer.writerow(["1", "A"])

        with pytest.raises(ValueError, match="Header mismatch"):
            merge_csv_files([file1, file2], output)


def test_csv_ignores_leading_empty_file(tmp_path: Path) -> None:
    empty, data, output = (
        tmp_path / name for name in ("empty.csv", "data.csv", "out.csv")
    )
    empty.write_text("")
    data.write_text("name\nAda\n")
    assert merge_csv_files([empty, data], output) == 1
    assert output.read_text() == "name\nAda\n"


@pytest.mark.parametrize("existing", [True, False])
def test_csv_header_failure_preserves_destination(
    tmp_path: Path, existing: bool
) -> None:
    first, second, output = (
        tmp_path / name for name in ("first.csv", "second.csv", "out.csv")
    )
    first.write_text("name\nAda\n")
    second.write_text("wrong\nBob\n")
    if existing:
        output.write_text("original")
    before = set(tmp_path.iterdir())
    with pytest.raises(ValueError, match="Header mismatch"):
        merge_csv_files([first, second], output)
    assert set(tmp_path.iterdir()) == before
    if existing:
        assert output.read_text() == "original"


def test_csv_output_can_be_input(tmp_path: Path) -> None:
    first, second = tmp_path / "first.csv", tmp_path / "second.csv"
    first.write_text("name\nAda\n")
    second.write_text("name\nBob\n")
    assert merge_csv_files([first, second], first) == 2
    assert first.read_text() == "name\nAda\nBob\n"


@pytest.mark.parametrize("failure", ["fsync", "replace"])
def test_csv_io_failure_preserves_output(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, failure: str
) -> None:
    import os

    source, output = tmp_path / "source.csv", tmp_path / "output.csv"
    source.write_text("name\nAda\n")
    output.write_text("original")
    error = OSError("injected failure")

    def fail(*args: object, **kwargs: object) -> None:
        raise error

    with monkeypatch.context() as patch:
        patch.setattr(os, failure, fail)
        with pytest.raises(OSError) as caught:
            merge_csv_files([source], output)
    assert caught.value is error
    assert output.read_text() == "original"
    assert set(tmp_path.iterdir()) == {source, output}


def test_csv_all_empty_files(tmp_path: Path) -> None:
    source, output = tmp_path / "source.csv", tmp_path / "output.csv"
    source.write_text("")
    assert merge_csv_files([source, source], output) == 0
    assert output.read_bytes() == b""
