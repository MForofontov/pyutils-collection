"""An explicit schema must not silently discard selected reflected tables."""

import pytest
from sqlalchemy import Column, Integer, MetaData, String, Table

from pyutils_collection.database_functions.schema_inspection import (
    analyze_column_cardinality,
    check_data_anomalies,
    check_encoding_issues,
)

pytestmark = [pytest.mark.unit, pytest.mark.database]


@pytest.mark.parametrize(
    "analyze", [analyze_column_cardinality, check_data_anomalies, check_encoding_issues]
)
def test_explicit_table_analysis_preserves_results_with_schema(memory_engine, analyze):
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
            table.insert(), [{"id": 1, "label": "Ã©"}, {"id": 2, "label": "Ã©"}]
        )
        connection.commit()
        expected = analyze(connection, tables=["records"])
        assert expected, "fixture must exercise a reported analysis result"
        assert analyze(connection, tables=["records"], schema="main") == expected
        assert connection.execute(table.select()).all() == [(1, "Ã©"), (2, "Ã©")]
