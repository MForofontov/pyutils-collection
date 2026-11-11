"""Process running status check."""

import psutil


def is_process_running(process_name: str) -> bool:
    """
    Check if a process with the given name is running.

    Parameters
    ----------
    process_name : str
        Name of the process to check.

    Returns
    -------
    bool
        True if process is running, False otherwise.

    Raises
    ------
    TypeError
        If process_name is not a string.

    Examples
    --------
    >>> is_process_running('init')  # init process usually exists on Linux
    True
    >>> is_process_running('nonexistent_process_12345')
    False
    """
    if not isinstance(process_name, str):
        raise TypeError("process_name must be a string")
    if not process_name:
        return False

    for proc in psutil.process_iter(["name"]):
        try:
            if proc.info["name"] == process_name:
                return True
        except psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess:
            continue

    return False


__all__ = ["is_process_running"]
