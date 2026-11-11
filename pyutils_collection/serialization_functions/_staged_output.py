"""Publish a completed serialization output without truncating its destination."""

import os
import stat
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def staged_output(destination: str | Path) -> Iterator[Path]:
    """Yield a sibling path; sync and replace only after its writer has closed.

    Preserve existing permission bits. A destination symlink is replaced rather
    than followed; ownership and other metadata are not copied. This is atomic
    per file, not a transaction across multiple outputs or a power-loss guarantee.
    """
    destination = Path(destination)
    with tempfile.NamedTemporaryFile(
        dir=destination.parent,
        prefix=".serialize-",
        suffix=destination.suffix,
        delete=False,
    ) as stream:
        temporary = Path(stream.name)
    try:
        yield temporary
        # Windows _commit requires a writable descriptor, even after the writer
        # has closed. Sync before copying possibly read-only permission bits.
        with temporary.open("r+b") as completed:
            os.fsync(completed.fileno())
        if destination.exists():
            temporary.chmod(stat.S_IMODE(destination.stat().st_mode))
        os.replace(temporary, destination)
    finally:
        try:
            temporary.unlink(missing_ok=True)
        except PermissionError:
            # A failed Windows replacement may leave a read-only staged file.
            temporary.chmod(temporary.stat().st_mode | stat.S_IWRITE)
            temporary.unlink(missing_ok=True)
