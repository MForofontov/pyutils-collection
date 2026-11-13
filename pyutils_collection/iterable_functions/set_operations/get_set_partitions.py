"""Get set partitions utilities."""

from typing import TypeVar

T = TypeVar("T")


def get_set_partitions(input_set: set[T], k: int) -> list[list[set[T]]]:
    """
    Generate all possible ways to partition a set into k non-empty subsets.

    This generates all distinct partitions of the set into exactly k subsets.
    Note: This can be computationally expensive for large sets.

    Parameters
    ----------
    input_set : set[T]
        The input set to partition.
    k : int
        Number of subsets to partition into.

    Returns
    -------
    list[list[set[T]]]
        List of all possible partitions, where each partition is a list of
        ``k`` subsets.

    Raises
    ------
    TypeError
        If input_set is not a set or k is not an int.
    ValueError
        If k is less than 1 or greater than the set size.

    Examples
    --------
    >>> s = {1, 2, 3}
    >>> partitions = get_set_partitions(s, 2)
    >>> len(partitions)  # Number of ways to partition into 2 subsets
    3

    >>> # One possible partition: [{1}, {2, 3}]
    >>> # Another: [{2}, {1, 3}]
    >>> # Another: [{3}, {1, 2}]

    Notes
    -----
    This uses backtracking to generate each distinct partition exactly once.
    Output groups follow their first element in sorted input order; returned
    subsets are independent sets, and the input set is unchanged.
    For large sets, this can be very slow due to combinatorial explosion.

    Complexity
    ----------
    Time: O(n * k * Stirling2nd(n,k)), output space: O(n * Stirling2nd(n,k)).
    Backtracking uses O(n) additional working state.
    """
    # Input validation
    if not isinstance(input_set, set):
        raise TypeError(f"input_set must be a set, got {type(input_set).__name__}")

    if not isinstance(k, int):
        raise TypeError(f"k must be an int, got {type(k).__name__}")

    if k < 1:
        raise ValueError(f"k must be at least 1, got {k}")

    if k > len(input_set):
        raise ValueError(f"k cannot be greater than set size {len(input_set)}, got {k}")

    # Convert to sorted list for consistent ordering
    elements = sorted(list(input_set))  # type: ignore[type-var]

    partitions: list[list[set[T]]] = []
    groups: list[set[T]] = []

    def generate(index: int) -> None:
        remaining = len(elements) - index
        if len(groups) + remaining < k:
            return
        if index == len(elements):
            if len(groups) == k:
                partitions.append([group.copy() for group in groups])
            return

        element = elements[index]
        # Existing groups are ordered by their first sorted element. A new
        # group is introduced only at the end, so unlabeled partitions are
        # generated exactly once.
        for group in groups:
            group.add(element)
            generate(index + 1)
            group.remove(element)
        if len(groups) < k:
            groups.append({element})
            generate(index + 1)
            groups.pop()

    generate(0)
    return partitions


__all__ = ["get_set_partitions"]
