import pytest

pytestmark = [pytest.mark.unit, pytest.mark.logger_functions]
import logging
import re
import time

from pyutils_collection.logger_functions.performance_formatter import performance_formatter


def test_performance_formatter_basic() -> None:

    """
    Test case 1: Basic performance formatter functionality.
    """
    formatter = performance_formatter()
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

    # Should contain performance format with separators
    assert " | " in result
    assert "INFO" in result
    assert "Test message" in result
    assert "+0.0ms" in result  # Initial elapsed time


def test_performance_formatter_timestamp() -> None:
    """
    Test case 2: Performance formatter includes timestamp.
    """
    formatter = performance_formatter()

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

    # Should start with timestamp in [HH:MM:SS.mmm] format
    assert result.startswith("[")
    assert re.match(r"\[\d{2}:\d{2}:\d{2}\.\d{3}\]", result)


def test_performance_formatter_thread_info() -> None:

    """
    Test case 3: Thread information inclusion.
    """
    formatter = performance_formatter(include_thread_info=True)

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

    # Should contain thread information
    assert "T" in result
    parts = result.split(" | ")
    assert parts[1].startswith("T")


def test_performance_formatter_no_thread_info() -> None:

    """
    Test case 4: Exclusion of thread information.
    """
    formatter = performance_formatter(include_thread_info=False)

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

    # Should not have thread info as second part
    assert not parts[1].startswith("T")
    assert parts[1] == "ERROR"


def test_performance_formatter_elapsed_time() -> None:

    """
    Test case 5: Elapsed time calculation.
    """
    formatter = performance_formatter()

    # Wait a bit to ensure elapsed time > 0
    time.sleep(0.01)

    record = logging.LogRecord(
        name="test_logger",
        level=logging.CRITICAL,
        pathname="test.py",
        lineno=25,
        msg="Critical message",
        args=(),
        exc_info=None,
    )

    result = formatter.format(record)

    # Should contain elapsed time
    assert "ms" in result

    # Extract elapsed time
    parts = result.split(" | ")
    elapsed_part = [part for part in parts if "ms" in part][0]
    elapsed_value = float(elapsed_part.replace("ms", "").replace("+", ""))

    # Should be greater than 0
    assert elapsed_value > 0


def test_performance_formatter_module_function() -> None:

    """
    Test case 6: Module and function name formatting.
    """
    formatter = performance_formatter(include_thread_info=False)

    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test.py",
        lineno=30,
        msg="Module function message",
        args=(),
        exc_info=None,
    )
    record.funcName = "test_function"

    result = formatter.format(record)

    parts = result.split(" | ")

    # Should contain module.function:line format
    location_part = parts[2]
    assert "test.test_function:30" in location_part


def test_performance_formatter_multiple_calls() -> None:

    """
    Test case 7: Elapsed time accumulation across multiple calls.
    """
    formatter = performance_formatter(include_thread_info=False)

    # First call
    record1 = logging.LogRecord(
        name="test_logger",
        level=logging.DEBUG,
        pathname="test.py",
        lineno=35,
        msg="First message",
        args=(),
        exc_info=None,
    )

    result1 = formatter.format(record1)
    parts1 = result1.split(" | ")
    elapsed1 = float(
        [part for part in parts1 if "ms" in part][0].replace("ms", "").replace("+", "")
    )

    # Wait a bit
    time.sleep(0.005)

    # Second call
    record2 = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test.py",
        lineno=40,
        msg="Second message",
        args=(),
        exc_info=None,
    )

    result2 = formatter.format(record2)
    parts2 = result2.split(" | ")
    elapsed2 = float(
        [part for part in parts2 if "ms" in part][0].replace("ms", "").replace("+", "")
    )

    # Second elapsed time should be greater than first
    assert elapsed2 > elapsed1


def test_performance_formatter_with_formatting() -> None:

    """
    Test case 8: Performance formatter with message formatting.
    """
    formatter = performance_formatter(include_thread_info=False)

    record = logging.LogRecord(
        name="test_logger",
        level=logging.WARNING,
        pathname="test.py",
        lineno=45,
        msg="Value: %s, Time: %.2f",
        args=("test", 1.23),
        exc_info=None,
    )

    result = formatter.format(record)

    parts = result.split(" | ")
    message_part = parts[-1]

    # Should have formatted message
    assert "Value: test, Time: 1.23" in message_part


def test_performance_formatter_all_parts() -> None:
    """
    Test case 9: All expected parts are present.
    """
    formatter = performance_formatter(include_thread_info=True)

    record = logging.LogRecord(
        name="test_logger",
        level=logging.ERROR,
        pathname="test.py",
        lineno=50,
        msg="Complete test message",
        args=(),
        exc_info=None,
    )
    record.funcName = "complete_test"

    result = formatter.format(record)

    parts = result.split(" | ")

    # Should have expected number of parts
    assert len(parts) >= 5

    # Check key parts exist
    assert parts[0].startswith("[")  # timestamp
    assert parts[1].startswith("T")  # thread
    assert parts[2] == "ERROR"  # level
    assert "complete_test:50" in parts[3]  # location
    assert "Complete test message" in parts[-1]  # message
