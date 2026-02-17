import logging

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.logger_functions]
from pyutils_collection.logger_functions.contextual_logger import (
    ContextualLogger,
    LogContext,
    contextual_logger,
)


def test_contextual_logger_creation() -> None:
    """Test case 1: Test creating a contextual logger."""
    logger = contextual_logger("test_logger")
    assert isinstance(logger, ContextualLogger)
    assert logger.logger.name == "test_logger"


def test_contextual_logger_with_context() -> None:
    """Test case 2: Test creating a contextual logger with initial context."""
    context = LogContext(user_id="123", operation="test")
    logger = contextual_logger("test_logger", context)

    # Check that context is stored
    assert logger.context.user_id == "123"
    assert logger.context.operation == "test"


def test_log_context_creation() -> None:
    """Test case 3: Test LogContext creation and methods."""
    context = LogContext(
        context_id="ctx123",
        user_id="user456",
        session_id="sess789",
        component="test_component",
    )

    assert context.context_id == "ctx123"
    assert context.user_id == "user456"
    assert context.session_id == "sess789"
    assert context.component == "test_component"


def test_log_context_to_dict() -> None:
    """Test case 4: Test LogContext to_dict method."""
    context = LogContext(user_id="123", operation="test")
    context_dict = context.to_dict()

    expected = {
        "user_id": "123",
        "operation": "test",
        "metadata": {},
    }
    assert context_dict == expected


def test_log_context_update() -> None:
    """Test case 5: Test LogContext update method."""
    context = LogContext(user_id="123")
    context.update(operation="updated_op", custom_field="custom_value")

    assert context.operation == "updated_op"
    assert context.metadata["custom_field"] == "custom_value"


def test_contextual_logger_logging(caplog: pytest.LogCaptureFixture) -> None:
    """Test case 6: Test basic logging functionality."""
    logger = contextual_logger("test_logger")

    with caplog.at_level(logging.INFO):
        logger.info("Test message")

    assert len(caplog.records) == 1
    assert caplog.records[0].message == "Test message"
    assert caplog.records[0].name == "test_logger"


def test_contextual_logger_with_context_logging(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Test case 7: Test logging with context information."""
    context = LogContext(user_id="123", operation="test_op")
    logger = contextual_logger("test_logger", context)

    with caplog.at_level(logging.INFO):
        logger.info("Context test message")

    assert len(caplog.records) == 1
    record = caplog.records[0]

    # Check that context is included in log record
    assert hasattr(record, "user_id")
    assert record.user_id == "123"
    assert hasattr(record, "operation")
    assert record.operation == "test_op"


def test_contextual_logger_different_levels(caplog: pytest.LogCaptureFixture) -> None:
    """Test case 8: Test logging at different levels."""
    logger = contextual_logger("test_logger")

    with caplog.at_level(logging.DEBUG):
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")

    assert len(caplog.records) == 5
    levels = [record.levelname for record in caplog.records]
    assert levels == ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


def test_contextual_logger_exception_logging(caplog: pytest.LogCaptureFixture) -> None:
    """Test case 9: Test exception logging."""
    logger = contextual_logger("test_logger")

    with caplog.at_level(logging.ERROR):
        try:
            raise ValueError("Test exception")
        except ValueError:
            logger.exception("Exception occurred")

    assert len(caplog.records) == 1
    # Only the message is present, not the exception type
    assert "Exception occurred" in caplog.records[0].message


def test_contextual_logger_extra_fields(caplog: pytest.LogCaptureFixture) -> None:
    """Test case 10: Test logging with extra fields."""
    logger = contextual_logger("test_logger")

    with caplog.at_level(logging.INFO):
        logger.info("Message with extra", extra={"custom_field": "custom_value"})

    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert hasattr(record, "custom_field")
    assert record.custom_field == "custom_value"


def test_contextual_logger_context_scope() -> None:
    """Test case 11: Test context scope management."""
    logger = contextual_logger("test_logger")

    # Initial context should be empty
    initial_context = logger._get_context()
    assert initial_context.user_id == ""

    # Use context scope
    with logger.context_scope(user_id="scoped_user", operation="scoped_op"):
        scoped_context = logger._get_context()
        assert scoped_context.user_id == "scoped_user"
        assert scoped_context.operation == "scoped_op"

    # Context should be restored after scope
    final_context = logger._get_context()
    assert final_context.user_id == ""


def test_contextual_logger_thread_local_context() -> None:
    """Test case 12: Test thread-local context storage."""
    logger = contextual_logger("test_logger")

    # Set thread-local context
    thread_context = LogContext(user_id="thread_user")
    logger._set_context(thread_context)

    # Should return thread-local context
    retrieved_context = logger._get_context()
    assert retrieved_context.user_id == "thread_user"

    # Reset to instance context
    logger._set_context(logger.context)
    retrieved_context = logger._get_context()
    assert retrieved_context.user_id == ""


def test_contextual_logger_multiple_context_updates() -> None:
    """Test case 13: Test multiple context updates."""
    logger = contextual_logger("test_logger")

    # Multiple updates
    with logger.context_scope(user_id="user1"):
        assert logger._get_context().user_id == "user1"

        with logger.context_scope(operation="op1"):
            context = logger._get_context()
            assert context.user_id == "user1"
            assert context.operation == "op1"

        # Should keep user_id but lose operation
        assert logger._get_context().user_id == "user1"
        assert logger._get_context().operation == ""

    # Should be back to original
    assert logger._get_context().user_id == ""


def test_log_context_empty_fields() -> None:
    """Test case 14: Test LogContext with empty fields."""
    context = LogContext()
    context_dict = context.to_dict()

    # Should only include 'metadata' for empty context
    expected_keys = {"metadata"}
    assert set(context_dict.keys()) == expected_keys
    assert context_dict["metadata"] == {}
