"""SSH file transfer utilities."""

import subprocess
from pathlib import Path
from typing import Any

from ._validation import validate_target


def ssh_copy_file(
    local_path: str,
    remote_path: str,
    host: str,
    user: str | None = None,
    port: int = 22,
    timeout: float = 30.0,
) -> dict[str, Any]:
    """
    Copy a local file to a remote host using SCP.

    Parameters
    ----------
    local_path : str
        Path to the local file to copy.
    remote_path : str
        Destination path on the remote host.
    host : str
        Hostname or IP address of the remote machine.
    user : str, optional
        SSH username (default: None, uses current user).
    port : int, optional
        SSH port (default: 22).
    timeout : float, optional
        Timeout in seconds (default: 30.0).

    Returns
    -------
    dict[str, Any]
        Dictionary with keys: 'stdout', 'stderr', 'exit_code'.

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If parameters have invalid values.
    RuntimeError
        If SCP command fails.

    Examples
    --------
    >>> ssh_copy_file('file.txt', '/tmp/file.txt', 'example.com')
    {'stdout': '', 'stderr': '', 'exit_code': 0}

    Notes
    -----
    Requires SSH access and `scp` command available.

    Complexity
    ----------
    Time: O(1), Space: O(1)
    """
    if not isinstance(local_path, str):
        raise TypeError(f"local_path must be a string, got {type(local_path).__name__}")
    if not isinstance(remote_path, str):
        raise TypeError(
            f"remote_path must be a string, got {type(remote_path).__name__}"
        )
    if not isinstance(host, str):
        raise TypeError(f"host must be a string, got {type(host).__name__}")
    if user is not None and not isinstance(user, str):
        raise TypeError(f"user must be a string or None, got {type(user).__name__}")
    if not isinstance(port, int):
        raise TypeError(f"port must be an integer, got {type(port).__name__}")
    if not (1 <= port <= 65535):
        raise ValueError(f"port must be in 1-65535, got {port}")
    if not isinstance(timeout, (int, float)):
        raise TypeError(f"timeout must be a number, got {type(timeout).__name__}")
    if timeout <= 0:
        raise ValueError(f"timeout must be positive, got {timeout}")

    validate_target(host, user, timeout)
    if not local_path or not remote_path or "\x00" in remote_path:
        raise ValueError("local_path and remote_path must be non-empty paths")
    # Brackets disambiguate IPv6 addresses from SCP's path separator.
    scp_host = f"[{host}]" if ":" in host and not host.startswith("[") else host
    scp_target = f"{user + '@' if user else ''}{scp_host}:{remote_path}"
    # Absolute local paths cannot be interpreted as SCP options or remote hosts.
    scp_cmd = ["scp", "-P", str(port), str(Path(local_path).absolute()), scp_target]
    try:
        proc = subprocess.run(scp_cmd, capture_output=True, text=True, timeout=timeout)
        return {
            "stdout": proc.stdout.strip(),
            "stderr": proc.stderr.strip(),
            "exit_code": proc.returncode,
        }
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"SCP command timed out after {timeout} seconds") from exc
    except Exception as exc:
        raise RuntimeError(f"SCP command failed: {exc}") from exc


__all__ = ["ssh_copy_file"]
