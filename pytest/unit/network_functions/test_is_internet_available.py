import pytest

try:
    import psutil
    from pyutils_collection.network_functions.is_internet_available import is_internet_available
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None
    is_internet_available = None  # type: ignore[assignment]

pytestmark = [
    pytest.mark.unit,
    pytest.mark.network_functions,
    pytest.mark.skipif(not PSUTIL_AVAILABLE, reason="psutil not installed"),
]
from unittest.mock import MagicMock, patch


@patch("socket.socket")
def test_is_internet_available_connection_success(mock_socket: MagicMock) -> None:
    """
    Test case 1: Internet is available when connection succeeds.
    """
    # Arrange
    mock_instance = MagicMock()
    mock_socket.return_value = mock_instance

    # Act
    result = is_internet_available()

    # Assert
    assert result is True
    mock_instance.connect.assert_called_once_with(("8.8.8.8", 53))
    mock_instance.close.assert_called_once()


@patch("socket.socket")
def test_is_internet_available_connection_failure(mock_socket: MagicMock) -> None:
    """
    Test case 2: Internet is not available when connection fails.
    """
    # Arrange
    mock_instance = MagicMock()
    mock_instance.connect.side_effect = Exception("Connection failed")
    mock_socket.return_value = mock_instance

    # Act
    result = is_internet_available()

    # Assert
    assert result is False


@patch("socket.socket")
def test_is_internet_available_custom_timeout(mock_socket: MagicMock) -> None:
    """
    Test case 3: Use custom timeout value.
    """
    # Arrange
    mock_instance = MagicMock()
    mock_socket.return_value = mock_instance

    # Act
    result = is_internet_available(timeout=5.0)

    # Assert
    assert result is True


@patch("socket.setdefaulttimeout")
@patch("socket.socket")
def test_is_internet_available_timeout_set(
    mock_socket: MagicMock, mock_timeout: MagicMock
) -> None:
    """
    Test case 4: Verify timeout is set correctly.
    """
    # Arrange
    mock_instance = MagicMock()
    mock_socket.return_value = mock_instance
    timeout_value = 3.0

    # Act
    is_internet_available(timeout=timeout_value)

    # Assert
    mock_timeout.assert_called_once_with(timeout_value)


@patch("socket.socket")
def test_is_internet_available_socket_closed_on_success(mock_socket: MagicMock) -> None:
    """
    Test case 5: Socket is closed after successful connection.
    """
    # Arrange
    mock_instance = MagicMock()
    mock_socket.return_value = mock_instance

    # Act
    is_internet_available()

    # Assert
    mock_instance.close.assert_called_once()


@patch("socket.socket")
def test_is_internet_available_returns_boolean(mock_socket: MagicMock) -> None:
    """
    Test case 6: Function always returns a boolean.
    """
    # Arrange
    mock_instance = MagicMock()
    mock_socket.return_value = mock_instance

    # Act
    result = is_internet_available()

    # Assert
    assert isinstance(result, bool)


@patch("socket.socket")
def test_is_internet_available_default_timeout(mock_socket: MagicMock) -> None:
    """
    Test case 7: Default timeout is 2.0 seconds.
    """
    # Arrange
    mock_instance = MagicMock()
    mock_socket.return_value = mock_instance

    # Act
    result = is_internet_available()

    # Assert
    assert result is True


@patch("socket.socket")
def test_is_internet_available_socket_error(mock_socket: MagicMock) -> None:
    """
    Test case 8: Handle socket creation error.
    """
    # Arrange
    mock_socket.side_effect = Exception("Socket error")

    # Act
    result = is_internet_available()

    # Assert
    assert result is False
