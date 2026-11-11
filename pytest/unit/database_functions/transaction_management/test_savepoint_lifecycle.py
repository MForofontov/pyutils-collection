"""Savepoint contexts release only their own successfully created savepoint."""

import asyncio
import sqlite3
from contextlib import closing
from unittest.mock import Mock

import pytest
from pyutils_collection.database_functions import savepoint_context

pytestmark = [pytest.mark.unit, pytest.mark.database]


@pytest.mark.parametrize("on_error", ["rollback", "ignore"])
def test_error_exit_releases_savepoint_and_preserves_outer_work(on_error):
    with closing(sqlite3.connect(":memory:")) as connection:
        connection.execute("CREATE TABLE items (id INTEGER)")
        connection.execute("INSERT INTO items VALUES (1)")
        try:
            with savepoint_context(connection, "owned", on_error=on_error):
                connection.execute("INSERT INTO items VALUES (2)")
                raise ValueError("body failed")
        except ValueError:
            assert on_error == "rollback"
        expected = [(1,)] if on_error == "rollback" else [(1,), (2,)]
        assert (
            connection.execute("SELECT id FROM items ORDER BY id").fetchall()
            == expected
        )
        assert connection.in_transaction
        with pytest.raises(sqlite3.OperationalError, match="no such savepoint"):
            connection.execute("RELEASE SAVEPOINT owned")
        connection.rollback()
        assert connection.execute("SELECT id FROM items").fetchall() == []


@pytest.mark.parametrize("on_error", ["rollback", "ignore"])
def test_creation_failure_is_not_suppressed_or_cleaned_up(on_error):
    create = Mock(side_effect=RuntimeError("create failed"))
    rollback, release = Mock(), Mock()
    with pytest.raises(RuntimeError, match="create failed"):
        with savepoint_context(
            object(),
            "owned",
            on_error=on_error,
            create_savepoint_func=create,
            rollback_savepoint_func=rollback,
            release_savepoint_func=release,
        ):
            pytest.fail("body cannot run without a savepoint")
    rollback.assert_not_called()
    release.assert_not_called()


def test_successful_body_release_failure_is_not_ignored():
    release = Mock(side_effect=RuntimeError("release failed"))
    with pytest.raises(RuntimeError, match="release failed"):
        with savepoint_context(
            object(),
            "owned",
            on_error="ignore",
            create_savepoint_func=Mock(),
            release_savepoint_func=release,
        ):
            pass


def test_rollback_failure_preserves_original_error_without_releasing(caplog):
    release = Mock()
    with pytest.raises(ValueError, match="body failed"):
        with savepoint_context(
            object(),
            "owned",
            create_savepoint_func=Mock(),
            rollback_savepoint_func=Mock(side_effect=RuntimeError("rollback failed")),
            release_savepoint_func=release,
        ):
            raise ValueError("body failed")
    release.assert_not_called()
    assert "rollback failed" in caplog.text


def test_release_failure_after_rollback_preserves_original_error(caplog):
    with pytest.raises(ValueError, match="body failed"):
        with savepoint_context(
            object(),
            "owned",
            create_savepoint_func=Mock(),
            rollback_savepoint_func=Mock(),
            release_savepoint_func=Mock(side_effect=RuntimeError("release failed")),
        ):
            raise ValueError("body failed")
    assert "release failed" in caplog.text


@pytest.mark.parametrize("on_error", ["rollback", "ignore"])
@pytest.mark.parametrize(
    "error_type", [KeyboardInterrupt, SystemExit, asyncio.CancelledError]
)
def test_base_exception_always_rolls_back_and_releases(on_error, error_type):
    calls = []
    with pytest.raises(error_type):
        with savepoint_context(
            object(),
            "owned",
            on_error=on_error,
            create_savepoint_func=lambda _: calls.append("create"),
            rollback_savepoint_func=lambda _: calls.append("rollback"),
            release_savepoint_func=lambda _: calls.append("release"),
        ):
            raise error_type()
    assert calls == ["create", "rollback", "release"]
