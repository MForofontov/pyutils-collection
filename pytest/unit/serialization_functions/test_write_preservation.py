"""Writers must preserve inputs and destinations when an operation fails."""

import importlib
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

import pytest
from pyutils_collection.serialization_functions.csv_advanced.transform_csv_columns import (
    transform_csv_columns,
)
from pyutils_collection.serialization_functions.parquet_operations.append_parquet import (
    append_parquet,
)
from pyutils_collection.serialization_functions.excel_operations.transpose_excel_data import (
    transpose_excel_data,
)

pytestmark = [pytest.mark.unit, pytest.mark.serialization]


def test_csv_transform_in_place(tmp_path: Path) -> None:
    source = tmp_path / "data.csv"
    source.write_text("name,value\na,1\nb,2\n", encoding="utf-8")
    assert transform_csv_columns(source, source, transformers={"value": int}) == 2
    assert source.read_text(encoding="utf-8").splitlines() == [
        "name,value",
        "a,1",
        "b,2",
    ]


@pytest.mark.parametrize("in_place", [False, True])
@pytest.mark.parametrize("failure", ["transformer", "filter"])
def test_csv_failure_preserves_destination(tmp_path: Path, in_place, failure) -> None:
    source = tmp_path / "source.csv"
    source.write_text("value\n1\nbad\n", encoding="utf-8")
    destination = source if in_place else tmp_path / "output.csv"
    if not in_place:
        destination.write_bytes(b"original output")
    original = destination.read_bytes()
    options = (
        {"transformers": {"value": int}}
        if failure == "transformer"
        else {"filter_func": lambda row: int(row["value"]) > 0}
    )
    with pytest.raises(ValueError):
        transform_csv_columns(source, destination, **options)
    assert destination.read_bytes() == original
    assert sorted(path.name for path in tmp_path.iterdir()) == (
        ["source.csv"] if in_place else ["output.csv", "source.csv"]
    )


@pytest.mark.parametrize("existing", [False, True])
def test_append_parquet_failure_preserves_destination(tmp_path, monkeypatch, existing):
    destination = tmp_path / "data.parquet"
    if existing:
        pq.write_table(pa.table({"value": [1]}), destination)
    original = destination.read_bytes() if existing else None
    module = importlib.import_module(append_parquet.__module__)

    def fail_after_write(table, where, **kwargs):
        Path(where).write_bytes(b"partial parquet")
        raise OSError("disk write failed")

    monkeypatch.setattr(module.pq, "write_table", fail_after_write)
    with pytest.raises(OSError, match="disk write failed"):
        append_parquet([{"value": 2}], str(destination))
    assert (destination.read_bytes() if destination.exists() else None) == original
    assert list(tmp_path.iterdir()) == ([destination] if existing else [])


def test_transpose_failure_preserves_destination(tmp_path, monkeypatch):
    import openpyxl

    source, destination = tmp_path / "source.xlsx", tmp_path / "output.xlsx"
    workbook = openpyxl.Workbook()
    workbook.active.append([1, 2])
    workbook.save(source)
    workbook.close()
    destination.write_bytes(b"previous output")

    def fail_save(self, filename):
        Path(filename).write_bytes(b"partial workbook")
        raise OSError("save failed")

    monkeypatch.setattr(openpyxl.Workbook, "save", fail_save)
    with pytest.raises(OSError, match="save failed"):
        transpose_excel_data(source, destination)
    assert destination.read_bytes() == b"previous output"
    assert sorted(path.name for path in tmp_path.iterdir()) == [
        "output.xlsx",
        "source.xlsx",
    ]


@pytest.mark.parametrize("failure", ["sync", "replace"])
def test_csv_publish_failure_preserves_destination(tmp_path, monkeypatch, failure):
    source, destination = tmp_path / "source.csv", tmp_path / "output.csv"
    source.write_text("value\n1\n", encoding="utf-8")
    destination.write_bytes(b"previous output")

    def fail(*args):
        raise OSError("publish failed")

    monkeypatch.setattr("os.fsync" if failure == "sync" else "os.replace", fail)
    with pytest.raises(OSError, match="publish failed"):
        transform_csv_columns(source, destination)
    assert destination.read_bytes() == b"previous output"
    assert sorted(path.name for path in tmp_path.iterdir()) == [
        "output.csv",
        "source.csv",
    ]
