import bz2
import gzip
import lzma
from collections.abc import Callable
from pathlib import Path

import pytest

from pyutils_collection.compression_functions import (
    compress_file_bz2,
    compress_file_gzip,
    compress_file_lzma,
    compress_tar,
    compress_zip,
    decompress_file_bz2,
    decompress_file_gzip,
    decompress_file_lzma,
)

pytestmark = [pytest.mark.unit, pytest.mark.compression]


@pytest.mark.parametrize("alias", [False, True], ids=["same-path", "hard-link"])
@pytest.mark.parametrize(
    "operation, encode",
    [
        (compress_file_bz2, bytes),
        (compress_file_gzip, bytes),
        (compress_file_lzma, bytes),
        (compress_tar, bytes),
        (compress_zip, bytes),
        (decompress_file_bz2, bz2.compress),
        (decompress_file_gzip, gzip.compress),
        (decompress_file_lzma, lzma.compress),
    ],
)
def test_alias_rejection_preserves_source(
    tmp_path: Path,
    alias: bool,
    operation: Callable[[str, str], None],
    encode: Callable[[bytes], bytes],
) -> None:
    original = encode(b"irreplaceable input\n")
    source = tmp_path / "source"
    source.write_bytes(original)
    output = source
    if alias:
        output = tmp_path / "alias"
        output.hardlink_to(source)
    with pytest.raises(OSError, match="different files"):
        operation(str(source), str(output))
    assert source.read_bytes() == original
    assert output.read_bytes() == original
