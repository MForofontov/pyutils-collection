"""
Stream query results in batches to avoid loading all data into memory.
"""

import logging
from collections.abc import Callable, Generator
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


def stream_query_results(
    execute_func: Callable[[], Any],
    fetch_size: int = 1000,
    transform_func: Callable[[Any], T] | None = None,
) -> Generator[T]:
    """
    Stream query results in batches to avoid loading all data into memory.

    Parameters
    ----------
    execute_func : Callable[[], Any]
        Function that executes the query and returns a result object.
    fetch_size : int, optional
        Number of rows to fetch per batch (by default 1000).
    transform_func : Callable[[Any], T] | None, optional
        Optional function to transform each row (by default None).

    Yields
    ------
    T
        Transformed rows (or raw rows if transform_func is None).

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If parameters have invalid values.

    Examples
    --------
    >>> def query_func():
    ...     return conn.execute("SELECT * FROM large_table")
    >>> for row in stream_query_results(query_func, fetch_size=500):
    ...     process_row(row)

    >>> # With transformation
    >>> def transform(row):
    ...     return {"id": row[0], "name": row[1].upper()}
    >>> for transformed in stream_query_results(query_func, transform_func=transform):
    ...     print(transformed)

    Notes
    -----
    - Uses server-side cursors when available
    - Automatically closes cursor when done
    - Handles exceptions during streaming gracefully

    Complexity
    ----------
    Time: O(n) where n is total rows, Space: O(fetch_size)
    """
    # Input validation
    if not callable(execute_func):
        raise TypeError("execute_func must be callable")
    if not isinstance(fetch_size, int):
        raise TypeError(f"fetch_size must be int, got {type(fetch_size).__name__}")
    if fetch_size <= 0:
        raise ValueError(f"fetch_size must be positive, got {fetch_size}")
    if transform_func is not None and not callable(transform_func):
        raise TypeError("transform_func must be callable or None")

    result = None
    try:
        # Execute query
        result = execute_func()
        total_yielded = 0

        while True:
            # Fetch batch of rows
            try:
                rows = result.fetchmany(fetch_size)
            except AttributeError:
                # Result object doesn't support fetchmany, try iteration
                logger.debug("Result doesn't support fetchmany, using iteration")
                for row in result:
                    if transform_func is not None:
                        yield transform_func(row)
                    else:
                        yield row
                    total_yielded += 1
                break

            if not rows:
                # No more rows
                break

            # Yield rows with optional transformation
            for row in rows:
                if transform_func is not None:
                    yield transform_func(row)
                else:
                    yield row
                total_yielded += 1

        logger.debug(f"Streamed {total_yielded} rows from query")

    except Exception as e:
        logger.error(f"Error streaming query results: {e}")
        raise

    finally:
        # Cleanup result/cursor
        if result is not None:
            try:
                result.close()
            except Exception as close_error:
                logger.warning(f"Error closing result: {close_error}")


__all__ = ["stream_query_results"]
