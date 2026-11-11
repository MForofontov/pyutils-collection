"""SSH connection verification using paramiko."""

import getpass
from typing import Any

import paramiko


def ssh_check_connection(
    host: str,
    user: str | None = None,
    password: str | None = None,
    key_filename: str | None = None,
    port: int = 22,
    timeout: float = 10.0,
) -> dict[str, Any]:
    """
    Check SSH connectivity to a remote host using paramiko.

    Parameters
    ----------
    host : str
        Hostname or IP address of the remote machine.
    user : str, optional
        SSH username (default: None, uses current user).
    password : str, optional
        SSH password for authentication (default: None).
    key_filename : str, optional
        Path to private key file for authentication (default: None).
    port : int, optional
        SSH port (default: 22).
    timeout : float, optional
        Timeout in seconds (default: 10.0).

    Returns
    -------
    dict[str, Any]
        Dictionary with keys: 'success', 'message', 'error'.

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If parameters have invalid values.

    Examples
    --------
    >>> ssh_check_connection('example.com', user='myuser', password='mypass')
    {'success': True, 'message': 'Connection successful', 'error': None}
    >>> ssh_check_connection('badhost.com', user='myuser', password='mypass')
    {'success': False, 'message': 'Connection failed', 'error': '...'}

    Notes
    -----
    Uses paramiko to test SSH connectivity. Returns success status rather than
    raising exceptions for connection failures.

    Complexity
    ----------
    Time: O(1), Space: O(1)
    """
    if not isinstance(host, str):
        raise TypeError(f"host must be a string, got {type(host).__name__}")
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

    # Default to current user if not specified
    if user is None:
        user = getpass.getuser()

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Attempt to connect
        client.connect(
            hostname=host,
            port=port,
            username=user,
            password=password,
            key_filename=key_filename,
            timeout=timeout,
        )
        return {
            "success": True,
            "message": "Connection successful",
            "error": None,
        }
    except paramiko.AuthenticationException as exc:
        return {
            "success": False,
            "message": "Authentication failed",
            "error": str(exc),
        }
    except paramiko.SSHException as exc:
        return {
            "success": False,
            "message": "SSH connection error",
            "error": str(exc),
        }
    except TimeoutError as exc:
        return {
            "success": False,
            "message": f"Connection timed out after {timeout} seconds",
            "error": str(exc),
        }
    except Exception as exc:
        return {
            "success": False,
            "message": "Connection failed",
            "error": str(exc),
        }
    finally:
        client.close()


__all__ = ["ssh_check_connection"]
