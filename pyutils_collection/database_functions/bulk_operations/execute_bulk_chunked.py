"""
Execute bulk database operations with chunking and error handling.
"""

import logging
from collections.abc import Callable, Sequence
from typing import Any, Literal, TypedDict

logger = logging.getLogger(__name__)


class BulkOperationResult(TypedDict):
    """Result of a bulk operation."""

    successful: int
    failed: int
    total: int
    errors: list[dict[str, Any]]


def execute_bulk_chunked(
    connection: Any,
    statement_executor: Callable[[Sequence[dict[str, Any]]], Any],
    data: Sequence[dict[str, Any]],
    chunk_size: int = 1000,
    on_error: Literal["fail_fast", "skip", "continue"] = "fail_fast",
    commit_func: Callable[[], None] | None = None,
    rollback_func: Callable[[], None] | None = None,
    progress_callback: Callable[[int, int], None] | None = None,
) -> BulkOperationResult:
    """
    Execute bulk database operations (insert, update, upsert) in chunks with error handling.

    Parameters
    ----------
    connection : Any
        Database connection object (SQLAlchemy connection, cursor, etc.).
    statement_executor : Callable[[Sequence[dict[str, Any]]], Any]
        Function that takes a chunk of data and executes the database operation.
        This is library-agnostic - you provide the execution logic for your chosen library.

        For "skip" or "continue" error handling, include commit logic in your executor if needed:
        - With commit: lambda chunk: (cursor.executemany(..., chunk), conn.commit())
        - Without commit: lambda chunk: cursor.executemany(..., chunk)  # Caller commits at end

        Examples by library:
        - SQLAlchemy: lambda chunk: conn.execute(table.insert(), chunk)
        - psycopg2: lambda chunk: execute_values(cursor, "INSERT INTO ...", [(r['col1'], r['col2']) for r in chunk])
        - psycopg3: lambda chunk: cursor.executemany("INSERT INTO ... VALUES (%s, %s)", chunk)
        - pymongo: lambda chunk: collection.insert_many(chunk)
        - MySQL connector: lambda chunk: cursor.executemany("INSERT INTO ... VALUES (%s, %s)", [tuple(r.values()) for r in chunk])
    data : Sequence[dict[str, Any]]
        List of dictionaries representing rows to process.
    chunk_size : int, optional
        Number of rows to process per chunk (by default 1000).
    on_error : Literal["fail_fast", "skip", "continue"], optional
        Error handling strategy (by default "fail_fast"):
        - "fail_fast": Raise exception immediately on first error (caller handles transaction)
        - "skip": Skip entire failed chunk and continue processing
        - "continue": Try processing failed chunk row by row
    commit_func : Callable[[], None] | None, optional
        Function to commit the current transaction (by default None).
        When provided and using "skip" or "continue" modes, automatically commits after each successful chunk.
        For "fail_fast" mode, this is ignored (caller manages transaction).
        Examples: lambda: conn.commit(), lambda: connection.commit()
    rollback_func : Callable[[], None] | None, optional
        Function to rollback the current transaction (by default None).
        When provided and using "skip" or "continue" modes, automatically rolls back failed chunks.
        Examples: lambda: conn.rollback(), lambda: connection.rollback()
        Also invoked before propagating an execution failure in "fail_fast" mode.
    progress_callback : Callable[[int, int], None] | None, optional
        Function called after each chunk with (completed, total) counts.

    Returns
    -------
    BulkOperationResult
        Dictionary containing operation statistics and error details.
        With a commit callback, rows count as successful only after it returns
        successfully. Failed per-row commits invoke the rollback callback before
        processing the next row.

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If parameters have invalid values.

    Examples
    --------
    >>> # Example 1: SQLAlchemy - INSERT with automatic transaction (fail_fast)
    >>> from sqlalchemy import create_engine, Table, MetaData
    >>> engine = create_engine("postgresql://user:pass@localhost/db")
    >>> metadata = MetaData()
    >>> users = Table('users', metadata, autoload_with=engine)
    >>> data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
    >>> with engine.begin() as conn:  # Transaction managed by context manager
    ...     result = execute_bulk_chunked(
    ...         conn,
    ...         lambda chunk: conn.execute(users.insert(), chunk),
    ...         data,
    ...         on_error="fail_fast"  # Raises on error, context manager rolls back
    ...     )
    >>>
    >>> # Example 2: psycopg2 - INSERT with automatic per-chunk commit (skip errors)
    >>> import psycopg2
    >>> from psycopg2.extras import execute_values
    >>> conn = psycopg2.connect("dbname=mydb user=postgres")
    >>> cursor = conn.cursor()
    >>> data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
    >>> result = execute_bulk_chunked(
    ...     cursor,
    ...     lambda chunk: execute_values(
    ...         cursor,
    ...         "INSERT INTO users (name, age) VALUES %s",
    ...         [(r['name'], r['age']) for r in chunk]
    ...     ),
    ...     data,
    ...     on_error="skip",
    ...     commit_func=lambda: conn.commit(),  # Auto-commit after each chunk
    ...     rollback_func=lambda: conn.rollback()  # Auto-rollback failed chunks
    ... )  # Successful chunks already committed
    >>>
    >>> # Example 3: psycopg3 - INSERT with continue on error (per-row commit)
    >>> import psycopg
    >>> conn = psycopg.connect("dbname=mydb user=postgres")
    >>> cursor = conn.cursor()
    >>> result = execute_bulk_chunked(
    ...     cursor,
    ...     lambda chunk: cursor.executemany(
    ...         "INSERT INTO users (name, age) VALUES (%(name)s, %(age)s)",
    ...         chunk
    ...     ),
    ...     data,
    ...     on_error="continue",  # Process rows individually on chunk failure
    ...     commit_func=lambda: conn.commit(),  # Commit each successful row
    ...     rollback_func=lambda: conn.rollback()
    ... )
    >>> conn.close()
    >>>
    >>> # Example 4: pymongo - INSERT
    >>> from pymongo import MongoClient
    >>> client = MongoClient("mongodb://localhost:27017/")
    >>> db = client['mydb']
    >>> collection = db['users']
    >>> result = execute_bulk_chunked(
    ...     collection,
    ...     lambda chunk: collection.insert_many(chunk),
    ...     data
    ... )
    >>>
    >>> # Example 5: MySQL Connector - INSERT
    >>> import mysql.connector
    >>> conn = mysql.connector.connect(host="localhost", user="root", database="mydb")
    >>> cursor = conn.cursor()
    >>> result = execute_bulk_chunked(
    ...     cursor,
    ...     lambda chunk: cursor.executemany(
    ...         "INSERT INTO users (name, age) VALUES (%s, %s)",
    ...         [(r['name'], r['age']) for r in chunk]
    ...     ),
    ...     data
    ... )
    >>> conn.commit()
    >>>
    >>> # Example 6: SQLAlchemy - UPSERT with continue on error
    >>> from sqlalchemy.dialects.postgresql import insert
    >>> with engine.begin() as conn:
    ...     result = execute_bulk_chunked(
    ...         conn,
    ...         lambda chunk: conn.execute(
    ...             insert(users).values(chunk)
    ...             .on_conflict_do_update(
    ...                 index_elements=['id'],
    ...                 set_=dict(name=insert.excluded.name, age=insert.excluded.age)
    ...             )
    ...         ),
    ...         data,
    ...         on_error="continue"  # Try each row individually on chunk failure
    ...     )  # Context manager commits if no exception raised


    Notes
    -----
    - Transaction management:
      * "fail_fast" mode: Caller manages transaction (commit_func/rollback_func ignored)
      * "skip"/"continue" modes: If commit_func provided, commits after each successful chunk
      * "skip"/"continue" modes: If rollback_func provided, rolls back failed chunks
    - Without commit_func in "skip"/"continue" modes, caller must commit manually
    - Progress callback is called synchronously and should be fast
    - Row indices in error list refer to original data sequence

    Complexity
    ----------
    Time: O(n) where n is len(data), Space: O(chunk_size)
    """
    # Input validation
    if connection is None:
        raise TypeError("connection cannot be None")
    if not callable(statement_executor):
        raise TypeError("statement_executor must be callable")
    if not isinstance(data, Sequence):
        raise TypeError(f"data must be a Sequence, got {type(data).__name__}")
    if not isinstance(chunk_size, int):
        raise TypeError(f"chunk_size must be int, got {type(chunk_size).__name__}")
    if chunk_size <= 0:
        raise ValueError(f"chunk_size must be positive, got {chunk_size}")
    if on_error not in ("fail_fast", "skip", "continue"):
        raise ValueError(
            f"on_error must be 'fail_fast', 'skip', or 'continue', got {on_error!r}"
        )
    if commit_func is not None and not callable(commit_func):
        raise TypeError("commit_func must be callable or None")
    if rollback_func is not None and not callable(rollback_func):
        raise TypeError("rollback_func must be callable or None")
    if progress_callback is not None and not callable(progress_callback):
        raise TypeError("progress_callback must be callable or None")

    total = len(data)
    successful = 0
    failed = 0
    errors: list[dict[str, Any]] = []

    logger.info(f"Starting bulk operation on {total} rows with chunk_size={chunk_size}")

    for chunk_idx in range(0, total, chunk_size):
        chunk_end = min(chunk_idx + chunk_size, total)
        chunk = data[chunk_idx:chunk_end]
        chunk_number = chunk_idx // chunk_size + 1

        try:
            # Execute operation for this chunk
            statement_executor(chunk)
            logger.debug(
                f"Chunk {chunk_number} processed successfully ({len(chunk)} rows)"
            )

            # Commit after successful chunk for error-tolerant modes
            if on_error in ("skip", "continue") and commit_func is not None:
                try:
                    commit_func()
                    logger.debug(f"Chunk {chunk_number} committed")
                except Exception as commit_error:
                    logger.error(
                        f"Failed to commit chunk {chunk_number}: {commit_error}"
                    )
                    raise

            successful += len(chunk)

        except Exception as e:
            logger.warning(f"Chunk {chunk_number} failed: {e}")

            if on_error == "fail_fast":
                # Rollback if rollback_func provided, then re-raise
                if rollback_func is not None:
                    try:
                        rollback_func()
                        logger.debug(
                            f"Rolled back transaction for failed chunk {chunk_number}"
                        )
                    except Exception as rollback_error:
                        logger.error(
                            f"Failed to rollback transaction: {rollback_error}"
                        )

                logger.error(
                    f"Bulk operation failed at chunk {chunk_number}, failing fast"
                )
                raise

            elif on_error == "skip":
                # Rollback failed chunk if rollback_func provided
                if rollback_func is not None:
                    try:
                        rollback_func()
                        logger.debug(f"Rolled back failed chunk {chunk_number}")
                    except Exception as rollback_error:
                        logger.warning(
                            f"Failed to rollback chunk {chunk_number}: {rollback_error}"
                        )

                # Skip entire chunk and record error
                failed += len(chunk)
                errors.append(
                    {
                        "chunk_index": chunk_number,
                        "row_indices": list(range(chunk_idx, chunk_end)),
                        "error": str(e),
                        "error_type": type(e).__name__,
                    }
                )
                logger.warning(f"Skipped chunk {chunk_number} ({len(chunk)} rows)")

            elif on_error == "continue":
                # Rollback failed chunk before retrying rows individually
                if rollback_func is not None:
                    try:
                        rollback_func()
                        logger.debug(f"Rolled back failed chunk {chunk_number}")
                    except Exception as rollback_error:
                        logger.warning(
                            f"Failed to rollback chunk {chunk_number}: {rollback_error}"
                        )

                # Try executing rows individually
                logger.debug(
                    f"Attempting individual operations for chunk {chunk_number}"
                )
                for row_offset, row in enumerate(chunk):
                    row_index = chunk_idx + row_offset
                    try:
                        statement_executor([row])
                        successful += 1

                        # Commit each successful row if commit_func provided
                        if commit_func is not None:
                            try:
                                commit_func()
                            except Exception as commit_error:
                                logger.warning(
                                    f"Failed to commit row {row_index}: {commit_error}"
                                )
                                # Treat as failed if commit fails
                                successful -= 1
                                failed += 1
                                errors.append(
                                    {
                                        "row_index": row_index,
                                        "row_data": row,
                                        "error": f"Commit failed: {commit_error}",
                                        "error_type": "CommitError",
                                    }
                                )
                                if rollback_func is not None:
                                    try:
                                        rollback_func()
                                    except Exception as rollback_error:
                                        logger.warning(
                                            f"Failed to rollback row {row_index}: {rollback_error}"
                                        )
                    except Exception as row_error:
                        failed += 1
                        errors.append(
                            {
                                "row_index": row_index,
                                "row_data": row,
                                "error": str(row_error),
                                "error_type": type(row_error).__name__,
                            }
                        )
                        logger.debug(f"Row {row_index} failed: {row_error}")

                        # Rollback failed row if rollback_func provided
                        if rollback_func is not None:
                            try:
                                rollback_func()
                            except Exception as rollback_error:
                                logger.warning(
                                    f"Failed to rollback row {row_index}: {rollback_error}"
                                )

        # Call progress callback
        if progress_callback is not None:
            try:
                progress_callback(successful + failed, total)
            except Exception as callback_error:
                logger.warning(f"Progress callback failed: {callback_error}")

    result: BulkOperationResult = {
        "successful": successful,
        "failed": failed,
        "total": total,
        "errors": errors,
    }

    logger.info(
        f"Bulk operation completed: {successful}/{total} successful, "
        f"{failed} failed, {len(errors)} errors recorded"
    )

    return result


__all__ = ["BulkOperationResult", "execute_bulk_chunked"]
