"""Process termination by PID."""

import os
import signal

import psutil


def kill_process(pid: int, signal_type: int = signal.SIGTERM) -> bool:
    """
    Kill a process by its PID.

    Parameters
    ----------
    pid : int
        Process ID to kill.
    signal_type : int, optional
        Signal to send to the process (by default signal.SIGTERM).

    Returns
    -------
    bool
        True if process was successfully killed, False otherwise.

    Raises
    ------
    TypeError
        If pid is not an integer.
    ValueError
        If pid is not positive.

    Examples
    --------
    >>> # This would kill a process, so we can't really test it safely
    >>> # kill_process(12345)
    >>> # False  # Process doesn't exist
    """
    if not isinstance(pid, int):
        raise TypeError("pid must be an integer")

    if pid <= 0:
        raise ValueError("pid must be positive")

    try:
        # Check if process exists first
        if not psutil.pid_exists(pid):
            return False

        os.kill(pid, signal_type)
        return True
    except OSError, ProcessLookupError, PermissionError:
        return False


__all__ = ["kill_process"]
