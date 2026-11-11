"""Gateway discovery must tolerate incomplete output and stalled commands."""

import subprocess
from unittest.mock import patch

import pytest
from pyutils_collection.network_functions.get_default_gateway import (
    _gateway_from_command,
    _parse_route_get_default,
)

pytestmark = [pytest.mark.unit, pytest.mark.network_functions]


@pytest.mark.parametrize("output", ["gateway:", "gateway:   \n", "Gateway:\t"])
def test_missing_gateway_value_returns_empty_string(output: str) -> None:
    assert _parse_route_get_default(output) == ""


def test_gateway_command_timeout_returns_empty_string() -> None:
    with patch(
        "pyutils_collection.network_functions.get_default_gateway.subprocess.run",
        side_effect=subprocess.TimeoutExpired(["ip", "route"], 5),
    ) as run:
        assert _gateway_from_command(["ip", "route"], lambda output: output) == ""
    assert run.call_args.kwargs["timeout"] == 5


def test_failed_gateway_command_does_not_parse_stdout() -> None:
    result = subprocess.CompletedProcess(["ip", "route"], 1, stdout="diagnostic")
    with patch(
        "pyutils_collection.network_functions.get_default_gateway.subprocess.run",
        return_value=result,
    ):
        assert _gateway_from_command(["ip", "route"], lambda output: output) == ""
