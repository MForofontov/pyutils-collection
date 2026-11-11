"""Health queries must support SQLAlchemy and release failed connections."""

import sqlite3

from sqlalchemy import create_engine

import pytest
from pyutils_collection.database_functions import managed_db_connection

pytestmark = [pytest.mark.unit, pytest.mark.database]


def test_sqlalchemy_connection_accepts_default_health_query():
    engine = create_engine("sqlite://")
    opened = []

    def connect():
        connection = engine.connect()
        opened.append(connection)
        return connection

    try:
        with managed_db_connection(connect, max_retries=1) as connection:
            assert connection.exec_driver_sql("SELECT 2").scalar_one() == 2
        assert opened[0].closed
    finally:
        for connection in opened:
            connection.close()
        engine.dispose()


def test_invalid_health_query_closes_every_retry_connection():
    opened = []

    def connect():
        connection = sqlite3.connect(":memory:")
        opened.append(connection)
        return connection

    try:
        with pytest.raises(RuntimeError, match="no such column"):
            with managed_db_connection(
                connect,
                max_retries=2,
                retry_delay=0.001,
                health_check_query="SELECT missing_column",
            ):
                pytest.fail("invalid health query must not yield")
        for connection in opened:
            with pytest.raises(sqlite3.ProgrammingError, match="closed"):
                connection.execute("SELECT 1")
    finally:
        for connection in opened:
            connection.close()
