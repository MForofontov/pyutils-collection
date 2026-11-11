import sqlite3

import pytest

from pyutils_collection.database_functions.transaction_management.nested_transaction import (
    nested_transaction,
)

pytestmark = [pytest.mark.unit, pytest.mark.database]


def test_nested_transaction_sql_fallback_preserves_outer_transaction() -> None:
    """Inner failure rolls back only to savepoint when using SQL fallback."""
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE items (id INTEGER)")
    cursor.execute("BEGIN")
    cursor.execute("INSERT INTO items VALUES (1)")

    try:
        with nested_transaction(cursor, savepoint_name="inner_sp"):
            cursor.execute("INSERT INTO items VALUES (2)")
            raise ValueError("inner failure")
    except ValueError:
        pass

    cursor.execute("INSERT INTO items VALUES (3)")
    conn.commit()

    result = cursor.execute("SELECT id FROM items ORDER BY id").fetchall()
    assert result == [(1,), (3,)]
    conn.close()
