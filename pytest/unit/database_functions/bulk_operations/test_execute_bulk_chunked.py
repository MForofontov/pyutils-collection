"""
Unit tests for execute_bulk_chunked function.
"""

import sqlite3

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.database]
from pyutils_collection.database_functions import execute_bulk_chunked


def test_execute_bulk_chunked_successful_insert() -> None:
    """
    Test case 1: Successful bulk insert with real SQLite database.
    """
    # Arrange
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, age INTEGER)"
    )

    data = [
        {"id": 1, "name": "Alice", "age": 30},
        {"id": 2, "name": "Bob", "age": 25},
        {"id": 3, "name": "Charlie", "age": 35},
    ]

    def executor(chunk):
        cursor.executemany(
            "INSERT INTO users (id, name, age) VALUES (:id, :name, :age)", chunk
        )

    # Act
    result = execute_bulk_chunked(conn, executor, data, chunk_size=2)
    conn.commit()

    # Assert
    assert result["successful"] == 3
    assert result["failed"] == 0
    assert result["total"] == 3
    assert len(result["errors"]) == 0

    rows = cursor.execute("SELECT * FROM users ORDER BY id").fetchall()
    assert len(rows) == 3
    assert rows[0] == (1, "Alice", 30)

    conn.close()


def test_execute_bulk_chunked_with_updates() -> None:
    """
    Test case 2: Successful bulk update operation.
    """
    # Arrange
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT, score INTEGER)"
    )
    cursor.executemany(
        "INSERT INTO users VALUES (?, ?, ?)",
        [(1, "Alice", 100), (2, "Bob", 200), (3, "Charlie", 300)],
    )
    conn.commit()

    update_data = [
        {"id": 1, "score": 150},
        {"id": 2, "score": 250},
        {"id": 3, "score": 350},
    ]

    def executor(chunk):
        for row in chunk:
            cursor.execute("UPDATE users SET score = :score WHERE id = :id", row)

    # Act
    result = execute_bulk_chunked(conn, executor, update_data, chunk_size=2)
    conn.commit()

    # Assert
    assert result["successful"] == 3
    assert result["failed"] == 0

    rows = cursor.execute("SELECT score FROM users ORDER BY id").fetchall()
    assert rows == [(150,), (250,), (350,)]

    conn.close()


def test_execute_bulk_chunked_skip_mode() -> None:
    """
    Test case 3: Skip mode skips failed chunks and continues.
    """
    # Arrange
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
    cursor.execute("INSERT INTO users VALUES (2, 'Existing')")
    conn.commit()

    data = [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},  # Will fail - duplicate key
        {"id": 3, "name": "Charlie"},
        {"id": 4, "name": "David"},
    ]

    def executor(chunk):
        cursor.executemany("INSERT INTO users (id, name) VALUES (:id, :name)", chunk)

    # Act
    result = execute_bulk_chunked(
        conn,
        executor,
        data,
        chunk_size=2,
        on_error="skip",
        commit_func=lambda: conn.commit(),
        rollback_func=lambda: conn.rollback(),
    )

    # Assert
    assert result["failed"] == 2  # First chunk with id=1,2 failed
    assert result["successful"] == 2  # Second chunk with id=3,4 succeeded

    rows = cursor.execute("SELECT id FROM users ORDER BY id").fetchall()
    assert rows == [(2,), (3,), (4,)]

    conn.close()


def test_execute_bulk_chunked_continue_mode() -> None:
    """
    Test case 4: Continue mode processes rows individually on chunk failure.
    """
    # Arrange
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
    cursor.execute("INSERT INTO users VALUES (2, 'Existing')")
    conn.commit()

    data = [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},  # Will fail - duplicate key
        {"id": 3, "name": "Charlie"},
    ]

    def executor(chunk):
        cursor.executemany("INSERT INTO users (id, name) VALUES (:id, :name)", chunk)

    # Act
    result = execute_bulk_chunked(
        conn,
        executor,
        data,
        chunk_size=10,
        on_error="continue",
        commit_func=lambda: conn.commit(),
        rollback_func=lambda: conn.rollback(),
    )

    # Assert
    assert result["successful"] == 2  # Alice and Charlie
    assert result["failed"] == 1  # Bob
    assert len(result["errors"]) == 1

    rows = cursor.execute("SELECT id FROM users ORDER BY id").fetchall()
    assert rows == [(1,), (2,), (3,)]

    conn.close()


def test_execute_bulk_chunked_with_progress_callback() -> None:
    """
    Test case 5: Progress callback receives correct counts.
    """
    # Arrange
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")

    data = [{"id": i, "name": f"User{i}"} for i in range(1, 11)]

    progress_calls = []

    def progress_callback(completed, total):
        progress_calls.append((completed, total))

    def executor(chunk):
        cursor.executemany("INSERT INTO users (id, name) VALUES (:id, :name)", chunk)

    # Act
    result = execute_bulk_chunked(
        conn, executor, data, chunk_size=3, progress_callback=progress_callback
    )
    conn.commit()

    # Assert
    assert result["successful"] == 10
    assert len(progress_calls) == 4
    assert progress_calls[-1] == (10, 10)

    conn.close()


def test_execute_bulk_chunked_empty_data() -> None:
    """
    Test case 6: Empty data list returns zero results.
    """
    # Arrange
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE users (id INTEGER, name TEXT)")

    def executor(chunk):
        cursor.executemany("INSERT INTO users VALUES (:id, :name)", chunk)

    # Act
    result = execute_bulk_chunked(conn, executor, [], chunk_size=100)

    # Assert
    assert result["successful"] == 0
    assert result["failed"] == 0
    assert result["total"] == 0

    conn.close()


def test_execute_bulk_chunked_single_row() -> None:
    """
    Test case 7: Single row is processed correctly.
    """
    # Arrange
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE users (id INTEGER, name TEXT)")

    data = [{"id": 1, "name": "Alice"}]

    def executor(chunk):
        cursor.executemany("INSERT INTO users VALUES (:id, :name)", chunk)

    # Act
    result = execute_bulk_chunked(conn, executor, data, chunk_size=100)
    conn.commit()

    # Assert
    assert result["successful"] == 1
    assert result["failed"] == 0

    rows = cursor.execute("SELECT * FROM users").fetchall()
    assert len(rows) == 1

    conn.close()


def test_execute_bulk_chunked_large_chunk_size() -> None:
    """
    Test case 8: Chunk size larger than data processes all in one chunk.
    """
    # Arrange
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE users (id INTEGER, name TEXT)")

    data = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]

    def executor(chunk):
        cursor.executemany("INSERT INTO users VALUES (:id, :name)", chunk)

    # Act
    result = execute_bulk_chunked(conn, executor, data, chunk_size=1000)
    conn.commit()

    # Assert
    assert result["successful"] == 2
    assert result["failed"] == 0

    conn.close()


def test_execute_bulk_chunked_fail_fast_raises() -> None:
    """
    Test case 9: Fail-fast mode raises on first error.
    """
    # Arrange
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)")
    cursor.execute("INSERT INTO users VALUES (2, 'Existing')")
    conn.commit()

    data = [
        {"id": 1, "name": "Alice"},
        {"id": 2, "name": "Bob"},
        {"id": 3, "name": "Charlie"},
    ]

    def executor(chunk):
        cursor.executemany("INSERT INTO users VALUES (:id, :name)", chunk)

    # Act & Assert
    with pytest.raises(sqlite3.IntegrityError):
        execute_bulk_chunked(conn, executor, data, chunk_size=10, on_error="fail_fast")

    conn.close()


def test_execute_bulk_chunked_invalid_chunk_size() -> None:
    """
    Test case 10: Invalid chunk_size raises ValueError.
    """
    # Arrange
    conn = sqlite3.connect(":memory:")

    def executor(chunk):
        pass

    # Act & Assert
    with pytest.raises(ValueError):
        execute_bulk_chunked(conn, executor, [], chunk_size=0)

    with pytest.raises(ValueError):
        execute_bulk_chunked(conn, executor, [], chunk_size=-1)

    conn.close()


def test_execute_bulk_chunked_none_connection() -> None:
    """
    Test case 11: None connection raises TypeError.
    """

    # Arrange
    def executor(chunk):
        pass

    # Act & Assert
    with pytest.raises(TypeError):
        execute_bulk_chunked(None, executor, [])


def test_execute_bulk_chunked_invalid_executor() -> None:
    """
    Test case 12: Non-callable executor raises TypeError.
    """
    # Arrange
    conn = sqlite3.connect(":memory:")

    # Act & Assert
    with pytest.raises(TypeError):
        execute_bulk_chunked(conn, "not_callable", [])

    conn.close()


def test_execute_bulk_chunked_invalid_data_type() -> None:
    """
    Test case 13: Invalid data type raises TypeError.
    """
    # Arrange
    conn = sqlite3.connect(":memory:")

    def executor(chunk):
        pass

    # Act & Assert
    with pytest.raises(TypeError, match="data must be a Sequence"):
        execute_bulk_chunked(conn, executor, 12345)  # int is not a Sequence

    conn.close()


def test_execute_bulk_chunked_invalid_on_error() -> None:
    """
    Test case 14: Invalid on_error value raises ValueError.
    """
    # Arrange
    conn = sqlite3.connect(":memory:")

    def executor(chunk):
        pass

    # Act & Assert
    with pytest.raises(ValueError):
        execute_bulk_chunked(conn, executor, [], on_error="invalid")

    conn.close()


def test_execute_bulk_chunked_commit_failure_in_skip_mode() -> None:
    """
    Test case 15: Tests commit failure handling in skip mode.
    """
    # Arrange
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, value TEXT)")

    commit_called = []

    def failing_commit():
        commit_called.append(True)
        raise RuntimeError("Commit failed")

    def executor(chunk):
        for row in chunk:
            cursor.execute("INSERT INTO test VALUES (?, ?)", (row["id"], row["value"]))

    data = [{"id": 1, "value": "a"}, {"id": 2, "value": "b"}]

    # Act - in skip mode, commit errors cause the chunk to be skipped
    result = execute_bulk_chunked(
        conn, executor, data, chunk_size=2, on_error="skip", commit_func=failing_commit
    )

    # Assert - rows counted as both successful (executed) and failed (commit failed)
    assert len(commit_called) == 1
    assert result["successful"] == 0  # A failed commit is not a successful chunk
    assert result["failed"] == 2  # Commit failed, chunk skipped
    assert len(result["errors"]) == 1
    assert "Commit failed" in result["errors"][0]["error"]

    conn.close()


def test_execute_bulk_chunked_progress_callback_exception() -> None:
    """
    Test case 16: Tests that progress callback exceptions are caught and logged.
    """
    # Arrange
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")

    def executor(chunk):
        for row in chunk:
            cursor.execute("INSERT INTO test VALUES (?)", (row["id"],))

    def failing_callback(completed, total):
        raise RuntimeError("Callback error")

    data = [{"id": 1}, {"id": 2}]

    # Act - should complete despite callback failures
    result = execute_bulk_chunked(
        conn, executor, data, chunk_size=1, progress_callback=failing_callback
    )

    # Assert - operation should succeed
    assert result["successful"] == 2
    assert result["failed"] == 0

    conn.close()


def test_execute_bulk_chunked_continue_mode_commit_error() -> None:
    """
    Test case 17: Tests that commit errors in continue mode cause individual row retry which may fail.
    """
    # Arrange
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")

    commit_count = [0]

    def always_failing_commit():
        commit_count[0] += 1
        raise RuntimeError("Commit failed")

    def executor(chunk):
        for row in chunk:
            cursor.execute("INSERT INTO test VALUES (?)", (row["id"],))

    data = [{"id": 1}, {"id": 2}, {"id": 3}]

    # Act - in continue mode, when chunk commit fails, it retries individual rows
    # But those rows fail because data was already inserted (UNIQUE constraint)
    result = execute_bulk_chunked(
        conn,
        executor,
        data,
        chunk_size=10,
        on_error="continue",
        commit_func=always_failing_commit,
    )

    # Assert - commit failed, and individual rows failed on re-execution
    assert (
        commit_count[0] == 1
    )  # Only chunk commit attempted (row execution failed before commit)
    assert result["successful"] == 0  # The initial chunk was never committed
    assert result["failed"] == 3  # All 3 rows failed on individual retry
    assert len(result["errors"]) == 3  # 3 errors from individual row retries
    # Errors are IntegrityError, not commit errors, because re-execution failed
    assert all("UNIQUE constraint" in error["error"] for error in result["errors"])

    conn.close()


def test_execute_bulk_chunked_rollback_failure_in_fail_fast() -> None:
    """
    Test case 18: Tests rollback failure doesn't suppress original error in fail_fast mode.
    """
    # Arrange
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, value TEXT)")

    def failing_rollback():
        raise RuntimeError("Rollback failed")

    def failing_executor(chunk):
        raise ValueError("Executor error")

    data = [{"id": 1, "value": "a"}]

    # Act & Assert - original error should be raised, rollback logged
    with pytest.raises(ValueError, match="Executor error"):
        execute_bulk_chunked(
            conn,
            failing_executor,
            data,
            on_error="fail_fast",
            rollback_func=failing_rollback,
        )

    conn.close()


def test_execute_bulk_chunked_skip_mode_rollback_failure() -> None:
    """
    Test case 19: Tests that rollback failure in skip mode is logged but doesn't stop processing.
    """
    # Arrange
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
    cursor.execute("INSERT INTO test VALUES (2)")  # Create duplicate

    def failing_rollback():
        raise RuntimeError("Rollback failed")

    def executor(chunk):
        for row in chunk:
            cursor.execute("INSERT INTO test VALUES (?)", (row["id"],))

    # Make chunk 2 fail due to duplicate key
    data = [{"id": 1}, {"id": 2}, {"id": 3}]

    # Act - should continue despite rollback failure
    result = execute_bulk_chunked(
        conn,
        executor,
        data,
        chunk_size=1,
        on_error="skip",
        rollback_func=failing_rollback,
    )

    # Assert
    assert result["successful"] == 2  # Rows 1 and 3
    assert result["failed"] == 1  # Row 2

    conn.close()


def test_execute_bulk_chunked_continue_mode_with_rollback_per_row() -> None:
    """
    Test case 20: Tests rollback is called for failed chunk and failed row in continue mode.
    """
    # Arrange
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")
    cursor.execute("INSERT INTO test VALUES (2)")  # Create duplicate key
    conn.commit()

    rollback_count = [0]

    def counting_rollback():
        rollback_count[0] += 1
        conn.rollback()  # Actually rollback

    def executor(chunk):
        for row in chunk:
            cursor.execute("INSERT INTO test VALUES (?)", (row["id"],))

    data = [{"id": 1}, {"id": 2}, {"id": 3}]  # id=2 will fail

    # Act
    result = execute_bulk_chunked(
        conn,
        executor,
        data,
        chunk_size=10,
        on_error="continue",
        rollback_func=counting_rollback,
    )

    # Assert - in continue mode, chunk fails first (rollback called), then individual rows are tried
    # Row 1 succeeds, row 2 fails (rollback called), row 3 succeeds = 2 successful
    assert result["successful"] == 2
    assert result["failed"] == 1
    assert rollback_count[0] >= 2  # Rollback for chunk failure + row failure

    conn.close()


def test_execute_bulk_chunked_invalid_commit_func() -> None:
    """
    Test case 21: Tests invalid commit_func type raises TypeError.
    """
    # Arrange
    conn = sqlite3.connect(":memory:")

    # Act & Assert
    with pytest.raises(TypeError, match="commit_func must be callable or None"):
        execute_bulk_chunked(conn, lambda chunk: None, [], commit_func="not_callable")

    conn.close()


def test_execute_bulk_chunked_invalid_rollback_func() -> None:
    """
    Test case 22: Tests invalid rollback_func type raises TypeError.
    """
    # Arrange
    conn = sqlite3.connect(":memory:")

    # Act & Assert
    with pytest.raises(TypeError, match="rollback_func must be callable or None"):
        execute_bulk_chunked(conn, lambda chunk: None, [], rollback_func=123)

    conn.close()


def test_execute_bulk_chunked_invalid_progress_callback() -> None:
    """
    Test case 23: Tests invalid progress_callback type raises TypeError.
    """
    # Arrange
    conn = sqlite3.connect(":memory:")

    # Act & Assert
    with pytest.raises(TypeError, match="progress_callback must be callable or None"):
        execute_bulk_chunked(conn, lambda chunk: None, [], progress_callback=[1, 2, 3])

    conn.close()


def test_execute_bulk_chunked_continue_mode_individual_row_commit_failure() -> None:
    """
    Test case 24: Tests continue mode where individual row commits fail after successful execution.
    """
    # Arrange
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE test (id INTEGER PRIMARY KEY)")

    # Make first chunk fail to trigger continue mode
    execution_count = [0]

    def executor_that_fails_first(chunk):
        execution_count[0] += 1
        if execution_count[0] == 1 and len(chunk) > 1:
            # First chunk execution fails
            raise RuntimeError("Chunk execution failed")
        # Individual rows succeed
        for row in chunk:
            cursor.execute("INSERT INTO test VALUES (?)", (row["id"],))

    commit_count = [0]

    def commit_that_fails_on_second():
        commit_count[0] += 1
        if commit_count[0] == 2:  # Second commit (first individual row)
            raise RuntimeError("Row commit failed")

    data = [{"id": 1}, {"id": 2}, {"id": 3}]

    # Act
    result = execute_bulk_chunked(
        conn,
        executor_that_fails_first,
        data,
        chunk_size=10,
        on_error="continue",
        commit_func=commit_that_fails_on_second,
    )

    # Assert - chunk failed, then individual rows processed
    # Row 1 succeeds, row 2 commit fails, row 3 succeeds
    assert result["successful"] >= 1
    assert result["failed"] >= 1

    conn.close()


def test_execute_bulk_chunked_fail_fast_with_successful_rollback() -> None:
    """
    Test case 25: Tests fail_fast mode with successful rollback before re-raising.
    """
    # Arrange
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE test (id INTEGER)")

    rollback_called = [False]

    def rollback_func():
        rollback_called[0] = True
        conn.rollback()

    def failing_executor(chunk):
        raise ValueError("Execution failed")

    data = [{"id": 1}]

    # Act & Assert
    with pytest.raises(ValueError, match="Execution failed"):
        execute_bulk_chunked(
            conn,
            failing_executor,
            data,
            on_error="fail_fast",
            rollback_func=rollback_func,
        )

    assert rollback_called[0] is True
    conn.close()
