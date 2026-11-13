"""Check internet connectivity."""

import socket
from contextlib import closing


def is_internet_available(timeout: float = 2.0) -> bool:
    """
    Check if the machine has internet connectivity.

    Parameters
    ----------
    timeout : float, optional
        Timeout in seconds (default: 2.0).

    Returns
    -------
    bool
        True if internet is available, False otherwise.

    Notes
    -----
    The timeout applies only to this probe's socket; the process-wide default
    timeout is unchanged. The socket is closed on success and failure.

    Examples
    --------
    >>> is_internet_available()
    True
    """
    try:
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.settimeout(timeout)
            s.connect(("8.8.8.8", 53))
            return True
    except Exception:
        return False


__all__ = ["is_internet_available"]
