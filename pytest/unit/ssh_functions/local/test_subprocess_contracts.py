"""Exercise CLI argument safety and the real subprocess text contract."""

import importlib
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

PREFIX = "pyutils_collection.ssh_functions.local."
pytestmark = [pytest.mark.unit, pytest.mark.ssh_functions]
HELPERS = [
    "ssh_execute_command",
    "ssh_execute_script",
    "ssh_copy_file",
    "ssh_check_connection",
]


def invoke(name, host="example.com", **kwargs):
    function = getattr(importlib.import_module(PREFIX + name), name)
    if name == "ssh_execute_command":
        return function(host, "echo hello", **kwargs)
    if name == "ssh_execute_script":
        return function(host, "script.sh", **kwargs)
    if name == "ssh_copy_file":
        return function("file.txt", "/tmp/file.txt", host, **kwargs)
    return function(host, **kwargs)


@pytest.mark.parametrize("name", HELPERS)
@pytest.mark.parametrize(
    "host", ["", "-oProxyCommand=untrusted", "bad\nhost", "user@host"]
)
def test_rejects_unsafe_destinations_before_launch(name, host):
    with patch("subprocess.run") as run:
        with pytest.raises(ValueError):
            invoke(name, host)
        run.assert_not_called()


@pytest.mark.parametrize("name", HELPERS)
@pytest.mark.parametrize("timeout", [float("nan"), float("inf")])
def test_rejects_nonfinite_timeout(name, timeout):
    with pytest.raises(ValueError, match="finite"):
        invoke(name, timeout=timeout)


def test_script_uses_real_subprocess_text_input(tmp_path):
    script = tmp_path / "script.sh"
    script.write_text("echo café\n", encoding="utf-8")
    module = importlib.import_module(PREFIX + "ssh_execute_script")
    real_run = subprocess.run

    def local_echo(_command, **kwargs):
        return real_run(
            [sys.executable, "-c", "import sys; sys.stdout.write(sys.stdin.read())"],
            encoding="utf-8",
            **kwargs,
        )

    with patch.object(module.subprocess, "run", side_effect=local_echo):
        result = module.ssh_execute_script("example.com", str(script))
    assert result["stdout"] == "echo café"


def test_scp_option_like_local_path_and_ipv6_are_unambiguous():
    with patch(
        "subprocess.run", return_value=subprocess.CompletedProcess([], 0, "", "")
    ) as run:
        invoke("ssh_copy_file", "::1")
    args = run.call_args.args[0]
    assert Path(args[-2]).is_absolute()
    assert args[-1] == "[::1]:/tmp/file.txt"
