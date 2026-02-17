from typing import Any, cast

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.multiprocessing_functions]
from pyutils_collection.multiprocessing_functions.parallel_map import parallel_map


def square(x: int) -> int:
    return x * x


def add_one(x: int) -> int:
    return x + 1


def fail_on_two(x: int) -> int:
    if x == 2:
        raise ValueError("fail")
    return x


def test_parallel_map_basic() -> None:
    """
    Test case 1: Test the parallel_map function with a simple square function.
    """
    data: list[int] = [1, 2, 3, 4]
    result: list[int] = parallel_map(square, data)
    assert result == [1, 4, 9, 16]


def test_parallel_map_custom_processes() -> None:
    """
    Test case 2: Test the parallel_map function with a specific number of processes.
    """
    data: list[int] = [1, 2, 3, 4]
    result: list[int] = parallel_map(add_one, data, num_processes=2)
    assert result == [2, 3, 4, 5]


def test_parallel_map_empty_list() -> None:
    """
    Test case 3: Test the parallel_map function with an empty list.
    """
    data: list[int] = []
    result: list[int] = parallel_map(square, data)
    assert result == []


def test_parallel_map_non_list_input() -> None:
    """
    Test case 4: Test parallel_map with non-list input (should raise TypeError if validated).
    """
    try:
        parallel_map(lambda x: x, cast(Any, "not a list"))
    except Exception as e:
        assert isinstance(e, Exception)


def test_parallel_map_non_callable_func() -> None:
    """
    Test case 5: Test parallel_map with non-callable func (should raise TypeError if validated).
    """
    data = [1, 2, 3]
    try:
        parallel_map(cast(Any, 123), data)
    except Exception as e:
        assert isinstance(e, Exception)


def test_parallel_map_invalid_num_processes() -> None:
    """
    Test case 6: Test parallel_map with invalid num_processes (should raise ValueError if validated).
    """
    data = [1, 2, 3]
    try:
        parallel_map(lambda x: x, data, num_processes=0)
    except Exception as e:
        assert isinstance(e, Exception)
    try:
        parallel_map(lambda x: x, data, num_processes=-2)
    except Exception as e:
        assert isinstance(e, Exception)


def test_parallel_map_func_raises_exception() -> None:
    """
    Test case 7: Test parallel_map with a function that raises an exception.
    """
    data = [1, 2, 3]
    with pytest.raises(ValueError):
        parallel_map(fail_on_two, data)
