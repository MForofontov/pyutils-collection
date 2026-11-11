"""Real OpenSSH/SFTP checks with a fixture trust store and no user key discovery."""

import hashlib
import os
from pathlib import Path

import paramiko

import pytest
from pyutils_collection.ssh_functions.remote.ssh_check_connection import (
    ssh_check_connection,
)
from pyutils_collection.ssh_functions.remote.ssh_copy_file import ssh_copy_file
from pyutils_collection.ssh_functions.remote.ssh_execute_command import (
    ssh_execute_command,
)
from pyutils_collection.ssh_functions.remote.ssh_execute_script import (
    ssh_execute_script,
)

pytestmark = [pytest.mark.integration, pytest.mark.ssh_functions]


@pytest.fixture
def ssh(monkeypatch):
    port = os.environ.get("PYUTILS_SSH_PORT")
    if os.environ.get("PYUTILS_SERVICE_TESTS") != "1" or not port:
        pytest.skip(
            "run scripts/run_service_integration.py to start disposable OpenSSH"
        )
    known_hosts = os.environ["PYUTILS_SSH_KNOWN_HOSTS"]
    original = paramiko.SSHClient

    class IsolatedClient(original):
        def load_system_host_keys(self, filename=None):
            return super().load_system_host_keys(filename or known_hosts)

        def connect(self, *args, **kwargs):
            return super().connect(
                *args, **kwargs, allow_agent=False, look_for_keys=False
            )

    monkeypatch.setattr(paramiko, "SSHClient", IsolatedClient)
    return {
        "host": "127.0.0.1",
        "port": int(port),
        "user": "audit",
        "password": "pyutils_test_only",
        "timeout": 5,
    }


def test_real_ssh_connection_and_authentication_failure(ssh):
    assert ssh_check_connection(**ssh)["success"]
    assert not ssh_check_connection(**{**ssh, "password": "incorrect_test_password"})[
        "success"
    ]


def test_real_ssh_returns_unicode_output_and_nonzero_status(ssh):
    result = ssh_execute_command(
        command="printf 'olá\\n'; printf 'aviso\\n' >&2; exit 7", **ssh
    )
    assert result == {"stdout": "olá", "stderr": "aviso", "exit_code": 7}


def test_real_ssh_rejects_unknown_host_key(ssh, monkeypatch, tmp_path):
    empty = tmp_path / "known_hosts"
    empty.touch()
    monkeypatch.setattr(
        paramiko.SSHClient,
        "load_system_host_keys",
        lambda self: self.load_host_keys(str(empty)),
    )
    result = ssh_check_connection(**ssh)
    assert not result["success"]
    assert "known_hosts" in result["error"]


def test_real_sftp_copies_binary_contents(ssh, tmp_path):
    content = bytes(range(256)) * 4096
    source = tmp_path / "payload.bin"
    source.write_bytes(content)
    remote = f"/home/audit/{tmp_path.name}.bin"
    result = ssh_copy_file(str(source), remote, **ssh)
    assert result["bytes_transferred"] == len(content)
    checked = ssh_execute_command(command=f"sha256sum '{remote}'", **ssh)
    assert checked["stdout"].split()[0] == hashlib.sha256(content).hexdigest()


@pytest.mark.parametrize("mode", ["command", "script", "large-script"])
def test_real_ssh_drains_stderr_larger_than_channel_window(ssh, tmp_path: Path, mode):
    command = "head -c 3145728 /dev/zero >&2; printf done"
    if mode != "command":
        source = tmp_path / "large-stderr.sh"
        content = (
            command
            if mode == "script"
            else "head -c 3145728 /dev/zero >&2\n#" + "x" * 3145728 + "\nprintf done"
        )
        source.write_text(content, encoding="utf-8")
        result = ssh_execute_script(script_path=str(source), interpreter="sh", **ssh)
    else:
        result = ssh_execute_command(command=command, **ssh)
    assert result == {"stdout": "done", "stderr": "\x00" * 3145728, "exit_code": 0}


def test_real_ssh_timeout(ssh):
    with pytest.raises(RuntimeError, match="timed out"):
        ssh_execute_command(command="sleep 10", **{**ssh, "timeout": 1})
