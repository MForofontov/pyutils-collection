"""Memory information retrieval."""

import psutil


def get_memory_info() -> dict[str, int | float | None]:
    """
    Get system memory usage information.

    Returns
    -------
    dict[str, int | float | None]
        Dictionary containing memory information including total, available,
        used, free, and percentage used.

    Examples
    --------
    >>> mem_info = get_memory_info()
    >>> 'total' in mem_info
    True
    >>> mem_info['total'] > 0
    True
    >>> 0 <= mem_info['percent_used'] <= 100
    True

    Notes
    -----
    All memory values are in bytes.

    Complexity
    ----------
    Time: O(1), Space: O(1)
    """
    memory = psutil.virtual_memory()

    return {
        "total": memory.total,
        "available": memory.available,
        "used": memory.used,
        "free": memory.free,
        "percent_used": memory.percent,
        "cached": memory.cached if hasattr(memory, "cached") else None,
        "buffers": memory.buffers if hasattr(memory, "buffers") else None,
    }


__all__ = ["get_memory_info"]
