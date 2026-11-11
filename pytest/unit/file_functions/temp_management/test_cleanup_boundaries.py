"""Cleanup must not traverse a directory link out of its selected root."""

import os
import subprocess
import time
from pathlib import Path

import pytest

from pyutils_collection.file_functions.temp_management.cleanup_temp_files import (
    cleanup_temp_files,
)

pytestmark = [pytest.mark.unit, pytest.mark.file_functions]


@pytest.mark.parametrize("dry_run", [False, True])
@pytest.mark.parametrize("pattern", ["linked/*.tmp", "linked/nested/*.tmp"])
def test_directory_link_cannot_escape_cleanup_root(tmp_path, dry_run, pattern):
    root = tmp_path / "cleanup"
    root.mkdir()
    outside = tmp_path / "outside"
    (outside / "nested").mkdir(parents=True)
    files = [outside / "old.tmp", outside / "nested" / "old.tmp"]
    old = time.time() - 7200
    for path in files:
        path.write_text("preserve")
        os.utime(path, (old, old))
    link = root / "linked"
    if os.name == "nt":
        # Directory junctions do not require Windows symlink privileges.
        subprocess.run(
            ["cmd", "/c", "mklink", "/J", str(link), str(outside)],
            check=True,
            capture_output=True,
        )
    else:
        link.symlink_to(outside, target_is_directory=True)
    try:
        assert cleanup_temp_files(root, 1, pattern, dry_run) == []
        assert all(path.read_text() == "preserve" for path in files)
    finally:
        if os.name == "nt":
            link.rmdir()
        else:
            link.unlink()


def test_nested_regular_files_remain_eligible(tmp_path: Path):
    folder = tmp_path / "nested"
    folder.mkdir()
    path = folder / "old.tmp"
    path.write_text("expired")
    old = time.time() - 7200
    os.utime(path, (old, old))
    assert cleanup_temp_files(tmp_path, 1, "nested/*.tmp") == [str(path)]
    assert not path.exists()
