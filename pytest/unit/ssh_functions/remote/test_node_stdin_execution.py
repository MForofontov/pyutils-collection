"""Validate generated interpreter arguments with a real local Node executable."""

import importlib
import shlex
import shutil
import subprocess
from unittest.mock import MagicMock

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.ssh_functions]


def test_node_executes_supplied_script_from_stdin(tmp_path, monkeypatch):
    node = shutil.which("node")
    if node is None:
        pytest.skip("Node is unavailable for the interpreter argument probe")
    module = importlib.import_module(
        "pyutils_collection.ssh_functions.remote.ssh_execute_script"
    )
    script = tmp_path / "script.js"
    script.write_text("console.log('remote-stdin-executed')\n", encoding="utf-8")
    client = MagicMock()
    client.exec_command.return_value = (MagicMock(), MagicMock(), MagicMock())
    monkeypatch.setattr(module.paramiko, "SSHClient", lambda: client)

    def read_output(stdout, stderr, timeout, input_data=None):
        command = client.exec_command.call_args.args[0]
        arguments = shlex.split(command)
        assert arguments[0] == "node"
        result = subprocess.run(
            [node, *arguments[1:]],
            input=input_data,
            capture_output=True,
            timeout=10,
            check=False,
        )
        return (
            result.stdout.decode().strip(),
            result.stderr.decode().strip(),
            result.returncode,
        )

    monkeypatch.setattr(module, "read_command_output", read_output)
    assert module.ssh_execute_script("host", str(script), interpreter="node") == {
        "stdout": "remote-stdin-executed",
        "stderr": "",
        "exit_code": 0,
    }
    client.close.assert_called_once()
