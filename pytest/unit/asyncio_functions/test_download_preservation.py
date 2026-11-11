"""Async downloads preserve existing files on errors and cancellation."""

import asyncio
import importlib
from unittest.mock import Mock

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.asyncio_functions, pytest.mark.asyncio]


class Response:
    def __init__(self, *, status=200, body=b"new", broken=False):
        self.status = status
        self.headers = {"Content-Length": "3", "Accept-Ranges": "bytes"}
        self.headers["Content-Range"] = "bytes 0-2/3"
        self.content = self
        self.body = body
        self.broken = broken

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        pass

    def raise_for_status(self):
        pass

    async def iter_chunked(self, _size):
        yield self.body
        if self.broken:
            raise RuntimeError("stream failed")

    async def read(self):
        return self.body


class Session:
    def __init__(self, response):
        self.response = response

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        pass

    def head(self, _url):
        return Response()

    def get(self, _url, **_kwargs):
        return self.response


@pytest.mark.parametrize("failure", ["stream", "sync", "replace", "cancel"])
async def test_stream_download_preserves_original(tmp_path, monkeypatch, failure):
    module = importlib.import_module(
        "pyutils_collection.asyncio_functions.async_download"
    )
    writer = importlib.import_module(
        "pyutils_collection.asyncio_functions._download_writer"
    )
    destination = tmp_path / "file"
    destination.write_bytes(b"original")
    response = Response(broken=failure == "stream")
    if failure == "cancel":

        async def chunks(_size):
            yield b"partial"
            raise asyncio.CancelledError()

        response.iter_chunked = chunks
    monkeypatch.setattr(module.aiohttp, "ClientSession", lambda **_: Session(response))
    if failure in {"sync", "replace"}:
        monkeypatch.setattr(
            writer.os,
            "fsync" if failure == "sync" else "replace",
            Mock(side_effect=OSError("failed")),
        )
    with pytest.raises(asyncio.CancelledError if failure == "cancel" else RuntimeError):
        await module.async_download("https://example.com", str(destination))
    assert destination.read_bytes() == b"original"
    assert list(tmp_path.iterdir()) == [destination]


@pytest.mark.parametrize(("status", "body"), [(200, b"new"), (206, b"n")])
async def test_parallel_download_rejects_ignored_or_truncated_range(
    tmp_path, monkeypatch, status, body
):
    module = importlib.import_module(
        "pyutils_collection.asyncio_functions.async_parallel_download"
    )
    destination = tmp_path / "file"
    destination.write_bytes(b"original")
    response = Response(status=status, body=body)
    monkeypatch.setattr(module.aiohttp, "ClientSession", lambda **_: Session(response))
    with pytest.raises(RuntimeError, match="range|length"):
        await module.async_parallel_download(
            "https://example.com", str(destination), num_chunks=1
        )
    assert destination.read_bytes() == b"original"
    assert list(tmp_path.iterdir()) == [destination]
