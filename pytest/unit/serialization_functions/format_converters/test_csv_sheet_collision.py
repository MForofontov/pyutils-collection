"""Batch exports must reject overlapping sheet destinations before writing."""

from pathlib import Path

import openpyxl
import pytest

from pyutils_collection.serialization_functions.format_converters import excel_to_csv_batch

pytestmark = [pytest.mark.unit, pytest.mark.serialization]


def test_colliding_sheet_names_preserve_existing_output(tmp_path: Path) -> None:
    source = tmp_path / "input.xlsx"
    output = tmp_path / "output"
    output.mkdir()
    destination = output / "a_b.csv"
    destination.write_bytes(b"previous export")
    workbook = openpyxl.Workbook()
    workbook.active.title = "a b"
    workbook.active.append(["first"])
    workbook.create_sheet("a_b").append(["second"])
    workbook.save(source)
    workbook.close()
    with pytest.raises(ValueError, match="colliding filenames"):
        excel_to_csv_batch(source, output)
    assert destination.read_bytes() == b"previous export"
    assert list(output.iterdir()) == [destination]


def test_selecting_one_colliding_sheet_is_valid(tmp_path: Path) -> None:
    source = tmp_path / "input.xlsx"
    workbook = openpyxl.Workbook()
    workbook.active.title = "a b"
    workbook.active.append(["first"])
    workbook.create_sheet("a_b").append(["second"])
    workbook.save(source)
    workbook.close()
    output = tmp_path / "output"
    assert excel_to_csv_batch(source, output, sheet_names=["a_b"]) == {"a_b": 1}
    assert (output / "a_b.csv").read_text() == "second\n"
