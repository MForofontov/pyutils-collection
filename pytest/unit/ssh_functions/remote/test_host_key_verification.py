"""Remote utilities verify known host keys and close clients on setup errors."""

import importlib
from pathlib import Path
from unittest.mock import MagicMock, patch

import paramiko

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.ssh_functions]


@pytest.mark.parametrize(
    "name",
    [
        "ssh_check_connection",
        "ssh_copy_file",
        "ssh_execute_command",
        "ssh_execute_script",
    ],
)
@pytest.mark.parametrize("failure", ["connect", "load_system_host_keys"])
def test_host_keys_verified_and_client_closed(
    tmp_path: Path, name: str, failure: str
) -> None:
    module = importlib.import_module(f"pyutils_collection.ssh_functions.remote.{name}")
    function = getattr(module, name)
    local = tmp_path / "script.sh"
    local.write_text("echo hello", encoding="utf-8")
    arguments = {
        "ssh_check_connection": ("host",),
        "ssh_copy_file": (str(local), "/tmp/script.sh", "host"),
        "ssh_execute_command": ("host", "whoami"),
        "ssh_execute_script": ("host", str(local)),
    }[name]
    client = MagicMock()
    getattr(client, failure).side_effect = paramiko.SSHException("untrusted host key")
    with patch.object(module.paramiko, "SSHClient", return_value=client):
        if name == "ssh_check_connection":
            assert function(*arguments)["success"] is False
        else:
            with pytest.raises(RuntimeError, match="untrusted host key"):
                function(*arguments)
    client.load_system_host_keys.assert_called_once_with()
    client.close.assert_called_once_with()
    if failure == "connect":
        policy = client.set_missing_host_key_policy.call_args.args[0]
        assert isinstance(policy, paramiko.RejectPolicy)
        assert [call[0] for call in client.method_calls[:3]] == [
            "load_system_host_keys",
            "set_missing_host_key_policy",
            "connect",
        ]
    else:
        client.connect.assert_not_called()
