"""Atomic replacement of file contents."""

import os
import tempfile
from pathlib import Path


def atomic_write_file(
    path: str | os.PathLike[str], content: str | bytes, encoding: str = "utf-8"
) -> None:
    """
    Write content to a temporary file, then atomically replace the destination.

    Parameters
    ----------
    path : str or PathLike[str]
        Destination. Its parent directory must already exist.
    content : str or bytes
        Complete contents to write. Strings use encoding; bytes are unchanged.
    encoding : str, optional
        Text encoding (default 'utf-8'). No newline translation is performed.

    Raises
    ------
    TypeError
        If content or encoding has the wrong type, or path is invalid.
    OSError
        If writing, syncing, or replacing fails.
    UnicodeError
        If text cannot be encoded.

    Examples
    --------
    >>> atomic_write_file('settings.json', '{"enabled": true}')  # doctest: +SKIP

    Notes
    -----
    The temporary file is created beside the destination and removed on failure.
    Existing content survives failures before replacement. The new file uses
    temporary-file permissions; existing permissions are not preserved. Replacing
    a symlink replaces the link itself. Parent directory metadata is not synced,
    so this does not guarantee persistence across power loss.

    Complexity
    ----------
    Time and space: O(n), for content size n.
    """
    if not isinstance(content, (str, bytes)):
        raise TypeError("content must be str or bytes")
    if not isinstance(encoding, str):
        raise TypeError("encoding must be a string")
    destination = Path(path)
    data = content.encode(encoding) if isinstance(content, str) else content
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=destination.parent, prefix=".atomic-", delete=False
        ) as stream:
            temporary = Path(stream.name)
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


__all__ = ["atomic_write_file"]
