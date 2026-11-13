"""Foreign-key audits must match complete parent keys without NULL poisoning."""

import pytest
from sqlalchemy import create_engine

from pyutils_collection.database_functions.schema_inspection import verify_referential_integrity

pytestmark = [pytest.mark.unit, pytest.mark.database]


@pytest.mark.parametrize("self_reference", [False, True])
def test_complete_composite_key_matching(self_reference: bool) -> None:
    engine = create_engine("sqlite://")
    try:
        with engine.connect() as connection:
            if self_reference:
                connection.exec_driver_sql(
                    "CREATE TABLE child (a INTEGER, b INTEGER, x INTEGER, y INTEGER, "
                    "UNIQUE (a, b), FOREIGN KEY (x, y) REFERENCES child(a, b))"
                )
                connection.exec_driver_sql(
                    "INSERT INTO child VALUES (1, 1, NULL, NULL), "
                    "(2, 2, 1, 1), (3, 3, 1, 9), (4, 4, 1, NULL)"
                )
            else:
                connection.exec_driver_sql("CREATE TABLE parent (a INTEGER, b INTEGER, UNIQUE (a, b))")
                connection.exec_driver_sql("INSERT INTO parent VALUES (1, 1), (2, NULL)")
                connection.exec_driver_sql(
                    "CREATE TABLE child (x INTEGER, y INTEGER, "
                    "FOREIGN KEY (x, y) REFERENCES parent(a, b))"
                )
                connection.exec_driver_sql("INSERT INTO child VALUES (1, 1), (1, 9), (1, NULL), (NULL, 9)")
            violations = verify_referential_integrity(connection)
            assert len(violations) == 1
            assert violations[0]["column"] == "x"
            assert violations[0]["referenced_column"] == "a"
            assert violations[0]["orphaned_count"] == 1
            assert violations[0]["sample_ids"] == [1]
    finally:
        engine.dispose()


def test_nullable_parent_key_does_not_hide_orphans() -> None:
    engine = create_engine("sqlite://")
    try:
        with engine.connect() as connection:
            connection.exec_driver_sql("CREATE TABLE parent (key INTEGER UNIQUE)")
            connection.exec_driver_sql("INSERT INTO parent VALUES (1), (NULL)")
            connection.exec_driver_sql("CREATE TABLE child (key INTEGER REFERENCES parent(key))")
            connection.exec_driver_sql("INSERT INTO child VALUES (1), (9), (9), (NULL)")
            [violation] = verify_referential_integrity(connection)
            assert violation["orphaned_count"] == 2
            assert violation["sample_ids"] == [9]
    finally:
        engine.dispose()
