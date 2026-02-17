import pytest

try:
    import psutil
    from pyutils_collection.network_functions.get_ipv6_addresses import get_ipv6_addresses
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None
    get_ipv6_addresses = None  # type: ignore[assignment]

pytestmark = [
    pytest.mark.unit,
    pytest.mark.network_functions,
    pytest.mark.skipif(not PSUTIL_AVAILABLE, reason="psutil not installed"),
]
from unittest.mock import MagicMock, patch


@patch("psutil.net_if_addrs")
def test_get_ipv6_addresses_single_address(mock_net_if_addrs: MagicMock) -> None:
    """
    Test case 1: Get single IPv6 address.
    """
    # Arrange
    import socket

    mock_addr = MagicMock()
    mock_addr.family = socket.AF_INET6
    mock_addr.address = "fe80::1"

    mock_net_if_addrs.return_value = {"eth0": [mock_addr]}

    # Act
    result = get_ipv6_addresses()

    # Assert
    assert isinstance(result, list)
    assert len(result) == 1
    assert result[0] == "fe80::1"


@patch("psutil.net_if_addrs")
def test_get_ipv6_addresses_multiple_addresses(mock_net_if_addrs: MagicMock) -> None:
    """
    Test case 2: Get multiple IPv6 addresses.
    """
    # Arrange
    import socket

    mock_addr1 = MagicMock()
    mock_addr1.family = socket.AF_INET6
    mock_addr1.address = "fe80::1"

    mock_addr2 = MagicMock()
    mock_addr2.family = socket.AF_INET6
    mock_addr2.address = "2001:db8::1"

    mock_net_if_addrs.return_value = {"eth0": [mock_addr1, mock_addr2]}

    # Act
    result = get_ipv6_addresses()

    # Assert
    assert len(result) == 2
    assert "fe80::1" in result
    assert "2001:db8::1" in result


@patch("psutil.net_if_addrs")
def test_get_ipv6_addresses_mixed_with_ipv4(mock_net_if_addrs: MagicMock) -> None:
    """
    Test case 3: Filter out IPv4 addresses, keep only IPv6.
    """
    # Arrange
    import socket

    mock_ipv6 = MagicMock()
    mock_ipv6.family = socket.AF_INET6
    mock_ipv6.address = "fe80::1"

    mock_ipv4 = MagicMock()
    mock_ipv4.family = socket.AF_INET
    mock_ipv4.address = "192.168.1.1"

    mock_net_if_addrs.return_value = {"eth0": [mock_ipv6, mock_ipv4]}

    # Act
    result = get_ipv6_addresses()

    # Assert
    assert len(result) == 1
    assert result[0] == "fe80::1"


@patch("psutil.net_if_addrs")
def test_get_ipv6_addresses_no_ipv6(mock_net_if_addrs: MagicMock) -> None:
    """
    Test case 4: Return empty list when no IPv6 addresses.
    """
    # Arrange
    import socket

    mock_ipv4 = MagicMock()
    mock_ipv4.family = socket.AF_INET
    mock_ipv4.address = "192.168.1.1"

    mock_net_if_addrs.return_value = {"eth0": [mock_ipv4]}

    # Act
    result = get_ipv6_addresses()

    # Assert
    assert isinstance(result, list)
    assert len(result) == 0


@patch("psutil.net_if_addrs")
def test_get_ipv6_addresses_multiple_interfaces(mock_net_if_addrs: MagicMock) -> None:
    """
    Test case 5: Get IPv6 addresses from multiple interfaces.
    """
    # Arrange
    import socket

    mock_addr1 = MagicMock()
    mock_addr1.family = socket.AF_INET6
    mock_addr1.address = "fe80::1"

    mock_addr2 = MagicMock()
    mock_addr2.family = socket.AF_INET6
    mock_addr2.address = "fe80::2"

    mock_net_if_addrs.return_value = {"eth0": [mock_addr1], "eth1": [mock_addr2]}

    # Act
    result = get_ipv6_addresses()

    # Assert
    assert len(result) == 2
    assert "fe80::1" in result
    assert "fe80::2" in result


@patch("psutil.net_if_addrs")
def test_get_ipv6_addresses_empty_interfaces(mock_net_if_addrs: MagicMock) -> None:
    """
    Test case 6: Return empty list when no network interfaces.
    """
    # Arrange
    mock_net_if_addrs.return_value = {}

    # Act
    result = get_ipv6_addresses()

    # Assert
    assert isinstance(result, list)
    assert len(result) == 0


@patch("psutil.net_if_addrs")
def test_get_ipv6_addresses_returns_list(mock_net_if_addrs: MagicMock) -> None:
    """
    Test case 7: Function always returns a list.
    """
    # Arrange
    mock_net_if_addrs.return_value = {}

    # Act
    result = get_ipv6_addresses()

    # Assert
    assert isinstance(result, list)
