"""ID values and reflected identifiers must not become SQL syntax."""

import pytest
from sqlalchemy import (
    Column,
    ForeignKey,
    MetaData,
    String,
    Table,
    create_engine,
    select,
)
from sqlalchemy.exc import IntegrityError

from pyutils_collection.database_functions.schema_inspection.migrate_id_type import (
    migrate_id_type,
)

pytestmark = [pytest.mark.unit, pytest.mark.database]


def test_migration_binds_quote_containing_ids_and_quotes_identifiers():
    engine = create_engine("sqlite://")
    metadata = MetaData()
    parent = Table(
        "parent records", metadata, Column("record id", String, primary_key=True)
    )
    child = Table(
        "child records",
        metadata,
        Column("owner id", String, ForeignKey(parent.c["record id"])),
    )
    metadata.create_all(engine)
    old_id = "old' OR 1=1 --"
    new_id = "new'; DROP TABLE sentinel; --"
    try:
        with engine.begin() as connection:
            connection.execute(parent.insert(), [{"record id": old_id}])
            connection.execute(child.insert(), [{"owner id": old_id}])
        result = migrate_id_type(
            engine, "parent records", id_column="record id", id_generator=lambda: new_id
        )
        assert result["rows_migrated"] == 1
        assert result["fk_relationships_updated"] == 1
        assert result["id_mapping"] == {old_id: new_id}
        with engine.connect() as connection:
            assert (
                connection.execute(select(parent.c["record id"])).scalar_one() == new_id
            )
            assert (
                connection.execute(select(child.c["owner id"])).scalar_one() == new_id
            )
    finally:
        engine.dispose()


def test_failed_migration_rolls_back_partial_batches():
    engine = create_engine("sqlite://")
    metadata = MetaData()
    table = Table("items", metadata, Column("id", String, primary_key=True))
    metadata.create_all(engine)
    try:
        with engine.begin() as connection:
            connection.execute(table.insert(), [{"id": "first"}, {"id": "second"}])
        with pytest.raises(IntegrityError):
            migrate_id_type(
                engine, "items", id_generator=lambda: "duplicate", batch_size=1
            )
        with engine.connect() as connection:
            assert set(connection.execute(select(table.c.id)).scalars()) == {
                "first",
                "second",
            }
    finally:
        engine.dispose()


@pytest.mark.parametrize("fk_enabled", [False, True])
@pytest.mark.parametrize("fail", [False, True])
def test_sqlite_fk_policy_and_temporary_tables_are_restored(fk_enabled, fail):
    engine = create_engine("sqlite://")
    metadata = MetaData()
    table = Table("items", metadata, Column("id", String, primary_key=True))
    metadata.create_all(engine)
    generated = iter(["new-first", "new-second"])
    try:
        with engine.begin() as connection:
            connection.execute(table.insert(), [{"id": "first"}, {"id": "second"}])
        with engine.connect() as connection:
            connection.exec_driver_sql(
                "PRAGMA foreign_keys = ON"
                if fk_enabled
                else "PRAGMA foreign_keys = OFF"
            )
            connection.commit()
        if fail:
            with pytest.raises(IntegrityError):
                migrate_id_type(
                    engine, "items", id_generator=lambda: "duplicate", batch_size=1
                )
        else:
            migrate_id_type(
                engine, "items", id_generator=lambda: next(generated), batch_size=1
            )
        with engine.connect() as connection:
            assert (
                bool(connection.exec_driver_sql("PRAGMA foreign_keys").scalar_one())
                == fk_enabled
            )
            assert (
                connection.exec_driver_sql(
                    "SELECT count(*) FROM sqlite_temp_master WHERE name LIKE '_pyutils_id_map_%'"
                ).scalar_one()
                == 0
            )
    finally:
        engine.dispose()


def test_sqlite_unindexed_fk_with_multiple_references_and_unmatched_rows():
    engine = create_engine("sqlite://")
    metadata = MetaData()
    parent = Table("parents", metadata, Column("id", String, primary_key=True))
    child = Table(
        "children", metadata, Column("owner", String, ForeignKey(parent.c.id))
    )
    metadata.create_all(engine)
    ids = iter(["new-first", "new-second"])
    try:
        with engine.begin() as connection:
            connection.execute(parent.insert(), [{"id": "first"}, {"id": "second"}])
            connection.execute(
                child.insert(),
                [
                    {"owner": "first"},
                    {"owner": "first"},
                    {"owner": "second"},
                    {"owner": None},
                ],
            )
        result = migrate_id_type(
            engine, "parents", id_generator=lambda: next(ids), batch_size=10000
        )
        assert result["rows_migrated"] == 2
        assert result["fk_relationships_updated"] == 3
        with engine.connect() as connection:
            assert sorted(
                value
                for value in connection.execute(select(child.c.owner)).scalars()
                if value is not None
            ) == ["new-first", "new-first", "new-second"]
            assert connection.exec_driver_sql("PRAGMA foreign_key_check").all() == []
    finally:
        engine.dispose()
