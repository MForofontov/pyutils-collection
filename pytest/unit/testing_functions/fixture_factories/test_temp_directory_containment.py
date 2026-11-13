from pathlib import Path
from unittest.mock import patch

import pytest

from pyutils_collection.testing_functions import create_temp_dir_fixture

pytestmark = [pytest.mark.unit, pytest.mark.testing]


@pytest.mark.parametrize("absolute", [False, True], ids=["parent-traversal", "absolute"])
def test_fixture_cannot_overwrite_outside_files(tmp_path: Path, absolute: bool) -> None:
    owned = tmp_path / "fixture"
    owned.mkdir()
    victim = tmp_path / "victim"
    victim.write_text("keep", encoding="utf-8")
    filename = str(victim) if absolute else "../victim"
    with patch("tempfile.mkdtemp", return_value=str(owned)):
        with pytest.raises(ValueError, match="inside the temporary directory"):
            with create_temp_dir_fixture({filename: "destroyed"}):
                pass
    assert victim.read_text(encoding="utf-8") == "keep"
    assert not owned.exists()
