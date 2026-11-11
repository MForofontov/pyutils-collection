"""Stage downloaded bytes beside their destination before replacement."""

import os
import tempfile
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import BinaryIO, cast


@contextmanager
def download_writer(path: str) -> Generator[BinaryIO]:
    destination = Path(path)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb", dir=destination.parent, prefix=".download-", delete=False
        ) as stream:
            temporary = Path(stream.name)
            yield cast(BinaryIO, stream)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
