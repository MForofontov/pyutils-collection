"""Tests for transactional file replacement."""

import os
from pathlib import Path

import pytest
from pyutils_collection.file_functions import atomic_write_file

pytestmark = [pytest.mark.unit, pytest.mark.file_functions]


@pytest.mark.parametrize(
    "content,expected",
    [("Olá\n世界", "Olá\n世界".encode()), (b"\x00\xff", b"\x00\xff"), ("", b"")],
)
def test_create_and_replace(tmp_path: Path, content, expected) -> None:
    destination = tmp_path / "data"
    atomic_write_file(destination, content)
    assert destination.read_bytes() == expected
    atomic_write_file(str(destination), b"new")
    assert destination.read_bytes() == b"new"
    assert list(tmp_path.iterdir()) == [destination]


def test_custom_encoding(tmp_path: Path) -> None:
    destination = tmp_path / "data"
    atomic_write_file(destination, "Olá", encoding="utf-16")
    assert destination.read_bytes() == "Olá".encode("utf-16")


@pytest.mark.parametrize("failure_point", ["replace", "fsync"])
@pytest.mark.parametrize("existing", [True, False])
def test_failure_preserves_destination_and_cleans_temporary_file(
    tmp_path: Path, monkeypatch, failure_point, existing
) -> None:
    destination = tmp_path / "data"
    if existing:
        destination.write_bytes(b"original")

    def fail(*args):
        raise OSError("simulated failure")

    with monkeypatch.context() as operation_patch:
        operation_patch.setattr(os, failure_point, fail)
        with pytest.raises(OSError, match="simulated failure"):
            atomic_write_file(destination, b"replacement")
    assert destination.exists() is existing
    if existing:
        assert destination.read_bytes() == b"original"
    assert sorted(tmp_path.iterdir()) == ([destination] if existing else [])


def test_encoding_error_leaves_original_untouched(tmp_path: Path) -> None:
    destination = tmp_path / "data"
    destination.write_bytes(b"original")
    with pytest.raises(UnicodeEncodeError):
        atomic_write_file(destination, "世界", encoding="ascii")
    assert destination.read_bytes() == b"original"
    assert list(tmp_path.iterdir()) == [destination]


@pytest.mark.parametrize(
    "content,encoding", [(None, "utf-8"), (1, "utf-8"), ("a", None)]
)
def test_invalid_arguments(tmp_path: Path, content, encoding) -> None:
    with pytest.raises(TypeError):
        atomic_write_file(tmp_path / "data", content, encoding)
    assert not list(tmp_path.iterdir())


def test_missing_parent(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        atomic_write_file(tmp_path / "missing" / "data", "text")
