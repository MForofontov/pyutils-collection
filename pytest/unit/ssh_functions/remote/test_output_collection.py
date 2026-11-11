"""Output collection handles multiplexing, split UTF-8, and real deadlines."""

import importlib

import pytest

module = importlib.import_module("pyutils_collection.ssh_functions.remote._output")
pytestmark = [pytest.mark.unit, pytest.mark.ssh_functions]


class Stream:
    def __init__(self, channel):
        self.channel = channel
        self.closed = False

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.closed = True


def test_stderr_backpressure_and_split_utf8():
    class Channel:
        output = [b" \xe2", b"\x82\xac\n", b""]
        errors = [b"x" * 65536 for _ in range(40)] + [b""]

        def settimeout(self, value):
            assert value == 0

        def recv(self, size):
            if self.errors:
                raise TimeoutError()
            return self.output.pop(0)

        def recv_stderr(self, size):
            return self.errors.pop(0)

        def exit_status_ready(self):
            return True

        def recv_exit_status(self):
            return 7

    stdout = Stream(Channel())
    stderr = Stream(stdout.channel)
    assert module.read_command_output(stdout, stderr, 5) == ("€", "x" * (65536 * 40), 7)
    assert stdout.closed and stderr.closed


@pytest.mark.parametrize("eof", [True, False])
@pytest.mark.parametrize("input_data", [None, b"pending input"])
def test_deadline_includes_waiting_for_exit_status(monkeypatch, eof, input_data):
    now = [0.0]
    monkeypatch.setattr(module, "monotonic", lambda: now[0])
    monkeypatch.setattr(
        module, "sleep", lambda value: now.__setitem__(0, now[0] + value)
    )

    class Channel:
        def settimeout(self, value):
            pass

        def recv(self, size):
            if eof:
                return b""
            raise TimeoutError()

        recv_stderr = recv

        def send(self, data):
            raise TimeoutError()

        def exit_status_ready(self):
            return False

    stdout = Stream(Channel())
    stderr = Stream(stdout.channel)
    with pytest.raises(TimeoutError, match="deadline"):
        module.read_command_output(stdout, stderr, 0.03, input_data)
    assert stdout.closed and stderr.closed


def test_script_input_and_output_are_multiplexed():
    class Channel:
        def __init__(self):
            self.sent = bytearray()
            self.errors = [b"err", b""]
            self.output = [b"done", b""]
            self.input_eof = False

        def settimeout(self, value):
            pass

        def send(self, data):
            if self.errors:
                raise TimeoutError()
            count = min(len(data), 32768)
            self.sent.extend(data[:count])
            return count

        def shutdown_write(self):
            self.input_eof = True

        def recv(self, size):
            if not self.input_eof:
                raise TimeoutError()
            return self.output.pop(0)

        def recv_stderr(self, size):
            return self.errors.pop(0)

        def exit_status_ready(self):
            return True

        def recv_exit_status(self):
            return 0

    channel = Channel()
    stdout, stderr = Stream(channel), Stream(channel)
    data = b"echo \xe2\x82\xac\n" + b"x" * 200000
    assert module.read_command_output(stdout, stderr, 5, data) == ("done", "err", 0)
    assert channel.sent == data and channel.input_eof
