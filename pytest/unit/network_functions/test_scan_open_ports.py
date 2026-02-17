from typing import Any, cast
from unittest.mock import MagicMock, patch

import pytest

try:
    import psutil
    from pyutils_collection.network_functions.scan_open_ports import scan_open_ports
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None
    scan_open_ports = None  # type: ignore[assignment]

pytestmark = [
    pytest.mark.unit,
    pytest.mark.network_functions,
    pytest.mark.skipif(not PSUTIL_AVAILABLE, reason="psutil not installed"),
]


def test_scan_open_ports_normal() -> None:
    """
    Test case 1: Normal operation with mocked socket.
    """
    mock_sock = MagicMock()
    mock_sock.connect.return_value = None
    with patch("socket.socket", return_value=mock_sock):
        with patch.object(mock_sock, "settimeout"):
            open_ports = scan_open_ports("localhost", 22, 25, timeout=0.1)
            assert isinstance(open_ports, list)
            assert all(isinstance(port, int) for port in open_ports)


def test_scan_open_ports_closed() -> None:
    """
    Test case 2: All ports closed (mocked socket).
    """
    mock_sock = MagicMock()
    mock_sock.connect.side_effect = Exception()
    with patch("socket.socket") as mock_socket:
        mock_socket.return_value.__enter__.return_value = mock_sock
        with patch.object(mock_sock, "settimeout"):
            open_ports = scan_open_ports("localhost", 22, 25, timeout=0.1)
            assert open_ports == []


def test_scan_open_ports_type_error_host() -> None:
    """
    Test case 3: TypeError for non-string host (simulate error).
    """
    with pytest.raises(TypeError, match="host must be a string"):
        scan_open_ports(cast(Any, 123), 22, 25)


def test_scan_open_ports_type_error_port() -> None:
    """
    Test case 4: TypeError for non-integer port (simulate error).
    """
    with pytest.raises(TypeError, match="start_port must be an integer"):
        scan_open_ports("localhost", cast(Any, "not_an_int"), 25)
