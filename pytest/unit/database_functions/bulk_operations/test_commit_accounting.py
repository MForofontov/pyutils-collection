import sqlite3
from collections.abc import Sequence
from typing import Any, Literal

import pytest

from pyutils_collection.database_functions import execute_bulk_chunked

pytestmark = [pytest.mark.unit, pytest.mark.database]


@pytest.mark.parametrize("mode", ["skip", "continue"])
def test_failed_chunk_commit_is_not_counted_as_success(
    mode: Literal["skip", "continue"],
) -> None:
    conn = sqlite3.connect(":memory:")
    try:
        conn.execute("CREATE TABLE entries (id INTEGER)")
        commits = 0
        progress: list[tuple[int, int]] = []

        def execute(rows: Sequence[dict[str, Any]]) -> None:
            conn.executemany("INSERT INTO entries VALUES (:id)", rows)

        def commit() -> None:
            nonlocal commits
            commits += 1
            if commits == 1:
                raise RuntimeError("commit failed")
            conn.commit()

        result = execute_bulk_chunked(
            conn, execute, [{"id": 1}, {"id": 2}], on_error=mode,
            commit_func=commit, rollback_func=conn.rollback,
            progress_callback=lambda done, total: progress.append((done, total)),
        )
        assert result["successful"] == (0 if mode == "skip" else 2)
        assert result["failed"] == (2 if mode == "skip" else 0)
        assert result["successful"] + result["failed"] == result["total"] == 2
        assert progress == [(2, 2)]
        assert conn.execute("SELECT id FROM entries").fetchall() == (
            [] if mode == "skip" else [(1,), (2,)]
        )
    finally:
        conn.close()


def test_failed_row_commit_rolls_back_before_next_row() -> None:
    conn = sqlite3.connect(":memory:")
    try:
        conn.execute("CREATE TABLE entries (id INTEGER)")
        executions = 0
        commits = 0

        def execute(rows: Sequence[dict[str, Any]]) -> None:
            nonlocal executions
            executions += 1
            if executions == 1:
                raise RuntimeError("retry individually")
            conn.executemany("INSERT INTO entries VALUES (:id)", rows)

        def commit() -> None:
            nonlocal commits
            commits += 1
            if commits == 1:
                raise RuntimeError("row commit failed")
            conn.commit()

        result = execute_bulk_chunked(
            conn, execute, [{"id": 1}, {"id": 2}], on_error="continue",
            commit_func=commit, rollback_func=conn.rollback,
        )
        assert result["successful"] == result["failed"] == 1
        assert conn.execute("SELECT id FROM entries").fetchall() == [(2,)]
        assert result["errors"][0]["error_type"] == "CommitError"
    finally:
        conn.close()
