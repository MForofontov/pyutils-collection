"""SSH file transfer utilities using paramiko."""

import getpass
import math
import os
from typing import Any

import paramiko


def ssh_copy_file(
    local_path: str,
    remote_path: str,
    host: str,
    user: str | None = None,
    password: str | None = None,
    key_filename: str | None = None,
    port: int = 22,
    timeout: float = 30.0,
) -> dict[str, Any]:
    """
    Copy a local file to a remote host using SFTP via paramiko.

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
        Dictionary with keys: 'success', 'message', 'bytes_transferred'.

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If parameters have invalid values or local file doesn't exist.
    RuntimeError
        If file transfer fails.

    Examples
    --------
    >>> ssh_copy_file('file.txt', '/tmp/file.txt', 'example.com', user='myuser', password='mypass')
    {'success': True, 'message': 'File transferred successfully', 'bytes_transferred': 1024}

    Notes
    -----
    Uses paramiko SFTP for secure file transfer. Either password or key_filename
    should be provided for authentication.

    Complexity
    ----------
    Time: O(n) where n is file size, Space: O(1)
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

    # Check if local file exists
    if not os.path.exists(local_path):
        raise ValueError(f"Local file not found: {local_path}")
    if not os.path.isfile(local_path):
        raise ValueError(f"Local path is not a file: {local_path}")

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

        # Open SFTP session
        sftp = client.open_sftp()

        # Transfer the file
        sftp.put(local_path, remote_path)

        # Get file size for reporting
        file_size = os.path.getsize(local_path)

        sftp.close()

        return {
            "success": True,
            "message": "File transferred successfully",
            "bytes_transferred": file_size,
        }
    except paramiko.AuthenticationException as exc:
        raise RuntimeError(f"SSH authentication failed for {user}@{host}") from exc
    except paramiko.SSHException as exc:
        raise RuntimeError(f"SSH connection error: {exc}") from exc
    except FileNotFoundError as exc:
        raise ValueError(f"Local file not found: {local_path}") from exc
    except TimeoutError as exc:
        raise RuntimeError(f"File transfer timed out after {timeout} seconds") from exc
    except Exception as exc:
        raise RuntimeError(f"File transfer failed: {exc}") from exc
    finally:
        client.close()


__all__ = ["ssh_copy_file"]
