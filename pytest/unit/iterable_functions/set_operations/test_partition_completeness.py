"""Set partitions must satisfy their exact-k contract without filtering."""

import pytest

from pyutils_collection.iterable_functions.set_operations.get_set_partitions import (
    get_set_partitions,
)

pytestmark = [pytest.mark.unit, pytest.mark.iterable_functions]


@pytest.mark.parametrize(
    ("n", "k", "count"), [(3, 2, 3), (4, 2, 7), (4, 3, 6), (5, 3, 25), (3, 3, 1)]
)
def test_exact_partition_count_and_invariants(n: int, k: int, count: int) -> None:
    source = set(range(n))
    result = get_set_partitions(source, k)
    assert len(result) == count
    canonical = set()
    for partition in result:
        assert len(partition) == k
        assert all(partition)
        assert set.union(*partition) == source
        assert sum(map(len, partition)) == n
        canonical.add(frozenset(map(frozenset, partition)))
    assert len(canonical) == count
    assert source == set(range(n))


def test_three_element_partition_membership() -> None:
    result = get_set_partitions({1, 2, 3}, 2)
    assert {frozenset(map(frozenset, p)) for p in result} == {
        frozenset([frozenset([1]), frozenset([2, 3])]),
        frozenset([frozenset([2]), frozenset([1, 3])]),
        frozenset([frozenset([3]), frozenset([1, 2])]),
    }
