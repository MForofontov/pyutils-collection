"""Non-finite deadlines must fail before creating a network client."""

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

pytestmark = [pytest.mark.unit, pytest.mark.ssh_functions]


@pytest.mark.parametrize(
    "function,arguments",
    [
        (ssh_check_connection, {}),
        (ssh_copy_file, {"local_path": "unused", "remote_path": "unused"}),
        (ssh_execute_command, {"command": "unused"}),
        (ssh_execute_script, {"script_path": "unused"}),
    ],
)
@pytest.mark.parametrize("timeout", [float("nan"), float("inf")])
def test_nonfinite_timeout_is_rejected_before_connecting(
    monkeypatch, function, arguments, timeout
):
    monkeypatch.setattr(
        "paramiko.SSHClient", lambda: pytest.fail("client must not be created")
    )
    with pytest.raises(ValueError, match="positive"):
        function(host="unused", timeout=timeout, **arguments)
