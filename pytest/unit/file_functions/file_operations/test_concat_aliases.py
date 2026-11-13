"""Prevent self-appending and side effects from missing inputs."""

import os
import shutil
from pathlib import Path
from unittest.mock import patch

import pytest

from pyutils_collection.file_functions import concat_files

pytestmark = [pytest.mark.unit, pytest.mark.file_functions]


@pytest.mark.parametrize("alias", [False, True])
def test_same_file_rejected_before_copy(tmp_path: Path, alias: bool) -> None:
    source = tmp_path / "source.txt"
    source.write_text("original")
    destination = tmp_path / "alias.txt" if alias else source
    if alias:
        os.link(source, destination)
    # Never allow a defective implementation to actually self-append forever.
    with patch.object(
        shutil, "copyfileobj", side_effect=AssertionError("unsafe copy")
    ) as copy:
        with pytest.raises(shutil.SameFileError):
            concat_files(str(source), str(destination))
    copy.assert_not_called()
    assert source.read_text() == "original"


def test_missing_source_does_not_create_output(tmp_path: Path) -> None:
    destination = tmp_path / "output.txt"
    with pytest.raises(FileNotFoundError):
        concat_files(str(tmp_path / "missing.txt"), str(destination))
    assert not destination.exists()
