import pytest

pytestmark = [pytest.mark.unit, pytest.mark.decorators]
from pyutils_collection.decorators.cache import cache

call_counts = {"add": 0, "concat": 0}


@cache
def add(a, b=0):
    call_counts["add"] += 1
    return a + b


@cache
def concat(*args, **kwargs):
    call_counts["concat"] += 1
    return "".join(args) + "".join(kwargs.values())


def test_cache_basic() -> None:

    """
    Test case 1: Basic caching functionality.
    """
    call_counts["add"] = 0
    assert add(1, 2) == 3
    assert add(1, 2) == 3  # Should return cached result
    add.cache_clear()
    assert call_counts["add"] == 1  # Function should be called only once
    call_counts["add"] = 0


def test_cache_different_args() -> None:

    """
    Test case 2: Caching with different arguments.
    """
    call_counts["add"] = 0
    assert add(1, 2) == 3
    assert add(2, 3) == 5  # Different arguments, should not use cache
    add.cache_clear()
    assert call_counts["add"] == 2  # Function should be called twice
    call_counts["add"] = 0


def test_cache_with_kwargs() -> None:

    """
    Test case 3: Caching with keyword arguments.
    """
    call_counts["add"] = 0
    assert add(a=1, b=2) == 3
    assert add(a=1, b=2) == 3  # Should return cached result
    add.cache_clear()
    assert call_counts["add"] == 1  # Function should be called only once
    call_counts["add"] = 0


def test_cache_concat() -> None:

    """
    Test case 4: Caching with variable arguments.
    """
    call_counts["concat"] = 0
    assert concat("a", "b", "c") == "abc"
    assert concat("a", "b", "c") == "abc"  # Should return cached result
    assert call_counts["concat"] == 1  # Function should be called only once
    call_counts["concat"] = 0


def test_cache_concat_different_args() -> None:

    """
    Test case 5: Caching with different variable arguments.
    """
    call_counts["concat"] = 0
    concat.cache_clear()  # Clear cache before test
    assert concat("a", "b", "c") == "abc"
    # Different arguments, should not use cache
    assert concat("x", "y", "z") == "xyz"
    assert (
        call_counts["concat"] == 2
    )  # Function should be called twice (different args)
    concat.cache_clear()
    call_counts["concat"] = 0


def test_cache_concat_kwargs() -> None:

    """
    Test case 6: Caching with keyword arguments in concat function.
    """
    call_counts["concat"] = 0
    assert concat(a="a", b="b", c="c") == "abc"
    assert concat(a="a", b="b", c="c") == "abc"  # Should return cached result
    assert call_counts["concat"] == 1  # Function should be called only once
    call_counts["concat"] = 0


def test_cache_concat_different_kwargs() -> None:

    """
    Test case 7: Caching with different keyword arguments in concat function.
    """
    call_counts["concat"] = 0
    assert concat(a="a", b="b", c="c") == "abc"
    assert (
        concat(x="x", y="y", z="z") == "xyz"
    )  # Different arguments, should not use cache
    assert call_counts["concat"] == 1  # Function should be called twice
    call_counts["concat"] = 0


def test_cache_concat_mixed_args() -> None:

    """
    Test case 8: Caching with mixed positional and keyword arguments in concat function.
    """
    call_counts["concat"] = 0
    assert concat("a", "b", c="c", d="d") == "abcd"
    # Should return cached result
    assert concat("a", "b", c="c", d="d") == "abcd"
    assert call_counts["concat"] == 1  # Function should be called only once
    call_counts["concat"] = 0


def test_cache_concat_different_mixed_args() -> None:

    """
    Test case 9: Caching with different mixed positional and keyword arguments in concat function.
    """
    call_counts["concat"] = 0
    assert concat("a", "b", c="c", d="d") == "abcd"
    assert (
        concat("x", "y", z="z", w="w") == "xyzw"
    )  # Different arguments, should not use cache
    assert call_counts["concat"] == 1  # Function should be called twice
    call_counts["concat"] = 0


def test_cache_clear() -> None:

    """
    Test case 10: Clearing the cache.
    """
    call_counts["add"] = 0
    assert add(1, 2) == 3
    add.cache_clear()
    assert add(1, 2) == 3  # Should recompute as cache was cleared
    assert call_counts["add"] == 2  # Function should be called twice
    call_counts["add"] = 0


def test_cache_with_unhashable_args() -> None:

    """
    Test case 11: Function with unhashable arguments.
    """

    @cache
    def example_function_unhashable(a):
        return sum(a)

    with pytest.raises(TypeError, match="Unhashable arguments"):
        example_function_unhashable(
            [1, 2, 3, {}]
        )  # Lists with dictionaries are unhashable


def test_cache_with_exception() -> None:

    """
    Test case 12: Function that raises an exception.
    """

    @cache
    def example_function_exception(a, b):
        raise ValueError("An error occurred")

    with pytest.raises(ValueError, match="An error occurred"):
        example_function_exception(1, 2)
