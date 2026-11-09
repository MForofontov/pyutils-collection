"""Failure paths must finish cleaning up scheduled work."""

import asyncio

import pytest

from pyutils_collection.asyncio_functions.gather_with_timeout import gather_with_timeout

pytestmark = [pytest.mark.unit, pytest.mark.asyncio_functions, pytest.mark.asyncio]


async def test_accepts_existing_tasks_and_futures():
    future = asyncio.get_running_loop().create_future()
    future.set_result(2)
    task = asyncio.create_task(asyncio.sleep(0, result=1))
    assert await gather_with_timeout([task, future], 1) == [1, 2]


async def test_failure_waits_for_sibling_cleanup():
    started = asyncio.Event()
    cleaned = asyncio.Event()

    async def sibling():
        try:
            started.set()
            await asyncio.Event().wait()
        finally:
            await asyncio.sleep(0)
            cleaned.set()

    async def fail():
        await started.wait()
        raise ValueError("operation failed")

    with pytest.raises(ValueError, match="operation failed"):
        await gather_with_timeout([sibling(), fail()], 1)
    assert cleaned.is_set()


async def test_iterator_error_cancels_already_scheduled_future():
    future = asyncio.get_running_loop().create_future()

    def broken_input():
        yield future
        raise ValueError("iterator failed")

    with pytest.raises(ValueError, match="iterator failed"):
        await gather_with_timeout(broken_input(), 1)
    assert future.cancelled()


async def test_caller_cancellation_waits_for_cleanup():
    started = asyncio.Event()
    cleaned = asyncio.Event()

    async def work():
        try:
            started.set()
            await asyncio.Event().wait()
        finally:
            await asyncio.sleep(0)
            cleaned.set()

    caller = asyncio.create_task(gather_with_timeout([work()], 5))
    await started.wait()
    caller.cancel()
    with pytest.raises(asyncio.CancelledError):
        await caller
    assert cleaned.is_set()
