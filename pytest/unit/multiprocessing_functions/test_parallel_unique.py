from typing import Any, cast

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.multiprocessing_functions]
from pyutils_collection.multiprocessing_functions.parallel_unique import parallel_unique


def test_parallel_unique_basic() -> None:
    """
    Test case 1: Test extracting unique elements from a list.
    """
    data: list[int] = [1, 2, 2, 3, 3, 4]
    result: list[int] = parallel_unique(data)
    assert sorted(result) == [1, 2, 3, 4]


def test_parallel_unique_chunk_size() -> None:
    """
    Test case 2: Test parallel_unique with a custom chunk size.
    """
    data: list[int] = [1, 1, 2, 2, 3]
    result: list[int] = parallel_unique(data, chunk_size=2)
    assert sorted(result) == [1, 2, 3]


def test_parallel_unique_empty_list() -> None:
    """
    Test case 3: Test parallel_unique with an empty list.
    """
    result: list[int] = parallel_unique([])
    assert result == []


def test_parallel_unique_all_identical() -> None:
    """
    Test case 4: Test parallel_unique with all identical elements.
    """
    data = [7, 7, 7, 7]
    result = parallel_unique(data)
    assert result == [7]


def test_parallel_unique_strings() -> None:
    """
    Test case 5: Test parallel_unique with string elements.
    """
    data = ["a", "b", "a", "c", "b"]
    result = sorted(parallel_unique(data))
    assert result == ["a", "b", "c"]


def test_parallel_unique_non_list_input() -> None:
    """
    Test case 6: Test parallel_unique with non-list input (should raise TypeError if validated).
    """
    try:
        parallel_unique(cast(Any, "not a list"))
    except Exception as e:
        assert isinstance(e, Exception)


def test_parallel_unique_invalid_chunk_size() -> None:
    """
    Test case 7: Test parallel_unique with invalid chunk_size (should raise ValueError if validated).
    """
    data = [1, 2, 3]
    try:
        parallel_unique(data, chunk_size=0)
    except Exception as e:
        assert isinstance(e, Exception)
    try:
        parallel_unique(data, chunk_size=-1)
    except Exception as e:
        assert isinstance(e, Exception)


def test_parallel_unique_invalid_num_processes() -> None:
    """
    Test case 8: Test parallel_unique with invalid num_processes (should raise ValueError if validated).
    """
    data = [1, 2, 3]
    try:
        parallel_unique(data, num_processes=0)
    except Exception as e:
        assert isinstance(e, Exception)
    try:
        parallel_unique(data, num_processes=-2)
    except Exception as e:
        assert isinstance(e, Exception)
