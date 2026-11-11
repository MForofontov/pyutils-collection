import asyncio
import importlib
from types import SimpleNamespace

import pytest

try:
    import aiohttp
    from pyutils_collection.asyncio_functions.async_periodic import async_periodic
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    aiohttp = None  # type: ignore
    async_periodic = None  # type: ignore

pytestmark = [
    pytest.mark.unit,
    pytest.mark.asyncio_functions,
    pytest.mark.skipif(not AIOHTTP_AVAILABLE, reason="aiohttp not installed"),
]


@pytest.fixture
def periodic_clock(monkeypatch: pytest.MonkeyPatch):
    clock = SimpleNamespace(now=0.0, sleeps=[])

    async def sleep(delay: float) -> None:
        clock.sleeps.append(delay)
        clock.now += delay

    module = importlib.import_module("pyutils_collection.asyncio_functions.async_periodic")
    monkeypatch.setattr(
        module,
        "asyncio",
        SimpleNamespace(
            get_running_loop=lambda: SimpleNamespace(time=lambda: clock.now),
            sleep=sleep,
        ),
    )
    return clock


@pytest.mark.asyncio
async def test_async_periodic_stops_after_timeout(periodic_clock) -> None:
    """
    Test case 1: Function runs periodically and stops after timeout.
    """
    # Arrange
    call_count = []

    async def periodic_task() -> None:
        call_count.append(1)

    # Act
    await async_periodic(periodic_task, interval=0.05, stop_after=0.15)

    # Assert
    assert len(call_count) == 4
    assert periodic_clock.now == pytest.approx(0.15)


@pytest.mark.asyncio
async def test_async_periodic_stops_on_event() -> None:
    """
    Test case 2: Function stops when event is set.
    """
    # Arrange
    call_count = []
    stop_event = asyncio.Event()

    async def periodic_task() -> None:
        call_count.append(1)
        if len(call_count) >= 3:
            stop_event.set()

    # Act
    await async_periodic(periodic_task, interval=0.01, stop_event=stop_event)

    # Assert
    assert len(call_count) == 3


@pytest.mark.asyncio
async def test_async_periodic_continuous_until_cancelled() -> None:
    """
    Test case 3: Function runs continuously until cancelled.
    """
    # Arrange
    call_count = []

    async def periodic_task() -> None:
        call_count.append(1)

    # Act
    task = asyncio.create_task(async_periodic(periodic_task, interval=0.02))
    await asyncio.sleep(0.08)
    task.cancel()

    try:
        await task
    except asyncio.CancelledError:
        pass

    # Assert
    # Should execute multiple times
    assert len(call_count) >= 2


@pytest.mark.asyncio
async def test_async_periodic_immediate_stop() -> None:
    """
    Test case 4: Stop event is already set before starting.
    """
    # Arrange
    call_count = []
    stop_event = asyncio.Event()
    stop_event.set()

    async def periodic_task() -> None:
        call_count.append(1)

    # Act
    await async_periodic(periodic_task, interval=0.1, stop_event=stop_event)

    # Assert
    # Should execute once before checking stop event
    assert len(call_count) == 1


@pytest.mark.asyncio
async def test_async_periodic_custom_interval(periodic_clock) -> None:
    """
    Test case 5: Custom interval controls execution frequency.
    """
    # Arrange
    call_times = []

    async def periodic_task() -> None:
        call_times.append(periodic_clock.now)

    # Act
    await async_periodic(periodic_task, interval=0.05, stop_after=0.12)

    # Assert
    assert call_times == pytest.approx([0.0, 0.05, 0.10, 0.12])
    assert periodic_clock.sleeps == pytest.approx([0.05, 0.05, 0.02])


@pytest.mark.asyncio
async def test_async_periodic_exception_stops_execution() -> None:
    """
    Test case 6: Exception in periodic task stops execution.
    """
    # Arrange
    call_count = []

    async def failing_task() -> None:
        call_count.append(1)
        if len(call_count) >= 2:
            raise ValueError("Task failed")

    # Act & Assert
    with pytest.raises(ValueError, match="Task failed"):
        await async_periodic(failing_task, interval=0.01, stop_after=0.1)

    assert len(call_count) == 2


@pytest.mark.asyncio
async def test_async_periodic_stop_event_during_wait() -> None:
    """
    Test case 7: Stop event is set during the interval wait period.
    """
    # Arrange
    call_count = []
    stop_event = asyncio.Event()

    async def periodic_task() -> None:
        call_count.append(1)

    async def set_event_later() -> None:
        await asyncio.sleep(0.05)  # Set event during the wait
        stop_event.set()

    # Act
    setter = asyncio.create_task(set_event_later())
    await async_periodic(periodic_task, interval=0.1, stop_event=stop_event)
    await setter

    # Assert
    # Should execute once, then stop during the wait for next interval
    assert len(call_count) >= 1
