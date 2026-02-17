from typing import Any, cast
from unittest.mock import MagicMock, patch

import pytest

try:
    import psutil
    from pyutils_collection.network_functions.check_port_open import check_port_open
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None
    check_port_open = None  # type: ignore[assignment]

pytestmark = [
    pytest.mark.unit,
    pytest.mark.network_functions,
    pytest.mark.skipif(not PSUTIL_AVAILABLE, reason="psutil not installed"),
]


def test_check_port_open_success() -> None:
    """
    Test case 1: Normal operation with valid host and open port.
    """
    with patch("socket.socket") as mock_socket:
        mock_instance = mock_socket.return_value
        mock_instance.connect.return_value = None
        assert check_port_open("localhost", 80) is True


def test_check_port_open_closed() -> None:
    """
    Test case 2: Port is closed, should return False.
    """
    with patch("socket.socket") as mock_socket:
        mock_instance = MagicMock()
        mock_instance.connect.side_effect = Exception()
        mock_socket.return_value.__enter__.return_value = mock_instance
        assert check_port_open("localhost", 81) is False


def test_check_port_open_type_error_host() -> None:
    """
    Test case 3: TypeError for non-string host.
    """
    with pytest.raises(TypeError, match="host must be a string"):
        check_port_open(cast(Any, 123), 80)


def test_check_port_open_type_error_port() -> None:
    """
    Test case 4: TypeError for non-integer port.
    """
    with pytest.raises(TypeError, match="port must be an integer"):
        check_port_open("localhost", cast(Any, "80"))


def test_check_port_open_value_error_host() -> None:
    """
    Test case 5: ValueError for empty host.
    """
    with pytest.raises(ValueError, match="host cannot be empty"):
        check_port_open("", 80)


def test_check_port_open_value_error_port() -> None:
    """
    Test case 6: ValueError for out-of-range port.
    """
    with pytest.raises(ValueError, match="port must be between 1 and 65535"):
        check_port_open("localhost", 0)
    with pytest.raises(ValueError, match="port must be between 1 and 65535"):
        check_port_open("localhost", 70000)


def test_check_port_open_type_error_timeout() -> None:
    """
    Test case 7: TypeError for invalid timeout type.
    """
    with pytest.raises(TypeError, match="timeout must be a number"):
        check_port_open("localhost", 80, timeout=cast(Any, "invalid"))


def test_check_port_open_value_error_timeout() -> None:
    """
    Test case 8: ValueError for negative timeout.
    """
    with pytest.raises(ValueError, match="timeout must be positive"):
        check_port_open("localhost", 80, timeout=-1)
