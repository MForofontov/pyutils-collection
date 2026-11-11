import importlib
"""Download behavior using mocked transport and real temporary files."""

import os
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from unittest.mock import MagicMock, Mock

import pytest
from pyutils_collection.http_functions.download_file import download_file

pytestmark = [pytest.mark.unit, pytest.mark.http_functions]


@pytest.fixture
def transport(monkeypatch):
    response = MagicMock()
    response.headers = {"Content-Length": "12"}
    response.read.side_effect = [b"chunk1", b"chunk2", b""]
    opener = MagicMock()
    opener.return_value.__enter__.return_value = response
    monkeypatch.setattr(importlib.import_module("pyutils_collection.http_functions.download_file"), "open_http", opener)
    return opener, response


def test_download_file_successful(tmp_path: Path, transport) -> None:
    destination = tmp_path / "nested" / "data.txt"
    result = download_file("https://example.com/data", str(destination))
    assert result == {
        "success": True,
        "file_path": str(destination.absolute()),
        "file_size": 12,
        "message": "Successfully downloaded 12 bytes",
    }
    assert destination.read_bytes() == b"chunk1chunk2"
    assert list(destination.parent.iterdir()) == [destination]


def test_download_file_headers_and_timeout(tmp_path: Path, transport) -> None:
    opener, _ = transport
    download_file(
        "https://example.com/data", str(tmp_path / "data"),
        headers={"User-Agent": "TestAgent", "Authorization": "Bearer test"}, timeout=60,
    )
    request = opener.call_args.args[0]
    assert request.get_header("User-agent") == "TestAgent"
    assert request.get_header("Authorization") == "Bearer test"
    assert opener.call_args.kwargs["timeout"] == 60


def test_download_file_default_timeout(tmp_path: Path, transport) -> None:
    opener, _ = transport
    download_file("https://example.com/data", str(tmp_path / "data"))
    assert opener.call_args.kwargs["timeout"] == 30


@pytest.mark.parametrize("known_size", [True, False])
def test_download_file_progress_callback(tmp_path: Path, transport, known_size) -> None:
    _, response = transport
    if not known_size:
        response.headers = {}
    progress = []
    download_file(
        "https://example.com/data", str(tmp_path / "data"),
        progress_callback=lambda downloaded, total: progress.append((downloaded, total)),
    )
    total = 12 if known_size else 0
    assert progress == [(6, total), (12, total)]


@pytest.mark.parametrize("url", ["", "   ", None, 1])
def test_download_file_invalid_url(tmp_path: Path, url) -> None:
    with pytest.raises(ValueError, match="URL must be a non-empty string"):
        download_file(url, str(tmp_path / "data"))


@pytest.mark.parametrize("destination", ["", "   ", None, 1])
def test_download_file_invalid_destination(destination) -> None:
    with pytest.raises(ValueError, match="Destination must be a non-empty string"):
        download_file("https://example.com/data", destination)


@pytest.mark.parametrize("existing", [True, False])
@pytest.mark.parametrize("failure", ["request", "read", "callback", "write", "replace", "sync"])
def test_failure_preserves_destination_and_removes_partial_file(
    tmp_path: Path, monkeypatch, transport, existing, failure
) -> None:
    opener, response = transport
    destination = tmp_path / "data"
    if existing:
        destination.write_bytes(b"original")
    error = OSError("simulated failure")
    callback = None
    if failure == "request":
        opener.side_effect = error
    elif failure == "read":
        response.read.side_effect = [b"partial", error]
    elif failure == "callback":
        callback = Mock(side_effect=error)
    elif failure == "write":
        original = tempfile.NamedTemporaryFile

        def create_file(**kwargs):
            stream = original(**kwargs)
            stream.write = Mock(side_effect=error)
            return stream

        monkeypatch.setattr(tempfile, "NamedTemporaryFile", create_file)
    else:
        monkeypatch.setattr(os, "replace" if failure == "replace" else "fsync", Mock(side_effect=error))

    with pytest.raises(OSError) as caught:
        download_file("https://example.com/data", str(destination), progress_callback=callback)
    assert caught.value is error
    if existing:
        assert destination.read_bytes() == b"original"
    else:
        assert not destination.exists()
    assert list(tmp_path.iterdir()) == ([destination] if existing else [])


def test_truncated_download_preserves_original(tmp_path: Path, transport) -> None:
    _, response = transport
    response.headers = {"Content-Length": "100"}
    destination = tmp_path / "data"
    destination.write_bytes(b"original")
    with pytest.raises(urllib.error.ContentTooShortError):
        download_file("https://example.com/data", str(destination))
    assert destination.read_bytes() == b"original"
    assert list(tmp_path.iterdir()) == [destination]


def test_destination_is_replaced_only_after_download(tmp_path: Path, transport) -> None:
    destination = tmp_path / "data"
    destination.write_bytes(b"original")

    def progress(downloaded, total):
        assert destination.read_bytes() == b"original"

    download_file("https://example.com/data", str(destination), progress_callback=progress)
    assert destination.read_bytes() == b"chunk1chunk2"
