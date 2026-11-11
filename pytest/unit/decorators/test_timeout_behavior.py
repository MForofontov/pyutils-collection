import time

import pytest

from pyutils_collection.decorators.timeout import TimeoutException, timeout

pytestmark = [pytest.mark.unit, pytest.mark.decorators]


def test_timeout_raises_without_blocking_on_slow_function() -> None:
    @timeout(1)
    def slow_function() -> str:
        time.sleep(5)
        return "done"

    start = time.monotonic()
    with pytest.raises(TimeoutException):
        slow_function()
    elapsed = time.monotonic() - start
    assert elapsed < 3
