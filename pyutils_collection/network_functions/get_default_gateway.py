"""Default gateway address determination."""

from __future__ import annotations

import ipaddress
import os
import socket
import struct
import subprocess
from collections.abc import Callable, Iterable


def get_default_gateway() -> str:
    """
    Get the default gateway IP address.

    Returns
    -------
    str
        Default gateway IP address as a string, or empty string if not found.

    Examples
    --------
    >>> get_default_gateway()
    '192.168.1.1'
    """
    gateway = _gateway_from_proc()
    if gateway:
        return gateway

    for command, parser in _COMMANDS:
        gateway = _gateway_from_command(command, parser)
        if gateway:
            return gateway

    return ""


def _gateway_from_proc() -> str:
    path = "/proc/net/route"
    if not os.path.exists(path):
        return ""

    try:
        with open(path, encoding="utf-8", errors="ignore") as route_file:
            lines = [line.strip() for line in route_file.readlines() if line.strip()]
    except OSError:
        return ""

    if len(lines) <= 1:
        return ""

    headers = lines[0].split()
    try:
        dest_idx = headers.index("Destination")
        gateway_idx = headers.index("Gateway")
    except ValueError:
        return ""

    for line in lines[1:]:
        fields = line.split()
        if len(fields) <= max(dest_idx, gateway_idx):
            continue

        if fields[dest_idx] != "00000000":
            continue

        gateway = _hex_to_ipv4(fields[gateway_idx])
        if gateway:
            return gateway

    return ""


def _gateway_from_command(command: Iterable[str], parser: Callable[[str], str]) -> str:
    try:
        result = subprocess.run(
            list(command),
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )
    except OSError, ValueError, subprocess.TimeoutExpired:
        return ""

    if result.returncode != 0:
        return ""

    output = result.stdout or ""
    if not output.strip():
        return ""

    return parser(output)


def _parse_ip_route(output: str) -> str:
    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line or not line.startswith("default"):
            continue

        tokens = line.split()
        if "via" in tokens:
            via_index = tokens.index("via")
            if via_index + 1 < len(tokens):
                gateway = _normalize_ipv4(tokens[via_index + 1])
                if gateway:
                    return gateway
        else:
            for token in tokens[1:]:
                gateway = _normalize_ipv4(token)
                if gateway:
                    return gateway

    return ""


def _parse_route_get_default(output: str) -> str:
    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        if line.lower().startswith("gateway:"):
            _, value = line.split(":", 1)
            tokens = value.split()
            if not tokens:
                continue
            gateway = _normalize_ipv4(tokens[0])
            if gateway:
                return gateway

    return ""


def _parse_netstat_rn(output: str) -> str:
    for raw_line in output.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        lower = line.lower()
        if lower.startswith("destination") or "routing" in lower:
            continue

        if not (lower.startswith("default") or line.startswith("0.0.0.0")):  # nosec B104 # Route text, not a bind address.
            continue

        tokens = line.split()
        for token in tokens[1:]:
            gateway = _normalize_ipv4(token)
            if gateway:
                return gateway

    return ""


def _hex_to_ipv4(value: str) -> str:
    try:
        packed = struct.pack("<L", int(value, 16))
    except ValueError, struct.error, OverflowError:
        return ""

    return _normalize_ipv4(socket.inet_ntoa(packed))


def _normalize_ipv4(value: str) -> str:
    candidate = value.strip()
    if not candidate:
        return ""

    try:
        ip = ipaddress.ip_address(candidate)
    except ValueError:
        return ""

    if ip.version != 4 or ip.is_unspecified:
        return ""

    return str(ip)


_COMMANDS: list[tuple[list[str], Callable[[str], str]]] = [
    (["ip", "route"], _parse_ip_route),
    (["route", "-n", "get", "default"], _parse_route_get_default),
    (["netstat", "-rn"], _parse_netstat_rn),
]

__all__ = ["get_default_gateway"]
