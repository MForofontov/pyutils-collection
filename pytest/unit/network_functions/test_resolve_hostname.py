import socket
from typing import Any, cast
from unittest.mock import patch

import pytest

try:
    import psutil
    from pyutils_collection.network_functions.resolve_hostname import resolve_hostname
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    psutil = None
    resolve_hostname = None  # type: ignore[assignment]

pytestmark = [
    pytest.mark.unit,
    pytest.mark.network_functions,
    pytest.mark.skipif(not PSUTIL_AVAILABLE, reason="psutil not installed"),
]


def test_resolve_hostname_success() -> None:
    """
    Test case 1: Normal operation with mocked gethostbyname.
    """
    with patch("socket.gethostbyname", return_value="1.2.3.4"):
        ip = resolve_hostname("example.com")
        assert ip == "1.2.3.4"


def test_resolve_hostname_performance() -> None:
    """
    Test case 2: Performance with repeated calls.
    """
    with patch("socket.gethostbyname", return_value="1.2.3.4"):
        for _ in range(10):
            ip = resolve_hostname("example.com")
            assert ip == "1.2.3.4"


def test_resolve_hostname_type_error() -> None:
    """
    Test case 3: TypeError for non-string hostname.
    """
    with pytest.raises(TypeError, match="hostname must be a string"):
        resolve_hostname(cast(Any, 123))


def test_resolve_hostname_value_error_empty() -> None:
    """
    Test case 4: ValueError for empty hostname.
    """
    with pytest.raises(ValueError, match="hostname cannot be empty"):
        resolve_hostname("")


def test_resolve_hostname_value_error_unresolvable() -> None:
    """
    Test case 5: ValueError for unresolvable hostname.
    """
    with patch("socket.gethostbyname", side_effect=socket.gaierror("not found")):
        with pytest.raises(ValueError, match="Could not resolve hostname"):
            resolve_hostname("badhost")
