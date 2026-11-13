"""Get local IP address."""

import socket
from contextlib import closing


def get_local_ip() -> str:
    """
    Get the local IP address of the current machine.

    Returns
    -------
    str
        Local IP address as a string.

    Notes
    -----
    The probe socket is closed on success and failure. Failures return 127.0.0.1.

    Examples
    --------
    >>> get_local_ip()
    '192.168.1.100'
    """
    try:
        with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as s:
            s.connect(("8.8.8.8", 80))
            return str(s.getsockname()[0])
    except Exception:
        return "127.0.0.1"


__all__ = ["get_local_ip"]
