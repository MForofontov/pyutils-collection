"""
Managed database connection with automatic retry and cleanup.
"""

import logging
import time
from collections.abc import Callable, Generator
from contextlib import contextmanager
from typing import Any, Protocol, TypeVar

logger = logging.getLogger(__name__)


class DatabaseConnection(Protocol):
    """Protocol for database connection objects."""

    def execute(self, query: str) -> Any:
        """Execute a query."""
        ...

    def close(self) -> None:
        """Close the connection."""
        ...


T = TypeVar("T", bound=DatabaseConnection)


@contextmanager
def managed_db_connection(
    connection_factory: Callable[[], T],
    max_retries: int = 3,
    retry_delay: float = 1.0,
    health_check_query: str | None = "SELECT 1",
) -> Generator[T, None, None]:
    """
    Context manager for database connection with automatic retry and cleanup.

    Parameters
    ----------
    connection_factory : Callable[[], T]
        Function that creates a database connection.
    max_retries : int, optional
        Maximum number of connection attempts (by default 3).
    retry_delay : float, optional
        Initial delay between retries in seconds (by default 1.0).
    health_check_query : str | None, optional
        SQL query to verify connection health (by default "SELECT 1").

    Yields
    ------
    T
        Database connection object.

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If parameters have invalid values.
    RuntimeError
        If unable to establish connection after all retries.

    Examples
    --------
    >>> def create_conn():
    ...     return create_engine("postgresql://...").connect()
    >>> with managed_db_connection(create_conn, max_retries=3) as conn:
    ...     result = conn.execute("SELECT * FROM users")

    Notes
    -----
    Uses exponential backoff for retries: delay * (2 ** attempt).

    Complexity
    ----------
    Time: O(1) per attempt, Space: O(1)
    """
    # Input validation
    if not callable(connection_factory):
        raise TypeError("connection_factory must be callable")
    if not isinstance(max_retries, int):
        raise TypeError(f"max_retries must be int, got {type(max_retries).__name__}")
    if max_retries < 1:
        raise ValueError(f"max_retries must be at least 1, got {max_retries}")
    if not isinstance(retry_delay, (int, float)):
        raise TypeError(
            f"retry_delay must be a number, got {type(retry_delay).__name__}"
        )
    if retry_delay <= 0:
        raise ValueError(f"retry_delay must be positive, got {retry_delay}")
    if health_check_query is not None and not isinstance(health_check_query, str):
        raise TypeError(
            f"health_check_query must be str or None, got {type(health_check_query).__name__}"
        )

    connection = None
    last_error = None

    for attempt in range(max_retries):
        try:
            # Attempt to create connection
            connection = connection_factory()

            # Perform health check if specified
            if health_check_query is not None:
                try:
                    connection.execute(health_check_query)
                except Exception as health_error:
                    logger.warning(
                        f"Health check failed on attempt {attempt + 1}: {health_error}"
                    )
                    try:
                        connection.close()
                    except Exception:
                        pass
                    connection = None
                    raise health_error

            # Connection successful
            logger.debug(f"Database connection established on attempt {attempt + 1}")
            yield connection
            return

        except Exception as e:
            last_error = e
            logger.warning(
                f"Connection attempt {attempt + 1}/{max_retries} failed: {e}"
            )

            if attempt < max_retries - 1:
                # Exponential backoff
                sleep_time = retry_delay * (2**attempt)
                logger.debug(f"Retrying in {sleep_time} seconds...")
                time.sleep(sleep_time)
            else:
                # Final attempt failed
                logger.error(f"All connection attempts failed. Last error: {e}")

        finally:
            # Cleanup connection if established
            if connection is not None:
                try:
                    connection.close()
                    logger.debug("Connection closed successfully")
                except Exception as close_error:
                    logger.error(f"Error closing connection: {close_error}")

    # All retries exhausted
    raise RuntimeError(
        f"Failed to establish database connection after {max_retries} attempts. "
        f"Last error: {last_error}"
    )


__all__ = ["managed_db_connection"]
