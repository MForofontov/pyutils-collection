import operator

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.multiprocessing_functions]
from pyutils_collection.multiprocessing_functions.parallel_accumulate import (
    parallel_accumulate,
)


def add(a: int, b: int) -> int:
    return a + b


def test_parallel_accumulate_basic() -> None:
    """
    Test case 1: Test parallel_accumulate with a simple addition function.
    """
    data: list[int] = [1, 2, 3, 4]
    result: list[int] = parallel_accumulate(add, data)
    assert result == [1, 3, 6, 10]


def test_parallel_accumulate_chunk_size() -> None:
    """
    Test case 2: Test parallel_accumulate with a custom chunk size.
    """
    data: list[int] = [1, 2, 3, 4]
    result: list[int] = parallel_accumulate(add, data, chunk_size=2)
    assert result == [1, 3, 6, 10]


def test_parallel_accumulate_empty() -> None:
    """
    Test case 3: Test parallel_accumulate with an empty list.
    """
    data: list[int] = []
    result: list[int] = parallel_accumulate(add, data)
    assert result == []


@pytest.mark.parametrize("chunk_size", [1, 2, 3])
def test_parallel_accumulate_uses_operation(chunk_size: int) -> None:
    assert parallel_accumulate(
        operator.mul, [2, 3, 4, 5], num_processes=2, chunk_size=chunk_size
    ) == [2, 6, 24, 120]


def test_parallel_accumulate_preserves_operand_order() -> None:
    assert parallel_accumulate(
        operator.add, ["a", "b", "c", "d"], num_processes=2, chunk_size=2
    ) == ["a", "ab", "abc", "abcd"]
