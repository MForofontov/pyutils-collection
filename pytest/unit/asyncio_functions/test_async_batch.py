import asyncio

import pytest


@pytest.mark.asyncio
@pytest.mark.parametrize("batch_size", [0, -1, -100])
@pytest.mark.parametrize("items", [[], [1, 2]])
async def test_async_batch_rejects_nonpositive_sizes(batch_size, items) -> None:
    async def process_batch(batch):
        pytest.fail("processor must not run for an invalid batch size")

    with pytest.raises(ValueError, match="batch_size must be positive"):
        await async_batch(process_batch, items, batch_size)


@pytest.mark.asyncio
@pytest.mark.parametrize("batch_size", [True, False, 1.5, "2", None])
async def test_async_batch_rejects_invalid_size_types(batch_size) -> None:
    async def process_batch(batch):
        pytest.fail("processor must not run for an invalid batch size")

    with pytest.raises(TypeError, match="batch_size must be an integer"):
        await async_batch(process_batch, [1], batch_size)


try:
    import aiohttp
    from pyutils_collection.asyncio_functions.async_batch import async_batch

    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    aiohttp = None  # type: ignore
    async_batch = None  # type: ignore

pytestmark = [
    pytest.mark.unit,
    pytest.mark.asyncio_functions,
    pytest.mark.skipif(not AIOHTTP_AVAILABLE, reason="aiohttp not installed"),
]


@pytest.mark.asyncio
async def test_async_batch_normal_operation() -> None:
    """
    Test case 1: Normal operation with valid batch processing.
    """

    # Arrange
    async def process_batch(batch: list[int]) -> list[int]:
        await asyncio.sleep(0.001)
        return [x * 2 for x in batch]

    items = [1, 2, 3, 4, 5]
    batch_size = 2

    # Act
    results = await async_batch(process_batch, items, batch_size)

    # Assert
    assert results == [2, 4, 6, 8, 10]


@pytest.mark.asyncio
async def test_async_batch_single_batch() -> None:
    """
    Test case 2: All items fit in a single batch.
    """

    # Arrange
    async def process_batch(batch: list[int]) -> list[int]:
        return [x + 1 for x in batch]

    items = [1, 2, 3]
    batch_size = 5

    # Act
    results = await async_batch(process_batch, items, batch_size)

    # Assert
    assert results == [2, 3, 4]


@pytest.mark.asyncio
async def test_async_batch_exact_batches() -> None:
    """
    Test case 3: Items divide evenly into batches.
    """

    # Arrange
    async def process_batch(batch: list[int]) -> list[int]:
        return [x * 3 for x in batch]

    items = [1, 2, 3, 4, 5, 6]
    batch_size = 2

    # Act
    results = await async_batch(process_batch, items, batch_size)

    # Assert
    assert results == [3, 6, 9, 12, 15, 18]


@pytest.mark.asyncio
async def test_async_batch_empty_list() -> None:
    """
    Test case 4: Empty input list returns empty results.
    """

    # Arrange
    async def process_batch(batch: list[int]) -> list[int]:
        return [x * 2 for x in batch]

    items: list[int] = []
    batch_size = 2

    # Act
    results = await async_batch(process_batch, items, batch_size)

    # Assert
    assert results == []


@pytest.mark.asyncio
async def test_async_batch_batch_size_one() -> None:
    """
    Test case 5: Batch size of 1 processes each item individually.
    """

    # Arrange
    async def process_batch(batch: list[str]) -> list[str]:
        return [s.upper() for s in batch]

    items = ["a", "b", "c"]
    batch_size = 1

    # Act
    results = await async_batch(process_batch, items, batch_size)

    # Assert
    assert results == ["A", "B", "C"]


@pytest.mark.asyncio
async def test_async_batch_string_processing() -> None:
    """
    Test case 6: Process batches of strings.
    """

    # Arrange
    async def process_batch(batch: list[str]) -> list[str]:
        await asyncio.sleep(0.001)
        return [s + "_processed" for s in batch]

    items = ["item1", "item2", "item3", "item4", "item5"]
    batch_size = 2

    # Act
    results = await async_batch(process_batch, items, batch_size)

    # Assert
    assert results == [
        "item1_processed",
        "item2_processed",
        "item3_processed",
        "item4_processed",
        "item5_processed",
    ]
