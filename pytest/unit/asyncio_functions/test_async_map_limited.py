"""Tests for bounded async mapping and worker cleanup."""

import asyncio

import pytest
from pyutils_collection.asyncio_functions import async_map_limited

pytestmark = [pytest.mark.unit, pytest.mark.asyncio_functions, pytest.mark.asyncio]


async def test_order_and_concurrency() -> None:
    gate = asyncio.Event()
    saturated = asyncio.Event()
    active = 0
    maximum = 0

    async def process(value):
        nonlocal active, maximum
        active += 1
        maximum = max(maximum, active)
        if active == 3:
            saturated.set()
        await gate.wait()
        # Force differing completion order without relying on wall-clock timing.
        for _ in range(5 - value % 5):
            await asyncio.sleep(0)
        active -= 1
        return value * 2

    task = asyncio.create_task(async_map_limited(process, iter(range(20)), limit=3))
    await asyncio.wait_for(saturated.wait(), 2)
    assert maximum == 3
    gate.set()
    assert await asyncio.wait_for(task, 2) == list(range(0, 40, 2))
    assert maximum == 3


async def test_empty_and_large_limit() -> None:
    async def process(value):
        return value

    assert await async_map_limited(process, [], 1000) == []
    assert await async_map_limited(process, [None, 1], 1000) == [None, 1]


async def test_input_is_consumed_incrementally() -> None:
    gate = asyncio.Event()
    saturated = asyncio.Event()
    consumed = []
    started = []

    def items():
        for value in range(20):
            consumed.append(value)
            yield value

    async def process(value):
        started.append(value)
        if len(started) == 2:
            saturated.set()
        await gate.wait()
        return value

    task = asyncio.create_task(async_map_limited(process, items(), 2))
    await asyncio.wait_for(saturated.wait(), 2)
    assert consumed == [0, 1]
    gate.set()
    assert await asyncio.wait_for(task, 2) == list(range(20))


async def test_failure_cancels_and_awaits_other_workers() -> None:
    started = asyncio.Event()
    cleaned = []
    error = RuntimeError("operation failed")

    async def process(value):
        if value == 0:
            await started.wait()
            raise error
        try:
            started.set()
            await asyncio.Event().wait()
        finally:
            cleaned.append(value)

    with pytest.raises(RuntimeError) as caught:
        await asyncio.wait_for(async_map_limited(process, [0, 1], 2), 2)
    assert caught.value is error
    assert cleaned == [1]


async def test_caller_cancellation_cleans_up_workers() -> None:
    started = asyncio.Event()
    cleaned = []

    async def process(value):
        try:
            started.set()
            await asyncio.Event().wait()
        finally:
            cleaned.append(value)

    task = asyncio.create_task(async_map_limited(process, [1], 1))
    await asyncio.wait_for(started.wait(), 2)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert cleaned == [1]


async def test_iterator_failure_propagates() -> None:
    async def process(value):
        await asyncio.sleep(0)
        return value

    def items():
        yield 1
        yield 2
        raise RuntimeError("iterator failed")

    with pytest.raises(RuntimeError, match="iterator failed"):
        await async_map_limited(process, items(), 1)


@pytest.mark.parametrize(
    "limit,error",
    [(0, ValueError), (-1, ValueError), (True, TypeError), (1.5, TypeError)],
)
async def test_invalid_limit(limit, error) -> None:
    async def process(value):
        pytest.fail("must not be called")

    with pytest.raises(error):
        await async_map_limited(process, [], limit)


async def test_invalid_callable_and_iterable() -> None:
    with pytest.raises(TypeError):
        await async_map_limited(None, [])

    async def process(value):
        return value

    with pytest.raises(TypeError):
        await async_map_limited(process, None)
