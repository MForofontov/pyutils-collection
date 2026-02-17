from typing import Any, cast
from unittest.mock import MagicMock, patch

import pytest

try:
    import psutil
    from pyutils_collection.network_functions.multicast_send import multicast_send
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None
    multicast_send = None  # type: ignore[assignment]

pytestmark = [
    pytest.mark.unit,
    pytest.mark.network_functions,
    pytest.mark.skipif(not PSUTIL_AVAILABLE, reason="psutil not installed"),
]


def test_multicast_send_normal() -> None:
    """
    Test case 1: Normal operation with mocked socket.
    """
    mock_sock = MagicMock()
    with patch("socket.socket", return_value=mock_sock):
        with patch.object(mock_sock, "setsockopt"):
            with patch.object(mock_sock, "sendto"):
                with patch.object(mock_sock, "close"):
                    multicast_send("hello", "224.0.0.1", 5007)
                    mock_sock.sendto.assert_called_once()


def test_multicast_send_type_error_message() -> None:
    """
    Test case 2: TypeError for non-string message (simulate error).
    """
    with pytest.raises(AttributeError):
        multicast_send(cast(Any, 123), "224.0.0.1", 5007)


def test_multicast_send_type_error_group() -> None:
    """
    Test case 3: TypeError for non-string group (simulate error).
    """
    with pytest.raises((TypeError, OSError)):
        multicast_send("hello", cast(Any, 123), 5007)


def test_multicast_send_type_error_port() -> None:
    """
    Test case 4: TypeError for non-integer port (simulate error).
    """
    with pytest.raises(TypeError):
        multicast_send("hello", "224.0.0.1", cast(Any, "not_an_int"))
