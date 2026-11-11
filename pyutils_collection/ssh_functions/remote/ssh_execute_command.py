"""SSH command execution using paramiko."""

import getpass
import math
from typing import Any

import paramiko

from pyutils_collection.ssh_functions.remote._output import read_command_output


def ssh_execute_command(
    host: str,
    command: str,
    user: str | None = None,
    password: str | None = None,
    key_filename: str | None = None,
    port: int = 22,
    timeout: float = 30.0,
) -> dict[str, Any]:
    """
    Execute a command on a remote host via SSH using paramiko.

    Parameters
    ----------
    host : str
        Hostname or IP address of the remote machine.
    command : str
        Command to execute remotely.
    user : str, optional
        SSH username (default: None, uses current user).
    password : str, optional
        SSH password for authentication (default: None).
    key_filename : str, optional
        Path to private key file for authentication (default: None).
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
        If SSH command fails or connection cannot be established.

    Examples
    --------
    >>> ssh_execute_command('example.com', 'ls /tmp', user='myuser', password='mypass')
    {'stdout': 'file1\\nfile2', 'stderr': '', 'exit_code': 0}
    >>> ssh_execute_command('example.com', 'ls /tmp', user='myuser', key_filename='~/.ssh/id_rsa')
    {'stdout': 'file1\\nfile2', 'stderr': '', 'exit_code': 0}

    Notes
    -----
    Uses paramiko for SSH connectivity. Either password or key_filename should be provided
    for authentication. If neither is provided, attempts to use default SSH keys.
    Output streams are drained together with a finite output-collection deadline;
    large stderr output cannot block stdout. Unused command stdin is closed.

    Complexity
    ----------
    Time: O(1), Space: O(1)
    """
    # Input validation
    if not isinstance(host, str):
        raise TypeError(f"host must be a string, got {type(host).__name__}")
    if not isinstance(command, str):
        raise TypeError(f"command must be a string, got {type(command).__name__}")
    if user is not None and not isinstance(user, str):
        raise TypeError(f"user must be a string or None, got {type(user).__name__}")
    if password is not None and not isinstance(password, str):
        raise TypeError(
            f"password must be a string or None, got {type(password).__name__}"
        )
    if key_filename is not None and not isinstance(key_filename, str):
        raise TypeError(
            f"key_filename must be a string or None, got {type(key_filename).__name__}"
        )
    if not isinstance(port, int):
        raise TypeError(f"port must be an integer, got {type(port).__name__}")
    if not (1 <= port <= 65535):
        raise ValueError(f"port must be in 1-65535, got {port}")
    if not isinstance(timeout, (int, float)):
        raise TypeError(f"timeout must be a number, got {type(timeout).__name__}")
    if timeout <= 0 or not math.isfinite(timeout):
        raise ValueError(f"timeout must be positive and finite, got {timeout}")

    # Default to current user if not specified
    if user is None:
        user = getpass.getuser()

    client = paramiko.SSHClient()

    try:
        client.load_system_host_keys()
        client.set_missing_host_key_policy(paramiko.RejectPolicy())
        # Connect to the remote host
        client.connect(
            hostname=host,
            port=port,
            username=user,
            password=password,
            key_filename=key_filename,
            timeout=timeout,
        )

        # Execute the command
        stdin, stdout, stderr = client.exec_command(command, timeout=timeout)  # nosec B601 # Runs the caller's requested remote command.

        # Get results
        stdin.close()
        stdout_data, stderr_data, exit_code = read_command_output(
            stdout, stderr, timeout
        )

        return {
            "stdout": stdout_data,
            "stderr": stderr_data,
            "exit_code": exit_code,
        }
    except paramiko.AuthenticationException as exc:
        raise RuntimeError(f"SSH authentication failed for {user}@{host}") from exc
    except paramiko.SSHException as exc:
        raise RuntimeError(f"SSH connection error: {exc}") from exc
    except TimeoutError as exc:
        raise RuntimeError(f"SSH command timed out after {timeout} seconds") from exc
    except Exception as exc:
        raise RuntimeError(f"SSH command failed: {exc}") from exc
    finally:
        client.close()


__all__ = ["ssh_execute_command"]
