"""Measuring one call must not disable tracing owned by its caller."""

import tracemalloc

import pytest
from pyutils_collection.testing_functions.benchmark_helpers.measure_memory_usage import (
    measure_memory_usage,
)

pytestmark = [pytest.mark.unit, pytest.mark.testing]


@pytest.mark.parametrize("failure", [False, True])
def test_measurement_preserves_existing_tracing(failure):
    def operation():
        if failure:
            raise RuntimeError("operation failed")
        return list(range(100))

    tracemalloc.start()
    try:
        if failure:
            with pytest.raises(RuntimeError, match="operation failed"):
                measure_memory_usage(operation)
        else:
            assert measure_memory_usage(operation)["result"] == list(range(100))
        assert tracemalloc.is_tracing()
    finally:
        tracemalloc.stop()
