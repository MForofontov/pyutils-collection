"""
Connection pool manager with health checks.
"""

import logging
import time
from collections.abc import Callable, Generator
from contextlib import contextmanager
from typing import Any

logger = logging.getLogger(__name__)


class ConnectionPoolManager:
    """
    Manages database connection pool with health monitoring and automatic recovery.

    Attributes
    ----------
    connection_factory : Callable
        Function that creates a new database connection.
    max_connections : int
        Maximum number of connections in the pool.
    health_check_query : str | None
        SQL query to verify connection health.

    Examples
    --------
    >>> def create_conn():
    ...     return create_engine("postgresql://...").connect()
    >>> pool = ConnectionPoolManager(create_conn, max_connections=5)
    >>> with pool.get_connection() as conn:
    ...     result = conn.execute("SELECT 1")
    """

    def __init__(
        self,
        connection_factory: Callable[[], Any],
        max_connections: int = 10,
        health_check_query: str | None = "SELECT 1",
        health_check_interval: float = 60.0,
    ) -> None:
        """
        Initialize the connection pool manager.

        Parameters
        ----------
        connection_factory : Callable[[], Any]
            Function that creates a new database connection.
        max_connections : int, optional
            Maximum number of connections in pool (by default 10).
        health_check_query : str | None, optional
            SQL query to verify connection health (by default "SELECT 1").
        health_check_interval : float, optional
            Seconds between health checks (by default 60.0).

        Raises
        ------
        TypeError
            If parameters are of wrong type.
        ValueError
            If parameters have invalid values.
        """
        if not callable(connection_factory):
            raise TypeError("connection_factory must be callable")
        if not isinstance(max_connections, int):
            raise TypeError(
                f"max_connections must be int, got {type(max_connections).__name__}"
            )
        if max_connections <= 0:
            raise ValueError(f"max_connections must be positive, got {max_connections}")
        if health_check_query is not None and not isinstance(health_check_query, str):
            raise TypeError(
                f"health_check_query must be str or None, got {type(health_check_query).__name__}"
            )
        if not isinstance(health_check_interval, (int, float)):
            raise TypeError(
                f"health_check_interval must be a number, got {type(health_check_interval).__name__}"
            )
        if health_check_interval <= 0:
            raise ValueError(
                f"health_check_interval must be positive, got {health_check_interval}"
            )

        self._connection_factory = connection_factory
        self._max_connections = max_connections
        self._health_check_query = health_check_query
        self._health_check_interval = health_check_interval
        self._pool: list[dict[str, Any]] = []
        self._active_connections: int = 0
        self._total_created: int = 0
        self._total_closed: int = 0

    def _create_connection(self) -> dict[str, Any]:
        """Create a new connection with metadata."""
        conn = self._connection_factory()
        self._total_created += 1
        return {
            "connection": conn,
            "created_at": time.time(),
            "last_health_check": time.time(),
            "is_healthy": True,
        }

    def _check_health(self, conn_info: dict[str, Any]) -> bool:
        """
        Check if connection is healthy.

        Parameters
        ----------
        conn_info : dict[str, Any]
            Connection info dictionary.

        Returns
        -------
        bool
            True if connection is healthy, False otherwise.
        """
        if self._health_check_query is None:
            return True

        now = time.time()
        if now - conn_info["last_health_check"] < self._health_check_interval:
            return bool(conn_info["is_healthy"])

        try:
            conn = conn_info["connection"]
            # Attempt to execute health check query
            conn.execute(self._health_check_query)
            conn_info["last_health_check"] = now
            conn_info["is_healthy"] = True
            return True
        except Exception as e:
            logger.warning(f"Connection health check failed: {e}")
            conn_info["is_healthy"] = False
            return False

    @contextmanager
    def get_connection(self) -> Generator[Any]:
        """
        Get a connection from the pool with automatic health check.

        Yields
        ------
        Any
            Database connection object.

        Raises
        ------
        RuntimeError
            If unable to get a healthy connection.

        Examples
        --------
        >>> with pool.get_connection() as conn:
        ...     result = conn.execute("SELECT * FROM users")
        """
        conn_info = None
        connection = None

        try:
            # Try to get connection from pool
            while self._pool:
                conn_info = self._pool.pop(0)
                if self._check_health(conn_info):
                    connection = conn_info["connection"]
                    self._active_connections += 1
                    break
                else:
                    # Close unhealthy connection
                    try:
                        conn_info["connection"].close()
                        self._total_closed += 1
                    except Exception:
                        pass
                    conn_info = None

            # Create new connection if needed
            if connection is None:
                if self._active_connections >= self._max_connections:
                    raise RuntimeError(
                        f"Maximum connections ({self._max_connections}) reached"
                    )
                conn_info = self._create_connection()
                connection = conn_info["connection"]
                self._active_connections += 1

            yield connection

        finally:
            # Return connection to pool
            if connection is not None:
                self._active_connections -= 1
                if conn_info and self._check_health(conn_info):
                    self._pool.append(conn_info)
                else:
                    # Close unhealthy connection
                    try:
                        connection.close()
                        self._total_closed += 1
                    except Exception:
                        pass

    def get_stats(self) -> dict[str, int]:
        """
        Get connection pool statistics.

        Returns
        -------
        dict[str, int]
            Dictionary with pool statistics.
        """
        return {
            "pool_size": len(self._pool),
            "active_connections": self._active_connections,
            "max_connections": self._max_connections,
            "total_created": self._total_created,
            "total_closed": self._total_closed,
        }

    def close_all(self) -> None:
        """Close all connections in the pool."""
        for conn_info in self._pool:
            try:
                conn_info["connection"].close()
                self._total_closed += 1
            except Exception as e:
                logger.error(f"Error closing connection: {e}")

        self._pool.clear()


__all__ = ["ConnectionPoolManager"]
