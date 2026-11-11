import pytest

from pyutils_collection.ssh_functions.remote.ssh_execute_script import ssh_execute_script

pytestmark = [pytest.mark.unit, pytest.mark.ssh_functions]


def test_ssh_execute_script_rejects_unsafe_interpreter(tmp_path) -> None:
    script = tmp_path / "script.sh"
    script.write_text("echo hi\n", encoding="utf-8")
    with pytest.raises(ValueError, match="interpreter must be one of"):
        ssh_execute_script(
            "example.com",
            str(script),
            user="user",
            password="pass",
            interpreter="bash; rm -rf /",
        )
