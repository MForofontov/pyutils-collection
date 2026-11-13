"""Network interface information retrieval."""

import socket

import psutil


def get_network_info() -> dict[str, dict[str, list[dict[str, str | int]]]]:
    """
    Get network interface information for all network adapters.

    Returns
    -------
    dict[str, dict[str, list[dict[str, str | int]]]]
        Dictionary mapping interface names to their address information.
        Each interface contains address families (AF_INET, AF_INET6, etc.)
        with lists of address dictionaries.

    Examples
    --------
    >>> net_info = get_network_info()
    >>> isinstance(net_info, dict)
    True
    >>> len(net_info) >= 0  # May have no interfaces in some environments
    True

    Notes
    -----
    IPv4, IPv6, and MAC addresses are classified using native platform family
    constants, including Windows-specific values. Unknown families use "other".

    Returned dictionary structure:
    {
        'interface_name': {
            'ipv4': [{'address': '192.168.1.1', 'netmask': '255.255.255.0', ...}],
            'ipv6': [{'address': 'fe80::1', 'netmask': 'ffff:ffff:ffff:ffff::', ...}],
            'mac': [{'address': '00:11:22:33:44:55', ...}]
        }
    }

    Complexity
    ----------
    Time: O(n) where n is number of network interfaces
    Space: O(n * m) where m is average addresses per interface
    """
    interfaces = psutil.net_if_addrs()
    result = {}

    for interface_name, addresses in interfaces.items():
        interface_info: dict[str, list[dict[str, str | int]]] = {
            "ipv4": [],
            "ipv6": [],
            "mac": [],
            "other": [],
        }

        for addr in addresses:
            addr_dict = {
                "address": addr.address,
                "netmask": addr.netmask,
                "broadcast": addr.broadcast,
                "ptp": addr.ptp if hasattr(addr, "ptp") else None,
            }

            # Categorize by address family
            if addr.family == socket.AF_INET:
                interface_info["ipv4"].append(addr_dict)
            elif addr.family == socket.AF_INET6:
                interface_info["ipv6"].append(addr_dict)
            elif addr.family == psutil.AF_LINK:
                interface_info["mac"].append(addr_dict)
            else:
                interface_info["other"].append(addr_dict)

        result[interface_name] = interface_info

    return result


__all__ = ["get_network_info"]
