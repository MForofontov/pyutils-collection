"""Generic data compression with algorithm selection."""

from pyutils_collection.compression_functions.binary_compression.compress_bz2 import (
    compress_bz2,
)
from pyutils_collection.compression_functions.binary_compression.compress_gzip import (
    compress_gzip,
)
from pyutils_collection.compression_functions.binary_compression.compress_lzma import (
    compress_lzma,
)
from pyutils_collection.compression_functions.binary_compression.compress_snappy import (
    compress_snappy,
)
from pyutils_collection.compression_functions.binary_compression.compress_zstd import (
    compress_zstd,
)


def compress_data(data: bytes, algorithm: str = "gzip", level: int = 3) -> bytes:
    """
    Compress data using the specified algorithm.

    Parameters
    ----------
    data : bytes
        The data to be compressed.
    algorithm : str, optional
        Compression algorithm to use ('gzip', 'bz2', 'lzma', 'snappy', 'zstd').
    level : int, optional
        The compression level (default is 3, applicable for zstd).

    Returns
    -------
    bytes
        Compressed binary data.

    Raises
    ------
    ValueError
        If the specified algorithm is not supported.
    TypeError
        If data is not bytes or level is not an integer.

    Examples
    --------
    >>> from compression_functions.binary_compression.decompress_data import decompress_data
    >>> compressed = compress_data(b'example', 'gzip')
    >>> decompress_data(compressed, 'gzip')
    b'example'
    """
    if not isinstance(data, bytes):
        raise TypeError("data must be bytes")
    if not isinstance(level, int):
        raise TypeError("level must be an integer")

    if algorithm == "gzip":
        return compress_gzip(data)
    elif algorithm == "bz2":
        return compress_bz2(data)
    elif algorithm == "lzma":
        return compress_lzma(data)
    elif algorithm == "snappy":
        return compress_snappy(data)
    elif algorithm == "zstd":
        return compress_zstd(data, level=level)
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")


__all__ = ["compress_data"]
