"""
Nested transaction context manager using savepoints.
"""

import logging
import re
import uuid
from collections.abc import Callable, Generator
from contextlib import contextmanager
from typing import Any

logger = logging.getLogger(__name__)

_SAVEPOINT_NAME_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


def _validate_savepoint_name(savepoint_name: str) -> None:
    if not _SAVEPOINT_NAME_PATTERN.match(savepoint_name):
        raise ValueError(
            "savepoint_name must contain only letters, digits, and underscores "
            "and start with a letter or underscore"
        )


@contextmanager
def nested_transaction(
    connection: Any,
    savepoint_name: str | None = None,
    create_savepoint_func: Callable[[str], None] | None = None,
    release_savepoint_func: Callable[[str], None] | None = None,
    rollback_savepoint_func: Callable[[str], None] | None = None,
) -> Generator[Any, None, None]:
    """
    Context manager for nested transactions using savepoints.

    This is library-agnostic - you provide the savepoint control functions for your database library.

    Parameters
    ----------
    connection : Any
        Database connection object.
    savepoint_name : str | None, optional
        Name for the savepoint (auto-generated if None).
    create_savepoint_func : Callable[[str], None] | None, optional
        Function to create a savepoint, receives savepoint name (by default None).
        If None, attempts to call connection.begin_nested() or execute SAVEPOINT SQL.
        Examples:
        - lambda name: cursor.execute(f"SAVEPOINT {name}")
        - lambda name: connection.begin_nested()
    release_savepoint_func : Callable[[str], None] | None, optional
        Function to release a savepoint, receives savepoint name (by default None).
        If None, attempts to commit nested transaction or execute RELEASE SAVEPOINT SQL.
        Examples: lambda name: cursor.execute(f"RELEASE SAVEPOINT {name}")
    rollback_savepoint_func : Callable[[str], None] | None, optional
        Function to rollback to a savepoint, receives savepoint name (by default None).
        If None, attempts to rollback nested transaction or execute ROLLBACK TO SAVEPOINT SQL.
        Examples: lambda name: cursor.execute(f"ROLLBACK TO SAVEPOINT {name}")

    Yields
    ------
    Any
        The database connection within nested transaction context.

    Raises
    ------
    TypeError
        If parameters are of wrong type.

    Examples
    --------
    >>> # Example 1: PostgreSQL with psycopg2 - manual SQL savepoints
    >>> import psycopg2
    >>> conn = psycopg2.connect("dbname=mydb")
    >>> cursor = conn.cursor()
    >>> with atomic_transaction(conn, commit_func=lambda: conn.commit(), rollback_func=lambda: conn.rollback()):
    ...     cursor.execute("INSERT INTO users VALUES (1, 'Alice')")
    ...
    ...     try:
    ...         with nested_transaction(
    ...             cursor,
    ...             create_savepoint_func=lambda name: cursor.execute(f"SAVEPOINT {name}"),
    ...             release_savepoint_func=lambda name: cursor.execute(f"RELEASE SAVEPOINT {name}"),
    ...             rollback_savepoint_func=lambda name: cursor.execute(f"ROLLBACK TO SAVEPOINT {name}")
    ...         ):
    ...             cursor.execute("INSERT INTO users VALUES (2, 'Bob')")
    ...             raise ValueError("Bob's insert failed")
    ...     except ValueError:
    ...         pass  # Bob's insert rolled back to savepoint
    ...
    ...     cursor.execute("INSERT INTO users VALUES (3, 'Charlie')")
    >>> # Alice and Charlie inserted, Bob rolled back
    >>>
    >>> # Example 2: SQLAlchemy with nested transaction support
    >>> from sqlalchemy import create_engine
    >>> engine = create_engine("postgresql://user:pass@localhost/db")
    >>> conn = engine.connect()
    >>> with atomic_transaction(conn, commit_func=lambda: conn.commit(), rollback_func=lambda: conn.rollback()):
    ...     conn.execute("INSERT INTO users VALUES (1, 'Alice')")
    ...
    ...     with nested_transaction(conn):  # Uses connection.begin_nested() by default
    ...         conn.execute("INSERT INTO users VALUES (2, 'Bob')")

    Notes
    -----
    - This function is library-agnostic through callable injection
    - Requires database support for savepoints (PostgreSQL, MySQL, Oracle, SQL Server)
    - Savepoint is created on enter, released on success, rolled back on exception
    - Can be nested multiple levels deep
    - If callables not provided, falls back to connection.begin_nested() or SQL commands

    Complexity
    ----------
    Time: O(1), Space: O(1)
    """
    # Input validation
    if connection is None:
        raise TypeError("connection cannot be None")
    if savepoint_name is not None and not isinstance(savepoint_name, str):
        raise TypeError(
            f"savepoint_name must be str or None, got {type(savepoint_name).__name__}"
        )
    if create_savepoint_func is not None and not callable(create_savepoint_func):
        raise TypeError("create_savepoint_func must be callable or None")
    if release_savepoint_func is not None and not callable(release_savepoint_func):
        raise TypeError("release_savepoint_func must be callable or None")
    if rollback_savepoint_func is not None and not callable(rollback_savepoint_func):
        raise TypeError("rollback_savepoint_func must be callable or None")

    # Generate savepoint name if not provided
    if savepoint_name is None:
        savepoint_name = f"sp_{uuid.uuid4().hex[:8]}"
    else:
        _validate_savepoint_name(savepoint_name)

    used_sql_savepoint = False

    try:
        # Create savepoint
        if create_savepoint_func is not None:
            try:
                create_savepoint_func(savepoint_name)
                logger.debug(
                    f"Savepoint '{savepoint_name}' created via create_savepoint_func"
                )
            except Exception as e:
                logger.error(f"Failed to create savepoint: {e}")
                raise
        else:
            # Fallback: try connection.begin_nested() or manual SQL
            try:
                connection.begin_nested()
                logger.debug(
                    f"Savepoint '{savepoint_name}' created via connection.begin_nested()"
                )
            except AttributeError:
                try:
                    connection.execute(f"SAVEPOINT {savepoint_name}")
                    used_sql_savepoint = True
                    logger.debug(f"Savepoint '{savepoint_name}' created via SQL")
                except Exception as e:
                    logger.error(f"Failed to create savepoint: {e}")
                    raise

        yield connection

        # Release savepoint on success
        if release_savepoint_func is not None:
            try:
                release_savepoint_func(savepoint_name)
                logger.debug(
                    f"Savepoint '{savepoint_name}' released via release_savepoint_func"
                )
            except Exception as e:
                logger.warning(f"Failed to release savepoint: {e}")
        else:
            # Fallback: try SQL release before committing the outer transaction
            if used_sql_savepoint or hasattr(connection, "execute"):
                try:
                    connection.execute(f"RELEASE SAVEPOINT {savepoint_name}")
                    logger.debug(f"Savepoint '{savepoint_name}' released via SQL")
                except AttributeError:
                    try:
                        connection.commit()
                        logger.debug(
                            f"Savepoint '{savepoint_name}' released via connection.commit()"
                        )
                    except AttributeError as e:
                        logger.warning(f"Failed to release savepoint: {e}")
                except Exception as e:
                    logger.warning(f"Failed to release savepoint: {e}")
            else:
                try:
                    connection.commit()
                    logger.debug(
                        f"Savepoint '{savepoint_name}' released via connection.commit()"
                    )
                except AttributeError as e:
                    logger.warning(f"Failed to release savepoint: {e}")

    except Exception as e:
        # Rollback to savepoint on error
        logger.warning(
            f"Nested transaction failed, rolling back to savepoint '{savepoint_name}': {e}"
        )

        if rollback_savepoint_func is not None:
            try:
                rollback_savepoint_func(savepoint_name)
                logger.debug(
                    f"Rolled back to savepoint '{savepoint_name}' via rollback_savepoint_func"
                )
            except Exception as rollback_error:
                logger.error(f"Savepoint rollback failed: {rollback_error}")
        else:
            # Fallback: prefer savepoint rollback over full transaction rollback
            if used_sql_savepoint or hasattr(connection, "execute"):
                try:
                    connection.execute(f"ROLLBACK TO SAVEPOINT {savepoint_name}")
                    logger.debug(f"Rolled back to savepoint '{savepoint_name}' via SQL")
                except AttributeError:
                    try:
                        connection.rollback()
                        logger.debug(
                            f"Rolled back to savepoint '{savepoint_name}' via connection.rollback()"
                        )
                    except Exception as rollback_error:
                        logger.error(f"Savepoint rollback failed: {rollback_error}")
                except Exception as rollback_error:
                    logger.error(f"Savepoint rollback failed: {rollback_error}")
            else:
                try:
                    connection.rollback()
                    logger.debug(
                        f"Rolled back to savepoint '{savepoint_name}' via connection.rollback()"
                    )
                except AttributeError:
                    try:
                        connection.execute(f"ROLLBACK TO SAVEPOINT {savepoint_name}")
                        logger.debug(f"Rolled back to savepoint '{savepoint_name}' via SQL")
                    except Exception as rollback_error:
                        logger.error(f"Savepoint rollback failed: {rollback_error}")

        raise


__all__ = ["nested_transaction"]
