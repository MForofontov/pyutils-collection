import time

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.decorators]
from pyutils_collection.decorators.cache_with_expiration import cache_with_expiration

call_counts = {"add": 0, "concat": 0}


@cache_with_expiration(2)
def add(a: int, b: int) -> int:
    call_counts["add"] += 1
    return a + b


@cache_with_expiration(2)
def concat(*args: str, **kwargs: str) -> str:
    call_counts["concat"] += 1
    return "".join(args) + "".join(kwargs.values())


def test_cache_basic() -> None:

    """
    Test case 1: Basic caching functionality.
    """
    call_counts["add"] = 0
    assert add(1, 2) == 3
    assert add(1, 2) == 3  # Should return cached result
    assert call_counts["add"] == 1  # Function should be called only once
    call_counts["add"] = 0


def test_cache_expiration() -> None:

    """
    Test case 2: Cache expiration.
    """
    call_counts["add"] = 0
    assert add(1, 2) == 3
    time.sleep(3)
    assert add(1, 2) == 3  # Should recompute as cache expired
    assert call_counts["add"] == 1  # Function should be called twice
    call_counts["add"] = 0


def test_cache_different_args() -> None:

    """
    Test case 3: Caching with different arguments.
    """
    call_counts["add"] = 0
    assert add(1, 2) == 3
    assert add(2, 3) == 5  # Different arguments, should not use cache
    assert call_counts["add"] == 1  # Function should be called twice
    call_counts["add"] = 0


def test_cache_with_kwargs() -> None:

    """
    Test case 4: Caching with keyword arguments.
    """
    call_counts["add"] = 0
    assert add(a=1, b=2) == 3
    assert add(a=1, b=2) == 3  # Should return cached result
    assert call_counts["add"] == 1  # Function should be called only once
    call_counts["add"] = 0


def test_cache_concat() -> None:

    """
    Test case 5: Caching with variable arguments.
    """
    call_counts["concat"] = 0
    assert concat("a", "b", "c") == "abc"
    assert concat("a", "b", "c") == "abc"  # Should return cached result
    assert call_counts["concat"] == 1  # Function should be called only once
    call_counts["concat"] = 0


def test_cache_concat_different_args() -> None:

    """
    Test case 6: Caching with different variable arguments.
    """
    call_counts["concat"] = 0
    assert concat("a", "b", "c") == "abc"
    # Different arguments, should not use cache
    assert concat("x", "y", "z") == "xyz"
    assert call_counts["concat"] == 1  # Function should be called twice
    call_counts["concat"] = 0


def test_cache_concat_kwargs() -> None:

    """
    Test case 7: Caching with keyword arguments in concat function.
    """
    call_counts["concat"] = 0
    assert concat(a="a", b="b", c="c") == "abc"
    assert concat(a="a", b="b", c="c") == "abc"  # Should return cached result
    assert call_counts["concat"] == 1  # Function should be called only once
    call_counts["concat"] = 0


def test_cache_clear() -> None:

    """
    Test case 8: Clearing the cache.
    """
    call_counts["add"] = 0
    add.cache_clear()
    assert add(1, 2) == 3
    add.cache_clear()
    assert add(1, 2) == 3  # Should recompute as cache was cleared
    assert call_counts["add"] == 2  # Function should be called twice
    call_counts["add"] = 0


def test_cache_with_expiration_zero() -> None:

    """
    Test case 9: Cache with zero expiration time.
    """
    call_counts["add_no_cache"] = 0

    @cache_with_expiration(0)
    def add_no_cache(a: int, b: int) -> int:
        call_counts["add_no_cache"] += 1
        return a + b

    assert add_no_cache(1, 2) == 3
    assert add_no_cache(1, 2) == 3  # Should recompute as cache time is 0
    assert call_counts["add_no_cache"] == 2  # Function should be called twice


def test_cache_with_negative_expiration() -> None:

    """
    Test case 10: Cache with negative expiration time.
    """
    with pytest.raises(ValueError, match="expiration_time must be a positive integer"):

        @cache_with_expiration(-1)
        def example_function_negative_expiration(a, b):
            return a + b


def test_cache_with_non_integer_expiration() -> None:

    """
    Test case 11: Cache with non-integer expiration time.
    """
    with pytest.raises(ValueError, match="expiration_time must be a positive integer"):

        @cache_with_expiration(2.5)
        def example_function_non_integer_expiration(a, b):
            return a + b


def test_cache_with_unhashable_args() -> None:

    """
    Test case 12: Function with unhashable arguments.
    """

    @cache_with_expiration(2)
    def example_function_unhashable(a):
        return sum(a)

    with pytest.raises(TypeError, match="Unhashable arguments"):
        example_function_unhashable(
            [1, 2, 3, {}]
        )  # Lists with dictionaries are unhashable


def test_cache_with_exception() -> None:

    """
    Test case 13: Function that raises an exception.
    """

    @cache_with_expiration(2)
    def example_function_exception(a, b):
        raise ValueError("An error occurred")

    with pytest.raises(ValueError, match="An error occurred"):
        example_function_exception(1, 2)
