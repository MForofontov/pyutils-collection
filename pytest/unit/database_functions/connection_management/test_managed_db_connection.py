"""
Unit tests for managed_db_connection function.
"""

import sqlite3

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.database]
from pyutils_collection.database_functions import managed_db_connection


def test_managed_db_connection_successful_operation() -> None:
    """
    Test case 1: Successful database operation with automatic cleanup.
    """

    # Arrange
    def create_conn():
        conn = sqlite3.connect(":memory:")
        conn.execute("CREATE TABLE users (id INTEGER, name TEXT)")
        return conn

    # Act
    with managed_db_connection(create_conn) as conn:
        conn.execute("INSERT INTO users VALUES (1, 'Alice')")
        result = conn.execute("SELECT * FROM users").fetchall()

    # Assert
    assert len(result) == 1
    assert result[0] == (1, "Alice")


def test_managed_db_connection_retry_on_failure() -> None:
    """
    Test case 2: Retries connection on failure and eventually succeeds.
    """
    # Arrange
    attempt_count = [0]

    def create_conn_with_failures():
        attempt_count[0] += 1
        if attempt_count[0] < 3:
            raise ConnectionError("Connection failed")
        conn = sqlite3.connect(":memory:")
        conn.execute("CREATE TABLE test (id INTEGER)")
        return conn

    # Act
    with managed_db_connection(
        create_conn_with_failures, max_retries=3, retry_delay=0.01
    ) as conn:
        conn.execute("INSERT INTO test VALUES (1)")
        result = conn.execute("SELECT * FROM test").fetchall()

    # Assert
    assert len(result) == 1
    assert attempt_count[0] == 3


def test_managed_db_connection_max_retries_exceeded() -> None:
    """
    Test case 3: Raises RuntimeError after max retries exceeded.
    """

    # Arrange
    def failing_factory():
        raise ConnectionError("Cannot connect")

    # Act & Assert
    with pytest.raises(RuntimeError):
        with managed_db_connection(failing_factory, max_retries=2, retry_delay=0.01):
            pass


def test_managed_db_connection_health_check_passes() -> None:
    """
    Test case 4: Health check passes for valid connection.
    """

    # Arrange
    def create_conn():
        return sqlite3.connect(":memory:")

    # Act
    with managed_db_connection(create_conn, health_check_query="SELECT 1") as conn:
        result = conn.execute("SELECT 1").fetchone()

    # Assert
    assert result == (1,)


def test_managed_db_connection_no_health_check() -> None:
    """
    Test case 5: Works without health check.
    """

    # Arrange
    def create_conn():
        return sqlite3.connect(":memory:")

    # Act
    with managed_db_connection(create_conn, health_check_query=None) as conn:
        result = conn.execute("SELECT 1").fetchone()

    # Assert
    assert result == (1,)


def test_managed_db_connection_cleanup_on_exception() -> None:
    """
    Test case 6: Connection is closed even when exception occurs.
    """

    # Arrange
    def create_conn():
        conn = sqlite3.connect(":memory:")
        conn.execute("CREATE TABLE test (id INTEGER)")
        return conn

    # Act & Assert
    with pytest.raises(ValueError, match="Test error"):
        with managed_db_connection(create_conn) as conn:
            conn.execute("INSERT INTO test VALUES (1)")
            raise ValueError("Test error")

    # Connection should be closed (no way to verify directly in SQLite)


def test_managed_db_connection_invalid_factory() -> None:
    """
    Test case 7: Non-callable factory raises TypeError.
    """
    # Act & Assert
    with pytest.raises(TypeError):
        with managed_db_connection("not_callable"):
            pass


def test_managed_db_connection_invalid_max_retries() -> None:
    """
    Test case 8: Invalid max_retries raises ValueError.
    """

    # Arrange
    def create_conn():
        return sqlite3.connect(":memory:")

    # Act & Assert
    with pytest.raises(ValueError):
        with managed_db_connection(create_conn, max_retries=0):
            pass


def test_managed_db_connection_invalid_retry_delay() -> None:
    """
    Test case 9: Invalid retry_delay raises ValueError.
    """

    # Arrange
    def create_conn():
        return sqlite3.connect(":memory:")

    # Act & Assert
    with pytest.raises(ValueError):
        with managed_db_connection(create_conn, retry_delay=0):
            pass

    with pytest.raises(ValueError):
        with managed_db_connection(create_conn, retry_delay=-1):
            pass
