"""Validation deadlines must terminate spawned worker processes as well."""

import subprocess
import sys
from pathlib import Path

import psutil
import pytest

ROOT = Path(__file__).resolve().parents[3]
pytestmark = [pytest.mark.unit, pytest.mark.dev_utilities]


def test_runner_preserves_failure_status_and_output(tmp_path):
    log = tmp_path / "check.log"
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/run_with_deadline.py"),
            "--seconds",
            "10",
            "--log",
            str(log),
            "--",
            sys.executable,
            "-c",
            "print('diagnostic'); raise SystemExit(7)",
        ],
        capture_output=True,
        text=True,
        timeout=20,
    )
    assert result.returncode == 7
    assert "diagnostic" in log.read_text()


def test_deadline_terminates_child_process(tmp_path):
    log = tmp_path / "check.log"
    command = (
        "import subprocess, sys, time; "
        "child = subprocess.Popen([sys.executable, '-c', 'import time; time.sleep(60)']); "
        "print(child.pid, flush=True); time.sleep(60)"
    )
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/run_with_deadline.py"),
            "--seconds",
            "3",
            "--log",
            str(log),
            "--",
            sys.executable,
            "-c",
            command,
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 124, result.stdout + result.stderr
    child_pid = int(log.read_text().splitlines()[0])
    if psutil.pid_exists(child_pid):
        assert psutil.Process(child_pid).status() == psutil.STATUS_ZOMBIE
