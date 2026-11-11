"""File download functionality."""

import os
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
from pathlib import Path
from typing import Any

from ._transport import open_http


def download_file(
    url: str,
    destination: str,
    headers: dict[str, str] | None = None,
    timeout: int = 30,
    progress_callback: Callable[[int, int], None] | None = None,
) -> dict[str, Any]:
    """
    Download a file from a URL to a local destination.

    Parameters
    ----------
    url : str
        The URL of the file to download.
    destination : str
        Local path where the file should be saved.
    headers : dict of str, optional
        HTTP headers to include in the request.
    timeout : int, optional
        Timeout in seconds (default: 30).
    progress_callback : callable, optional
        Function to call with (downloaded_bytes, total_bytes) for progress tracking.

    Returns
    -------
    dict
        Dictionary containing 'success', 'file_path', 'file_size', and 'message' on success.

    Raises
    ------
    ValueError
        If URL or destination is invalid.
    Exception
        For any error during download, including network errors and file writing issues. All exceptions are cleaned up and re-raised.

    Examples
    --------
    >>> result = download_file('https://httpbin.org/image/png', 'test.png')
    >>> result['success']
    True
    >>> os.path.exists(result['file_path'])
    True

    Notes
    -----
    Downloads are streamed to a temporary file beside the destination and
    replaced only after the transfer completes. Existing contents survive
    network, callback, write, or replacement failures. The replacement uses
    temporary-file permissions. Known truncated responses raise ContentTooShortError.
    """
    if not isinstance(url, str) or not url.strip():
        raise ValueError("URL must be a non-empty string")
    if urllib.parse.urlsplit(url).scheme.lower() not in {"http", "https"}:
        raise ValueError("URL must use http or https")

    if not isinstance(destination, str) or not destination.strip():
        raise ValueError("Destination must be a non-empty string")

    # Create destination directory if it doesn't exist
    dest_path = Path(destination)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    # Create request
    req = urllib.request.Request(url)

    # Add headers if provided
    if headers:
        for key, value in headers.items():
            req.add_header(key, value)

    temporary_path: Path | None = None
    try:
        with open_http(req, timeout=timeout) as response:
            content_length = response.headers.get("Content-Length")
            total_size = int(content_length) if content_length else 0

            downloaded = 0
            chunk_size = 8192

            with tempfile.NamedTemporaryFile(
                mode="wb", dir=dest_path.parent, prefix=".download-", delete=False
            ) as f:
                temporary_path = Path(f.name)
                while True:
                    chunk = response.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    if progress_callback:
                        progress_callback(downloaded, total_size)
                if content_length is not None and downloaded < total_size:
                    raise urllib.error.ContentTooShortError(
                        f"Downloaded {downloaded} of {total_size} bytes",
                        None,  # type: ignore[arg-type]  # No partial file is retained.
                    )
                f.flush()
                os.fsync(f.fileno())

        assert temporary_path is not None
        os.replace(temporary_path, dest_path)

        return {
            "success": True,
            "file_path": str(dest_path.absolute()),
            "file_size": downloaded,
            "message": f"Successfully downloaded {downloaded} bytes",
        }
    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
