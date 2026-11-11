import asyncio

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.asyncio_functions]
from pyutils_collection.asyncio_functions.async_connection_pool import (
    AsyncConnectionPool,
    use_connection,
)


@pytest.mark.parametrize("capacity", [0, -1])
def test_capacity_must_be_positive(capacity):
    with pytest.raises(ValueError):
        AsyncConnectionPool(capacity)


@pytest.mark.asyncio
async def test_checked_out_connections_count_toward_capacity():
    pool = AsyncConnectionPool(1)
    connection = object()
    await pool.add_connection(connection)
    assert await pool.acquire() is connection
    with pytest.raises(RuntimeError, match="full"):
        await pool.add_connection(object())
    await asyncio.wait_for(pool.release(connection), 1)
    assert await pool.acquire() is connection


@pytest.mark.asyncio
async def test_duplicate_or_foreign_release_is_rejected_without_blocking():
    pool = AsyncConnectionPool(1)
    connection = object()
    await pool.add_connection(connection)
    with pytest.raises(ValueError, match="already released"):
        await asyncio.wait_for(pool.release(connection), 1)
    with pytest.raises(ValueError, match="does not belong"):
        await asyncio.wait_for(pool.release(object()), 1)


@pytest.mark.asyncio
async def test_cancelled_use_returns_connection():
    pool = AsyncConnectionPool(1)
    connection = object()
    await pool.add_connection(connection)
    started = asyncio.Event()

    async def work(_connection):
        started.set()
        await asyncio.Event().wait()

    task = asyncio.create_task(use_connection(pool, work))
    await started.wait()
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert await asyncio.wait_for(pool.acquire(), 1) is connection


@pytest.mark.asyncio
async def test_async_connection_pool_add_and_acquire() -> None:
    """
    Test case 1: Add connection to pool and acquire it.
    """
    # Arrange
    pool: AsyncConnectionPool[str] = AsyncConnectionPool(max_connections=2)
    await pool.add_connection("conn1")

    # Act
    conn = await pool.acquire()

    # Assert
    assert conn == "conn1"


@pytest.mark.asyncio
async def test_async_connection_pool_release_connection() -> None:
    """
    Test case 2: Acquire and release a connection.
    """
    # Arrange
    pool: AsyncConnectionPool[str] = AsyncConnectionPool(max_connections=2)
    await pool.add_connection("conn1")
    conn = await pool.acquire()

    # Act
    await pool.release(conn)
    conn2 = await pool.acquire()

    # Assert
    assert conn2 == "conn1"


@pytest.mark.asyncio
async def test_async_connection_pool_multiple_connections() -> None:
    """
    Test case 3: Manage multiple connections in the pool.
    """
    # Arrange
    pool: AsyncConnectionPool[int] = AsyncConnectionPool(max_connections=3)
    await pool.add_connection(1)
    await pool.add_connection(2)
    await pool.add_connection(3)

    # Act
    conn1 = await pool.acquire()
    conn2 = await pool.acquire()
    conn3 = await pool.acquire()

    # Assert
    assert {conn1, conn2, conn3} == {1, 2, 3}


@pytest.mark.asyncio
async def test_use_connection_function() -> None:
    """
    Test case 4: Use use_connection helper function.
    """
    # Arrange
    pool: AsyncConnectionPool[str] = AsyncConnectionPool(max_connections=1)
    await pool.add_connection("database")

    async def task(conn: str) -> str:
        return conn.upper()

    # Act
    result = await use_connection(pool, task)

    # Assert
    assert result == "DATABASE"


@pytest.mark.asyncio
async def test_use_connection_reuse() -> None:
    """
    Test case 5: Connection is properly reused after release.
    """
    # Arrange
    pool: AsyncConnectionPool[str] = AsyncConnectionPool(max_connections=1)
    await pool.add_connection("conn")

    async def task1(conn: str) -> str:
        return f"{conn}_1"

    async def task2(conn: str) -> str:
        return f"{conn}_2"

    # Act
    result1 = await use_connection(pool, task1)
    result2 = await use_connection(pool, task2)

    # Assert
    assert result1 == "conn_1"
    assert result2 == "conn_2"


@pytest.mark.asyncio
async def test_use_connection_concurrent_access() -> None:
    """
    Test case 6: Concurrent tasks use different connections.
    """
    # Arrange
    pool: AsyncConnectionPool[int] = AsyncConnectionPool(max_connections=2)
    await pool.add_connection(1)
    await pool.add_connection(2)

    results = []

    async def task(conn: int) -> int:
        await asyncio.sleep(0.01)
        return conn * 10

    # Act
    tasks = [use_connection(pool, task) for _ in range(2)]
    results = await asyncio.gather(*tasks)

    # Assert
    assert set(results) == {10, 20}


@pytest.mark.asyncio
async def test_async_connection_pool_full_error() -> None:
    """
    Test case 7: RuntimeError when adding to a full pool.
    """
    # Arrange
    pool: AsyncConnectionPool[str] = AsyncConnectionPool(max_connections=1)
    await pool.add_connection("conn1")

    # Act & Assert
    with pytest.raises(RuntimeError, match="Connection pool is full"):
        await pool.add_connection("conn2")


@pytest.mark.asyncio
async def test_use_connection_exception_handling() -> None:
    """
    Test case 8: Connection is released even when task raises exception.
    """
    # Arrange
    pool: AsyncConnectionPool[str] = AsyncConnectionPool(max_connections=1)
    await pool.add_connection("conn")

    async def failing_task(conn: str) -> str:
        raise ValueError("Task failed")

    # Act & Assert
    with pytest.raises(ValueError, match="Task failed"):
        await use_connection(pool, failing_task)

    # Verify connection is still available
    conn = await pool.acquire()
    assert conn == "conn"
