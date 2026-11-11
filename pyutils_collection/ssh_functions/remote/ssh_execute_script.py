"""SSH script execution using paramiko."""

import getpass
import os
from typing import Any

import paramiko

_ALLOWED_INTERPRETERS = frozenset(
    {"bash", "sh", "python", "python3", "perl", "ruby", "node", "php"}
)


def ssh_execute_script(
    host: str,
    script_path: str,
    user: str | None = None,
    password: str | None = None,
    key_filename: str | None = None,
    port: int = 22,
    timeout: float = 60.0,
    interpreter: str = "bash",
) -> dict[str, Any]:
    """
    Execute a local script file on a remote host via SSH using paramiko.

    Parameters
    ----------
    host : str
        Hostname or IP address of the remote machine.
    script_path : str
        Path to the local script file to execute remotely.
    user : str, optional
        SSH username (default: None, uses current user).
    password : str, optional
        SSH password for authentication (default: None).
    key_filename : str, optional
        Path to private key file for authentication (default: None).
    port : int, optional
        SSH port (default: 22).
    timeout : float, optional
        Timeout in seconds (default: 60.0).
    interpreter : str, optional
        Script interpreter to use (default: "bash").

    Returns
    -------
    dict[str, Any]
        Dictionary with keys: 'stdout', 'stderr', 'exit_code'.

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If parameters have invalid values or script file doesn't exist.
    RuntimeError
        If SSH command fails.

    Examples
    --------
    >>> ssh_execute_script('example.com', 'myscript.sh', user='myuser', password='mypass')
    {'stdout': 'result', 'stderr': '', 'exit_code': 0}
    >>> ssh_execute_script('example.com', 'script.py', user='myuser', key_filename='~/.ssh/id_rsa', interpreter='python3')
    {'stdout': 'result', 'stderr': '', 'exit_code': 0}

    Notes
    -----
    Uses paramiko to read the script file and execute it remotely via the specified interpreter.
    The script content is piped to the interpreter stdin.

    Complexity
    ----------
    Time: O(n) where n is script size, Space: O(n)
    """
    if not isinstance(host, str):
        raise TypeError(f"host must be a string, got {type(host).__name__}")
    if not isinstance(script_path, str):
        raise TypeError(
            f"script_path must be a string, got {type(script_path).__name__}"
        )
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
    if timeout <= 0:
        raise ValueError(f"timeout must be positive, got {timeout}")
    if not isinstance(interpreter, str):
        raise TypeError(
            f"interpreter must be a string, got {type(interpreter).__name__}"
        )
    if interpreter not in _ALLOWED_INTERPRETERS:
        raise ValueError(
            f"interpreter must be one of {sorted(_ALLOWED_INTERPRETERS)}, got {interpreter!r}"
        )

    # Check if script file exists
    if not os.path.exists(script_path):
        raise ValueError(f"Script file not found: {script_path}")
    if not os.path.isfile(script_path):
        raise ValueError(f"Script path is not a file: {script_path}")

    # Default to current user if not specified
    if user is None:
        user = getpass.getuser()

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connect to the remote host
        client.connect(
            hostname=host,
            port=port,
            username=user,
            password=password,
            key_filename=key_filename,
            timeout=timeout,
        )

        # Read the script content
        with open(script_path, encoding="utf-8") as script_file:
            script_content = script_file.read()

        # Execute the script by piping it to the interpreter
        command = f"{interpreter} -s"
        stdin, stdout, stderr = client.exec_command(command, timeout=timeout)

        # Send script content to stdin
        stdin.write(script_content)
        stdin.close()

        # Get results
        stdout_data = stdout.read().decode("utf-8").strip()
        stderr_data = stderr.read().decode("utf-8").strip()
        exit_code = stdout.channel.recv_exit_status()

        return {
            "stdout": stdout_data,
            "stderr": stderr_data,
            "exit_code": exit_code,
        }
    except paramiko.AuthenticationException as exc:
        raise RuntimeError(f"SSH authentication failed for {user}@{host}") from exc
    except paramiko.SSHException as exc:
        raise RuntimeError(f"SSH connection error: {exc}") from exc
    except FileNotFoundError as exc:
        raise ValueError(f"Script file not found: {script_path}") from exc
    except TimeoutError as exc:
        raise RuntimeError(f"SSH command timed out after {timeout} seconds") from exc
    except Exception as exc:
        raise RuntimeError(f"SSH command failed: {exc}") from exc
    finally:
        client.close()


__all__ = ["ssh_execute_script"]
