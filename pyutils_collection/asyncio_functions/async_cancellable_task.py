"""Cancellable async task utilities."""

import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar

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
        If the caller is cancelled or the cancellation event is set before the
        task completes. Both owned tasks are cancelled and awaited before exit.
    asyncio.TimeoutError
        If ``timeout`` is provided and the operation takes longer than the
        specified number of seconds.

    Notes
    -----
    Exceptions raised by worker cleanup after cancellation are retrieved without
    replacing the caller's cancellation or timeout. Normal worker failures propagate.

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
    cancel_future = asyncio.create_task(cancel_event.wait())

    try:
        done, _ = await asyncio.wait(
            {task_future, cancel_future},
            return_when=asyncio.FIRST_COMPLETED,
            timeout=timeout,
        )

        if not done:
            raise TimeoutError("async_cancellable_task timed out.")

        if cancel_future in done:
            raise asyncio.CancelledError("Task was cancelled.")

        return task_future.result()
    finally:
        for owned_task in (task_future, cancel_future):
            if not owned_task.done():
                owned_task.cancel()
        await asyncio.gather(task_future, cancel_future, return_exceptions=True)


__all__ = ["async_cancellable_task"]
