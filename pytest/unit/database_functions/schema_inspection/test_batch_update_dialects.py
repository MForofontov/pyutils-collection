"""Non-SQLite migration updates must keep values bound and identifiers quoted."""

from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from sqlalchemy.dialects import mysql, postgresql

from pyutils_collection.database_functions.schema_inspection.migrate_id_type import (
    _execute_batch_update,
)

pytestmark = [pytest.mark.unit, pytest.mark.database]


@pytest.mark.parametrize("dialect", [mysql.dialect(), postgresql.dialect()])
@pytest.mark.parametrize("rowcount", [2, None])
def test_case_update_keeps_caller_values_out_of_sql(dialect, rowcount):
    connection = Mock()
    connection.dialect = dialect
    connection.execute.return_value = SimpleNamespace(rowcount=rowcount)
    old_id = "old' OR 1=1 --"
    new_id = "new'; DROP TABLE items; --"
    result = _execute_batch_update(
        connection, "table-name", "column-name", [(new_id, old_id), ("new2", "old2")]
    )
    assert result == (rowcount or 0)
    statement, parameters = connection.execute.call_args.args
    query = str(statement)
    assert old_id not in query and new_id not in query
    assert dialect.identifier_preparer.quote("table-name") in query
    assert dialect.identifier_preparer.quote("column-name") in query
    assert parameters == {
        "old_0": old_id,
        "new_0": new_id,
        "old_1": "old2",
        "new_1": "new2",
    }
    connection.exec_driver_sql.assert_not_called()
