"""Partition files must retain every group without unsafe or colliding names."""

from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

import pytest
from pyutils_collection.serialization_functions.parquet_operations.partition_parquet_by_column import (
    partition_parquet_by_column,
)

pytestmark = [pytest.mark.unit, pytest.mark.serialization]


def test_partition_rejects_colliding_names_before_writing(tmp_path: Path) -> None:
    source = tmp_path / "source.parquet"
    output = tmp_path / "output"
    pq.write_table(pa.table({"group": ["a/b", "a_b"]}), source)
    with pytest.raises(ValueError, match="colliding filenames"):
        partition_parquet_by_column(source, output, "group")
    assert list(output.iterdir()) == []


def test_partition_retains_null_rows(tmp_path: Path) -> None:
    source = tmp_path / "source.parquet"
    output = tmp_path / "output"
    pq.write_table(pa.table({"group": [None, "a", None], "value": [1, 2, 3]}), source)
    counts = partition_parquet_by_column(source, output, "group")
    assert counts == {None: 2, "a": 1}
    assert pq.read_table(output / "None.parquet").column("value").to_pylist() == [1, 3]


def test_partition_retains_nan_rows(tmp_path: Path) -> None:
    source = tmp_path / "source.parquet"
    output = tmp_path / "output"
    pq.write_table(
        pa.table(
            {"group": [float("nan"), 1.0, None, float("nan")], "id": [1, 2, 3, 4]}
        ),
        source,
    )
    counts = partition_parquet_by_column(source, output, "group")
    assert sum(counts.values()) == 4
    assert pq.read_table(output / "nan.parquet").column("id").to_pylist() == [1, 4]


@pytest.mark.parametrize(
    "value", ["C:\\Windows", "a:b", "CON", "NUL", "LPT1", "a?b", "a*b"]
)
def test_partition_filenames_work_on_windows(tmp_path: Path, value: str) -> None:
    source = tmp_path / "source.parquet"
    output = tmp_path / "output"
    pq.write_table(pa.table({"group": [value]}), source)
    assert partition_parquet_by_column(source, output, "group") == {value: 1}
    [partition] = list(output.glob("*.parquet"))
    assert pq.read_table(partition).column("group").to_pylist() == [value]
