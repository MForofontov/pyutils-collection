import pytest

pytestmark = [pytest.mark.unit, pytest.mark.logger_functions]
import logging
from datetime import datetime

from pyutils_collection.logger_functions.structured_formatter import structured_formatter


def test_structured_formatter_basic() -> None:

    """Test case 1: Test basic structured formatter functionality."""
    formatter = structured_formatter()
    assert isinstance(formatter, logging.Formatter)

    # Create a test log record
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test.py",
        lineno=10,
        msg="Test message",
        args=(),
        exc_info=None,
    )

    # Format the record
    result = formatter.format(record)

    # Should contain structured format with separators
    assert " | " in result
    assert "INFO" in result
    assert "Test message" in result
    assert "test" in result  # module name


def test_structured_formatter_timestamp() -> None:

    """Test case 2: Test that structured formatter includes timestamp."""
    formatter = structured_formatter()

    record = logging.LogRecord(
        name="test_logger",
        level=logging.DEBUG,
        pathname="test.py",
        lineno=5,
        msg="Debug message",
        args=(),
        exc_info=None,
    )

    result = formatter.format(record)

    # Should start with timestamp in YYYY-MM-DD HH:MM:SS format
    parts = result.split(" | ")
    timestamp_str = parts[0]

    # Should be able to parse as datetime
    datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")


def test_structured_formatter_level_alignment() -> None:

    """Test case 3: Test level name alignment."""
    formatter = structured_formatter(max_level_width=10)

    record = logging.LogRecord(
        name="test_logger",
        level=logging.WARNING,
        pathname="test.py",
        lineno=15,
        msg="Warning message",
        args=(),
        exc_info=None,
    )

    result = formatter.format(record)

    parts = result.split(" | ")
    level_part = parts[1]

    # Should be padded to max_level_width
    assert len(level_part) == 10
    assert level_part.strip() == "WARNING"


def test_structured_formatter_module_alignment() -> None:

    """Test case 4: Module name alignment."""
    formatter = structured_formatter(max_module_width=12)

    record = logging.LogRecord(
        name="test_logger",
        level=logging.ERROR,
        pathname="test.py",
        lineno=20,
        msg="Error message",
        args=(),
        exc_info=None,
    )

    result = formatter.format(record)

    parts = result.split(" | ")
    module_part = parts[2]

    # Should be padded to max_module_width
    assert len(module_part) == 12
    assert module_part.strip() == "test"


def test_structured_formatter_location() -> None:

    """Test case 5: Function and line number formatting."""
    formatter = structured_formatter()

    record = logging.LogRecord(
        name="test_logger",
        level=logging.CRITICAL,
        pathname="test.py",
        lineno=25,
        msg="Critical message",
        args=(),
        exc_info=None,
    )
    record.funcName = "test_function"

    result = formatter.format(record)

    parts = result.split(" | ")
    location_part = parts[3]

    # Should contain function name and line number
    assert "test_function:25" in location_part


def test_structured_formatter_long_module_name() -> None:
    """Test case 6: Handling of long module names."""
    formatter = structured_formatter(max_module_width=10)

    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="very_long_module_name.py",
        lineno=30,
        msg="Long module message",
        args=(),
        exc_info=None,
    )

    result = formatter.format(record)

    parts = result.split(" | ")
    module_part = parts[2]

    # Should be padded or truncated to max_module_width
    assert module_part[:10] == "very_long_"  # first 10 chars of module name


def test_structured_formatter_all_parts() -> None:
    """Test case 7: All parts are present in formatted output."""
    formatter = structured_formatter()

    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test.py",
        lineno=35,
        msg="Complete test message",
        args=(),
        exc_info=None,
    )
    record.funcName = "test_func"

    result = formatter.format(record)

    parts = result.split(" | ")

    # Should have 5 parts: timestamp, level, module, location, message
    assert len(parts) == 5

    # Check each part
    assert len(parts[0]) == 19  # YYYY-MM-DD HH:MM:SS
    assert "INFO" in parts[1]
    assert "test" in parts[2]
    assert "test_func:35" in parts[3]
    assert "Complete test message" in parts[4]


def test_structured_formatter_with_formatting() -> None:
    """Test case 8: Structured formatter with message formatting."""
    formatter = structured_formatter()

    record = logging.LogRecord(
        name="test_logger",
        level=logging.WARNING,
        pathname="test.py",
        lineno=40,
        msg="Value: %s, Count: %d",
        args=("test_value", 42),
        exc_info=None,
    )

    result = formatter.format(record)

    parts = result.split(" | ")
    message_part = parts[4]

    # Should have formatted message
    assert "Value: test_value, Count: 42" in message_part
