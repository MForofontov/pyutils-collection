import pytest

pytestmark = [pytest.mark.unit, pytest.mark.multiprocessing_functions]
from pyutils_collection.multiprocessing_functions.parallel_gather_errors import parallel_gather_errors


def risky(x: int) -> int:
    if x == 2:
        raise ValueError("bad")
    return x * x


def inc(x: int) -> int:
    return x + 1


def returns_none_for_two(x: int) -> int | None:
    return None if x == 2 else x


def test_parallel_gather_errors_with_exception() -> None:
    """
    Test case 1: Test gathering errors when some inputs raise exceptions.
    """
    data: list[int] = [1, 2, 3]
    results, errors = parallel_gather_errors(risky, data)
    assert results == [1, 9]
    assert len(errors) == 1 and isinstance(errors[0], ValueError)


def test_parallel_gather_errors_no_error() -> None:
    """
    Test case 2: Test when function does not raise any exceptions.
    """
    data: list[int] = [1, 2, 3]
    results, errors = parallel_gather_errors(inc, data)
    assert results == [2, 3, 4]
    assert errors == []


def test_parallel_gather_errors_preserves_none_results() -> None:
    """Successful None results are preserved in the output list."""
    results, errors = parallel_gather_errors(returns_none_for_two, [1, 2, 3])
    assert results == [1, None, 3]
    assert errors == []
