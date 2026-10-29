"""Resource sampling must not turn a completed call into an indefinite wait."""

import subprocess
import sys
from pathlib import Path

import pytest

from pyutils_collection.decorators import time_and_resource_function

pytestmark = [pytest.mark.unit, pytest.mark.decorators]
ROOT = Path(__file__).resolve().parents[3]


@pytest.mark.parametrize("blocked", [False, True])
def test_shutdown_interrupts_long_sample_intervals_and_bounds_os_waits(
    tmp_path, blocked
):
    code = r"""
import importlib
import sys
import threading
import warnings
from types import SimpleNamespace

module = importlib.import_module('pyutils_collection.decorators.time_and_resource_function')
sampled = threading.Event()
release = threading.Event()
blocked = sys.argv[1] == 'True'

class Process:
    def memory_info(self):
        sampled.set()
        if blocked:
            release.wait()
        return SimpleNamespace(rss=1)
    def children(self, **kwargs):
        return []

module.psutil.Process = Process

@module.time_and_resource_function(
    monitor_memory=True, monitor_cpu=False, monitor_io=False,
    monitor_network=False, monitor_disk=False, monitor_threads=False,
    monitor_gc=False, monitor_context_switches=False,
    monitor_open_files=False, monitor_page_faults=False, interval=3600,
)
def work():
    assert sampled.wait(3)
    return 7

with warnings.catch_warnings(record=True) as captured:
    warnings.simplefilter('always')
    assert work() == 7
    assert bool(captured) == blocked
release.set()
for thread in threading.enumerate():
    if thread.name == 'pyutils-resource-monitor':
        thread.join(timeout=2)
        assert not thread.is_alive()
print('shutdown verified')
"""
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/run_with_deadline.py"),
            "--seconds",
            "10",
            "--log",
            str(tmp_path / "monitor.log"),
            "--",
            sys.executable,
            "-c",
            code,
            str(blocked),
        ],
        capture_output=True,
        text=True,
        timeout=20,
        cwd=ROOT,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "shutdown verified" in result.stdout


@pytest.mark.parametrize("interval", [0, -1, float("nan"), float("inf")])
def test_invalid_monitor_intervals(interval):
    with pytest.raises(ValueError, match="finite and positive"):
        time_and_resource_function(interval=interval)
