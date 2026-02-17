from unittest.mock import patch

import pytest

try:
    import psutil
    from pyutils_collection.network_functions.get_mac_address import get_mac_address
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None
    get_mac_address = None  # type: ignore[assignment]

pytestmark = [
    pytest.mark.unit,
    pytest.mark.network_functions,
    pytest.mark.skipif(not PSUTIL_AVAILABLE, reason="psutil not installed"),
]


def test_get_mac_address_type() -> None:
    """
    Test case 1: get_mac_address returns a string.
    """
    mac = get_mac_address()
    assert isinstance(mac, str)


def test_get_mac_address_format() -> None:
    """
    Test case 2: MAC address format is correct.
    """
    mac = get_mac_address()
    parts = mac.split(":")
    assert len(parts) == 6
    assert all(len(part) == 2 for part in parts)


def test_get_mac_address_mocked() -> None:
    """
    Test case 3: Mocked uuid.getnode returns expected MAC.
    """
    with patch("uuid.getnode", return_value=0x001A2B3C4D5E):
        mac = get_mac_address()
        assert mac == "00:1a:2b:3c:4d:5e"


def test_get_mac_address_edge_case() -> None:
    """
    Test case 4: Edge case with all zeros MAC.
    """
    with patch("uuid.getnode", return_value=0):
        mac = get_mac_address()
        assert mac == "00:00:00:00:00:00"


def test_get_mac_address_type_error() -> None:
    """
    Test case 5: TypeError if uuid.getnode returns non-int (simulate error).
    """
    with patch("uuid.getnode", return_value="not_an_int"):
        with pytest.raises(TypeError):
            get_mac_address()
