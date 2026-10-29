"""Nested work must never commit or roll back its outer transaction."""

import sqlite3

import pytest
from sqlalchemy import create_engine, text

from pyutils_collection.database_functions import nested_transaction, savepoint_context

pytestmark = [pytest.mark.unit, pytest.mark.database]


@pytest.mark.parametrize("fail", [False, True])
def test_sqlalchemy_savepoint_preserves_outer_transaction(fail):
    engine = create_engine("sqlite://")
    try:
        with engine.connect() as connection:
            connection.execute(text("CREATE TABLE items (id INTEGER)"))
            connection.commit()
            outer = connection.begin()
            connection.execute(text("INSERT INTO items VALUES (1)"))
            try:
                with nested_transaction(connection):
                    connection.execute(text("INSERT INTO items VALUES (2)"))
                    if fail:
                        raise ValueError("rollback nested work")
            except ValueError:
                pass
            assert outer.is_active
            assert not connection.in_nested_transaction()
            assert connection.execute(
                text("SELECT id FROM items ORDER BY id")
            ).all() == ([(1,)] if fail else [(1,), (2,)])
            outer.rollback()
            assert connection.execute(text("SELECT id FROM items")).all() == []
    finally:
        engine.dispose()


@pytest.mark.parametrize("manager", [nested_transaction, savepoint_context])
@pytest.mark.parametrize("name", ["sp; DROP TABLE items", "sp\n", "sp name", "sp--"])
def test_savepoint_names_are_validated_before_sql(manager, name):
    connection = sqlite3.connect(":memory:")
    try:
        with pytest.raises(ValueError, match="savepoint_name"):
            with manager(connection, savepoint_name=name):
                pytest.fail("invalid savepoint entered")
    finally:
        connection.close()
