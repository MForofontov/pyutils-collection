"""Worker lifetime when the caller cancels the wrapper."""

import asyncio

import pytest

from pyutils_collection.asyncio_functions import async_cancellable_task

pytestmark = [pytest.mark.unit, pytest.mark.asyncio_functions]


@pytest.mark.asyncio
async def test_caller_cancellation_awaits_both_owned_tasks() -> None:
    existing = asyncio.all_tasks()
    started, closed = asyncio.Event(), asyncio.Event()

    async def worker() -> None:
        started.set()
        try:
            await asyncio.Event().wait()
        finally:
            closed.set()

    wrapper = asyncio.create_task(async_cancellable_task(worker, asyncio.Event()))
    await started.wait()
    wrapper.cancel()
    try:
        with pytest.raises(asyncio.CancelledError):
            await wrapper
        assert closed.is_set()
        assert not (asyncio.all_tasks() - existing)
    finally:
        remaining = asyncio.all_tasks() - existing
        for task in remaining:
            task.cancel()
        await asyncio.gather(*remaining, return_exceptions=True)


@pytest.mark.asyncio
@pytest.mark.parametrize("mode", ["event", "timeout"])
async def test_worker_cleanup_error_preserves_cancellation(mode: str) -> None:
    event, started = asyncio.Event(), asyncio.Event()

    async def worker() -> None:
        started.set()
        try:
            await asyncio.Event().wait()
        finally:
            raise RuntimeError("cleanup failed")

    wrapper = asyncio.create_task(
        async_cancellable_task(worker, event, timeout=0 if mode == "timeout" else None)
    )
    if mode == "event":
        await started.wait()
        event.set()
    with pytest.raises(asyncio.CancelledError if mode == "event" else TimeoutError):
        await wrapper
