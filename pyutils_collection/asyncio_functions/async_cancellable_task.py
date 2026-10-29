"""Cancellable async task utilities."""

import asyncio
import contextlib
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar

# Define a type variable T to represent the return type of the task
T = TypeVar("T")


async def async_cancellable_task(
    task: Callable[[], Awaitable[T]],
    cancel_event: asyncio.Event,
    timeout: float | None = None,
) -> T:
    """
    Run an asynchronous task that can be cancelled.

    Parameters
    ----------
    task : Callable[[], Awaitable[T]]
        The asynchronous function to run.
    cancel_event : asyncio.Event
        The event used to signal cancellation.
    timeout : float | None, optional
        Maximum number of seconds to wait for the task to finish or for the
        cancellation event to be set. If ``None`` (the default), wait
        indefinitely.

    Returns
    -------
    T
        The result of the task if it completes before cancellation or timeout.

    Raises
    ------
    asyncio.CancelledError
        If the cancellation event is set before the task completes.
    asyncio.TimeoutError
        If ``timeout`` is provided and the operation takes longer than the
        specified number of seconds.

    Examples
    --------
    >>> async def long_running_task() -> str:
    >>>     await asyncio.sleep(10)
    >>>     return "Completed"
    >>>
    >>> cancel_event = asyncio.Event()
    >>> result = asyncio.run(
    ...     async_cancellable_task(long_running_task, cancel_event, timeout=10)
    ... )
    """
    if cancel_event.is_set():
        raise asyncio.CancelledError("Task was cancelled.")

    task_future: asyncio.Task[T] = asyncio.create_task(task())  # type: ignore[arg-type]
    cancel_future: asyncio.Task[Any] = asyncio.create_task(cancel_event.wait())
    pending: set[asyncio.Task[Any]] = set()

    try:
        done, pending = await asyncio.wait(
            {task_future, cancel_future},
            return_when=asyncio.FIRST_COMPLETED,
            timeout=timeout,
        )

        if not done:
            task_future.cancel()
            cancel_future.cancel()
            raise TimeoutError("async_cancellable_task timed out.")

        if cancel_future in done:
            task_future.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await task_future
            raise asyncio.CancelledError("Task was cancelled.")

        cancel_future.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await cancel_future
        return task_future.result()
    finally:
        for pending_future in pending:
            pending_future.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await pending_future


__all__ = ["async_cancellable_task"]
