"""Run service checks in a unique disposable Compose project on loopback ports."""

import argparse
import json
import os
import subprocess
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPOSE = ROOT / "pytest/integration/services/compose.yml"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--report-dir", type=Path, default=ROOT / ".major-check/services"
    )
    parser.add_argument(
        "--services",
        nargs="+",
        choices=["postgres", "mysql", "ssh"],
        default=["postgres", "mysql", "ssh"],
    )
    args = parser.parse_args()
    report = args.report_dir.resolve()
    report.mkdir(parents=True, exist_ok=True)
    project = "pyutils-audit-" + uuid.uuid4().hex[:12]
    prefix = ["docker", "compose", "-f", str(COMPOSE), "-p", project]
    (report / "project.txt").write_text(project + "\n", encoding="utf-8")

    def compose(*arguments: str, timeout: int = 120) -> str:
        # Reuse the process-tree deadline runner so Docker's Compose/Buildx
        # children cannot survive a timed-out command on Windows or Linux.
        command_log = (
            report / f"compose-{len(list(report.glob('compose-*.log'))):02d}.log"
        )
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/run_with_deadline.py"),
                "--seconds",
                str(timeout),
                "--log",
                str(command_log),
                "--",
                *prefix,
                *arguments,
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=timeout + 45,
        )
        with (report / "compose.log").open("a", encoding="utf-8") as log:
            log.write(" ".join(arguments) + "\n" + result.stdout + result.stderr + "\n")
        result.check_returncode()
        return result.stdout.strip()

    status = 1
    try:
        print(
            f"Starting isolated project {project}: {', '.join(args.services)}",
            flush=True,
        )
        compose(
            "up",
            "-d",
            "--build",
            "--wait",
            "--wait-timeout",
            "360",
            *args.services,
            timeout=900,
        )
        env = os.environ.copy()
        env["PYUTILS_SERVICE_TESTS"] = "1"
        tests = []
        endpoints = {}
        for service in args.services:
            internal = {"postgres": "5432", "mysql": "3306", "ssh": "22"}[service]
            endpoint = compose("port", service, internal)
            host, port = endpoint.rsplit(":", 1)
            if host != "127.0.0.1":
                raise RuntimeError(
                    f"Service must be restricted to loopback: {endpoint}"
                )
            endpoints[service] = endpoint
            if service in ("postgres", "mysql"):
                dialect = (
                    "postgresql+pg8000" if service == "postgres" else "mysql+pymysql"
                )
                env[f"PYUTILS_{service.upper()}_URL"] = (
                    f"{dialect}://audit:pyutils_test_only@{endpoint}/pyutils_audit"
                )
                if "pytest/integration/test_database_services.py" not in tests:
                    tests.append("pytest/integration/test_database_services.py")
            else:
                public = compose(
                    "exec", "-T", "ssh", "cat", "/etc/ssh/ssh_host_ed25519_key.pub"
                ).split()
                known_hosts = report / "known_hosts"
                known_hosts.write_text(
                    f"[{host}]:{port} {public[0]} {public[1]}\n", encoding="utf-8"
                )
                env.update(
                    PYUTILS_SSH_PORT=port, PYUTILS_SSH_KNOWN_HOSTS=str(known_hosts)
                )
                tests.append("pytest/integration/test_ssh_services.py")
        container_output = compose("ps", "--format", "json")
        try:
            containers = json.loads(container_output)
        except json.JSONDecodeError:
            containers = [
                json.loads(line)
                for line in container_output.splitlines()
                if line.strip()
            ]
        if isinstance(containers, dict):
            containers = [containers]
        (report / "services.json").write_text(
            json.dumps(
                {
                    "project": project,
                    "endpoints": endpoints,
                    "containers": containers,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"Services ready; running {len(tests)} test files", flush=True)
        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/run_with_deadline.py"),
                "--seconds",
                "180",
                "--log",
                str(report / "tests.log"),
                "--",
                sys.executable,
                "-u",
                "-m",
                "pytest",
                *tests,
                "-ra",
                f"--junitxml={report / 'tests.xml'}",
            ],
            cwd=ROOT,
            env=env,
            timeout=210,
        )
        status = result.returncode
    finally:
        try:
            compose("logs", "--no-color", timeout=30)
        finally:
            print(f"Removing only isolated project {project}", flush=True)
            compose(
                "down",
                "--volumes",
                "--remove-orphans",
                "--rmi",
                "local",
                "--timeout",
                "5",
                timeout=60,
            )
    return status


if __name__ == "__main__":
    raise SystemExit(main())
