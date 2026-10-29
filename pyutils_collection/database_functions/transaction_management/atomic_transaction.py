"""
Atomic transaction context manager with automatic rollback.
"""

import logging
from collections.abc import Callable, Generator
from contextlib import contextmanager
from typing import Any

logger = logging.getLogger(__name__)


@contextmanager
def atomic_transaction(
    connection: Any,
    commit_func: Callable[[], None] | None = None,
    rollback_func: Callable[[], None] | None = None,
    begin_func: Callable[[], None] | None = None,
    auto_commit: bool = True,
) -> Generator[Any]:
    """
    Context manager for atomic database transactions with automatic rollback.

    This is library-agnostic - you provide the transaction control functions for your database library.

    Parameters
    ----------
    connection : Any
        Database connection object.
    commit_func : Callable[[], None] | None, optional
        Function to commit the transaction (by default None).
        If None, attempts to call connection.commit().
        Examples: lambda: conn.commit(), lambda: transaction.commit()
    rollback_func : Callable[[], None] | None, optional
        Function to rollback the transaction (by default None).
        If None, attempts to call connection.rollback().
        Examples: lambda: conn.rollback(), lambda: transaction.rollback()
    begin_func : Callable[[], None] | None, optional
        Function to begin the transaction (by default None).
        If None, transaction is assumed to be implicit or already started.
        Examples: lambda: conn.begin(), lambda: cursor.execute("BEGIN")
    auto_commit : bool, optional
        Whether to commit automatically on success (by default True).

    Yields
    ------
    Any
        The database connection within transaction context.

    Raises
    ------
    TypeError
        If parameters are of wrong type.

    Examples
    --------
    >>> # Example 1: SQLAlchemy with explicit transaction control
    >>> from sqlalchemy import create_engine
    >>> engine = create_engine("postgresql://user:pass@localhost/db")
    >>> conn = engine.connect()
    >>> with atomic_transaction(
    ...     conn,
    ...     commit_func=lambda: conn.commit(),
    ...     rollback_func=lambda: conn.rollback()
    ... ) as trans_conn:
    ...     trans_conn.execute("INSERT INTO users VALUES (1, 'Alice')")
    ...     trans_conn.execute("INSERT INTO users VALUES (2, 'Bob')")
    >>> # Automatically committed
    >>>
    >>> # Example 2: psycopg2 with manual transaction control
    >>> import psycopg2
    >>> conn = psycopg2.connect("dbname=mydb user=postgres")
    >>> cursor = conn.cursor()
    >>> with atomic_transaction(
    ...     conn,
    ...     commit_func=lambda: conn.commit(),
    ...     rollback_func=lambda: conn.rollback()
    ... ):
    ...     cursor.execute("INSERT INTO users VALUES (1, 'Alice')")
    ...     cursor.execute("INSERT INTO users VALUES (2, 'Bob')")
    >>>
    >>> # Example 3: psycopg3 with BEGIN statement
    >>> import psycopg
    >>> conn = psycopg.connect("dbname=mydb user=postgres")
    >>> cursor = conn.cursor()
    >>> with atomic_transaction(
    ...     cursor,
    ...     begin_func=lambda: cursor.execute("BEGIN"),
    ...     commit_func=lambda: conn.commit(),
    ...     rollback_func=lambda: conn.rollback()
    ... ):
    ...     cursor.execute("INSERT INTO users VALUES (1, 'Alice')")
    >>>
    >>> # Example 4: Rollback on error
    >>> try:
    ...     with atomic_transaction(
    ...         conn,
    ...         commit_func=lambda: conn.commit(),
    ...         rollback_func=lambda: conn.rollback()
    ...     ):
    ...         cursor.execute("INSERT INTO users VALUES (1, 'Alice')")
    ...         raise ValueError("Something went wrong")
    ... except ValueError:
    ...     pass
    >>> # Automatically rolled back

    Notes
    -----
    - This function is library-agnostic through callable injection
    - Transaction lifecycle: begin (if provided) → operations → commit/rollback
    - Commit happens on successful exit if auto_commit=True
    - Rollback happens automatically on any exception
    - If callables not provided, falls back to connection.commit()/rollback()

    Complexity
    ----------
    Time: O(1), Space: O(1)
    """
    # Input validation
    if connection is None:
        raise TypeError("connection cannot be None")
    if commit_func is not None and not callable(commit_func):
        raise TypeError("commit_func must be callable or None")
    if rollback_func is not None and not callable(rollback_func):
        raise TypeError("rollback_func must be callable or None")
    if begin_func is not None and not callable(begin_func):
        raise TypeError("begin_func must be callable or None")
    if not isinstance(auto_commit, bool):
        raise TypeError(f"auto_commit must be bool, got {type(auto_commit).__name__}")

    try:
        # Begin transaction if begin_func provided
        if begin_func is not None:
            try:
                begin_func()
                logger.debug("Transaction started via begin_func")
            except Exception as e:
                logger.error(f"Failed to begin transaction: {e}")
                raise

        yield connection

        # Commit on success
        if auto_commit:
            if commit_func is not None:
                try:
                    commit_func()
                    logger.debug("Transaction committed via commit_func")
                except Exception as commit_error:
                    logger.error(f"Failed to commit transaction: {commit_error}")
                    raise
            else:
                # Fallback to connection.commit() if no commit_func provided
                try:
                    connection.commit()
                    logger.debug("Transaction committed via connection.commit()")
                except AttributeError:
                    logger.warning(
                        "No commit_func provided and connection.commit() not available"
                    )
                except Exception as commit_error:
                    logger.error(f"Failed to commit transaction: {commit_error}")
                    raise

    except Exception as e:
        # Rollback on error
        logger.warning(f"Transaction failed, rolling back: {e}")

        if rollback_func is not None:
            try:
                rollback_func()
                logger.debug("Transaction rolled back via rollback_func")
            except Exception as rollback_error:
                logger.error(f"Rollback failed: {rollback_error}")
        else:
            # Fallback to connection.rollback() if no rollback_func provided
            try:
                connection.rollback()
                logger.debug("Transaction rolled back via connection.rollback()")
            except AttributeError:
                logger.warning(
                    "No rollback_func provided and connection.rollback() not available"
                )
            except Exception as rollback_error:
                logger.error(f"Rollback failed: {rollback_error}")

        raise


__all__ = ["atomic_transaction"]
