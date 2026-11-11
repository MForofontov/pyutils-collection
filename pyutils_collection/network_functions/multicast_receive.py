"""Multicast message receiving."""

import socket


def multicast_receive(group: str, port: int, timeout: float = 5.0) -> str | None:
    """
    Receive a UDP multicast message from a group.

    Parameters
    ----------
    group : str
        Multicast group IP.
    port : int
        Port number.
    timeout : float, optional
        Timeout in seconds (default: 5.0).

    Returns
    -------
    Optional[str]
        Received message or None if timeout.

    Examples
    --------
    >>> multicast_receive('224.0.0.1', 5007)
    'hello'
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("", port))
        mreq = socket.inet_aton(group) + socket.inet_aton("0.0.0.0")  # nosec B104 # INADDR_ANY selects the multicast interface.
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        sock.settimeout(timeout)
        try:
            data, _ = sock.recvfrom(1024)
            return data.decode()
        except TimeoutError:
            return None
    finally:
        sock.close()


__all__ = ["multicast_receive"]
