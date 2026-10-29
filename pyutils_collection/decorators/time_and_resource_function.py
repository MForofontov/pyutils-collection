"""Function timing and resource measurement decorator."""

import gc
import logging
import math
import threading
import time
import warnings
from collections.abc import Callable
from functools import wraps
from types import SimpleNamespace
from typing import Any, ParamSpec, TypeVar

import psutil

from pyutils_collection.logger_functions.logger import validate_logger

P = ParamSpec("P")
R = TypeVar("R")


def time_and_resource_function(
    monitor_memory: bool = True,
    monitor_cpu: bool = True,
    monitor_io: bool = True,
    monitor_network: bool = True,
    monitor_disk: bool = True,
    monitor_threads: bool = True,
    monitor_gc: bool = True,
    monitor_context_switches: bool = True,
    monitor_open_files: bool = True,
    monitor_page_faults: bool = True,
    interval: float = 0.1,
    logger: logging.Logger | None = None,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Decorator to measure the execution time and optionally the maximum memory, CPU usage, I/O operations, network usage, disk usage, number of threads, GC statistics, context switches, open files, and page faults of a function.

    Parameters
    ----------
    monitor_memory : bool
        Whether to monitor memory usage. Default is True.
    monitor_cpu : bool
        Whether to monitor CPU usage. Default is True.
    monitor_io : bool
        Whether to monitor I/O operations. Default is True.
    monitor_network : bool
        Whether to monitor network usage. Default is True.
    monitor_disk : bool
        Whether to monitor disk usage. Default is True.
    monitor_threads : bool
        Whether to monitor the number of threads. Default is True.
    monitor_gc : bool
        Whether to monitor garbage collection statistics. Default is True.
    monitor_context_switches : bool
        Whether to monitor context switches. Default is True.
    monitor_open_files : bool
        Whether to monitor open file descriptors. Default is True.
    monitor_page_faults : bool
        Whether to monitor page faults. Default is True.
    interval : float
        The interval in seconds between each resource measurement. Default is 0.1.
        Must be finite and positive. Shutdown waits at most one second for a
        sample; a blocked OS query may finish later in the daemon thread.

    Returns
    -------
    function
        The wrapped function with added time and optional resource measurement.

    Raises
    ------
    TypeError
        If logger is not an instance of logging.Logger or None, or interval is
        not a number.
    ValueError
        If interval is not finite and positive.
    """
    validate_logger(logger)
    if not isinstance(interval, (int, float)) or isinstance(interval, bool):
        raise TypeError("interval must be a number")
    if not math.isfinite(interval) or interval <= 0:
        raise ValueError("interval must be finite and positive")

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            process = psutil.Process()

            # Initialize monitoring variables
            max_memory_usage = 0
            max_cpu_usage = 0.0
            max_cpu_cores = 0
            max_threads = 0
            max_open_files = 0
            max_page_faults = 0
            total_gc_collections = [
                0,
                0,
                0,
            ]  # [generation 0, generation 1, generation 2]
            initial_gc_collections = (
                [item["collections"] for item in gc.get_stats()] if monitor_gc else []
            )
            total_voluntary_context_switches = 0
            total_involuntary_context_switches = 0

            total_read_ops = 0
            total_write_ops = 0
            total_bytes_sent = 0
            total_bytes_recv = 0
            total_read_bytes = 0
            total_write_bytes = 0

            # Initial counters
            initial_io_counters = (
                process.io_counters()
                if monitor_io and hasattr(process, "io_counters")
                else None
            )
            initial_net_io_counters = (
                psutil.net_io_counters()
                if monitor_network and hasattr(psutil, "net_io_counters")
                else None
            )
            initial_disk_io_counters = (
                psutil.disk_io_counters()
                if monitor_disk and hasattr(psutil, "disk_io_counters")
                else None
            )

            stop_event = threading.Event()
            sample_finished = threading.Event()
            if monitor_cpu:
                process.cpu_percent(interval=None)

            def monitor_resources() -> None:
                nonlocal \
                    max_memory_usage, \
                    max_cpu_usage, \
                    max_cpu_cores, \
                    max_threads, \
                    max_open_files, \
                    max_page_faults
                nonlocal \
                    total_gc_collections, \
                    total_voluntary_context_switches, \
                    total_involuntary_context_switches
                nonlocal \
                    total_read_ops, \
                    total_write_ops, \
                    total_bytes_sent, \
                    total_bytes_recv
                nonlocal total_read_bytes, total_write_bytes

                while not stop_event.is_set():
                    try:
                        # Monitor main process
                        total_memory_usage = (
                            process.memory_info().rss if monitor_memory else 0
                        )
                        total_cpu_usage = (
                            process.cpu_percent(interval=None) if monitor_cpu else 0.0
                        )
                        total_threads = process.num_threads() if monitor_threads else 0
                        open_files = (
                            len(process.open_files())
                            if monitor_open_files and hasattr(process, "open_files")
                            else 0
                        )
                        if monitor_page_faults and hasattr(process, "memory_full_info"):
                            memory_info: Any = process.memory_full_info()
                        elif monitor_page_faults:
                            memory_info = process.memory_info()
                        else:
                            memory_info = SimpleNamespace(pfaults=0)
                        page_faults = getattr(memory_info, "pfaults", 0)
                        if monitor_context_switches and hasattr(
                            process, "num_ctx_switches"
                        ):
                            context_switches: Any = process.num_ctx_switches()
                        else:
                            context_switches = SimpleNamespace(
                                voluntary=0, involuntary=0
                            )

                        # Monitor GC statistics
                        if monitor_gc:
                            gc_stats = gc.get_stats()
                            for i in range(3):
                                total_gc_collections[i] = (
                                    gc_stats[i]["collections"]
                                    - initial_gc_collections[i]
                                )

                        # Monitor child processes
                        for child in process.children(recursive=True):
                            try:
                                if monitor_memory:
                                    total_memory_usage += child.memory_info().rss
                                if monitor_cpu:
                                    total_cpu_usage += child.cpu_percent(interval=None)
                                if monitor_threads:
                                    total_threads += child.num_threads()
                                if monitor_io and hasattr(child, "io_counters"):
                                    child_io_counters = child.io_counters()
                                    total_read_ops += child_io_counters.read_count
                                    total_write_ops += child_io_counters.write_count
                                    total_read_bytes += child_io_counters.read_bytes
                                    total_write_bytes += child_io_counters.write_bytes
                                if monitor_open_files and hasattr(child, "open_files"):
                                    open_files += len(child.open_files())
                                if monitor_page_faults and hasattr(
                                    child, "memory_full_info"
                                ):
                                    child_memory_info = child.memory_full_info()
                                    page_faults += getattr(
                                        child_memory_info, "pfaults", 0
                                    )
                                if monitor_context_switches and hasattr(
                                    child, "num_ctx_switches"
                                ):
                                    child_context_switches = child.num_ctx_switches()
                                    total_voluntary_context_switches += (
                                        child_context_switches.voluntary
                                    )
                                    total_involuntary_context_switches += (
                                        child_context_switches.involuntary
                                    )
                            except psutil.NoSuchProcess, psutil.AccessDenied:
                                continue

                        # Update maximums
                        if monitor_memory:
                            max_memory_usage = max(max_memory_usage, total_memory_usage)
                        if monitor_cpu:
                            max_cpu_usage = max(max_cpu_usage, total_cpu_usage)
                            max_cpu_cores = max(
                                max_cpu_cores, int(total_cpu_usage / 100)
                            )
                        if monitor_threads:
                            max_threads = max(max_threads, total_threads)
                        if monitor_open_files:
                            max_open_files = max(max_open_files, open_files)
                        if monitor_page_faults:
                            max_page_faults = max(max_page_faults, page_faults)
                        if monitor_context_switches:
                            total_voluntary_context_switches += (
                                context_switches.voluntary
                            )
                            total_involuntary_context_switches += (
                                context_switches.involuntary
                            )

                        stop_event.wait(interval)
                    except psutil.NoSuchProcess, psutil.AccessDenied:
                        stop_event.wait(interval)

            def sample_until_stopped() -> None:
                try:
                    monitor_resources()
                finally:
                    sample_finished.set()

            # Wait for Python sampling to finish rather than an OS thread join.
            # A timed native join can itself stall during Windows thread teardown.
            resource_thread = threading.Thread(
                target=sample_until_stopped,
                daemon=True,
                name="pyutils-resource-monitor",
            )
            resource_thread.start()

            start_time = time.perf_counter()
            try:
                result = func(*args, **kwargs)
            finally:
                end_time = time.perf_counter()
                stop_event.set()
                if not sample_finished.wait(timeout=1.0):
                    warnings.warn(
                        "Resource monitor is waiting on an OS query; measurements may be incomplete",
                        RuntimeWarning,
                        stacklevel=2,
                    )

            # End time
            execution_time = end_time - start_time

            # Final counters
            final_io_counters = (
                process.io_counters()
                if monitor_io and hasattr(process, "io_counters")
                else None
            )
            final_net_io_counters = (
                psutil.net_io_counters()
                if monitor_network and hasattr(psutil, "net_io_counters")
                else None
            )
            final_disk_io_counters = (
                psutil.disk_io_counters()
                if monitor_disk and hasattr(psutil, "disk_io_counters")
                else None
            )

            # Print or log results
            def log_or_print(message: str) -> None:
                if logger:
                    logger.debug(message)
                else:
                    print(message)

            # Print results
            log_or_print(f"Execution time: {execution_time:.2f} seconds")

            if monitor_memory:
                log_or_print(
                    f"Maximum memory usage: {max_memory_usage / (1024 * 1024):.2f} MB"
                )
            if monitor_cpu:
                log_or_print(f"Maximum CPU usage: {max_cpu_usage:.2f}%")
                log_or_print(f"Maximum CPU cores used: {max_cpu_cores:.2f}")
            if monitor_io:
                if initial_io_counters and final_io_counters:
                    read_ops = (
                        final_io_counters.read_count
                        - initial_io_counters.read_count
                        + total_read_ops
                    )
                    write_ops = (
                        final_io_counters.write_count
                        - initial_io_counters.write_count
                        + total_write_ops
                    )
                else:
                    read_ops = total_read_ops
                    write_ops = total_write_ops
                log_or_print(f"Read operations: {read_ops}")
                log_or_print(f"Write operations: {write_ops}")
            if monitor_network:
                if initial_net_io_counters and final_net_io_counters:
                    bytes_sent = (
                        final_net_io_counters.bytes_sent
                        - initial_net_io_counters.bytes_sent
                    )
                    bytes_recv = (
                        final_net_io_counters.bytes_recv
                        - initial_net_io_counters.bytes_recv
                    )
                else:
                    bytes_sent = total_bytes_sent
                    bytes_recv = total_bytes_recv
                log_or_print(f"Bytes sent: {bytes_sent}")
                log_or_print(f"Bytes received: {bytes_recv}")
            if monitor_disk:
                if initial_disk_io_counters and final_disk_io_counters:
                    read_bytes = (
                        final_disk_io_counters.read_bytes
                        - initial_disk_io_counters.read_bytes
                        + total_read_bytes
                    )
                    write_bytes = (
                        final_disk_io_counters.write_bytes
                        - initial_disk_io_counters.write_bytes
                        + total_write_bytes
                    )
                else:
                    read_bytes = total_read_bytes
                    write_bytes = total_write_bytes
                log_or_print(f"Disk read bytes: {read_bytes}")
                log_or_print(f"Disk write bytes: {write_bytes}")
            if monitor_threads:
                log_or_print(f"Number of threads: {max_threads}")
            if monitor_gc:
                log_or_print(f"GC collections: {total_gc_collections}")
            if monitor_context_switches:
                log_or_print(
                    f"Voluntary context switches: {total_voluntary_context_switches}"
                )
                log_or_print(
                    f"Involuntary context switches: {total_involuntary_context_switches}"
                )
            if monitor_open_files:
                log_or_print(f"Maximum open files: {max_open_files}")
            if monitor_page_faults:
                log_or_print(f"Maximum page faults: {max_page_faults}")

            return result

        return wrapper

    return decorator


__all__ = ["time_and_resource_function"]
