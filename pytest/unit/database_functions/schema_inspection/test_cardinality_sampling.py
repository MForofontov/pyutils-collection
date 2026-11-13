"""A sample limit must constrain input rows before aggregate calculations."""

from sqlalchemy import Column, Integer, MetaData, String, Table

import pytest
from pyutils_collection.database_functions.schema_inspection import (
    analyze_column_cardinality,
)

pytestmark = [pytest.mark.unit, pytest.mark.database]


@pytest.mark.parametrize("sample_size", [None, 1, 3, 10])
def test_cardinality_sample_limits_all_aggregates(memory_engine, sample_size):
    metadata = MetaData()
    table = Table(
        "records",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("label", String),
    )
    metadata.create_all(memory_engine)
    with memory_engine.connect() as connection:
        connection.execute(
            table.insert(),
            [{"id": i, "label": None if i in (1, 4) else "same"} for i in range(6)],
        )
        connection.commit()
        result = analyze_column_cardinality(
            connection,
            tables=["records"],
            sample_size=sample_size,
            low_cardinality_threshold=0.9,
        )
        assert len(result) == 1
        stats = result[0]
        expected_total = min(sample_size or 6, 6)
        expected_null = sum(i in (1, 4) for i in range(expected_total))
        assert stats["total_rows"] == expected_total
        assert stats["null_count"] == expected_null
        assert stats["distinct_values"] == 1
        assert stats["cardinality_ratio"] == round(
            1 / (expected_total - expected_null), 4
        )
        assert stats["null_percentage"] == round(
            expected_null * 100 / expected_total, 2
        )
        if stats["top_values"] is not None:
            assert sum(item["count"] for item in stats["top_values"]) == expected_total
        assert connection.execute(table.select()).all() == [
            (i, None if i in (1, 4) else "same") for i in range(6)
        ]
