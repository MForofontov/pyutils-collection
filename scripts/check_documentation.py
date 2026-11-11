"""Require documentation impact for relevant committed changes (stdlib only)."""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[1]
DOC_NAMES = {"README.md", "CHANGELOG.md", "CONTRIBUTING.md", "MAINTENANCE_PLAN.md"}
AI_ROOTS = {".agents", ".codex", ".claude", ".gemini"}
CONFIG_NAMES = {
    "pyproject.toml",
    "pytest.sh",
    ".gitignore",
    "AGENTS.md",
    "CLAUDE.md",
    "GEMINI.md",
}


def generated(path: str) -> bool:
    parts = PurePosixPath(path).parts
    return any(
        part in {"__pycache__", ".pytest_cache", ".ruff_cache", ".mypy_cache", "_build"}
        for part in parts
    ) or PurePosixPath(path).suffix in {".pyc", ".pyo"}


def git(*args: str, root: Path = ROOT) -> str:
    """Run fixed Git arguments, never a shell or PR-provided commands."""
    return subprocess.check_output(
        ["git", *args], cwd=root, encoding="utf-8", errors="surrogateescape"
    ).strip("\n")


def changed_paths(base: str, head: str, root: Path = ROOT) -> list[tuple[str, str]]:
    """Include old and new rename paths; compare against the true merge base."""
    base_sha = git(
        "rev-parse", "--verify", "--end-of-options", f"{base}^{{commit}}", root=root
    )
    head_sha = git(
        "rev-parse", "--verify", "--end-of-options", f"{head}^{{commit}}", root=root
    )
    ancestor = git("merge-base", base_sha, head_sha, root=root)
    fields = git(
        "diff",
        "--name-status",
        "-z",
        "--find-renames",
        ancestor,
        head_sha,
        "--",
        root=root,
    ).split("\0")
    changes = []
    index = 0
    while index < len(fields) and fields[index]:
        status, path = fields[index], fields[index + 1]
        index += 2
        if status.startswith(("R", "C")):
            changes.append(("D" if status.startswith("R") else "C", path))
            changes.append(("A", fields[index]))
            index += 1
        else:
            changes.append((status, path))
    return changes


def requires_documentation(path: str) -> bool:
    """Classify maintained implementation/configuration, excluding generated files."""
    parts = PurePosixPath(path).parts
    if not parts or generated(path):
        return False
    if parts[0] in {"pyutils_collection", "scripts"}:
        return True
    if parts[0] in AI_ROOTS:
        return True
    if path.startswith(".github/workflows/"):
        return True
    if path in {".github/copilot-instructions.md", ".github/pull_request_template.md"}:
        return True
    return path in CONFIG_NAMES or (
        len(parts) == 1
        and parts[0].startswith("requirements")
        and path.endswith(".txt")
    )


def is_documentation(path: str) -> bool:
    parts = PurePosixPath(path).parts
    if not parts or generated(path) or parts[0] in AI_ROOTS | {".github"}:
        return False
    return (
        path in DOC_NAMES
        or (parts[0] == "docs" and path.endswith(".md"))
        or (parts[0] == "pyutils_collection" and parts[-1] == "README.md")
        or (parts[0] == "pytest" and parts[-1] == "README.md")
    )


def exception_reason(body: str) -> str:
    """Read an explicit explanation outside comments, code fences, and quotes."""
    body = re.sub(r"<!--.*?(?:-->|\Z)", "", body, flags=re.S)
    fence = ""
    for line in body.splitlines():
        stripped = line.strip()
        marker = re.match(r"(`{3,}|~{3,})", stripped)
        if marker:
            token = marker.group(1)
            if not fence:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = ""
            continue
        if fence or line.startswith(("    ", "\t")) or stripped.startswith(">"):
            continue
        match = re.fullmatch(r"Documentation not required:\s*(.+)", stripped, re.I)
        if match:
            reason = match.group(1).strip()
            if reason.casefold() not in {
                "n/a",
                "none",
                "todo",
                "tbd",
                "<specific reason>",
            }:
                return reason
    return ""


def check(changes: list[tuple[str, str]], body: str) -> tuple[bool, str]:
    relevant = sorted({path for _, path in changes if requires_documentation(path)})
    if not relevant:
        return True, "No implementation/configuration changes require documentation."
    docs = sorted(
        {path for status, path in changes if status != "D" and is_documentation(path)}
    )
    if docs:
        return True, "Documentation updated: " + ", ".join(docs)
    reason = exception_reason(body)
    if reason:
        return True, "Documentation exception (review required): " + reason
    return False, (
        "Documentation impact missing for: "
        + ", ".join(relevant)
        + ". Update affected documentation/changelog or add a nonempty "
        "'Documentation not required: <specific reason>' line to the PR body. "
        "See CONTRIBUTING.md."
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", required=True)
    parser.add_argument("--head", default="HEAD")
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--body-file", type=Path)
    source.add_argument("--event-file", type=Path)
    args = parser.parse_args()
    try:
        body = ""
        if args.event_file:
            event = json.loads(args.event_file.read_text(encoding="utf-8"))
            body = event["pull_request"].get("body") or ""
        elif args.body_file:
            body = args.body_file.read_text(encoding="utf-8")
        success, message = check(changed_paths(args.base, args.head), body)
    except (
        OSError,
        subprocess.CalledProcessError,
        ValueError,
        KeyError,
        TypeError,
    ) as error:
        print(f"Documentation check could not run: {error}", file=sys.stderr)
        return 2
    # Do not echo PR text as a GitHub Actions command/annotation.
    print(json.dumps({"passed": success, "message": message}, ensure_ascii=True))
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
