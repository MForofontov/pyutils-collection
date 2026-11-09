"""
Explicit savepoint context manager with error handling.
"""

import logging
from collections.abc import Callable, Generator
from contextlib import contextmanager
from typing import Any

from .nested_transaction import _validate_savepoint_name

logger = logging.getLogger(__name__)


@contextmanager
def savepoint_context(
    connection: Any,
    savepoint_name: str,
    on_error: str = "rollback",
    create_savepoint_func: Callable[[str], None] | None = None,
    release_savepoint_func: Callable[[str], None] | None = None,
    rollback_savepoint_func: Callable[[str], None] | None = None,
) -> Generator[Any]:
    """
    Context manager for explicit savepoint management with error handling.

    This is library-agnostic - you provide the savepoint control functions for your database library.

    Parameters
    ----------
    connection : Any
        Database connection object.
    savepoint_name : str
        Name for the savepoint.
    on_error : str, optional
        Error handling strategy: "rollback" or "ignore" (by default "rollback").
    create_savepoint_func : Callable[[str], None] | None, optional
        Function to create a savepoint, receives savepoint name (by default None).
        If None, executes SQL: SAVEPOINT {savepoint_name}.
        Examples: lambda name: cursor.execute(f"SAVEPOINT {name}")
    release_savepoint_func : Callable[[str], None] | None, optional
        Function to release a savepoint, receives savepoint name (by default None).
        If None, executes SQL: RELEASE SAVEPOINT {savepoint_name}.
        Examples: lambda name: cursor.execute(f"RELEASE SAVEPOINT {name}")
    rollback_savepoint_func : Callable[[str], None] | None, optional
        Function to rollback to a savepoint, receives savepoint name (by default None).
        If None, executes SQL: ROLLBACK TO SAVEPOINT {savepoint_name}.
        Examples: lambda name: cursor.execute(f"ROLLBACK TO SAVEPOINT {name}")

    Yields
    ------
    Any
        The database connection within savepoint context.

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If parameters have invalid values.

    Examples
    --------
    >>> # Example 1: PostgreSQL with psycopg2 - default SQL execution
    >>> import psycopg2
    >>> conn = psycopg2.connect("dbname=mydb")
    >>> cursor = conn.cursor()
    >>> with savepoint_context(cursor, "before_risky_operation"):
    ...     cursor.execute("DELETE FROM users WHERE inactive = true")
    >>> # If DELETE fails, automatically rollback to savepoint
    >>>
    >>> # Example 2: With explicit callable functions
    >>> with savepoint_context(
    ...     cursor,
    ...     "optional_insert",
    ...     on_error="ignore",
    ...     create_savepoint_func=lambda name: cursor.execute(f"SAVEPOINT {name}"),
    ...     release_savepoint_func=lambda name: cursor.execute(f"RELEASE SAVEPOINT {name}"),
    ...     rollback_savepoint_func=lambda name: cursor.execute(f"ROLLBACK TO SAVEPOINT {name}")
    ... ):
    ...     cursor.execute("INSERT INTO logs VALUES ('optional entry')")
    >>> # If INSERT fails, error is ignored (no rollback)
    >>>
    >>> # Example 3: MySQL with mysql.connector
    >>> import mysql.connector
    >>> conn = mysql.connector.connect(host="localhost", database="mydb")
    >>> cursor = conn.cursor()
    >>> with savepoint_context(cursor, "audit_savepoint"):
    ...     cursor.execute("INSERT INTO audit_log VALUES (NOW(), 'action')")

    Notes
    -----
    - This function is library-agnostic through callable injection
    - Requires database support for savepoints
    - "rollback" mode: Roll back to and release the savepoint, then re-raise.
    - "ignore" mode: Ignore body errors, retain partial work, and release the
      savepoint. Database errors that abort the transaction may prevent release.
    - Setup and release failures propagate even in "ignore" mode. If rollback
      fails, log the cleanup failure and preserve the original body exception;
      do not release a savepoint whose rollback failed.
    - Cancellation, KeyboardInterrupt, and SystemExit always roll back and
      release the savepoint, then propagate, even in "ignore" mode.
    - If callables not provided, falls back to standard SQL commands

    Complexity
    ----------
    Time: O(1), Space: O(1)
    """
    # Input validation
    if connection is None:
        raise TypeError("connection cannot be None")
    if not isinstance(savepoint_name, str):
        raise TypeError(
            f"savepoint_name must be str, got {type(savepoint_name).__name__}"
        )
    if not savepoint_name:
        raise ValueError("savepoint_name cannot be empty")
    _validate_savepoint_name(savepoint_name)
    if on_error not in ("rollback", "ignore"):
        raise ValueError(f"on_error must be 'rollback' or 'ignore', got {on_error!r}")
    if create_savepoint_func is not None and not callable(create_savepoint_func):
        raise TypeError("create_savepoint_func must be callable or None")
    if release_savepoint_func is not None and not callable(release_savepoint_func):
        raise TypeError("release_savepoint_func must be callable or None")
    if rollback_savepoint_func is not None and not callable(rollback_savepoint_func):
        raise TypeError("rollback_savepoint_func must be callable or None")

    # Setup failures must propagate; there is no owned savepoint to clean up yet.
    if create_savepoint_func is not None:
        create_savepoint_func(savepoint_name)
    else:
        connection.execute(f"SAVEPOINT {savepoint_name}")

    def release() -> None:
        if release_savepoint_func is not None:
            release_savepoint_func(savepoint_name)
        else:
            connection.execute(f"RELEASE SAVEPOINT {savepoint_name}")

    try:
        yield connection
    except BaseException as error:
        if on_error == "rollback" or not isinstance(error, Exception):
            logger.warning("Rolling back to savepoint '%s': %s", savepoint_name, error)
            try:
                if rollback_savepoint_func is not None:
                    rollback_savepoint_func(savepoint_name)
                else:
                    connection.execute(f"ROLLBACK TO SAVEPOINT {savepoint_name}")
            except Exception as rollback_error:
                # Releasing after a failed rollback could retain unwanted writes.
                logger.error("Savepoint rollback failed: %s", rollback_error)
            else:
                try:
                    release()
                except Exception as release_error:
                    logger.error("Savepoint release failed: %s", release_error)
            raise
        logger.warning("Error in savepoint '%s' (ignored): %s", savepoint_name, error)
        # Ignore body failures, retaining partial work as documented. Lifecycle
        # failures still propagate so callers can repair the transaction state.
        release()
    else:
        release()


__all__ = ["savepoint_context"]
