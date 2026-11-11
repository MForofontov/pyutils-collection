try:
    import psutil  # noqa: F401
    from pyutils_collection.cli_functions.is_process_running import is_process_running

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None  # type: ignore
    is_process_running = None  # type: ignore

import pytest


def test_is_process_running_empty_name_skips_scan(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from unittest.mock import Mock

    scan = Mock()
    monkeypatch.setattr(psutil, "process_iter", scan)
    assert is_process_running("") is False
    scan.assert_not_called()


pytestmark = pytest.mark.skipif(not PSUTIL_AVAILABLE, reason="psutil not installed")
pytestmark = [pytestmark, pytest.mark.unit, pytest.mark.cli_functions]


def test_is_process_running_valid_process() -> None:
    """
    Test case 1: Test is_process_running function with a process that should exist.
    """
    result = is_process_running("init")
    assert isinstance(result, bool)


def test_is_process_running_nonexistent_process() -> None:
    """
    Test case 2: Test is_process_running function with a nonexistent process.
    """
    result = is_process_running("nonexistent_process_12345")
    assert not result


def test_is_process_running_handles_psutil_exceptions() -> None:
    """
    Test case 3: Test is_process_running handles psutil exceptions gracefully.
    """
    from unittest.mock import MagicMock, patch

    import psutil

    # Mock process_iter to raise exceptions during iteration
    with patch("psutil.process_iter") as mock_iter:
        # Create mock process that raises NoSuchProcess
        mock_proc = MagicMock()
        mock_proc.info = {"name": "test_process"}
        mock_proc.__getitem__.side_effect = psutil.NoSuchProcess(pid=123)

        mock_iter.return_value = [mock_proc]

        # Should handle exception and continue, returning False
        result = is_process_running("test_process")
        assert isinstance(result, bool)


def test_is_process_running_invalid_type_error() -> None:
    """
    Test case 4: Test is_process_running function with invalid input type raises TypeError.
    """
    with pytest.raises(TypeError, match="process_name must be a string"):
        is_process_running(123)

    with pytest.raises(TypeError):
        is_process_running(None)

    with pytest.raises(TypeError):
        is_process_running(["process_name"])


def test_is_process_running_empty_string() -> None:
    """
    Test case 5: Test is_process_running with empty string returns False.
    """
    result = is_process_running("")
    assert result is False


def test_is_process_running_current_process() -> None:
    """
    Test case 6: Test is_process_running can find python process.
    """
    import os

    import psutil

    # Get current process name
    current_proc = psutil.Process(os.getpid())
    current_name = current_proc.name()

    # Should find a process with the same name
    result = is_process_running(current_name)
    assert isinstance(result, bool)
    # Should be True since current process is running
    assert result is True
