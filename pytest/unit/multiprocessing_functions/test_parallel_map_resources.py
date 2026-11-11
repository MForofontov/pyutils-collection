"""Default process counts should be bounded by useful work."""

from unittest.mock import patch

import pytest
from pyutils_collection.multiprocessing_functions.parallel_map import parallel_map

pytestmark = [pytest.mark.unit, pytest.mark.multiprocessing_functions]


def test_empty_default_map_does_not_start_workers() -> None:
    with patch(
        "pyutils_collection.multiprocessing_functions.parallel_map.Pool"
    ) as pool:
        pool.return_value.__enter__.return_value.map.return_value = []
        assert parallel_map(abs, []) == []
    pool.assert_not_called()


def test_default_map_starts_no_more_workers_than_items() -> None:
    with (
        patch(
            "pyutils_collection.multiprocessing_functions.parallel_map.cpu_count",
            return_value=64,
        ),
        patch("pyutils_collection.multiprocessing_functions.parallel_map.Pool") as pool,
    ):
        pool.return_value.__enter__.return_value.map.return_value = [1, 2]
        assert parallel_map(abs, [-1, -2]) == [1, 2]
    pool.assert_called_once_with(processes=2)


def test_explicit_worker_count_is_preserved() -> None:
    with patch(
        "pyutils_collection.multiprocessing_functions.parallel_map.Pool"
    ) as pool:
        pool.return_value.__enter__.return_value.map.return_value = [1]
        assert parallel_map(abs, [-1], num_processes=4) == [1]
    pool.assert_called_once_with(processes=4)
