"""Schema selection must preserve observable analysis of existing data."""

from sqlalchemy import Column, ForeignKey, Integer, MetaData, String, Table

import pytest
from pyutils_collection.database_functions import schema_inspection as inspection

pytestmark = [pytest.mark.unit, pytest.mark.database]


@pytest.mark.parametrize(
    "name",
    [
        "find_unused_columns",
        "suggest_data_type_optimizations",
        "check_sequence_health",
        "get_table_sizes",
        "find_duplicate_rows",
        "get_column_statistics",
        "compare_table_data",
        "find_missing_indexes",
        "verify_referential_integrity",
    ],
)
def test_schema_selection_preserves_analysis(memory_engine, name):
    metadata = MetaData()
    parent = Table("parents", metadata, Column("id", Integer, primary_key=True))
    table = Table(
        "records",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("label", String(1000)),
        Column("unused", String),
        Column("parent_id", Integer, ForeignKey(parent.c.id)),
    )
    metadata.create_all(memory_engine)
    with memory_engine.connect() as connection:
        connection.execute(
            table.insert(),
            [
                {"id": value, "label": "same", "parent_id": 99}
                for value in (2147483645, 2147483646)
            ],
        )
        connection.commit()
        analyze = getattr(inspection, name)

        def run(schema):
            if name == "compare_table_data":
                return analyze(
                    connection,
                    connection,
                    "records",
                    source_schema=schema,
                    target_schema=schema,
                )
            if name == "find_duplicate_rows":
                return analyze(connection, "records", ["label"], schema=schema)
            if name == "get_column_statistics":
                return analyze(connection, "records", schema=schema)
            if name == "verify_referential_integrity":
                return analyze(connection, schema=schema)
            return analyze(connection, tables=["records"], schema=schema)

        expected = run(None)
        assert expected, "fixture must exercise a nonempty result"
        assert run("main") == expected
        assert len(connection.execute(table.select()).all()) == 2
