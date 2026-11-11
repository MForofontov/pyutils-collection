from functools import partial
try:
    from compression import zstd
    from pyutils_collection.compression_functions.binary_compression.decompress_zstd import decompress_zstd

    ZSTANDARD_AVAILABLE = True
except ImportError:
    ZSTANDARD_AVAILABLE = False
    zstd = None  # type: ignore
    decompress_zstd = None  # type: ignore

import pytest

pytestmark = pytest.mark.skipif(not ZSTANDARD_AVAILABLE, reason="standard-library Zstandard unavailable")
pytestmark = [pytestmark, pytest.mark.unit, pytest.mark.compression]


def test_decompress_zstd_basic() -> None:
    """
    Test case 1: Test the decompress_zstd function with basic input.
    """
    data: bytes = b"hello world"
    compressor = partial(zstd.compress)
    compressed_data: bytes = compressor(data)
    decompressed_data: bytes = decompress_zstd(compressed_data)
    assert decompressed_data == data, "Decompressed data should match the original data"


def test_decompress_zstd_empty() -> None:
    """
    Test case 2: Test the decompress_zstd function with empty byte string.
    """
    data: bytes = b""
    compressor = partial(zstd.compress)
    compressed_data: bytes = compressor(data)
    decompressed_data: bytes = decompress_zstd(compressed_data)
    assert decompressed_data == data, "Decompressed data should match the original data"


def test_decompress_zstd_large_data() -> None:
    """
    Test case 3: Test the decompress_zstd function with large data.
    """
    data: bytes = b"a" * 1000000  # 1 MB of data
    compressor = partial(zstd.compress)
    compressed_data: bytes = compressor(data)
    decompressed_data: bytes = decompress_zstd(compressed_data)
    assert decompressed_data == data, "Decompressed data should match the original data"


def test_decompress_zstd_special_characters() -> None:
    """
    Test case 4: Test the decompress_zstd function with special characters.
    """
    data: bytes = b"!@#$%^&*()_+-=[]{}|;':,.<>/?"
    compressor = partial(zstd.compress)
    compressed_data: bytes = compressor(data)
    decompressed_data: bytes = decompress_zstd(compressed_data)
    assert decompressed_data == data, "Decompressed data should match the original data"


def test_decompress_zstd_binary_data() -> None:
    """
    Test case 5: Test the decompress_zstd function with binary data.
    """
    data: bytes = bytes(range(256))
    compressor = partial(zstd.compress)
    compressed_data: bytes = compressor(data)
    decompressed_data: bytes = decompress_zstd(compressed_data)
    assert decompressed_data == data, "Decompressed data should match the original data"


def test_decompress_zstd_small_data() -> None:
    """
    Test case 6: Test the decompress_zstd function with very small data.
    """
    data: bytes = b"a"
    compressor = partial(zstd.compress)
    compressed_data: bytes = compressor(data)
    decompressed_data: bytes = decompress_zstd(compressed_data)
    assert decompressed_data == data, "Decompressed data should match the original data"


def test_decompress_zstd_unicode_data() -> None:
    """
    Test case 7: Test the decompress_zstd function with Unicode data.
    """
    data: bytes = "你好，世界".encode()
    compressor = partial(zstd.compress)
    compressed_data: bytes = compressor(data)
    decompressed_data: bytes = decompress_zstd(compressed_data)
    assert decompressed_data == data, "Decompressed data should match the original data"


def test_decompress_zstd_invalid_type() -> None:
    """
    Test case 8: Test the decompress_zstd function with invalid data type.
    """
    with pytest.raises(TypeError):
        decompress_zstd("not bytes")  # type: ignore


def test_decompress_zstd_decompression_error() -> None:
    """
    Test case 9: Test the decompress_zstd function handling of decompression errors.
    """
    with pytest.raises(ValueError):
        # Provide invalid compressed data
        invalid_compressed_data: bytes = b"invalid compressed data"
        decompress_zstd(invalid_compressed_data)
