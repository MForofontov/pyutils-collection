import pytest

try:
    from unittest.mock import patch
    import psutil
    from pyutils_collection.network_functions.get_default_gateway import get_default_gateway
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    patch = None  # type: ignore[assignment]
    psutil = None
    get_default_gateway = None  # type: ignore[assignment]

pytestmark = [
    pytest.mark.unit,
    pytest.mark.network_functions,
    pytest.mark.skipif(not PSUTIL_AVAILABLE, reason="psutil not installed"),
]


def test_get_default_gateway_normal() -> None:
    """
    Test case 1: Normal operation returns a string IP or empty string.
    """
    gateway = get_default_gateway()
    assert isinstance(gateway, str)
    if gateway:
        parts = gateway.split(".")
        assert len(parts) == 4
        assert all(part.isdigit() and 0 <= int(part) <= 255 for part in parts)


def test_get_default_gateway_fallback() -> None:
    """
    Test case 2: Fallback returns empty string if no gateway found.
    """
    with patch(
        "pyutils_collection.network_functions.get_default_gateway._gateway_from_proc", return_value=""
    ):
        with patch(
            "pyutils_collection.network_functions.get_default_gateway._gateway_from_command",
            return_value="",
        ):
            assert get_default_gateway() == ""


def test_get_default_gateway_type() -> None:
    """
    Test case 3: Return type is always string.
    """
    gateway = get_default_gateway()
    assert isinstance(gateway, str)


def test_get_default_gateway_edge_case() -> None:
    """
    Test case 4: Edge case with unusual system config.
    """
    with patch(
        "pyutils_collection.network_functions.get_default_gateway._gateway_from_proc",
        return_value="0.0.0.0",
    ):
        assert get_default_gateway() == "0.0.0.0"


def test_get_default_gateway_value_error() -> None:
    """
    Test case 5: ValueError for invalid gateway format (simulate parser error).
    """
    with patch(
        "pyutils_collection.network_functions.get_default_gateway._gateway_from_proc",
        return_value="not_an_ip",
    ):
        gateway = get_default_gateway()
        assert isinstance(gateway, str)
        assert gateway == "not_an_ip"
