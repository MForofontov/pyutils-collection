from unittest.mock import Mock

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.batch_processing]
from pyutils_collection.batch_processing_functions.chunked_processor import (
    ChunkedProcessor,
    chunked_processor,
)


def test_chunked_processor_normal_operation() -> None:
    """
    Test case 1: Normal operation with valid inputs.
    """
    items = list(range(10))
    processor = Mock(side_effect=lambda batch: [x * 2 for x in batch])

    results = list(chunked_processor(items, processor, chunk_size=3))

    assert len(results) == 10
    assert results == [0, 2, 4, 6, 8, 10, 12, 14, 16, 18]
    assert processor.call_count == 4  # ceil(10/3) = 4 chunks


def test_chunked_processor_exact_chunk_size() -> None:
    """
    Test case 2: Items count is exact multiple of chunk_size.
    """
    items = list(range(12))
    processor = Mock(side_effect=lambda batch: [x + 1 for x in batch])

    results = list(chunked_processor(items, processor, chunk_size=4))

    assert len(results) == 12
    assert results == list(range(1, 13))


def test_chunked_processor_single_chunk() -> None:
    """
    Test case 3: All items fit in single chunk.
    """
    items = [1, 2, 3]
    processor = Mock(side_effect=lambda batch: [x * 2 for x in batch])

    results = list(chunked_processor(items, processor, chunk_size=5))

    assert len(results) == 3
    assert results == [2, 4, 6]


def test_chunked_processor_with_strings() -> None:
    """
    Test case 4: Processing strings.
    """
    items = ["hello", "world", "test"]
    processor = Mock(side_effect=lambda batch: [s.upper() for s in batch])

    results = list(chunked_processor(items, processor, chunk_size=2))

    assert results == ["HELLO", "WORLD", "TEST"]


def test_chunked_processor_edge_case_empty_iterable() -> None:
    """
    Test case 5: Empty iterable.
    """
    items: list[int] = []
    processor = Mock(side_effect=lambda batch: batch)

    results = list(chunked_processor(items, processor, chunk_size=3))

    assert len(results) == 0
    assert processor.call_count == 0


def test_chunked_processor_edge_case_single_item() -> None:
    """
    Test case 6: Single item in iterable.
    """
    items = [42]
    processor = Mock(side_effect=lambda batch: [x * 2 for x in batch])

    results = list(chunked_processor(items, processor, chunk_size=3))

    assert results == [84]


def test_chunked_processor_edge_case_chunk_size_one() -> None:
    """
    Test case 7: Chunk size of 1.
    """
    items = [1, 2, 3, 4]
    processor = Mock(side_effect=lambda batch: [x + 10 for x in batch])

    results = list(chunked_processor(items, processor, chunk_size=1))

    assert results == [11, 12, 13, 14]


def test_chunked_processor_edge_case_processor_returns_none() -> None:
    """
    Test case 8: Processor returns None for some items.
    """
    items = [1, 2, 3, 4]
    processor = Mock(
        side_effect=lambda batch: [None if x % 2 == 0 else x for x in batch]
    )

    results = list(chunked_processor(items, processor, chunk_size=2))

    assert results == [1, None, 3, None]


def test_chunked_processor_edge_case_large_chunk_size() -> None:
    """
    Test case 9: Chunk size larger than iterable.
    """
    items = [1, 2, 3]
    processor = Mock(side_effect=lambda batch: [x * 3 for x in batch])

    results = list(chunked_processor(items, processor, chunk_size=100))

    assert results == [3, 6, 9]


def test_chunked_processor_type_error_non_iterable() -> None:
    """
    Test case 10: TypeError for non-iterable items.
    """
    processor = Mock()

    with pytest.raises(TypeError, match="items must be iterable"):
        list(chunked_processor(42, processor, chunk_size=3))  # type: ignore[arg-type]


def test_chunked_processor_type_error_non_callable_processor() -> None:
    """
    Test case 11: TypeError for non-callable processor.
    """
    items = [1, 2, 3]

    with pytest.raises(TypeError, match="processor must be callable"):
        list(chunked_processor(items, "not_callable", chunk_size=3))  # type: ignore[arg-type]


def test_chunked_processor_type_error_invalid_chunk_size_type() -> None:
    """
    Test case 12: TypeError for invalid chunk_size type.
    """
    items = [1, 2, 3]
    processor = Mock()

    with pytest.raises(TypeError, match="chunk_size must be an integer"):
        list(chunked_processor(items, processor, chunk_size="3"))  # type: ignore[arg-type]


def test_chunked_processor_value_error_zero_chunk_size() -> None:
    """
    Test case 13: ValueError for zero chunk_size.
    """
    items = [1, 2, 3]
    processor = Mock()

    with pytest.raises(ValueError, match="chunk_size must be positive"):
        list(chunked_processor(items, processor, chunk_size=0))


def test_chunked_processor_value_error_negative_chunk_size() -> None:
    """
    Test case 14: ValueError for negative chunk_size.
    """
    items = [1, 2, 3]
    processor = Mock()

    with pytest.raises(ValueError, match="chunk_size must be positive"):
        list(chunked_processor(items, processor, chunk_size=-5))


def test_chunked_processor_class_normal_operation() -> None:
    """
    Test case 15: ChunkedProcessor class normal operation.
    """
    items = list(range(6))
    processor = Mock(side_effect=lambda batch: [x * 2 for x in batch])

    cp = ChunkedProcessor(processor, chunk_size=2)
    results = list(cp.process(items))

    assert results == [0, 2, 4, 6, 8, 10]


def test_chunked_processor_class_with_memory_threshold() -> None:
    """
    Test case 16: ChunkedProcessor with max_memory_mb.
    """
    items = list(range(10))
    processor = Mock(side_effect=lambda batch: [x + 1 for x in batch])

    cp = ChunkedProcessor(processor, chunk_size=3, max_memory_mb=90)
    results = list(cp.process(items))

    assert len(results) == 10


def test_chunked_processor_class_batch_processor() -> None:
    """
    Test case 17: ChunkedProcessor with batch processor.
    """
    items = list(range(9))

    def batch_proc(batch: list[int]) -> list[int]:
        return [x * 2 for x in batch]

    cp = ChunkedProcessor(batch_proc, chunk_size=3)
    results = list(cp.process(items))

    assert results == [0, 2, 4, 6, 8, 10, 12, 14, 16]


def test_chunked_processor_class_reusability() -> None:
    """
    Test case 18: ChunkedProcessor reusability.
    """
    items = list(range(5))
    processor = Mock(side_effect=lambda batch: batch)

    cp = ChunkedProcessor(processor, chunk_size=2)
    results1 = list(cp.process(items))
    results2 = list(cp.process(items))

    assert results1 == list(range(5))
    assert results2 == list(range(5))
    assert processor.call_count == 6  # 3 chunks per call * 2 calls


def test_chunked_processor_class_different_datasets() -> None:
    """
    Test case 19: ChunkedProcessor with different datasets.
    """
    processor = Mock(side_effect=lambda batch: [x * 2 for x in batch])

    cp = ChunkedProcessor(processor, chunk_size=2)

    results1 = list(cp.process([1, 2, 3]))
    results2 = list(cp.process([10, 20]))

    assert results1 == [2, 4, 6]
    assert results2 == [20, 40]


def test_chunked_processor_class_type_error_invalid_chunk_size() -> None:
    """
    Test case 20: TypeError for invalid chunk_size.
    """
    processor = Mock()
    with pytest.raises(TypeError, match="chunk_size must be an integer"):
        ChunkedProcessor(processor, chunk_size=2.5)  # type: ignore[arg-type]


def test_chunked_processor_class_value_error_zero_chunk_size() -> None:
    """
    Test case 21: ValueError for zero chunk_size.
    """
    processor = Mock()
    with pytest.raises(ValueError, match="chunk_size must be positive"):
        ChunkedProcessor(processor, chunk_size=0)


def test_chunked_processor_class_type_error_invalid_max_memory_mb() -> None:
    """
    Test case 22: TypeError for invalid max_memory_mb.
    """
    processor = Mock()
    with pytest.raises(TypeError, match="max_memory_mb must be an integer or None"):
        ChunkedProcessor(processor, chunk_size=3, max_memory_mb="90")  # type: ignore[arg-type]


def test_chunked_processor_class_value_error_max_memory_mb_negative() -> None:
    """
    Test case 23: ValueError for negative max_memory_mb.
    """
    processor = Mock()
    with pytest.raises(ValueError, match="max_memory_mb must be positive"):
        ChunkedProcessor(processor, chunk_size=3, max_memory_mb=-10)


def test_chunked_processor_class_type_error_non_callable_processor() -> None:
    """
    Test case 24: TypeError for non-callable processor.
    """
    with pytest.raises(TypeError, match="processor must be callable"):
        ChunkedProcessor("not_callable", chunk_size=3)  # type: ignore[arg-type]


def test_chunked_processor_type_error_processor_returns_non_list() -> None:
    """
    Test case 25: TypeError when processor returns non-list.
    """
    items = [1, 2, 3]
    processor = Mock(
        side_effect=lambda batch: tuple(batch)
    )  # Returns tuple instead of list

    with pytest.raises(TypeError, match="processor must return a list"):
        list(chunked_processor(items, processor, chunk_size=2))


def test_chunked_processor_preserves_retained_batches() -> None:
    batches = []

    def process(batch):
        batches.append(batch)
        return [batch]

    result = list(chunked_processor(range(5), process, chunk_size=2))
    assert result == [[0, 1], [2, 3], [4]]
    assert batches == [[0, 1], [2, 3], [4]]
    assert len({id(batch) for batch in batches}) == 3
