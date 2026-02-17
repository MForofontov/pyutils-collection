import pytest

try:
    import psutil
    from pyutils_collection.network_functions.get_local_ip import get_local_ip
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None
    get_local_ip = None  # type: ignore[assignment]

pytestmark = [
    pytest.mark.unit,
    pytest.mark.network_functions,
    pytest.mark.skipif(not PSUTIL_AVAILABLE, reason="psutil not installed"),
]
from unittest.mock import MagicMock, patch


@patch("socket.socket")
def test_get_local_ip_successful_connection(mock_socket: MagicMock) -> None:
    """
    Test case 1: Successfully get local IP address.
    """
    # Arrange
    mock_instance = MagicMock()
    mock_instance.getsockname.return_value = ("192.168.1.100", 12345)
    mock_socket.return_value = mock_instance

    # Act
    result = get_local_ip()

    # Assert
    assert result == "192.168.1.100"
    mock_instance.connect.assert_called_once_with(("8.8.8.8", 80))
    mock_instance.close.assert_called_once()


@patch("socket.socket")
def test_get_local_ip_connection_failure(mock_socket: MagicMock) -> None:
    """
    Test case 2: Return localhost on connection failure.
    """
    # Arrange
    mock_socket.side_effect = Exception("Connection failed")

    # Act
    result = get_local_ip()

    # Assert
    assert result == "127.0.0.1"


@patch("socket.socket")
def test_get_local_ip_different_addresses(mock_socket: MagicMock) -> None:
    """
    Test case 3: Test with different IP addresses.
    """
    # Arrange
    test_ips = ["192.168.0.1", "10.0.0.5", "172.16.0.100"]

    for ip in test_ips:
        mock_instance = MagicMock()
        mock_instance.getsockname.return_value = (ip, 12345)
        mock_socket.return_value = mock_instance

        # Act
        result = get_local_ip()

        # Assert
        assert result == ip


@patch("socket.socket")
def test_get_local_ip_socket_closed(mock_socket: MagicMock) -> None:
    """
    Test case 4: Verify socket is properly closed.
    """
    # Arrange
    mock_instance = MagicMock()
    mock_instance.getsockname.return_value = ("192.168.1.1", 12345)
    mock_socket.return_value = mock_instance

    # Act
    get_local_ip()

    # Assert
    mock_instance.close.assert_called_once()


@patch("socket.socket")
def test_get_local_ip_getsockname_exception(mock_socket: MagicMock) -> None:
    """
    Test case 5: Handle exception during getsockname.
    """
    # Arrange
    mock_instance = MagicMock()
    mock_instance.getsockname.side_effect = Exception("Socket error")
    mock_socket.return_value = mock_instance

    # Act
    result = get_local_ip()

    # Assert
    assert result == "127.0.0.1"


@patch("socket.socket")
def test_get_local_ip_returns_string(mock_socket: MagicMock) -> None:
    """
    Test case 6: Result is always a string.
    """
    # Arrange
    mock_instance = MagicMock()
    mock_instance.getsockname.return_value = ("10.0.0.1", 12345)
    mock_socket.return_value = mock_instance

    # Act
    result = get_local_ip()

    # Assert
    assert isinstance(result, str)
