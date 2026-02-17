from typing import Any, cast

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.multiprocessing_functions]
from pyutils_collection.multiprocessing_functions.parallel_sort import parallel_sort


def test_parallel_sort_basic() -> None:
    """
    Test case 1: Test parallel_sort on an unsorted list.
    """
    data: list[int] = [5, 2, 3, 1, 4]
    result: list[int] = parallel_sort(data)
    assert result == [1, 2, 3, 4, 5]


def test_parallel_sort_chunk_size() -> None:
    """
    Test case 2: Test parallel_sort with a specific chunk size.
    """
    data: list[int] = [4, 3, 2, 1]
    result: list[int] = parallel_sort(data, chunk_size=2)
    assert result == [1, 2, 3, 4]


def test_parallel_sort_empty_list() -> None:
    """
    Test case 3: Test parallel_sort with empty list.
    """
    data: list[int] = []
    result: list[int] = parallel_sort(data)
    assert result == []


def test_parallel_sort_single_element() -> None:
    """
    Test case 4: Test parallel_sort with single element.
    """
    data: list[int] = [42]
    result: list[int] = parallel_sort(data)
    assert result == [42]


def test_parallel_sort_already_sorted() -> None:
    """
    Test case 5: Test parallel_sort with already sorted list.
    """
    data: list[int] = [1, 2, 3, 4, 5]
    result: list[int] = parallel_sort(data)
    assert result == [1, 2, 3, 4, 5]


def test_parallel_sort_reverse_sorted() -> None:
    """
    Test case 6: Test parallel_sort with reverse sorted list.
    """
    data: list[int] = [5, 4, 3, 2, 1]
    result: list[int] = parallel_sort(data)
    assert result == [1, 2, 3, 4, 5]


def test_parallel_sort_duplicates() -> None:
    """
    Test case 7: Test parallel_sort with duplicate values.
    """
    data: list[int] = [3, 1, 4, 1, 5, 9, 2, 6, 5]
    result: list[int] = parallel_sort(data)
    assert result == [1, 1, 2, 3, 4, 5, 5, 6, 9]


def test_parallel_sort_large_list() -> None:
    """
    Test case 8: Test parallel_sort with larger list.
    """
    data: list[int] = list(range(100, 0, -1))  # [100, 99, ..., 1]
    result: list[int] = parallel_sort(data)
    assert result == list(range(1, 101))  # [1, 2, ..., 100]


def test_parallel_sort_invalid_data_type() -> None:
    """
    Test case 9: Test parallel_sort with invalid data type.
    """
    with pytest.raises(TypeError):
        parallel_sort(cast(Any, "not_a_list"))


def test_parallel_sort_invalid_num_processes_type() -> None:
    """
    Test case 10: Test parallel_sort with invalid num_processes type.
    """
    with pytest.raises(TypeError):
        parallel_sort([1, 2, 3], num_processes=cast(Any, "invalid"))


def test_parallel_sort_invalid_chunk_size_type() -> None:
    """
    Test case 11: Test parallel_sort with invalid chunk_size type.
    """
    with pytest.raises(TypeError):
        parallel_sort([1, 2, 3], chunk_size=cast(Any, "invalid"))


def test_parallel_sort_zero_chunk_size() -> None:
    """
    Test case 12: Test parallel_sort with zero chunk_size.
    """
    with pytest.raises(ValueError):
        parallel_sort([1, 2, 3], chunk_size=0)


def test_parallel_sort_negative_chunk_size() -> None:
    """
    Test case 13: Test parallel_sort with negative chunk_size.
    """
    with pytest.raises(ValueError):
        parallel_sort([1, 2, 3], chunk_size=-1)


def test_parallel_sort_zero_num_processes() -> None:
    """
    Test case 14: Test parallel_sort with zero num_processes.
    """
    with pytest.raises(ValueError):
        parallel_sort([1, 2, 3], num_processes=0)


def test_parallel_sort_negative_num_processes() -> None:
    """
    Test case 15: Test parallel_sort with negative num_processes.
    """
    with pytest.raises(ValueError):
        parallel_sort([1, 2, 3], num_processes=-1)
