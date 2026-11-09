"""Shell command execution."""

import subprocess
from typing import Any


def execute_command(
    command: str | list[str],
    shell: bool = False,
    timeout: float | None = None,
    capture_output: bool = True,
    check: bool = False,
    cwd: str | None = None,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    """
    Execute a shell command and return the result.

    Parameters
    ----------
    command : str | list[str]
        Command to execute. If string and shell=False, will be split.
        If list, will be passed directly to subprocess.
    shell : bool, optional
        Whether to execute command through shell (by default False).
    timeout : float | None, optional
        Command timeout in seconds (by default None).
    capture_output : bool, optional
        Whether to capture stdout and stderr (by default True).
    check : bool, optional
        Whether to raise CalledProcessError on non-zero exit (by default False).
    cwd : str | None, optional
        Working directory for command execution (by default None).
    env : dict[str, str] | None, optional
        Environment variables for command (by default None).

    Returns
    -------
    dict[str, Any]
        Dictionary containing return_code, stdout, stderr, and success status.

    Raises
    ------
    TypeError
        If command is not a string or list.
    ValueError
        If timeout is negative.
    subprocess.TimeoutExpired
        If command execution exceeds timeout.
    subprocess.CalledProcessError
        If check=True and command returns non-zero exit code.

    Examples
    --------
    >>> result = execute_command('echo "hello"', shell=True)
    >>> result['success']
    True
    >>> result['return_code']
    0

    Notes
    -----
    Using shell=True can be a security hazard. Only use with trusted input.

    Complexity
    ----------
    Time: O(n) where n is command execution time
    Space: O(m) where m is output size
    """
    if not isinstance(command, (str, list)):
        raise TypeError(
            f"command must be a string or list, got {type(command).__name__}"
        )

    if timeout is not None and not isinstance(timeout, (int, float)):
        raise TypeError(
            f"timeout must be a number or None, got {type(timeout).__name__}"
        )

    if timeout is not None and timeout < 0:
        raise ValueError(f"timeout must be non-negative, got {timeout}")

    if not isinstance(shell, bool):
        raise TypeError(f"shell must be a boolean, got {type(shell).__name__}")

    if not isinstance(capture_output, bool):
        raise TypeError(
            f"capture_output must be a boolean, got {type(capture_output).__name__}"
        )

    if not isinstance(check, bool):
        raise TypeError(f"check must be a boolean, got {type(check).__name__}")

    if cwd is not None and not isinstance(cwd, str):
        raise TypeError(f"cwd must be a string or None, got {type(cwd).__name__}")

    if env is not None and not isinstance(env, dict):
        raise TypeError(f"env must be a dictionary or None, got {type(env).__name__}")

    # Convert string command to list if not using shell
    if isinstance(command, str) and not shell:
        command = command.split()

    try:
        result = subprocess.run(  # nosec B602 # Shell execution requires explicit shell=True.
            command,
            shell=shell,
            timeout=timeout,
            capture_output=capture_output,
            check=check,
            cwd=cwd,
            env=env,
            text=True,
        )

        return {
            "return_code": result.returncode,
            "stdout": result.stdout if capture_output else None,
            "stderr": result.stderr if capture_output else None,
            "success": result.returncode == 0,
        }
    except subprocess.TimeoutExpired as e:
        return {
            "return_code": -1,
            "stdout": e.stdout if hasattr(e, "stdout") else None,
            "stderr": e.stderr if hasattr(e, "stderr") else None,
            "success": False,
            "error": "timeout",
        }
    except subprocess.CalledProcessError as e:
        return {
            "return_code": e.returncode,
            "stdout": e.stdout if hasattr(e, "stdout") else None,
            "stderr": e.stderr if hasattr(e, "stderr") else None,
            "success": False,
            "error": "non_zero_exit",
        }


__all__ = ["execute_command"]
