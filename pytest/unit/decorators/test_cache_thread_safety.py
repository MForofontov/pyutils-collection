import threading
import time

import pytest

from pyutils_collection.decorators.cache import cache

pytestmark = [pytest.mark.unit, pytest.mark.decorators]


def test_cache_thread_safety() -> None:
    call_count = 0
    lock = threading.Lock()

    @cache
    def expensive(x: int) -> int:
        nonlocal call_count
        with lock:
            call_count += 1
        time.sleep(0.01)
        return x * 2

    results: list[int] = []
    errors: list[Exception] = []

    def worker() -> None:
        try:
            results.append(expensive(1))
        except Exception as exc:
            errors.append(exc)

    threads = [threading.Thread(target=worker) for _ in range(10)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert not errors
    assert results == [2] * 10
    assert call_count == 1


def test_cache_allows_recursive_calls() -> None:
    @cache
    def factorial(n: int) -> int:
        if n <= 1:
            return 1
        return n * factorial(n - 1)

    assert factorial(5) == 120
