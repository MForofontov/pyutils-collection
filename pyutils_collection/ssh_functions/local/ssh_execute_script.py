"""SSH script execution."""

import subprocess
from typing import Any

from ._validation import validate_target


def ssh_execute_script(
    host: str,
    script_path: str,
    user: str | None = None,
    port: int = 22,
    timeout: float = 60.0,
) -> dict[str, Any]:
    """
    Execute a local script file on a remote host via SSH.

    Parameters
    ----------
    host : str
        Hostname or IP address of the remote machine.
    script_path : str
        Path to the local script file to execute remotely.
    user : str, optional
        SSH username (default: None, uses current user).
    port : int, optional
        SSH port (default: 22).
    timeout : float, optional
        Timeout in seconds (default: 60.0).

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
        If SSH command fails.

    Examples
    --------
    >>> ssh_execute_script('example.com', 'myscript.sh')
    {'stdout': 'result', 'stderr': '', 'exit_code': 0}

    Notes
    -----
    The script is piped to the remote host and executed via SSH.

    Complexity
    ----------
    Time: O(1), Space: O(1)
    """
    if not isinstance(host, str):
        raise TypeError(f"host must be a string, got {type(host).__name__}")
    if not isinstance(script_path, str):
        raise TypeError(
            f"script_path must be a string, got {type(script_path).__name__}"
        )
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
    ssh_target = f"{user + '@' if user else ''}{host}"
    ssh_cmd = ["ssh", "-p", str(port), ssh_target, "bash -s"]
    try:
        with open(script_path, encoding="utf-8") as script_file:
            proc = subprocess.run(
                ssh_cmd,
                input=script_file.read(),
                capture_output=True,
                text=True,
                timeout=timeout,
            )
        return {
            "stdout": proc.stdout.strip(),
            "stderr": proc.stderr.strip(),
            "exit_code": proc.returncode,
        }
    except FileNotFoundError as exc:
        raise ValueError(f"Script file not found: {script_path}") from exc
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(f"SSH command timed out after {timeout} seconds") from exc
    except Exception as exc:
        raise RuntimeError(f"SSH command failed: {exc}") from exc


__all__ = ["ssh_execute_script"]
