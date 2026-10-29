"""Async file download utilities."""

import aiohttp

from ._download_writer import download_writer


async def async_download(url: str, dest_path: str, timeout: float = 30.0) -> None:
    """
    Download a file asynchronously from a URL and save to dest_path.

    Parameters
    ----------
    url : str
        The URL to download from.
    dest_path : str
        The local file path to save the downloaded content.
    timeout : float, optional
        Timeout in seconds (default 30.0).

    Raises
    ------
    TypeError
        If url or dest_path is not a string.
    ValueError
        If url is empty.
    RuntimeError
        If download fails.

    Notes
    -----
    Output is staged beside the destination and replaced only after a complete
    download and successful flush. Failures and cancellation remove the staging
    file and preserve an existing destination. Replacement uses temporary-file
    permissions and replaces a destination symlink itself.

    Examples
    --------
    >>> asyncio.run(async_download('https://example.com/file.txt', '/tmp/file.txt'))

    Complexity
    ----------
    Time: O(n), Space: O(1)
    """
    if not isinstance(url, str):
        raise TypeError(f"url must be str, got {type(url).__name__}")
    if not isinstance(dest_path, str):
        raise TypeError(f"dest_path must be str, got {type(dest_path).__name__}")
    if not url:
        raise ValueError("url cannot be empty")
    if not isinstance(timeout, (int, float)):
        raise TypeError(f"timeout must be a number, got {type(timeout).__name__}")
    if timeout <= 0:
        raise ValueError("timeout must be positive")

    try:
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=timeout)
        ) as session:
            async with session.get(url) as resp:
                resp.raise_for_status()
                with download_writer(dest_path) as f:
                    async for chunk in resp.content.iter_chunked(8192):
                        f.write(chunk)
    except Exception as exc:
        raise RuntimeError(f"Download failed: {exc}") from exc


__all__ = ["async_download"]
