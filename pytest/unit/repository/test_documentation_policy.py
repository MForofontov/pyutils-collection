"""Exercise documentation policy and real Git merge-base/rename behavior."""

import json
import subprocess
import sys

import pytest
from scripts.check_documentation import (
    ROOT,
    changed_paths,
    check,
    exception_reason,
    requires_documentation,
)


@pytest.mark.parametrize(
    "path",
    [
        "pyutils_collection/file_functions/example.py",
        "pyutils_collection/py.typed",
        "scripts/check_documentation.py",
        "scripts/helper.ps1",
        "pyutils_collection/example/schema.sql",
        "pyproject.toml",
        "requirements_integration.txt",
        ".github/workflows/test-check.yml",
        ".github/copilot-instructions.md",
        ".github/pull_request_template.md",
        ".agents/skills/major-check/SKILL.md",
        ".cursor/rules/repository.mdc",
        ".codex/config.toml",
        ".claude/rules/example.md",
        ".gemini/settings.json",
        "AGENTS.md",
        "CLAUDE.md",
        "GEMINI.md",
        "pytest.sh",
        ".gitignore",
    ],
)
def test_implementation_and_configuration_need_documentation(path):
    assert requires_documentation(path)
    assert not check([("M", path)], "")[0]


@pytest.mark.parametrize(
    "path",
    [
        "pytest/unit/test_example.py",
        "pytest/integration/test_example.py",
        "pytest/performance/test_example.py",
        ".major-check/results.json",
        "dist/package.whl",
        ".venv315/Lib/site-packages/example.py",
        "pyutils_collection/__pycache__/example.pyc",
        "scripts/__pycache__/example.pyc",
    ],
)
def test_tests_and_generated_artifacts_do_not_trigger_policy(path):
    assert check([("A", path)], "")[0]


@pytest.mark.parametrize(
    "path",
    [
        "README.md",
        "CHANGELOG.md",
        "CONTRIBUTING.md",
        "MAINTENANCE_PLAN.md",
        "docs/setup.md",
        "pyutils_collection/file_functions/README.md",
        "pytest/performance/README.md",
    ],
)
def test_added_or_modified_docs_satisfy_gate(path):
    assert check([("M", "scripts/tool.py"), ("M", path)], "")[0]


def test_deleted_docs_and_instruction_edits_do_not_satisfy_gate():
    assert not check([("M", "scripts/tool.py"), ("D", "README.md")], "")[0]
    assert not check([("M", "AGENTS.md")], "")[0]
    assert not check([("M", "scripts/tool.py"), ("A", "docs/_build/README.md")], "")[0]


@pytest.mark.parametrize(
    "body",
    [
        "Documentation not required:",
        "Documentation not required: TODO",
        "Documentation not required: <specific reason>",
        "<!-- Documentation not required: hidden reason -->",
        "<!-- Documentation not required: unfinished comment",
        "```text\nDocumentation not required: example reason\n```",
        "~~~~\nDocumentation not required: example reason\n~~~~",
        "> Documentation not required: quoted reason",
        "    Documentation not required: indented example",
    ],
)
def test_template_and_example_exceptions_are_rejected(body):
    assert not exception_reason(body)
    assert not check([("M", "scripts/tool.py")], body)[0]


def test_explicit_exception_is_data_and_requires_review(tmp_path):
    sentinel = tmp_path / "must-not-exist"
    body = f"Documentation not required: $(touch {sentinel}) `echo example`"
    success, message = check([("M", "scripts/tool.py")], body)
    assert success
    assert "review required" in message
    assert not sentinel.exists()


@pytest.fixture
def repository(tmp_path):
    def git(*arguments):
        return subprocess.check_output(
            ["git", *arguments], cwd=tmp_path, text=True, encoding="utf-8"
        ).strip()

    git("init", "-b", "main")
    git("config", "user.name", "Documentation test")
    git("config", "user.email", "documentation@example.invalid")
    # Disable user signing/hooks and conversion in this disposable repository.
    git("config", "commit.gpgsign", "false")
    git("config", "core.hooksPath", str(tmp_path / "no-hooks"))
    git("config", "core.autocrlf", "false")
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts/tool.py").write_text("print('baseline')\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("Baseline documentation\n", encoding="utf-8")
    git("add", ".")
    git("commit", "-m", "baseline")
    return tmp_path, git


def test_merge_base_does_not_count_docs_added_only_to_base(repository):
    root, git = repository
    baseline = git("rev-parse", "HEAD")
    git("checkout", "-b", "feature")
    (root / "scripts/tool.py").write_text("print('candidate')\n", encoding="utf-8")
    git("commit", "-am", "implementation only")
    head = git("rev-parse", "HEAD")
    git("checkout", "main")
    (root / "README.md").write_text("Base branch update\n", encoding="utf-8")
    git("commit", "-am", "unrelated base documentation")
    changes = changed_paths("main", head, root)
    assert changes == [("M", "scripts/tool.py")]
    assert not check(changes, "")[0]
    assert changed_paths(baseline, head, root) == changes


def test_rename_out_of_code_still_requires_documentation(repository):
    root, git = repository
    base = git("rev-parse", "HEAD")
    git("mv", "scripts/tool.py", "tool.txt")
    git("commit", "-m", "rename implementation")
    changes = changed_paths(base, "HEAD", root)
    assert ("D", "scripts/tool.py") in changes
    assert ("A", "tool.txt") in changes
    assert not check(changes, "")[0]


def test_deleted_docs_in_real_diff_do_not_satisfy_gate(repository):
    root, git = repository
    base = git("rev-parse", "HEAD")
    git("rm", "README.md")
    (root / "scripts/tool.py").write_text("print('changed')\n", encoding="utf-8")
    git("commit", "-am", "code and deleted docs")
    assert not check(changed_paths(base, "HEAD", root), "")[0]


def test_renamed_documentation_satisfies_gate(repository):
    root, git = repository
    base = git("rev-parse", "HEAD")
    (root / "docs").mkdir()
    git("mv", "README.md", "docs/overview.md")
    (root / "scripts/tool.py").write_text("print('changed')\n", encoding="utf-8")
    git("commit", "-am", "implementation with moved documentation")
    changes = changed_paths(base, "HEAD", root)
    assert ("D", "README.md") in changes
    assert ("A", "docs/overview.md") in changes
    assert check(changes, "")[0]


def test_null_pr_body_and_fork_metadata_are_supported(monkeypatch, tmp_path):
    from scripts import check_documentation as policy

    event = tmp_path / "event.json"
    event.write_text(
        json.dumps({"pull_request": {"body": None, "head": {"repo": {"fork": True}}}}),
        encoding="utf-8",
    )
    monkeypatch.setattr(policy, "changed_paths", lambda *_: [("M", "scripts/tool.py")])
    monkeypatch.setattr(
        sys, "argv", ["check", "--base", "main", "--event-file", str(event)]
    )
    assert policy.main() == 1
    event.write_text(
        json.dumps(
            {
                "pull_request": {
                    "body": "Documentation not required: Internal refactor preserves public behavior."
                }
            }
        ),
        encoding="utf-8",
    )
    assert policy.main() == 0


def test_cli_handles_missing_base_without_succeeding(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            str(ROOT / "scripts/check_documentation.py"),
            "--base",
            "nonexistent-documentation-policy-reference",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 2
    assert "could not run" in result.stderr
