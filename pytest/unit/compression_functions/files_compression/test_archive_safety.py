"""Archive validation must precede writes and protect destination boundaries."""

import io
import tarfile
import zipfile

import pytest

from pyutils_collection.compression_functions.files_compression.decompress_file_tar import (
    decompress_file_tar,
)
from pyutils_collection.compression_functions.files_compression.decompress_file_zip import (
    decompress_file_zip,
)

pytestmark = [pytest.mark.unit, pytest.mark.compression]


@pytest.mark.parametrize(
    "name", ["../escape.txt", "/absolute.txt", "C:/escape.txt", "..\\escape.txt"]
)
def test_zip_rejects_unsafe_later_member_before_writing(tmp_path, name):
    archive = tmp_path / "archive.zip"
    destination = tmp_path / "out"
    destination.mkdir()
    original = destination / "original.txt"
    original.write_text("original")
    with zipfile.ZipFile(archive, "w") as stream:
        stream.writestr("original.txt", "replacement")
        stream.writestr(name, "unsafe")
    with pytest.raises(ValueError, match="Unsafe ZIP"):
        decompress_file_zip(str(archive), str(destination))
    assert original.read_text() == "original"
    assert not (tmp_path / "escape.txt").exists()


def test_zip_rejects_existing_symlink_escape(tmp_path):
    destination = tmp_path / "out"
    outside = tmp_path / "outside"
    destination.mkdir()
    outside.mkdir()
    try:
        (destination / "link").symlink_to(outside, target_is_directory=True)
    except OSError:
        pytest.skip("Symlink creation privileges unavailable")
    archive = tmp_path / "archive.zip"
    with zipfile.ZipFile(archive, "w") as stream:
        stream.writestr("link/escape.txt", "unsafe")
    with pytest.raises(ValueError, match="Unsafe ZIP"):
        decompress_file_zip(str(archive), str(destination))
    assert not (outside / "escape.txt").exists()


def test_tar_preflights_late_traversal_member(tmp_path):
    archive = tmp_path / "archive.tar.gz"
    destination = tmp_path / "out"
    destination.mkdir()
    original = destination / "original.txt"
    original.write_bytes(b"original")
    with tarfile.open(archive, "w:gz") as stream:
        for name in ("original.txt", "../escape.txt"):
            member = tarfile.TarInfo(name)
            member.size = 3
            stream.addfile(member, io.BytesIO(b"new"))
    with pytest.raises(tarfile.FilterError):
        decompress_file_tar(str(archive), str(destination))
    assert original.read_bytes() == b"original"
