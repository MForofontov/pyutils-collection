import pytest

try:
    import psutil
    from pyutils_collection.cli_functions.kill_process import kill_process
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None  # type: ignore
    kill_process = None  # type: ignore

pytestmark = [
    pytest.mark.unit,
    pytest.mark.cli_functions,
    pytest.mark.skipif(not PSUTIL_AVAILABLE, reason="psutil not installed"),
]


def test_kill_process_nonexistent_pid() -> None:
    """
    Test case 1: Test kill_process function with a nonexistent PID returns False.
    """
    result = kill_process(999999)
    assert not result


def test_kill_process_handles_os_errors() -> None:
    """
    Test case 2: Test kill_process handles OSError and PermissionError gracefully.
    """
    from unittest.mock import patch

    # Test OSError handling
    with patch("os.kill", side_effect=OSError("Operation not permitted")):
        with patch("psutil.pid_exists", return_value=True):
            result = kill_process(12345)
            assert result is False

    # Test PermissionError handling
    with patch("os.kill", side_effect=PermissionError("Permission denied")):
        with patch("psutil.pid_exists", return_value=True):
            result = kill_process(12345)
            assert result is False


def test_kill_process_invalid_type_error() -> None:
    """
    Test case 3: Test kill_process function with invalid input types raises TypeError.
    """
    with pytest.raises(TypeError, match="pid must be an integer"):
        kill_process("123")

    with pytest.raises(TypeError):
        kill_process(None)

    with pytest.raises(TypeError):
        kill_process(12.5)


def test_kill_process_invalid_pid_error() -> None:
    """
    Test case 4: Test kill_process function with invalid PID values raises ValueError.
    """
    with pytest.raises(ValueError, match="pid must be positive"):
        kill_process(0)

    with pytest.raises(ValueError):
        kill_process(-1)

    with pytest.raises(ValueError):
        kill_process(-999)


def test_kill_process_with_different_signals() -> None:
    """
    Test case 5: Test kill_process with different signal types.
    """
    import signal

    # These should all return False for non-existent PID without raising
    result1 = kill_process(999999, signal.SIGTERM)
    result2 = kill_process(999999, getattr(signal, "SIGKILL", signal.SIGTERM))

    assert result1 is False
    assert result2 is False


def test_kill_process_process_lookup_error() -> None:
    """
    Test case 6: Test kill_process handles ProcessLookupError.
    """
    from unittest.mock import patch

    with patch("os.kill", side_effect=ProcessLookupError("No such process")):
        with patch("psutil.pid_exists", return_value=True):
            result = kill_process(12345)
            assert result is False
