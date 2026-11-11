"""Keep legacy client mocks at the output-adapter boundary, not the wire layer."""

import importlib

import pytest


@pytest.fixture
def mocked_output_reader(monkeypatch):
    def read(stdout, stderr, timeout, input_data=None):
        return (
            stdout.read().decode("utf-8").strip(),
            stderr.read().decode("utf-8").strip(),
            stdout.channel.recv_exit_status(),
        )

    for name in ("ssh_execute_command", "ssh_execute_script"):
        module = importlib.import_module(
            "pyutils_collection.ssh_functions.remote." + name
        )
        monkeypatch.setattr(module, "read_command_output", read)
