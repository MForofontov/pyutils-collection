import importlib
from pathlib import Path
from unittest.mock import patch

import openpyxl
import pytest

pytestmark = [pytest.mark.unit, pytest.mark.serialization]


@pytest.mark.parametrize("name", ["read_excel_sheet", "read_excel_range"])
@pytest.mark.parametrize("failure", ["name", "index", "iteration"])
def test_reader_closes_workbook_on_failure(
    tmp_path: Path, name: str, failure: str
) -> None:
    path = tmp_path / "data.xlsx"
    original = openpyxl.Workbook()
    original.save(path)
    original.close()
    workbook = openpyxl.load_workbook(path, read_only=True)
    module = importlib.import_module(
        f"pyutils_collection.serialization_functions.excel_operations.{name}"
    )
    reader = getattr(module, name)
    try:
        with patch.object(module, "load_workbook", return_value=workbook):
            if failure == "iteration":
                error = RuntimeError("iteration failed")
                with patch.object(workbook.active, "iter_rows", side_effect=error):
                    with pytest.raises(RuntimeError) as raised:
                        reader(str(path))
                assert raised.value is error
            else:
                with pytest.raises(ValueError):
                    reader(str(path), sheet_name="missing" if failure == "name" else 99)
        assert workbook._archive.fp is None
        assert path.read_bytes().startswith(b"PK")
    finally:
        workbook.close()
