# Contributing

Use Python 3.15+ with standard-library `compression.zstd`. Package version comes
from `pyutils_collection/_version.py`; dependencies/tooling are in `pyproject.toml`.
Install with `python -m pip install -e ".[dev,playwright]"`. Where PyYAML C wheels
are unavailable, set `PYYAML_FORCE_LIBYAML=0` before installation.

Read [AGENTS.md](AGENTS.md) for conventions and verification commands. Unit tests
mirror `pyutils_collection/` under `pytest/unit/`. Exercise behavior, boundaries,
and cleanup rather than satisfying test quotas.

## Documentation and version with each change

Update affected docstrings, README examples and setup instructions alongside code.
Record notable changes under `Unreleased` in [CHANGELOG.md](CHANGELOG.md), preserving
published history. Keep current measured results and outstanding checks in
[MAINTENANCE_PLAN.md](MAINTENANCE_PLAN.md). Never count skipped or unavailable
checks as passes, or publish as part of ordinary maintenance.

Always update documentation based on the actual changes and update the package
version once per completed changeset, including documentation/tooling work.
Use the versioning policy in [AGENTS.md](AGENTS.md): patch for fixes/docs/tooling,
minor for new public capabilities, and an appropriate breaking-change increment.
Check whether the changeset already has a version bump before incrementing;
continuations must not bump it again. Keep metadata and release notes consistent.
The CI exception mechanism below does not waive this repository policy.

The `documentation-check` PR workflow compares head with the base/head merge base,
including both sides of renames. Package code, scripts, dependencies/configuration,
workflows, and AI guidance require an added/modified documentation file or a
nonempty PR-body line such as:

```text
Documentation not required: Internal refactor preserves all documented behavior.
```

Recognized documentation is root README, CHANGELOG, CONTRIBUTING, and
MAINTENANCE_PLAN Markdown, Markdown under `docs/`, and package/test README files.
Deleted docs and AI instructions do not count as documentation updates. Generated
artifacts and test-only changes do not trigger the requirement. Exception text
in HTML comments, fenced code, or quotations is ignored. Reviewers must assess
accuracy; a filename check cannot establish it.

Run locally against committed changes:

```bash
python scripts/check_documentation.py --base origin/main --head HEAD --body-file pr-body.md
python -m pytest pytest/unit/repository -q
```

The workflow uses `pull_request` and read-only permissions, including fork PRs.
PR bodies are read from event JSON as data; no PR text is executed.

## AI tools

Codex reads root `AGENTS.md` and discovers shared `.agents/skills/`. Cursor's
always-applied `.cursor/rules/repository.mdc`, Claude's `CLAUDE.md`, Gemini's
`GEMINI.md`, and Copilot's `.github/copilot-instructions.md` route to the same
guidance. Read shared skill files when a tool does not discover them automatically.
Keep policy in one place rather than maintaining divergent copies.

## Major validation

Follow [.agents/skills/major-check/SKILL.md](.agents/skills/major-check/SKILL.md)
for full audits, paired benchmarks, disposable service/browser tests, and clean
artifact verification. Preserve logs under ignored `.major-check/<run>/`.
Remote Windows/Linux/macOS checks must match the final pushed revision; previous
green checks do not certify an unpushed working tree.
