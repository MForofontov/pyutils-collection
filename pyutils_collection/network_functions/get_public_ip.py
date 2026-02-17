"""Get public IP address."""

import socket
from typing import Final

import requests

_PUBLIC_IP_ENDPOINT: Final[str] = "https://api.ipify.org"


def get_public_ip(timeout: float = 5.0) -> str:
    """
    Get the public IP address of the machine using an external service.

    Parameters
    ----------
    timeout : float, optional
        Timeout in seconds (default: 5.0).

    Returns
    -------
    str
        Public IP address as a string, or empty string if unavailable.

    Examples
    --------
    >>> get_public_ip()
    '8.8.8.8'
    """
    try:
        response = requests.get(_PUBLIC_IP_ENDPOINT, timeout=timeout)
        response.raise_for_status()
        ip: str = response.text.strip()
        if _is_valid_ipv4(ip):
            return ip
    except requests.RequestException:
        fallback_ip = _get_fallback_public_ip()
        if fallback_ip:
            return fallback_ip
        return ""
    except Exception:
        return ""

    fallback_ip = _get_fallback_public_ip()
    return fallback_ip or ""


def _is_valid_ipv4(value: str) -> bool:
    parts = value.split(".")
    if len(parts) != 4:
        return False
    for part in parts:
        if not part.isdigit():
            return False
        number = int(part)
        if number < 0 or number > 255:
            return False
    return True


def _get_fallback_public_ip() -> str:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            # The IP address doesn't need to be reachable; we just use it to
            # determine the preferred outbound interface.
            sock.connect(("8.8.8.8", 80))
            ip: str = str(sock.getsockname()[0])
        if _is_valid_ipv4(ip):
            return ip
    except OSError:
        pass

    try:
        ip = socket.gethostbyname(socket.gethostname())
        if _is_valid_ipv4(ip):
            return ip
    except socket.gaierror:
        pass

    return ""


__all__ = ["get_public_ip"]
