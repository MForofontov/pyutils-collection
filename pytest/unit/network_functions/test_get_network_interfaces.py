from unittest.mock import patch

import pytest

try:
    import psutil
    from pyutils_collection.network_functions.get_network_interfaces import get_network_interfaces
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None
    get_network_interfaces = None  # type: ignore[assignment]

pytestmark = [
    pytest.mark.unit,
    pytest.mark.network_functions,
    pytest.mark.skipif(not PSUTIL_AVAILABLE, reason="psutil not installed"),
]


def test_get_network_interfaces_type() -> None:
    """
    Test case 1: get_network_interfaces returns a dict.
    """
    interfaces = get_network_interfaces()
    assert isinstance(interfaces, dict)


def test_get_network_interfaces_keys_values() -> None:
    """
    Test case 2: Keys are strings, values are lists of strings.
    """
    interfaces = get_network_interfaces()
    for k, v in interfaces.items():
        assert isinstance(k, str)
        assert isinstance(v, list)
        assert all(isinstance(ip, str) for ip in v)


def test_get_network_interfaces_mocked() -> None:
    """
    Test case 3: Mock psutil.net_if_addrs returns expected structure.
    """
    import socket

    class Addr:
        def __init__(self, address: str) -> None:
            self.address = address
            self.family = socket.AF_INET

    mock_addrs = {
        "eth0": [Addr("192.168.1.2")],
        "lo": [Addr("127.0.0.1")],
    }
    with patch("psutil.net_if_addrs", return_value=mock_addrs):
        interfaces = get_network_interfaces()
        assert interfaces == {"eth0": ["192.168.1.2"], "lo": ["127.0.0.1"]}


def test_get_network_interfaces_empty() -> None:
    """
    Test case 4: Edge case with no interfaces.
    """
    with patch("psutil.net_if_addrs", return_value={}):
        interfaces = get_network_interfaces()
        assert interfaces == {}


def test_get_network_interfaces_type_error() -> None:
    """
    Test case 5: TypeError if psutil.net_if_addrs returns wrong type.
    """
    with patch("psutil.net_if_addrs", return_value="not_a_dict"):
        with pytest.raises(AttributeError):
            get_network_interfaces()
