"""Repeated samples must measure counter increments, not sum lifetime totals."""

import importlib
from types import SimpleNamespace

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.decorators]


@pytest.mark.parametrize("reused_pid", [False, True])
@pytest.mark.parametrize("initial_denied", [False, True])
def test_repeated_resource_samples_count_only_counter_increments(
    monkeypatch, capsys, reused_pid, initial_denied
):
    module = importlib.import_module(
        "pyutils_collection.decorators.time_and_resource_function"
    )

    class Event:
        def __init__(self):
            self.stopped = False
            self.waits = 0

        def is_set(self):
            return self.stopped

        def set(self):
            self.stopped = True

        def wait(self, *args, **kwargs):
            self.waits += 1
            if self.waits == 2:
                self.set()
            return self.stopped

    class Thread:
        def __init__(self, *, target, **kwargs):
            self.target = target

        def start(self):
            self.target()

    def io(count):
        return SimpleNamespace(
            read_count=count,
            write_count=count * 2,
            read_bytes=count * 10,
            write_bytes=count * 20,
        )

    child_io = iter([io(100), io(104)])
    child_ctx = iter([30, 33])
    creation_times = iter([1.0, 1.0, 2.0, 2.0])
    child = SimpleNamespace(
        pid=42,
        create_time=lambda: next(creation_times) if reused_pid else 1.0,
        io_counters=lambda: next(child_io),
        num_ctx_switches=lambda: SimpleNamespace(
            voluntary=next(child_ctx), involuntary=0
        ),
    )
    parent_io = iter([io(10), io(12)])
    parent_ctx = iter([10, 15, 20])

    def parent_context():
        count = next(parent_ctx)
        if initial_denied and count == 10:
            raise PermissionError("initial sample unavailable")
        return SimpleNamespace(voluntary=count, involuntary=0)

    parent = SimpleNamespace(
        io_counters=lambda: next(parent_io),
        num_ctx_switches=parent_context,
        children=lambda **kwargs: [child],
    )
    disk = iter([io(1000), io(1100)])
    monkeypatch.setattr(
        module, "threading", SimpleNamespace(Event=Event, Thread=Thread)
    )
    monkeypatch.setattr(
        module,
        "psutil",
        SimpleNamespace(
            Process=lambda: parent,
            disk_io_counters=lambda: next(disk),
            NoSuchProcess=ProcessLookupError,
            AccessDenied=PermissionError,
        ),
    )

    @module.time_and_resource_function(
        monitor_memory=False,
        monitor_cpu=False,
        monitor_io=True,
        monitor_network=False,
        monitor_disk=True,
        monitor_threads=False,
        monitor_gc=False,
        monitor_context_switches=True,
        monitor_open_files=False,
        monitor_page_faults=False,
    )
    def work():
        return 7

    assert work() == 7
    lines = capsys.readouterr().out.splitlines()
    expected_reads = 2 if reused_pid else 6
    expected_context = (5 if initial_denied else 10) + (0 if reused_pid else 3)
    assert f"Read operations: {expected_reads}" in lines
    assert f"Write operations: {expected_reads * 2}" in lines
    assert f"Voluntary context switches: {expected_context}" in lines
    assert "Disk read bytes: 1000" in lines
    assert "Disk write bytes: 2000" in lines
