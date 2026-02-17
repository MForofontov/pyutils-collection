from typing import Any, cast
from unittest.mock import MagicMock, patch

import pytest

try:
    import psutil
    from pyutils_collection.network_functions.traceroute_host import traceroute_host
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None
    traceroute_host = None  # type: ignore[assignment]

pytestmark = [
    pytest.mark.unit,
    pytest.mark.network_functions,
    pytest.mark.skipif(not PSUTIL_AVAILABLE, reason="psutil not installed"),
]


def test_traceroute_host_normal() -> None:
    """
    Test case 1: Normal operation with mocked subprocess.
    """
    mock_result = MagicMock()
    mock_result.stdout = "1 192.168.1.1\n2 10.0.0.1\n"
    with patch("subprocess.run", return_value=mock_result):
        hops = traceroute_host("google.com", max_hops=2)
        assert hops == ["10.0.0.1"]


def test_traceroute_host_error() -> None:
    """
    Test case 2: Exception in subprocess returns empty list.
    """
    with patch("subprocess.run", side_effect=Exception("fail")):
        hops = traceroute_host("google.com", max_hops=2)
        assert hops == []


def test_traceroute_host_type_error_host() -> None:
    """
    Test case 3: TypeError for non-string host.
    """
    with pytest.raises(TypeError, match="host must be a string"):
        traceroute_host(cast(Any, 123))


def test_traceroute_host_value_error_empty() -> None:
    """
    Test case 4: ValueError for empty host.
    """
    with pytest.raises(ValueError, match="host cannot be empty"):
        traceroute_host("")
