import sys

import pytest

try:
    import psutil
    from pyutils_collection.cli_functions.execute_command import execute_command
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None  # type: ignore
    execute_command = None  # type: ignore

pytestmark = [
    pytest.mark.unit,
    pytest.mark.cli_functions,
    pytest.mark.skipif(not PSUTIL_AVAILABLE, reason="psutil not installed"),
]


def test_execute_command_simple_echo() -> None:
    """
    Test case 1: Execute simple echo command successfully.
    """
    result = execute_command("echo hello", shell=True)

    assert isinstance(result, dict)
    assert result["success"] is True
    assert result["return_code"] == 0
    assert "hello" in result["stdout"]


def test_execute_command_list_command() -> None:
    """
    Test case 2: Execute command as list without shell.
    """
    result = execute_command([sys.executable, "-c", "print('hello')"])

    assert result["success"] is True
    assert result["return_code"] == 0
    assert "hello" in result["stdout"]


def test_execute_command_command_with_timeout() -> None:
    """
    Test case 3: Execute command with timeout.
    """
    result = execute_command("echo test", shell=True, timeout=5.0)

    assert result["success"] is True
    assert result["return_code"] == 0


def test_execute_command_invalid_command() -> None:
    """
    Test case 4: Execute invalid command returns non-zero exit code.
    """
    result = execute_command("nonexistent_command_xyz", shell=True)

    assert result["success"] is False
    assert result["return_code"] != 0


def test_execute_command_invalid_type_error() -> None:
    """
    Test case 5: Invalid command type raises TypeError.
    """
    with pytest.raises(TypeError, match="command must be a string or list"):
        execute_command(123)

    with pytest.raises(TypeError):
        execute_command(None)


def test_execute_command_negative_timeout_error() -> None:
    """
    Test case 6: Negative timeout raises ValueError.
    """
    with pytest.raises(ValueError, match="timeout must be non-negative"):
        execute_command("echo test", shell=True, timeout=-1)
