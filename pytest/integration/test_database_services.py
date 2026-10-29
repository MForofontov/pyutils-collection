"""Real PostgreSQL/MySQL checks; only disposable loopback audit databases."""

import os
import uuid

from sqlalchemy import (
    Column,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
    select,
    text,
)
from sqlalchemy.engine import make_url

import pytest
from pyutils_collection.database_functions import (
    atomic_transaction,
    managed_db_connection,
    nested_transaction,
    stream_query_results,
)

pytestmark = [pytest.mark.integration, pytest.mark.database]


@pytest.fixture(params=["postgres", "mysql"])
def database(request):
    address = os.environ.get(f"PYUTILS_{request.param.upper()}_URL")
    if os.environ.get("PYUTILS_SERVICE_TESTS") != "1" or not address:
        pytest.skip(
            "run scripts/run_service_integration.py to start disposable databases"
        )
    url = make_url(address)
    assert url.host == "127.0.0.1" and url.database == "pyutils_audit"
    engine = create_engine(url)
    metadata = MetaData()
    table = Table(
        "audit_" + uuid.uuid4().hex,
        metadata,
        Column("id", Integer, primary_key=True),
        Column("label", String(80)),
    )
    try:
        metadata.create_all(engine)
        yield engine, table
    finally:
        metadata.drop_all(engine)
        engine.dispose()


def test_managed_connection_health_and_closure(database):
    engine, _ = database
    with managed_db_connection(engine.connect, max_retries=1) as connection:
        assert connection.execute(text("SELECT 2")).scalar_one() == 2
    assert connection.closed
    assert engine.pool.checkedout() == 0


def test_failed_health_checks_return_connections(database):
    engine, _ = database
    opened = []

    def connect():
        connection = engine.connect()
        opened.append(connection)
        return connection

    with pytest.raises(RuntimeError, match="Failed to establish"):
        with managed_db_connection(
            connect,
            max_retries=2,
            retry_delay=0.01,
            health_check_query="SELECT missing_pyutils_audit_column",
        ):
            pytest.fail("an invalid health query must fail before yielding")
    try:
        assert len(opened) == 2
        assert all(connection.closed for connection in opened)
        assert engine.pool.checkedout() == 0
    finally:
        for connection in opened:
            connection.close()


def test_atomic_and_nested_transaction_ownership(database):
    engine, table = database
    with engine.connect() as connection:
        with atomic_transaction(connection):
            connection.execute(table.insert().values(id=1, label="committed"))
        with pytest.raises(ValueError, match="rollback"):
            with atomic_transaction(connection):
                connection.execute(table.insert().values(id=2, label="rolled back"))
                raise ValueError("rollback")
        with connection.begin():
            with nested_transaction(connection):
                connection.execute(table.insert().values(id=3, label="outer rollback"))
            assert connection.in_transaction()
            connection.rollback()
    with engine.connect() as connection:
        assert connection.execute(select(table.c.id)).scalars().all() == [1]


def test_streaming_closes_result_after_early_exit(database):
    engine, table = database
    with engine.begin() as connection:
        connection.execute(
            table.insert(), [{"id": value, "label": str(value)} for value in range(1, 6)]
        )
    with engine.connect() as connection:
        result = connection.execute(select(table.c.id).order_by(table.c.id))
        stream = stream_query_results(lambda: result, fetch_size=1)
        assert next(stream)[0] == 1
        stream.close()
        assert result.closed
        assert connection.execute(text("SELECT 1")).scalar_one() == 1
