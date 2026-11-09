"""Parallel async download with chunking support."""

import aiohttp

from ._download_writer import download_writer
from .gather_with_timeout import gather_with_timeout


async def async_parallel_download(
    url: str, dest_path: str, num_chunks: int = 8, timeout: float = 30.0
) -> None:
    """
    Download a file asynchronously from a URL in parallel chunks and save to dest_path.

    Parameters
    ----------
    url : str
        The URL to download from.
    dest_path : str
        The local file path to save the downloaded content.
    num_chunks : int, optional
        Number of parallel chunks (default 8). The actual chunk count will not
        exceed the file size so that every chunk downloads at least one byte.
    timeout : float, optional
        Timeout in seconds (default 30.0).

    Raises
    ------
    TypeError
        If url or dest_path is not a string, or num_chunks/timeout is not int/float.
    ValueError
        If url is empty, num_chunks < 1, or timeout <= 0.
    RuntimeError
        If download fails.

    Examples
    --------
    >>> asyncio.run(async_parallel_download('https://example.com/file.zip', '/tmp/file.zip'))

    Notes
    -----
    Requires server support for HTTP Range requests.
    Every response must report the requested range and length. Output is staged
    beside the destination and replaced only after all chunks succeed. Failed
    work is cancelled and awaited before returning; existing files survive errors.

    Complexity
    ----------
    Time: O(n/num_chunks), Space: O(num_chunks)
    """
    if not isinstance(url, str):
        raise TypeError(f"url must be str, got {type(url).__name__}")
    if not isinstance(dest_path, str):
        raise TypeError(f"dest_path must be str, got {type(dest_path).__name__}")
    if not url:
        raise ValueError("url cannot be empty")
    if not isinstance(num_chunks, int):
        raise TypeError(f"num_chunks must be int, got {type(num_chunks).__name__}")
    if num_chunks < 1:
        raise ValueError("num_chunks must be >= 1")
    if not isinstance(timeout, (int, float)):
        raise TypeError(f"timeout must be a number, got {type(timeout).__name__}")
    if timeout <= 0:
        raise ValueError("timeout must be positive")

    try:
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=timeout)
        ) as session:
            # Get file size
            async with session.head(url) as resp:
                resp.raise_for_status()
                size = int(resp.headers.get("Content-Length", 0))
                accept_ranges = resp.headers.get("Accept-Ranges", "none")
                if size <= 0 or accept_ranges.lower() != "bytes":
                    raise RuntimeError(
                        "Server does not support range requests or file size unknown"
                    )
            # Prepare chunk ranges
            chunk_count = min(num_chunks, size)
            base_chunk_size = size // chunk_count
            remainder = size % chunk_count
            ranges = []
            start = 0
            for i in range(chunk_count):
                chunk_len = base_chunk_size + (1 if i < remainder else 0)
                end = min(size, start + chunk_len) - 1
                ranges.append((start, end))
                start += chunk_len

            # Download chunks in parallel
            async def fetch_chunk(start: int, end: int, idx: int) -> tuple[int, bytes]:
                headers = {"Range": f"bytes={start}-{end}"}
                async with session.get(url, headers=headers) as resp:
                    resp.raise_for_status()
                    if resp.status != 206:
                        raise RuntimeError("Server did not honor the requested range")
                    if (
                        resp.headers.get("Content-Range")
                        != f"bytes {start}-{end}/{size}"
                    ):
                        raise RuntimeError("Server returned a different range")
                    data = await resp.content.read()
                    if len(data) != end - start + 1:
                        raise RuntimeError("Range response has an unexpected length")
                    return idx, data

            tasks = [
                fetch_chunk(start, end, idx) for idx, (start, end) in enumerate(ranges)
            ]
            results = await gather_with_timeout(tasks, timeout)
            # Write chunks in order
            results.sort()
            with download_writer(dest_path) as f:
                for _, data in results:
                    f.write(data)
    except Exception as exc:
        raise RuntimeError(f"Parallel download failed: {exc}") from exc


__all__ = ["async_parallel_download"]
