"""Periodic async task execution utilities."""

import asyncio
from collections.abc import Awaitable, Callable


# Define an asynchronous function to run another function periodically
async def async_periodic(
    func: Callable[[], Awaitable[None]],
    interval: float,
    stop_event: asyncio.Event | None = None,
    stop_after: float | None = None,
) -> None:
    """Run an asynchronous function periodically with a fixed time interval.

    Parameters
    ----------
    func : Callable[[], Awaitable[None]]
        The asynchronous function to run periodically.
    interval : float
        The time interval in seconds between executions.
    stop_event : asyncio.Event, optional
        Event used to signal that the periodic loop should stop.
    stop_after : float, optional
        Maximum time in seconds to run before stopping.

    Returns
    -------
    None

    Examples
    --------
    >>> async def say_hello() -> None:
    ...     print("Hello!")
    >>> asyncio.run(async_periodic(say_hello, interval=2, stop_after=5))
    (prints "Hello!" every 2 seconds for roughly 5 seconds)

    The periodic task can also be cancelled using an ``asyncio.Event``:

    >>> async def main() -> None:
    ...     stop = asyncio.Event()
    ...     async def tick() -> None:
    ...         print("tick")
    ...     task = asyncio.create_task(async_periodic(tick, 1, stop_event=stop))
    ...     await asyncio.sleep(3)
    ...     stop.set()  # cancel the periodic loop
    ...     await task
    >>> asyncio.run(main())
    tick
    tick
    tick
    """
    loop = asyncio.get_running_loop()
    end_time = loop.time() + stop_after if stop_after is not None else None

    while True:
        await func()

        if stop_event is not None and stop_event.is_set():
            break

        if end_time is not None and loop.time() >= end_time:
            break

        timeout = interval
        if end_time is not None:
            timeout = min(timeout, max(0, end_time - loop.time()))

        if stop_event is not None:
            try:
                await asyncio.wait_for(stop_event.wait(), timeout=timeout)
                break
            except TimeoutError:
                pass
        else:
            await asyncio.sleep(timeout)


__all__ = ["async_periodic"]
