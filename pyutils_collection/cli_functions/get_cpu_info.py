"""CPU information retrieval."""

import os

import psutil


def get_cpu_info(interval: float = 0.1) -> dict[str, int | float | list[float] | tuple[float, float, float] | None]:
    """
    Get CPU information and usage statistics.

    Parameters
    ----------
    interval : float, optional
        Interval in seconds to wait in between each call to ``psutil.cpu_percent``.

    Returns
    -------
    dict[str, int | float | list[float] | tuple[float, float, float] | None]
        Dictionary containing CPU information including count, usage, and frequencies.

    Examples
    --------
    >>> cpu_info = get_cpu_info()
    >>> 'cpu_count' in cpu_info
    True
    >>> cpu_info['cpu_count'] > 0
    True
    """
    freq = psutil.cpu_freq()

    return {
        "cpu_count": os.cpu_count(),
        "cpu_percent": psutil.cpu_percent(interval=interval),
        "cpu_percent_per_core": psutil.cpu_percent(interval=interval, percpu=True),
        "cpu_freq_current": freq.current if freq else None,
        "cpu_freq_min": freq.min if freq else None,
        "cpu_freq_max": freq.max if freq else None,
        "load_average": os.getloadavg() if hasattr(os, "getloadavg") else None,
    }


__all__ = ["get_cpu_info"]
