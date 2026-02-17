from typing import Any, cast
from unittest.mock import MagicMock, patch

import pytest

try:
    import psutil
    from pyutils_collection.network_functions.get_network_speed import get_network_speed
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None
    get_network_speed = None  # type: ignore[assignment]

pytestmark = [
    pytest.mark.unit,
    pytest.mark.network_functions,
    pytest.mark.skipif(not PSUTIL_AVAILABLE, reason="psutil not installed"),
]


def test_get_network_speed_normal() -> None:
    """
    Test case 1: Normal operation with mocked download.
    """
    mock_response = MagicMock()
    mock_response.iter_content.return_value = [b"a" * 8192] * 10
    with patch("requests.get", return_value=mock_response):
        result = get_network_speed("http://test", timeout=1)
        assert isinstance(result, dict)
        assert "download_mbps" in result
        assert result["download_mbps"] > 0


def test_get_network_speed_edge_case_empty_content() -> None:
    """
    Test case 2: Edge case with empty content.
    """
    mock_response = MagicMock()
    mock_response.iter_content.return_value = []
    with patch("requests.get", return_value=mock_response):
        result = get_network_speed("http://test", timeout=1)
        assert result["download_mbps"] == 0.0


def test_get_network_speed_network_error() -> None:
    """
    Test case 3: Network error returns 0.0 Mbps.
    """
    with patch("requests.get", side_effect=Exception("Network error")):
        with pytest.raises(Exception, match="Network error"):
            get_network_speed("http://test", timeout=1)


def test_get_network_speed_type_error_url() -> None:
    """
    Test case 4: TypeError for non-string URL (simulate error).
    """
    with pytest.raises(TypeError, match="test_url must be a string"):
        get_network_speed(cast(Any, 123), timeout=1)


def test_get_network_speed_value_error_empty_url() -> None:
    """Test case 5: ValueError for empty test_url."""
    with pytest.raises(ValueError, match="test_url cannot be empty"):
        get_network_speed("", timeout=1)


def test_get_network_speed_type_error_timeout() -> None:
    """Test case 6: TypeError for non-numeric timeout."""
    with pytest.raises(TypeError, match="timeout must be a number"):
        get_network_speed("http://test", timeout="fast")  # type: ignore


def test_get_network_speed_value_error_timeout() -> None:
    """Test case 7: ValueError for non-positive timeout."""
    with pytest.raises(ValueError, match="timeout must be positive"):
        get_network_speed("http://test", timeout=0)
