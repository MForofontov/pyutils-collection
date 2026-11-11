"""
Chunked processor with backpressure control for large dataset processing.
"""

from collections.abc import Callable, Generator, Iterable
from typing import TypeVar

T = TypeVar("T")
R = TypeVar("R")


def chunked_processor(
    items: Iterable[T],
    processor: Callable[[list[T]], list[R]],
    chunk_size: int = 1000,
    max_memory_mb: int | None = None,
) -> Generator[R]:
    """
    Process large datasets in chunks with backpressure control.

    Processes items in batches to prevent memory exhaustion, with optional
    memory limit monitoring. Uses generator pattern to provide results
    incrementally without loading entire result set into memory.

    Parameters
    ----------
    items : Iterable[T]
        Input items to process.
    processor : Callable[[list[T]], list[R]]
        Function that processes a chunk and returns results.
    chunk_size : int, optional
        Number of items per chunk (by default 1000).
    max_memory_mb : int | None, optional
        Maximum memory usage in MB, pauses if exceeded (by default None).

    Yields
    ------
    R
        Processed results one at a time.

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If parameters have invalid values.

    Examples
    --------
    >>> def process_batch(items):
    ...     return [x * 2 for x in items]
    >>> data = range(5)
    >>> results = list(chunked_processor(data, process_batch, chunk_size=2))
    >>> results
    [0, 2, 4, 6, 8]

    >>> # With memory monitoring
    >>> results = list(chunked_processor(data, process_batch, max_memory_mb=100))
    >>> len(results)
    5

    Notes
    -----
    The chunked processor prevents memory exhaustion when processing large
    datasets by:
    1. Processing items in fixed-size chunks
    2. Yielding results incrementally (backpressure)
    3. Optional memory monitoring and pausing

    This is essential for processing millions of records without running
    out of memory.

    Complexity
    ----------
    Time: O(n) where n is number of items, Space: O(chunk_size)
    """
    # Type validation
    if not hasattr(items, "__iter__"):
        raise TypeError(f"items must be iterable, got {type(items).__name__}")

    if not callable(processor):
        raise TypeError(f"processor must be callable, got {type(processor).__name__}")

    if not isinstance(chunk_size, int):
        raise TypeError(
            f"chunk_size must be an integer, got {type(chunk_size).__name__}"
        )

    if max_memory_mb is not None and not isinstance(max_memory_mb, int):
        raise TypeError(
            f"max_memory_mb must be an integer or None, got {type(max_memory_mb).__name__}"
        )

    # Value validation
    if chunk_size <= 0:
        raise ValueError(f"chunk_size must be positive, got {chunk_size}")

    if max_memory_mb is not None and max_memory_mb <= 0:
        raise ValueError(f"max_memory_mb must be positive, got {max_memory_mb}")

    chunk: list[T] = []

    for item in items:
        chunk.append(item)

        if len(chunk) >= chunk_size:
            # Process chunk
            results = processor(chunk)

            # Validate processor output
            if not isinstance(results, list):
                raise TypeError(
                    f"processor must return a list, got {type(results).__name__}"
                )

            # Yield results one by one (backpressure control)
            for result in results:
                yield result

            # A processor or result may retain this batch; do not mutate it.
            chunk = []

            # Optional memory check
            if max_memory_mb is not None:
                import psutil

                process = psutil.Process()
                memory_mb = process.memory_info().rss / 1024 / 1024

                if memory_mb > max_memory_mb:
                    import gc
                    import time

                    # Force garbage collection
                    gc.collect()
                    # Brief pause to allow memory to be freed
                    time.sleep(0.1)

    # Process remaining items in final chunk
    if chunk:
        results = processor(chunk)

        if not isinstance(results, list):
            raise TypeError(
                f"processor must return a list, got {type(results).__name__}"
            )

        for result in results:
            yield result


class ChunkedProcessor:
    """
    Reusable chunked processor with configured settings.

    Attributes
    ----------
    processor : Callable[[list[T]], list[R]]
        Function that processes chunks.
    chunk_size : int
        Number of items per chunk.
    max_memory_mb : int | None
        Maximum memory usage in MB.

    Parameters
    ----------
    processor : Callable[[list[T]], list[R]]
        Function that processes a chunk and returns results.
    chunk_size : int, optional
        Number of items per chunk (by default 1000).
    max_memory_mb : int | None, optional
        Maximum memory usage in MB (by default None).

    Examples
    --------
    >>> def process_batch(items):
    ...     return [x * 2 for x in items]
    >>> cp = ChunkedProcessor(process_batch, chunk_size=100)
    >>> results = list(cp.process(range(250)))
    >>> len(results)
    250

    Notes
    -----
    Use this class when you have a reusable processing pipeline that
    will be applied to multiple datasets with the same configuration.

    Complexity
    ----------
    Time: O(n) per process call, Space: O(chunk_size)
    """

    def __init__(
        self,
        processor: Callable[[list[T]], list[R]],
        chunk_size: int = 1000,
        max_memory_mb: int | None = None,
    ) -> None:
        """Initialize chunked processor with configuration."""
        if not callable(processor):
            raise TypeError(
                f"processor must be callable, got {type(processor).__name__}"
            )

        if not isinstance(chunk_size, int):
            raise TypeError(
                f"chunk_size must be an integer, got {type(chunk_size).__name__}"
            )

        if max_memory_mb is not None and not isinstance(max_memory_mb, int):
            raise TypeError(
                f"max_memory_mb must be an integer or None, got {type(max_memory_mb).__name__}"
            )

        if chunk_size <= 0:
            raise ValueError(f"chunk_size must be positive, got {chunk_size}")

        if max_memory_mb is not None and max_memory_mb <= 0:
            raise ValueError(f"max_memory_mb must be positive, got {max_memory_mb}")

        self.processor = processor
        self.chunk_size = chunk_size
        self.max_memory_mb = max_memory_mb

    def process(self, items: Iterable[T]) -> Generator[R]:
        """
        Process items using configured settings.

        Parameters
        ----------
        items : Iterable[T]
            Input items to process.

        Yields
        ------
        R
            Processed results one at a time.

        Examples
        --------
        >>> cp = ChunkedProcessor(lambda x: [i*2 for i in x])
        >>> list(cp.process([1, 2, 3]))
        [2, 4, 6]
        """
        return chunked_processor(
            items,
            self.processor,  # type: ignore[arg-type]
            chunk_size=self.chunk_size,
            max_memory_mb=self.max_memory_mb,
        )


__all__ = ["chunked_processor", "ChunkedProcessor"]
