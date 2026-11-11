"""Ping host utility."""

import subprocess
import sys


def ping_host(host: str, count: int = 1, timeout: int = 2) -> bool:
    """
    Ping a host to check if it is reachable.

    Parameters
    ----------
    host : str
        Hostname or IP address to ping.
    count : int, optional
        Number of ping attempts (default: 1).
    timeout : int, optional
        Timeout in seconds for each ping (default: 2).

    Returns
    -------
    bool
        True if host is reachable, False otherwise.

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If host is empty.

    Examples
    --------
    >>> ping_host('8.8.8.8')
    True
    """
    if not isinstance(host, str):
        raise TypeError(f"host must be a string, got {type(host).__name__}")
    if not host:
        raise ValueError("host cannot be empty")
    if not isinstance(count, int):
        raise TypeError(f"count must be an integer, got {type(count).__name__}")
    if not isinstance(timeout, int):
        raise TypeError(f"timeout must be an integer, got {type(timeout).__name__}")

    if sys.platform == "darwin":
        cmd = ["ping", "-c", str(count), "-t", str(timeout), host]
    elif sys.platform.startswith("win"):
        cmd = ["ping", "-n", str(count), "-w", str(timeout * 1000), host]
    else:
        cmd = ["ping", "-c", str(count), "-W", str(timeout), host]
    try:
        result = subprocess.run(
            cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        return result.returncode == 0
    except Exception:
        return False


__all__ = ["ping_host"]
