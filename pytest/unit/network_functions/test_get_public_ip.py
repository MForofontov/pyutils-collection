from unittest.mock import patch

try:
    import requests
    from pyutils_collection.network_functions.get_public_ip import get_public_ip

    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    requests = None  # type: ignore[assignment]
    get_public_ip = None  # type: ignore[assignment]

import pytest

pytestmark = [
    pytest.mark.skipif(not REQUESTS_AVAILABLE, reason="requests not installed"),
    pytest.mark.unit,
    pytest.mark.network_functions,
]


def test_get_public_ip_type() -> None:
    """
    Test case 1: get_public_ip returns a string.
    """
    ip = get_public_ip()
    assert isinstance(ip, str)


def test_get_public_ip_format() -> None:
    """
    Test case 2: IP address format is correct (IPv4).
    """
    ip = get_public_ip()
    parts = ip.split(".")
    assert len(parts) == 4
    assert all(part.isdigit() and 0 <= int(part) <= 255 for part in parts)


def test_get_public_ip_mocked() -> None:
    """
    Test case 3: Mock requests.get returns expected IP.
    """

    class MockResponse:
        def __init__(self, text: str) -> None:
            self.text = text

        def raise_for_status(self) -> None:
            pass

    with patch("requests.get", return_value=MockResponse("8.8.8.8")):
        ip = get_public_ip()
        assert ip == "8.8.8.8"


def test_get_public_ip_network_error() -> None:
    """
    Test case 4: Network error raises exception.
    """

    class MockResponse:
        def raise_for_status(self) -> None:
            raise Exception("Network error")

        @property
        def text(self) -> str:
            return ""

    with patch("requests.get", return_value=MockResponse()):
        ip = get_public_ip()
        assert ip == ""


def test_get_public_ip_type_error() -> None:
    """
    Test case 5: TypeError if requests.get returns wrong type.
    """
    with patch("requests.get", return_value="not_a_response"):
        ip = get_public_ip()
        assert ip == ""


def test_get_public_ip_invalid_response_uses_fallback() -> None:
    """
    Test case 6: Invalid response text triggers fallback public IP retrieval.
    """

    class MockResponse:
        def __init__(self, text: str) -> None:
            self.text = text

        def raise_for_status(self) -> None:
            pass

    with patch("requests.get", return_value=MockResponse("invalid_ip")):
        with patch(
            "pyutils_collection.network_functions.get_public_ip._get_fallback_public_ip",
            return_value="203.0.113.5",
        ):
            ip = get_public_ip()

    assert ip == "203.0.113.5"


def test_get_public_ip_request_exception_fallback_empty() -> None:
    """
    Test case 7: RequestException with empty fallback returns empty string.
    """

    with patch("requests.get", side_effect=requests.RequestException):
        with patch(
            "pyutils_collection.network_functions.get_public_ip._get_fallback_public_ip",
            return_value="",
        ):
            ip = get_public_ip()

    assert ip == ""
