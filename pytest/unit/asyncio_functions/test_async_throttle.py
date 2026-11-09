import asyncio
from collections.abc import AsyncGenerator

import pytest

try:
    import aiohttp
    from pyutils_collection.asyncio_functions.async_throttle import async_throttle

    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    aiohttp = None  # type: ignore
    async_throttle = None  # type: ignore

pytestmark = [
    pytest.mark.unit,
    pytest.mark.asyncio_functions,
    pytest.mark.skipif(not AIOHTTP_AVAILABLE, reason="aiohttp not installed"),
]


@pytest.mark.asyncio
async def test_async_throttle_normal_throttling() -> None:
    """
    Test case 1: Normal throttling with delay between items.
    """

    # Arrange
    async def generate_items() -> AsyncGenerator[int, None]:
        for i in range(3):
            yield i

    results = []
    start_time = asyncio.get_event_loop().time()

    # Act
    async for item in async_throttle(generate_items(), delay=0.05):
        results.append((item, asyncio.get_event_loop().time() - start_time))

    # Assert
    assert [r[0] for r in results] == [0, 1, 2]
    # Verify delays exist between items
    if len(results) >= 2:
        assert results[1][1] - results[0][1] >= 0.04


@pytest.mark.asyncio
async def test_async_throttle_empty_generator() -> None:
    """
    Test case 2: Empty generator yields nothing.
    """

    # Arrange
    async def empty_generator() -> AsyncGenerator[int, None]:
        return
        yield  # Make it a generator

    results = []

    # Act
    async for item in async_throttle(empty_generator(), delay=0.1):
        results.append(item)

    # Assert
    assert results == []


@pytest.mark.asyncio
async def test_async_throttle_single_item() -> None:
    """
    Test case 3: Single item generator.
    """

    # Arrange
    async def single_item_generator() -> AsyncGenerator[str, None]:
        yield "only_one"

    results = []

    # Act
    async for item in async_throttle(single_item_generator(), delay=0.01):
        results.append(item)

    # Assert
    assert results == ["only_one"]


@pytest.mark.asyncio
async def test_async_throttle_different_data_types() -> None:
    """
    Test case 4: Throttle generators with different data types.
    """

    # Arrange
    async def string_generator() -> AsyncGenerator[str, None]:
        for s in ["a", "b", "c"]:
            yield s

    results = []

    # Act
    async for item in async_throttle(string_generator(), delay=0.01):
        results.append(item)

    # Assert
    assert results == ["a", "b", "c"]


@pytest.mark.asyncio
async def test_async_throttle_verify_timing(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Test case 5: Delay only between items, without relying on OS scheduling.
    """

    # Arrange
    async def generate_items() -> AsyncGenerator[int, None]:
        for i in range(4):
            yield i

    from unittest.mock import AsyncMock, call

    sleep = AsyncMock()
    monkeypatch.setattr(asyncio, "sleep", sleep)
    results = []

    # Act
    async for item in async_throttle(generate_items(), delay=0.02):
        results.append(item)
        assert sleep.await_count == item

    # Assert
    assert results == [0, 1, 2, 3]
    assert sleep.await_args_list == [call(0.02)] * 3


@pytest.mark.asyncio
async def test_async_throttle_type_error_invalid_delay() -> None:
    """
    Test case 6: TypeError for non-numeric delay.
    """

    # Arrange
    async def generate_items() -> AsyncGenerator[int, None]:
        yield 1

    # Act & Assert
    with pytest.raises(TypeError, match="delay must be a float"):
        async for _ in async_throttle(generate_items(), delay="invalid"):  # type: ignore
            pass
