import asyncio

import pytest


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("retries", "delay", "error"),
    [
        (0, 0, ValueError),
        (-1, 0, ValueError),
        (True, 0, TypeError),
        (1.5, 0, TypeError),
        (1, -1, ValueError),
        (1, float("nan"), ValueError),
        (1, float("inf"), ValueError),
        (1, "1", TypeError),
        (1, True, TypeError),
    ],
)
async def test_retry_async_rejects_invalid_configuration(retries, delay, error) -> None:
    async def task():
        pytest.fail("task must not run for invalid retry settings")

    with pytest.raises(error):
        await retry_async(task, retries, delay)


@pytest.mark.asyncio
async def test_retry_async_single_attempt_does_not_sleep(monkeypatch) -> None:
    from unittest.mock import AsyncMock

    sleep = AsyncMock()
    monkeypatch.setattr(asyncio, "sleep", sleep)
    error = ValueError("failure")
    task = AsyncMock(side_effect=error)
    with pytest.raises(ValueError) as caught:
        await retry_async(task, 1, 0)
    assert caught.value is error
    task.assert_awaited_once()
    sleep.assert_not_awaited()


try:
    import aiohttp
    from pyutils_collection.asyncio_functions.retry_async import retry_async

    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    aiohttp = None  # type: ignore
    retry_async = None  # type: ignore

pytestmark = [
    pytest.mark.unit,
    pytest.mark.asyncio_functions,
    pytest.mark.skipif(not AIOHTTP_AVAILABLE, reason="aiohttp not installed"),
]


@pytest.mark.asyncio
async def test_retry_async_succeeds_first_try() -> None:
    """
    Test case 1: Function succeeds on first attempt.
    """
    # Arrange
    call_count = []

    async def successful_task() -> int:
        call_count.append(1)
        return 42

    # Act
    result = await retry_async(successful_task, retries=3, delay=0.01)

    # Assert
    assert result == 42
    assert len(call_count) == 1


@pytest.mark.asyncio
async def test_retry_async_succeeds_after_failures() -> None:
    """
    Test case 2: Function fails initially but succeeds on retry.
    """
    # Arrange
    call_count = []

    async def flaky_task() -> str:
        call_count.append(1)
        if len(call_count) < 3:
            raise ValueError("Temporary failure")
        return "success"

    # Act
    result = await retry_async(flaky_task, retries=5, delay=0.01)

    # Assert
    assert result == "success"
    assert len(call_count) == 3


@pytest.mark.asyncio
async def test_retry_async_single_retry() -> None:
    """
    Test case 3: Single retry attempt.
    """
    # Arrange
    call_count = []

    async def task() -> int:
        call_count.append(1)
        if len(call_count) == 1:
            raise ValueError("First attempt fails")
        return 100

    # Act
    result = await retry_async(task, retries=2, delay=0.01)

    # Assert
    assert result == 100
    assert len(call_count) == 2


@pytest.mark.asyncio
async def test_retry_async_different_exception_types() -> None:
    """
    Test case 4: Different exception types are handled.
    """
    # Arrange
    call_count = []

    async def task_with_different_errors() -> str:
        call_count.append(1)
        if len(call_count) == 1:
            raise ValueError("First error")
        elif len(call_count) == 2:
            raise RuntimeError("Second error")
        return "recovered"

    # Act
    result = await retry_async(task_with_different_errors, retries=5, delay=0.01)

    # Assert
    assert result == "recovered"
    assert len(call_count) == 3


@pytest.mark.asyncio
async def test_retry_async_fails_all_retries() -> None:
    """
    Test case 5: Function fails on all retry attempts.
    """
    # Arrange
    call_count = []

    async def always_failing_task() -> int:
        call_count.append(1)
        raise ValueError("Permanent failure")

    # Act & Assert
    with pytest.raises(ValueError, match="Permanent failure"):
        await retry_async(always_failing_task, retries=3, delay=0.01)

    assert len(call_count) == 3


@pytest.mark.asyncio
async def test_retry_async_delay_between_retries(monkeypatch) -> None:
    """
    Test case 6: Verify delay is applied between retries.
    """
    from unittest.mock import AsyncMock, call

    requested_sleep = AsyncMock()
    monkeypatch.setattr(asyncio, "sleep", requested_sleep)
    attempts = []

    async def failing_task() -> None:
        attempts.append(len(attempts))
        raise ValueError("Fail")

    # Act & Assert
    with pytest.raises(ValueError):
        await retry_async(failing_task, retries=3, delay=0.05)

    assert len(attempts) == 3
    assert requested_sleep.await_args_list == [call(0.05), call(0.05)]
