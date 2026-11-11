from functools import partial
try:
    from compression import zstd
    from pyutils_collection.compression_functions.binary_compression.compress_zstd import compress_zstd

    ZSTANDARD_AVAILABLE = True
except ImportError:
    ZSTANDARD_AVAILABLE = False
    zstd = None  # type: ignore
    compress_zstd = None  # type: ignore

import pytest

pytestmark = pytest.mark.skipif(not ZSTANDARD_AVAILABLE, reason="standard-library Zstandard unavailable")
pytestmark = [pytestmark, pytest.mark.unit, pytest.mark.compression]


def test_compress_zstd_basic() -> None:
    """
    Test case 1: Test the compress_zstd function with basic input.
    """
    data: bytes = b"hello world"
    compressed_data: bytes = compress_zstd(data)
    compressor = partial(zstd.compress, level=3)
    expected_compressed_data: bytes = compressor(data)
    assert compressed_data == expected_compressed_data, (
        "Compressed data should match expected zstd compression"
    )


def test_compress_zstd_empty() -> None:
    """
    Test case 2: Test the compress_zstd function with empty byte string.
    """
    data: bytes = b""
    compressed_data: bytes = compress_zstd(data)
    compressor = partial(zstd.compress, level=3)
    expected_compressed_data: bytes = compressor(data)
    assert compressed_data == expected_compressed_data, (
        "Compressed data should match expected zstd compression"
    )


def test_compress_zstd_large_data() -> None:
    """
    Test case 3: Test the compress_zstd function with large data.
    """
    data: bytes = b"a" * 1000000  # 1 MB of data
    compressed_data: bytes = compress_zstd(data)
    compressor = partial(zstd.compress, level=3)
    expected_compressed_data: bytes = compressor(data)
    assert compressed_data == expected_compressed_data, (
        "Compressed data should match expected zstd compression"
    )


def test_compress_zstd_special_characters() -> None:
    """
    Test case 4: Test the compress_zstd function with special characters.
    """
    data: bytes = b"!@#$%^&*()_+-=[]{}|;':,.<>/?"
    compressed_data: bytes = compress_zstd(data)
    compressor = partial(zstd.compress, level=3)
    expected_compressed_data: bytes = compressor(data)
    assert compressed_data == expected_compressed_data, (
        "Compressed data should match expected zstd compression"
    )


def test_compress_zstd_binary_data() -> None:
    """
    Test case 5: Test the compress_zstd function with binary data.
    """
    data: bytes = bytes(range(256))
    compressed_data: bytes = compress_zstd(data)
    compressor = partial(zstd.compress, level=3)
    expected_compressed_data: bytes = compressor(data)
    assert compressed_data == expected_compressed_data, (
        "Compressed data should match expected zstd compression"
    )


def test_compress_zstd_small_data() -> None:
    """
    Test case 6: Test the compress_zstd function with very small data.
    """
    data: bytes = b"a"
    compressed_data: bytes = compress_zstd(data)
    compressor = partial(zstd.compress, level=3)
    expected_compressed_data: bytes = compressor(data)
    assert compressed_data == expected_compressed_data, (
        "Compressed data should match expected zstd compression"
    )


def test_compress_zstd_already_compressed_data() -> None:
    """
    Test case 7: Test the compress_zstd function with already compressed data.
    """
    compressor = partial(zstd.compress, level=3)
    data: bytes = compressor(b"hello world")
    compressed_data: bytes = compress_zstd(data)
    expected_compressed_data: bytes = compressor(data)
    assert compressed_data == expected_compressed_data, (
        "Compressed data should match expected zstd compression"
    )


def test_compress_zstd_unicode_data() -> None:
    """
    Test case 8: Test the compress_zstd function with Unicode data.
    """
    data: bytes = "你好，世界".encode()
    compressed_data: bytes = compress_zstd(data)
    compressor = partial(zstd.compress, level=3)
    expected_compressed_data: bytes = compressor(data)
    assert compressed_data == expected_compressed_data, (
        "Compressed data should match expected zstd compression"
    )


def test_compress_zstd_different_level() -> None:
    """
    Test case 9: Test the compress_zstd function with a different compression level.
    """
    data: bytes = b"hello world"
    compressed_data: bytes = compress_zstd(data, level=5)
    compressor = partial(zstd.compress, level=5)
    expected_compressed_data: bytes = compressor(data)
    assert compressed_data == expected_compressed_data, (
        "Compressed data should match expected zstd compression with level 5"
    )


def test_compress_zstd_invalid_type() -> None:
    """
    Test case 10: Test the compress_zstd function with invalid data type.
    """
    with pytest.raises(TypeError):
        compress_zstd("not bytes")  # type: ignore


def test_compress_zstd_invalid_level() -> None:
    """
    Test case 11: Test the compress_zstd function with invalid compression level.
    """
    with pytest.raises(TypeError):
        compress_zstd(b"hello world", level="not an integer")  # type: ignore


def test_compress_zstd_compression_error() -> None:
    """
    Test case 12: Test the compress_zstd function handling of compression errors.
    """
    with pytest.raises(ValueError):
        # Mock zstd.ZstdCompressor to raise an exception
        original_compressor = zstd.compress
        zstd.compress = lambda *args, **kwargs: (_ for _ in ()).throw(
            Exception("Mock error")
        )  # type: ignore
        try:
            compress_zstd(b"data")
        finally:
            zstd.compress = original_compressor
