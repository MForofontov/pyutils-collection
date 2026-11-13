from pathlib import Path

import pytest

from pyutils_collection.file_functions import find_files_by_pattern

pytestmark = [pytest.mark.unit, pytest.mark.file_functions]


@pytest.mark.parametrize("sensitive, expected", [(True, []), (False, ["Report.TXT"])])
def test_explicit_case_matching_is_platform_independent(
    tmp_path: Path, sensitive: bool, expected: list[str]
) -> None:
    (tmp_path / "Report.TXT").write_text("kept", encoding="utf-8")
    result = find_files_by_pattern(tmp_path, "report.txt", case_sensitive=sensitive)
    assert [Path(path).name for path in result] == expected
    assert (tmp_path / "Report.TXT").read_text(encoding="utf-8") == "kept"
