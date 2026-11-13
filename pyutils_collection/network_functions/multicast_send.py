"""Multicast message sending."""

import socket
from contextlib import closing


def multicast_send(message: str, group: str, port: int) -> None:
    """
    Send a UDP multicast message to a group.

    Parameters
    ----------
    message : str
        Message to send.
    group : str
        Multicast group IP.
    port : int
        Port number.

    Returns
    -------
    None

    Notes
    -----
    The socket is closed even when configuring or sending the message fails.

    Examples
    --------
    >>> multicast_send('hello', '224.0.0.1', 5007)
    """
    with closing(
        socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    ) as sock:
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
        sock.sendto(message.encode(), (group, port))


__all__ = ["multicast_send"]
