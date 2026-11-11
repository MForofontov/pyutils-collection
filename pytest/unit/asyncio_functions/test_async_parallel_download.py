from pathlib import Path
from typing import Any
from unittest.mock import patch

import pytest

try:
    import aiohttp
    from pyutils_collection.asyncio_functions.async_parallel_download import async_parallel_download
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    aiohttp = None  # type: ignore
    async_parallel_download = None  # type: ignore

pytestmark = [
    pytest.mark.unit,
    pytest.mark.asyncio_functions,
    pytest.mark.skipif(not AIOHTTP_AVAILABLE, reason="aiohttp not installed"),
]


@pytest.mark.asyncio
async def test_async_parallel_download_normal_operation(tmp_path: Path) -> None:
    """
    Test case 1: Normal operation with valid URL and destination.
    """
    url: str = "https://example.com/file.zip"
    dest: Path = tmp_path / "file.zip"
    file_size: int = 16000
    num_chunks: int = 4
    chunk_data: bytes = b"x" * (file_size // num_chunks)
    last_chunk_data: bytes = b"y" * (
        file_size - (file_size // num_chunks) * (num_chunks - 1)
    )

    class MockHeadResponse:
        def __init__(self) -> None:
            self.status: int = 200
            self.headers: dict[str, str] = {
                "Content-Length": str(file_size),
                "Accept-Ranges": "bytes",
            }

        async def __aenter__(self) -> "MockHeadResponse":
            return self

        async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
            pass

        def raise_for_status(self) -> None:
            pass

    class MockGetResponse:
        def __init__(self, start: int, end: int) -> None:
            self.status: int = 206
            self._start: int = start
            self._end: int = end
            self.headers = {"Content-Range": f"bytes {start}-{end}/{file_size}"}

        async def __aenter__(self) -> "MockGetResponse":
            return self

        async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
            pass

        def raise_for_status(self) -> None:
            pass

        @property
        def content(self) -> Any:
            class Content:
                async def read(inner_self) -> bytes:
                    if self._end < file_size - 1:
                        return chunk_data
                    else:
                        return last_chunk_data

            return Content()

    class MockSession:
        async def __aenter__(self) -> "MockSession":
            return self

        async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
            pass

        def head(self, url: str) -> MockHeadResponse:
            return MockHeadResponse()

        def get(
            self, url: str, headers: dict[str, str] | None = None
        ) -> MockGetResponse:
            # Parse range
            if headers is None:
                raise ValueError("headers required")
            rng: str = headers["Range"].split("=")[1]
            start: int
            end: int
            start, end = map(int, rng.split("-"))
            return MockGetResponse(start, end)

    with patch("aiohttp.ClientSession", return_value=MockSession()):
        await async_parallel_download(url, str(dest), num_chunks=num_chunks)
        with open(dest, "rb") as f:
            data = f.read()
            assert data.count(b"x") == len(chunk_data) * (num_chunks - 1)
            assert data.endswith(last_chunk_data)


@pytest.mark.asyncio
async def test_async_parallel_download_more_chunks_than_size(tmp_path: Path) -> None:
    """
    Test case 2: Ensure chunks are capped by file size so each chunk has at least one byte.
    """

    url = "https://example.com/small.bin"
    dest = tmp_path / "small.bin"
    file_size = 3
    num_chunks = 10

    class MockHeadResponse:
        def __init__(self) -> None:
            self.status: int = 200
            self.headers: dict[str, str] = {
                "Content-Length": str(file_size),
                "Accept-Ranges": "bytes",
            }

        async def __aenter__(self) -> "MockHeadResponse":
            return self

        async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
            pass

        def raise_for_status(self) -> None:
            pass

    class MockGetResponse:
        def __init__(self, start: int, end: int, idx: int) -> None:
            self.status: int = 206
            self._start: int = start
            self._end: int = end
            self.headers = {"Content-Range": f"bytes {start}-{end}/{file_size}"}
            self._idx: int = idx

        async def __aenter__(self) -> "MockGetResponse":
            return self

        async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
            pass

        def raise_for_status(self) -> None:
            pass

        @property
        def content(self) -> Any:
            class Content:
                def __init__(inner_self, idx: int, start: int, end: int) -> None:
                    inner_self._idx: int = idx
                    inner_self._start: int = start
                    inner_self._end: int = end

                async def read(inner_self) -> bytes:
                    length: int = inner_self._end - inner_self._start + 1
                    return bytes([65 + inner_self._idx]) * length

            return Content(self._idx, self._start, self._end)

    class MockSession:
        def __init__(self) -> None:
            self.requests: list[tuple[int, int]] = []

        async def __aenter__(self) -> "MockSession":
            return self

        async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
            pass

        def head(self, url: str) -> MockHeadResponse:
            return MockHeadResponse()

        def get(
            self, url: str, headers: dict[str, str] | None = None
        ) -> MockGetResponse:
            if headers is None:
                headers = {}
            rng: str = headers["Range"].split("=")[1]
            start, end = map(int, rng.split("-"))
            idx: int = len(self.requests)
            self.requests.append((start, end))
            return MockGetResponse(start, end, idx)

    session = MockSession()
    with patch("aiohttp.ClientSession", return_value=session):
        await async_parallel_download(url, str(dest), num_chunks=num_chunks)

    assert len(session.requests) == file_size
    assert all(end - start == 0 for start, end in session.requests)

    with open(dest, "rb") as f:
        data = f.read()
    assert data == b"ABC"


@pytest.mark.asyncio
async def test_async_parallel_download_type_error_url(tmp_path: Path) -> None:
    """
    Test case 3: TypeError for non-string URL.
    """
    dest = tmp_path / "file.zip"
    with pytest.raises(TypeError, match="url must be str"):
        await async_parallel_download(123, str(dest))


@pytest.mark.asyncio
async def test_async_parallel_download_type_error_dest_path() -> None:
    """
    Test case 4: TypeError for non-string dest_path.
    """
    with pytest.raises(TypeError, match="dest_path must be str"):
        await async_parallel_download("https://example.com/file.zip", 123)


@pytest.mark.asyncio
async def test_async_parallel_download_value_error_url(tmp_path: Path) -> None:
    """
    Test case 5: ValueError for empty URL.
    """
    dest = tmp_path / "file.zip"
    with pytest.raises(ValueError, match="url cannot be empty"):
        await async_parallel_download("", str(dest))


@pytest.mark.asyncio
async def test_async_parallel_download_type_error_num_chunks(tmp_path: Path) -> None:
    """
    Test case 6: TypeError for invalid num_chunks type.
    """
    dest = tmp_path / "file.zip"
    with pytest.raises(TypeError, match="num_chunks must be int"):
        await async_parallel_download(
            "https://example.com/file.zip", str(dest), num_chunks="bad"
        )


@pytest.mark.asyncio
async def test_async_parallel_download_value_error_num_chunks(tmp_path: Path) -> None:
    """
    Test case 7: ValueError for num_chunks < 1.
    """
    dest = tmp_path / "file.zip"
    with pytest.raises(ValueError, match="num_chunks must be >= 1"):
        await async_parallel_download(
            "https://example.com/file.zip", str(dest), num_chunks=0
        )


@pytest.mark.asyncio
async def test_async_parallel_download_type_error_timeout(tmp_path: Path) -> None:
    """
    Test case 8: TypeError for invalid timeout type.
    """
    dest = tmp_path / "file.zip"
    with pytest.raises(TypeError, match="timeout must be a number"):
        await async_parallel_download(
            "https://example.com/file.zip", str(dest), timeout="bad"
        )


@pytest.mark.asyncio
async def test_async_parallel_download_value_error_timeout(tmp_path: Path) -> None:
    """
    Test case 9: ValueError for non-positive timeout.
    """
    dest = tmp_path / "file.zip"
    with pytest.raises(ValueError, match="timeout must be positive"):
        await async_parallel_download(
            "https://example.com/file.zip", str(dest), timeout=0
        )


@pytest.mark.asyncio
async def test_async_parallel_download_runtime_error_no_range(tmp_path: Path) -> None:
    """
    Test case 10: RuntimeError if server does not support range requests.
    """
    url = "https://example.com/file.zip"
    dest = tmp_path / "file.zip"

    class MockHeadResponse:
        def __init__(self) -> None:
            self.status: int = 200
            self.headers: dict[str, str] = {
                "Content-Length": "1000",
                "Accept-Ranges": "none",
            }

        async def __aenter__(self) -> "MockHeadResponse":
            return self

        async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
            pass

        def raise_for_status(self) -> None:
            pass

    class MockSession:
        async def __aenter__(self) -> "MockSession":
            return self

        async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
            pass

        def head(self, url: str) -> MockHeadResponse:
            return MockHeadResponse()

    with patch("aiohttp.ClientSession", return_value=MockSession()):
        with pytest.raises(
            RuntimeError, match="Server does not support range requests"
        ):
            await async_parallel_download(url, str(dest))


@pytest.mark.asyncio
async def test_async_parallel_download_runtime_error_download(tmp_path: Path) -> None:
    """
    Test case 11: RuntimeError for download failure.
    """
    url = "https://example.com/file.zip"
    dest = tmp_path / "file.zip"
    file_size = 1000
    num_chunks = 2

    class MockHeadResponse:
        def __init__(self) -> None:
            self.status: int = 200
            self.headers: dict[str, str] = {
                "Content-Length": str(file_size),
                "Accept-Ranges": "bytes",
            }

        async def __aenter__(self) -> "MockHeadResponse":
            return self

        async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
            pass

        def raise_for_status(self) -> None:
            pass

    class MockSession:
        async def __aenter__(self) -> "MockSession":
            return self

        async def __aexit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
            pass

        def head(self, url: str) -> MockHeadResponse:
            return MockHeadResponse()

        def get(self, url: str, headers: dict[str, str] | None = None) -> None:
            raise Exception("network error")

    with patch("aiohttp.ClientSession", return_value=MockSession()):
        with pytest.raises(
            RuntimeError, match="Parallel download failed: network error"
        ):
            await async_parallel_download(url, str(dest), num_chunks=num_chunks)
