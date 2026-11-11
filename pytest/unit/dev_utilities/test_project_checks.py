"""Behavioral checks for the project's validation entry points."""

import json
import os
import re
import shutil
import subprocess
import sys
import tomllib
from pathlib import Path

import yaml
from packaging.requirements import Requirement

import pytest

ROOT = Path(__file__).resolve().parents[3]
pytestmark = [pytest.mark.unit, pytest.mark.dev_utilities]


@pytest.mark.parametrize(
    ("filename", "extra"),
    [("requirements.txt", None), ("requirements_dev.txt", "dev")],
)
def test_dependency_entry_points_agree(filename: str, extra: str | None) -> None:
    metadata = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project = metadata["project"]
    declared = (
        project["dependencies"]
        if extra is None
        else project["optional-dependencies"][extra]
    )
    requirements = [
        line.strip()
        for line in (ROOT / filename).read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    assert {Requirement(item) for item in declared} == {
        Requirement(item) for item in requirements
    }


def _bash() -> str:
    if sys.platform == "win32":
        git = shutil.which("git")
        if git:
            candidate = Path(git).resolve().parents[1] / "bin" / "bash.exe"
            if candidate.is_file():
                return str(candidate)
        pytest.skip("Git Bash is required to test the Bash entry point on Windows")
    bash = shutil.which("bash")
    if bash is None:
        pytest.skip("Bash is not installed")
    return bash


@pytest.mark.parametrize("test_status", [0, 1, 2, 5])
@pytest.mark.parametrize("generate_report", ["true", "false"])
def test_shell_runner_preserves_test_status(
    tmp_path: Path, test_status: int, generate_report: str
) -> None:
    result = _run_shell(tmp_path, test_status, generate_report)
    assert result.returncode == test_status, result.stdout + result.stderr
    assert (tmp_path / "report-created").exists() == (
        test_status == 0 and generate_report == "true"
    )


def test_shell_runner_preserves_quoted_arguments_without_shell_evaluation(
    tmp_path: Path,
) -> None:
    result = _run_shell(
        tmp_path,
        0,
        "false",
        '-k "name with spaces" --log-file="$(touch injected)"',
    )
    assert result.returncode == 0, result.stdout + result.stderr
    arguments = (tmp_path / "arguments").read_text(encoding="utf-8").splitlines()
    assert "name with spaces" in arguments
    assert "--log-file=$(touch injected)" in arguments
    assert not (tmp_path / "injected").exists()


def _run_shell(
    tmp_path: Path, status: int, generate_report: str, extra_args: str = ""
) -> subprocess.CompletedProcess[str]:
    # Only pytest and Allure are faked. Quoting is parsed by the real Python.
    harness = r"""
    python() {
        if [ "$1" = "-m" ] && [ "$2" = "pytest" ]; then
            printf '%s\n' "$@" > "$ARGUMENT_LOG"
            return "$TEST_STATUS"
        fi
        "$REAL_PYTHON" "$@"
    }
    allure() { touch "$REPORT_MARKER"; }
    export -f python allure
    bash "$RUNNER" "$TEST_PATH" results report "$GENERATE_REPORT" false "$EXTRA_ARGS" false
    """
    env = {
        **os.environ,
        "REAL_PYTHON": Path(sys.executable).as_posix(),
        "RUNNER": (ROOT / "pytest.sh").as_posix(),
        "TEST_PATH": "directory with spaces",
        "ARGUMENT_LOG": (tmp_path / "arguments").as_posix(),
        "REPORT_MARKER": (tmp_path / "report-created").as_posix(),
        "TEST_STATUS": str(status),
        "GENERATE_REPORT": generate_report,
        "EXTRA_ARGS": extra_args,
        "CI": "true",
    }
    return subprocess.run(
        [_bash(), "-c", harness],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        timeout=30,
    )


def _workflow_step(filename: str, name: str) -> str:
    workflow = yaml.safe_load(
        (ROOT / ".github" / "workflows" / filename).read_text(encoding="utf-8")
    )
    for job in workflow["jobs"].values():
        for step in job.get("steps", []):
            if step.get("name") == name:
                return str(step["run"])
    raise AssertionError(f"Missing workflow step: {name}")


def _workflow_expressions(script: str, values: dict[str, str]) -> str:
    return re.sub(
        r"\$\{\{\s*(.*?)\s*\}\}", lambda match: values[match.group(1).strip()], script
    )


@pytest.mark.parametrize("status", [0, 1, 2])
def test_lint_pipeline_preserves_checker_failure(tmp_path: Path, status: int) -> None:
    checker = _workflow_step("lint-check.yml", "Ruff - lint (console)")
    environment = {
        **os.environ,
        "CHECKER_STATUS": str(status),
        "GITHUB_OUTPUT": (tmp_path / "outputs").as_posix(),
        "GITHUB_STEP_SUMMARY": (tmp_path / "summary").as_posix(),
    }
    result = subprocess.run(
        [
            _bash(),
            "-c",
            'ruff() { echo "checker output"; return "$CHECKER_STATUS"; }; export -f ruff\n'
            + checker,
        ],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0, result.stderr
    captured = (tmp_path / "outputs").read_text().strip().split("=", 1)[1]
    assert captured == str(status)
    summary = _workflow_expressions(
        _workflow_step("lint-check.yml", "Summary & final status"),
        {
            "steps.ruff_fmt.outputs.exit_code": "0",
            "steps.ruff_lint.outputs.exit_code": captured,
            "steps.mypy.outputs.exit_code": "0",
            "steps.pylint.outputs.exit_code": "",
            "inputs.run_pylint": "false",
            "inputs.fail_on_any_issue": "",
            "github.event_name": "pull_request",
        },
    )
    result = subprocess.run(
        [_bash(), "-c", summary],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert (result.returncode != 0) == (status != 0), result.stdout + result.stderr


@pytest.mark.parametrize(
    ("status", "event", "fail_on_findings", "audit_status", "fails"),
    [
        ("0", "pull_request", "", "0", False),
        ("1", "pull_request", "", "0", True),
        ("2", "workflow_dispatch", "false", "", True),
        ("", "workflow_dispatch", "false", "", True),
        ("1", "workflow_dispatch", "false", "", False),
        ("0", "pull_request", "", "", True),
    ],
)
def test_security_gate_distinguishes_findings_and_tool_errors(
    tmp_path: Path,
    status: str,
    event: str,
    fail_on_findings: str,
    audit_status: str,
    fails: bool,
) -> None:
    script = _workflow_expressions(
        _workflow_step("security-check.yml", "Decide final status"),
        {
            "steps.bandit_json.outputs.exit_code": status,
            "inputs.upload_sarif": "false",
            "steps.bandit_sarif.outputs.exit_code": "",
            "github.event_name": event,
            "inputs.run_pip_audit": "false",
            "steps.pip_audit.outputs.exit_code": audit_status,
            "inputs.fail_on_findings": fail_on_findings,
        },
    )
    result = subprocess.run(
        [_bash(), "-c", script],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert (result.returncode != 0) == fails, result.stdout + result.stderr


@pytest.mark.parametrize("report_kind", ["valid", "errors", "empty", "missing"])
def test_security_report_validation_rejects_incomplete_scans(
    tmp_path: Path, report_kind: str
) -> None:
    if report_kind != "missing":
        report = {"errors": [], "metrics": {"_totals": {}, "package.py": {}}}
        if report_kind == "errors":
            report["errors"] = [{"filename": "package.py", "reason": "parse error"}]
        if report_kind == "empty":
            report["metrics"] = {"_totals": {}}
        (tmp_path / "bandit.json").write_text(json.dumps(report), encoding="utf-8")
    script = _workflow_step("security-check.yml", "Validate scan reports")
    result = subprocess.run(
        [
            _bash(),
            "-c",
            'python() { "$REAL_PYTHON" "$@"; }; export -f python\n' + script,
        ],
        cwd=tmp_path,
        env={
            **os.environ,
            "REAL_PYTHON": Path(sys.executable).as_posix(),
            "AUDIT_ENABLED": "false",
        },
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert (result.returncode == 0) == (report_kind == "valid"), (
        result.stdout + result.stderr
    )
