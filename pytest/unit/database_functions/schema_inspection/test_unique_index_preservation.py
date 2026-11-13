"""A longer index does not replace a shorter uniqueness constraint."""

from sqlalchemy import Column, Index, Integer, MetaData, Table

import pytest
from pyutils_collection.database_functions.schema_inspection import (
    find_duplicate_indexes,
)

pytestmark = [pytest.mark.unit, pytest.mark.database]


@pytest.mark.parametrize("short_unique", [False, True])
@pytest.mark.parametrize("short_first", [False, True])
def test_prefix_index_preserves_uniqueness(memory_engine, short_unique, short_first):
    metadata = MetaData()
    table = Table(
        "records", metadata, Column("customer", Integer), Column("created", Integer)
    )
    short_name = "a_short" if short_first else "z_short"
    long_name = "z_long" if short_first else "a_long"
    Index(short_name, table.c.customer, unique=short_unique)
    Index(long_name, table.c.customer, table.c.created)
    metadata.create_all(memory_engine)
    with memory_engine.connect() as connection:
        result = find_duplicate_indexes(connection)
        redundant = {item["redundant_index"] for item in result["redundant"]}
        assert (short_name in redundant) is (not short_unique)
        assert result["summary"]["total_indexes"] == 2
        assert result["exact_duplicates"] == []
