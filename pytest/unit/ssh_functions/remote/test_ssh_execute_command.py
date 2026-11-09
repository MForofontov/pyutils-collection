"""Tests for remote SSH execute command using paramiko."""

from unittest.mock import MagicMock, patch

try:
    import paramiko
    from pyutils_collection.ssh_functions.remote.ssh_execute_command import ssh_execute_command
    PARAMIKO_AVAILABLE = True
except ImportError:
    PARAMIKO_AVAILABLE = False
    paramiko = None  # type: ignore
    ssh_execute_command = None  # type: ignore

import pytest

pytestmark = pytest.mark.skipif(not PARAMIKO_AVAILABLE, reason="paramiko not installed")
pytestmark = [pytestmark, pytest.mark.unit, pytest.mark.ssh_functions, pytest.mark.usefixtures("mocked_output_reader")]


def test_ssh_execute_command_successful_with_password() -> None:
    """
    Test case 1: Test successful command execution with password authentication.
    """
    with patch(
        "pyutils_collection.ssh_functions.remote.ssh_execute_command.paramiko.SSHClient"
    ) as mock_client:
        with patch(
            "pyutils_collection.ssh_functions.remote.ssh_execute_command.getpass.getuser",
            return_value="testuser",
        ):
            mock_ssh = MagicMock()
            mock_client.return_value = mock_ssh
            mock_stdin = MagicMock()
            mock_stdout = MagicMock()
            mock_stdout.read.return_value = b"output"
            mock_stdout.channel.recv_exit_status.return_value = 0
            mock_stderr = MagicMock()
            mock_stderr.read.return_value = b""
            mock_ssh.exec_command.return_value = (mock_stdin, mock_stdout, mock_stderr)

            result = ssh_execute_command(
                "host", "ls /tmp", user="user", password="pass"
            )
            assert result["stdout"] == "output"
            assert result["stderr"] == ""
            assert result["exit_code"] == 0
            mock_ssh.connect.assert_called_once_with(
                hostname="host",
                port=22,
                username="user",
                password="pass",
                key_filename=None,
                timeout=30.0,
            )


def test_ssh_execute_command_successful_with_key_file() -> None:
    """
    Test case 2: Test successful command execution with key file authentication.
    """
    with patch(
        "pyutils_collection.ssh_functions.remote.ssh_execute_command.paramiko.SSHClient"
    ) as mock_client:
        with patch(
            "pyutils_collection.ssh_functions.remote.ssh_execute_command.getpass.getuser",
            return_value="testuser",
        ):
            mock_ssh = MagicMock()
            mock_client.return_value = mock_ssh
            mock_stdin = MagicMock()
            mock_stdout = MagicMock()
            mock_stdout.read.return_value = b"output"
            mock_stdout.channel.recv_exit_status.return_value = 0
            mock_stderr = MagicMock()
            mock_stderr.read.return_value = b""
            mock_ssh.exec_command.return_value = (mock_stdin, mock_stdout, mock_stderr)

            result = ssh_execute_command(
                "host", "ls /tmp", user="user", key_filename="/path/to/key"
            )
            assert result["stdout"] == "output"
            assert result["exit_code"] == 0
            mock_ssh.connect.assert_called_once_with(
                hostname="host",
                port=22,
                username="user",
                password=None,
                key_filename="/path/to/key",
                timeout=30.0,
            )


def test_ssh_execute_command_with_stderr() -> None:
    """
    Test case 3: Test command execution with stderr output.
    """
    with patch(
        "pyutils_collection.ssh_functions.remote.ssh_execute_command.paramiko.SSHClient"
    ) as mock_client:
        with patch(
            "pyutils_collection.ssh_functions.remote.ssh_execute_command.getpass.getuser",
            return_value="testuser",
        ):
            mock_ssh = MagicMock()
            mock_client.return_value = mock_ssh
            mock_stdin = MagicMock()
            mock_stdout = MagicMock()
            mock_stdout.read.return_value = b""
            mock_stdout.channel.recv_exit_status.return_value = 1
            mock_stderr = MagicMock()
            mock_stderr.read.return_value = b"error"
            mock_ssh.exec_command.return_value = (mock_stdin, mock_stdout, mock_stderr)

            result = ssh_execute_command(
                "host", "bad_command", user="user", password="pass"
            )
            assert result["stderr"] == "error"
            assert result["exit_code"] == 1


def test_ssh_execute_command_with_custom_port() -> None:
    """
    Test case 4: Test command execution with custom port.
    """
    with patch(
        "pyutils_collection.ssh_functions.remote.ssh_execute_command.paramiko.SSHClient"
    ) as mock_client:
        with patch(
            "pyutils_collection.ssh_functions.remote.ssh_execute_command.getpass.getuser",
            return_value="testuser",
        ):
            mock_ssh = MagicMock()
            mock_client.return_value = mock_ssh
            mock_stdin = MagicMock()
            mock_stdout = MagicMock()
            mock_stdout.read.return_value = b"ok"
            mock_stdout.channel.recv_exit_status.return_value = 0
            mock_stderr = MagicMock()
            mock_stderr.read.return_value = b""
            mock_ssh.exec_command.return_value = (mock_stdin, mock_stdout, mock_stderr)

            result = ssh_execute_command(
                "host", "ls", user="user", password="pass", port=2222
            )
            assert result["exit_code"] == 0
            mock_ssh.connect.assert_called_once_with(
                hostname="host",
                port=2222,
                username="user",
                password="pass",
                key_filename=None,
                timeout=30.0,
            )


def test_ssh_execute_command_default_user() -> None:
    """
    Test case 5: Test command execution with default user from getpass.
    """
    with patch(
        "pyutils_collection.ssh_functions.remote.ssh_execute_command.paramiko.SSHClient"
    ) as mock_client:
        with patch(
            "pyutils_collection.ssh_functions.remote.ssh_execute_command.getpass.getuser",
            return_value="currentuser",
        ):
            mock_ssh = MagicMock()
            mock_client.return_value = mock_ssh
            mock_stdin = MagicMock()
            mock_stdout = MagicMock()
            mock_stdout.read.return_value = b"ok"
            mock_stdout.channel.recv_exit_status.return_value = 0
            mock_stderr = MagicMock()
            mock_stderr.read.return_value = b""
            mock_ssh.exec_command.return_value = (mock_stdin, mock_stdout, mock_stderr)

            result = ssh_execute_command("host", "ls", password="pass")
            assert result["exit_code"] == 0
            mock_ssh.connect.assert_called_once_with(
                hostname="host",
                port=22,
                username="currentuser",
                password="pass",
                key_filename=None,
                timeout=30.0,
            )


def test_ssh_execute_command_with_custom_timeout() -> None:
    """
    Test case 6: Test command execution with custom timeout.
    """
    with patch(
        "pyutils_collection.ssh_functions.remote.ssh_execute_command.paramiko.SSHClient"
    ) as mock_client:
        with patch(
            "pyutils_collection.ssh_functions.remote.ssh_execute_command.getpass.getuser",
            return_value="testuser",
        ):
            mock_ssh = MagicMock()
            mock_client.return_value = mock_ssh
            mock_stdin = MagicMock()
            mock_stdout = MagicMock()
            mock_stdout.read.return_value = b"ok"
            mock_stdout.channel.recv_exit_status.return_value = 0
            mock_stderr = MagicMock()
            mock_stderr.read.return_value = b""
            mock_ssh.exec_command.return_value = (mock_stdin, mock_stdout, mock_stderr)

            result = ssh_execute_command(
                "host", "ls", user="user", password="pass", timeout=60.0
            )
            assert result["exit_code"] == 0
            mock_ssh.connect.assert_called_once_with(
                hostname="host",
                port=22,
                username="user",
                password="pass",
                key_filename=None,
                timeout=60.0,
            )


def test_ssh_execute_command_boundary_port_min() -> None:
    """
    Test case 7: Test command execution with minimum port value.
    """
    with patch(
        "pyutils_collection.ssh_functions.remote.ssh_execute_command.paramiko.SSHClient"
    ) as mock_client:
        with patch(
            "pyutils_collection.ssh_functions.remote.ssh_execute_command.getpass.getuser",
            return_value="testuser",
        ):
            mock_ssh = MagicMock()
            mock_client.return_value = mock_ssh
            mock_stdin = MagicMock()
            mock_stdout = MagicMock()
            mock_stdout.read.return_value = b"ok"
            mock_stdout.channel.recv_exit_status.return_value = 0
            mock_stderr = MagicMock()
            mock_stderr.read.return_value = b""
            mock_ssh.exec_command.return_value = (mock_stdin, mock_stdout, mock_stderr)

            result = ssh_execute_command(
                "host", "ls", user="user", password="pass", port=1
            )
            assert result["exit_code"] == 0


def test_ssh_execute_command_boundary_port_max() -> None:
    """
    Test case 8: Test command execution with maximum port value.
    """
    with patch(
        "pyutils_collection.ssh_functions.remote.ssh_execute_command.paramiko.SSHClient"
    ) as mock_client:
        with patch(
            "pyutils_collection.ssh_functions.remote.ssh_execute_command.getpass.getuser",
            return_value="testuser",
        ):
            mock_ssh = MagicMock()
            mock_client.return_value = mock_ssh
            mock_stdin = MagicMock()
            mock_stdout = MagicMock()
            mock_stdout.read.return_value = b"ok"
            mock_stdout.channel.recv_exit_status.return_value = 0
            mock_stderr = MagicMock()
            mock_stderr.read.return_value = b""
            mock_ssh.exec_command.return_value = (mock_stdin, mock_stdout, mock_stderr)

            result = ssh_execute_command(
                "host", "ls", user="user", password="pass", port=65535
            )
            assert result["exit_code"] == 0


def test_ssh_execute_command_type_error_host() -> None:
    """
    Test case 9: Test TypeError for invalid host type.
    """
    with pytest.raises(TypeError, match="host must be a string"):
        ssh_execute_command(123, "ls")


def test_ssh_execute_command_type_error_command() -> None:
    """
    Test case 10: Test TypeError for invalid command type.
    """
    with pytest.raises(TypeError, match="command must be a string"):
        ssh_execute_command("host", 123)


def test_ssh_execute_command_type_error_user() -> None:
    """
    Test case 11: Test TypeError for invalid user type.
    """
    with pytest.raises(TypeError, match="user must be a string or None"):
        ssh_execute_command("host", "ls", user=123)


def test_ssh_execute_command_type_error_password() -> None:
    """
    Test case 12: Test TypeError for invalid password type.
    """
    with pytest.raises(TypeError, match="password must be a string or None"):
        ssh_execute_command("host", "ls", password=123)


def test_ssh_execute_command_type_error_key_filename() -> None:
    """
    Test case 13: Test TypeError for invalid key_filename type.
    """
    with pytest.raises(TypeError, match="key_filename must be a string or None"):
        ssh_execute_command("host", "ls", key_filename=123)


def test_ssh_execute_command_type_error_port() -> None:
    """
    Test case 14: Test TypeError for invalid port type.
    """
    with pytest.raises(TypeError, match="port must be an integer"):
        ssh_execute_command("host", "ls", port="22")


def test_ssh_execute_command_type_error_timeout() -> None:
    """
    Test case 15: Test TypeError for invalid timeout type.
    """
    with pytest.raises(TypeError, match="timeout must be a number"):
        ssh_execute_command("host", "ls", timeout="30")


def test_ssh_execute_command_value_error_port_too_low() -> None:
    """
    Test case 16: Test ValueError for port value too low.
    """
    with pytest.raises(ValueError, match="port must be in 1-65535"):
        ssh_execute_command("host", "ls", port=0)


def test_ssh_execute_command_value_error_port_too_high() -> None:
    """
    Test case 17: Test ValueError for port value too high.
    """
    with pytest.raises(ValueError, match="port must be in 1-65535"):
        ssh_execute_command("host", "ls", port=70000)


def test_ssh_execute_command_value_error_timeout_negative() -> None:
    """
    Test case 18: Test ValueError for negative timeout.
    """
    with pytest.raises(ValueError, match="timeout must be positive"):
        ssh_execute_command("host", "ls", timeout=-5)


def test_ssh_execute_command_value_error_timeout_zero() -> None:
    """
    Test case 19: Test ValueError for zero timeout.
    """
    with pytest.raises(ValueError, match="timeout must be positive"):
        ssh_execute_command("host", "ls", timeout=0)


def test_ssh_execute_command_runtime_error_auth_failure() -> None:
    """
    Test case 20: Test RuntimeError for authentication failure.
    """
    with patch(
        "pyutils_collection.ssh_functions.remote.ssh_execute_command.paramiko.SSHClient"
    ) as mock_client:
        with patch(
            "pyutils_collection.ssh_functions.remote.ssh_execute_command.getpass.getuser",
            return_value="testuser",
        ):
            mock_ssh = MagicMock()
            mock_client.return_value = mock_ssh
            import paramiko

            mock_ssh.connect.side_effect = paramiko.AuthenticationException(
                "Auth failed"
            )

            with pytest.raises(RuntimeError, match="SSH authentication failed"):
                ssh_execute_command("host", "ls", user="user", password="badpass")


def test_ssh_execute_command_runtime_error_ssh_exception() -> None:
    """
    Test case 21: Test RuntimeError for SSH exception.
    """
    with patch(
        "pyutils_collection.ssh_functions.remote.ssh_execute_command.paramiko.SSHClient"
    ) as mock_client:
        with patch(
            "pyutils_collection.ssh_functions.remote.ssh_execute_command.getpass.getuser",
            return_value="testuser",
        ):
            mock_ssh = MagicMock()
            mock_client.return_value = mock_ssh
            import paramiko

            mock_ssh.connect.side_effect = paramiko.SSHException("SSH error")

            with pytest.raises(RuntimeError, match="SSH connection error"):
                ssh_execute_command("host", "ls", user="user", password="pass")


def test_ssh_execute_command_runtime_error_timeout() -> None:
    """
    Test case 22: Test RuntimeError for timeout.
    """
    with patch(
        "pyutils_collection.ssh_functions.remote.ssh_execute_command.paramiko.SSHClient"
    ) as mock_client:
        with patch(
            "pyutils_collection.ssh_functions.remote.ssh_execute_command.getpass.getuser",
            return_value="testuser",
        ):
            mock_ssh = MagicMock()
            mock_client.return_value = mock_ssh
            mock_ssh.connect.side_effect = TimeoutError("Connection timed out")

            with pytest.raises(RuntimeError, match="SSH command timed out"):
                ssh_execute_command("host", "ls", user="user", password="pass")


def test_ssh_execute_command_runtime_error_general() -> None:
    """
    Test case 23: Test RuntimeError for general exception.
    """
    with patch(
        "pyutils_collection.ssh_functions.remote.ssh_execute_command.paramiko.SSHClient"
    ) as mock_client:
        with patch(
            "pyutils_collection.ssh_functions.remote.ssh_execute_command.getpass.getuser",
            return_value="testuser",
        ):
            mock_ssh = MagicMock()
            mock_client.return_value = mock_ssh
            mock_ssh.connect.side_effect = Exception("Connection failed")

            with pytest.raises(RuntimeError, match="SSH command failed"):
                ssh_execute_command("host", "ls", user="user", password="pass")
