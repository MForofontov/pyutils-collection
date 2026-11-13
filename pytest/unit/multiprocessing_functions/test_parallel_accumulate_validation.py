"""Validate chunk settings before starting worker processes."""

import importlib
import operator
from typing import Any
from unittest.mock import patch

import pytest

from pyutils_collection.multiprocessing_functions import parallel_accumulate

pytestmark = [pytest.mark.unit, pytest.mark.multiprocessing_functions]


@pytest.mark.parametrize("size", [0, -1])
def test_invalid_chunk_size_rejected_before_pool(size: int) -> None:
    module = importlib.import_module(
        "pyutils_collection.multiprocessing_functions.parallel_accumulate"
    )
    with patch.object(module, "Pool") as pool:
        with pytest.raises(ValueError, match="chunk_size"):
            parallel_accumulate(operator.add, [1, 2], chunk_size=size)
    pool.assert_not_called()


@pytest.mark.parametrize("size", [1.5, "2", None])
def test_noninteger_chunk_size_rejected_before_pool(size: Any) -> None:
    module = importlib.import_module(
        "pyutils_collection.multiprocessing_functions.parallel_accumulate"
    )
    with patch.object(module, "Pool") as pool:
        with pytest.raises(TypeError, match="chunk_size"):
            parallel_accumulate(operator.add, [1, 2], chunk_size=size)
    pool.assert_not_called()
