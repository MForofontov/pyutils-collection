"""Read legacy frames and verify newly written frames with another backend."""

import base64
import json
from pathlib import Path

import cramjam
import pytest

from pyutils_collection.compression_functions import compress_zstd, decompress_zstd

pytestmark = [pytest.mark.unit, pytest.mark.compression]
FRAMES = json.loads(Path(__file__).with_name("legacy_zstd_frames.json").read_text())[
    "frames"
]


@pytest.mark.parametrize("frame", FRAMES)
def test_legacy_python_zstandard_frames_remain_readable(frame):
    assert decompress_zstd(base64.b64decode(frame["compressed"])) == base64.b64decode(
        frame["payload"]
    )


@pytest.mark.parametrize(
    "data",
    [b"", b"hello", bytes(range(256)), b"compress me" * 10000],
    ids=["empty", "text", "binary", "large"],
)
@pytest.mark.parametrize("level", [-3, 0, 3, 19, 22])
def test_new_frames_are_readable_by_independent_backend(data, level):
    compressed = compress_zstd(data, level)
    assert bytes(cramjam.zstd.decompress(compressed)) == data


def test_truncated_frame_is_rejected():
    with pytest.raises(ValueError):
        decompress_zstd(compress_zstd(b"payload")[:-1])


def test_only_first_frame_is_returned_as_before():
    assert (
        decompress_zstd(compress_zstd(b"first") + compress_zstd(b"second")) == b"first"
    )
