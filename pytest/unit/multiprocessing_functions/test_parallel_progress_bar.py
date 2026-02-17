from typing import Any, cast

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.multiprocessing_functions]
from pyutils_collection.multiprocessing_functions.parallel_progress_bar import parallel_progress_bar


def square(x: int) -> int:
    return x * x


def add_one(x: int) -> int:
    return x + 1


def test_parallel_progress_bar_basic() -> None:
    """
    Test case 1: Test progress bar parallel execution.
    """
    data: list[int] = [1, 2, 3]
    result: list[int] = parallel_progress_bar(square, data)
    assert result == [1, 4, 9]


def test_parallel_progress_bar_custom_processes() -> None:
    """
    Test case 2: Test progress bar with custom num_processes.
    """
    data: list[int] = [1, 2, 3]
    result: list[int] = parallel_progress_bar(add_one, data, num_processes=2)
    assert result == [2, 3, 4]


def test_parallel_progress_bar_empty_data() -> None:
    """
    Test case 3: Test progress bar with empty data list.
    """
    data: list[int] = []
    result: list[int] = parallel_progress_bar(square, data)
    assert result == []


def test_parallel_progress_bar_single_process() -> None:
    """
    Test case 4: Test progress bar with single process.
    """
    data: list[int] = [1, 2, 3]
    result: list[int] = parallel_progress_bar(square, data, num_processes=1)
    assert result == [1, 4, 9]


def test_parallel_progress_bar_large_data() -> None:
    """
    Test case 5: Test progress bar with larger dataset.
    """
    data: list[int] = list(range(100))
    result: list[int] = parallel_progress_bar(square, data, num_processes=2)
    expected: list[int] = [x * x for x in range(100)]
    assert result == expected


def test_parallel_progress_bar_invalid_function_type() -> None:
    """
    Test case 6: Test parallel_progress_bar with invalid function type.
    """
    with pytest.raises(TypeError):
        parallel_progress_bar(cast(Any, "not_a_function"), [1, 2, 3])


def test_parallel_progress_bar_invalid_data_type() -> None:
    """
    Test case 7: Test parallel_progress_bar with invalid data type.
    """
    with pytest.raises(TypeError):
        parallel_progress_bar(square, cast(Any, "not_a_list"))


def test_parallel_progress_bar_invalid_num_processes_type() -> None:
    """
    Test case 8: Test parallel_progress_bar with invalid num_processes type.
    """
    with pytest.raises(TypeError):
        parallel_progress_bar(square, [1, 2, 3], num_processes=cast(Any, "not_an_int"))


def test_parallel_progress_bar_zero_num_processes() -> None:
    """
    Test case 9: Test parallel_progress_bar with zero num_processes.
    """
    with pytest.raises(ValueError):
        parallel_progress_bar(square, [1, 2, 3], num_processes=0)


def test_parallel_progress_bar_negative_num_processes() -> None:
    """
    Test case 10: Test parallel_progress_bar with negative num_processes.
    """
    with pytest.raises(ValueError):
        parallel_progress_bar(square, [1, 2, 3], num_processes=-1)
