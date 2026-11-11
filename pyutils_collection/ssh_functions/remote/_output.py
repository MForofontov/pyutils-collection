"""Drain both SSH output streams without exhausting their shared channel window."""

from time import monotonic, sleep

from paramiko.channel import ChannelFile


def read_command_output(
    stdout: ChannelFile,
    stderr: ChannelFile,
    timeout: float,
    input_data: bytes | None = None,
) -> tuple[str, str, int]:
    channel = stdout.channel
    channel.settimeout(0.0)
    deadline = monotonic() + timeout
    output: list[bytes] = []
    errors: list[bytes] = []
    output_eof = error_eof = False
    sent = 0
    input_eof = input_data is None
    with stdout, stderr:
        while True:
            remaining = deadline - monotonic()
            if remaining <= 0:
                raise TimeoutError("SSH output collection exceeded its deadline")
            progressed = False
            if input_data is not None and not input_eof:
                if sent < len(input_data):
                    try:
                        count = channel.send(input_data[sent : sent + 65536])
                    except TimeoutError:
                        pass
                    else:
                        if count == 0:
                            raise EOFError(
                                "SSH channel closed before script input completed"
                            )
                        sent += count
                        progressed = True
                if sent == len(input_data):
                    channel.shutdown_write()
                    input_eof = True
            if not output_eof:
                try:
                    chunk = channel.recv(65536)
                except TimeoutError:
                    pass
                else:
                    if chunk:
                        output.append(chunk)
                        progressed = True
                    else:
                        output_eof = True
            if not error_eof:
                try:
                    chunk = channel.recv_stderr(65536)
                except TimeoutError:
                    pass
                else:
                    if chunk:
                        errors.append(chunk)
                        progressed = True
                    else:
                        error_eof = True
            # Exit status may arrive before the final data, or after EOF. Wait
            # for both streams and the status so no trailing data is discarded.
            if output_eof and error_eof and channel.exit_status_ready():
                status = channel.recv_exit_status()
                break
            if not progressed:
                sleep(min(0.01, remaining))
    return (
        b"".join(output).decode("utf-8").strip(),
        b"".join(errors).decode("utf-8").strip(),
        status,
    )
