# Repository guidance

## Project and compatibility

- Source: `pyutils_collection/`; mirrored unit tests: `pytest/unit/`.
- `pyproject.toml` defines Python support, dependencies, tooling, and packaging.
  Use Python 3.15+ with `compression.zstd`. `_version.py` owns the package version.
- Preserve public signatures, exports, return shapes, ordering, and ownership
  contracts unless explicitly changing them. Reproduce defects before fixes.
- Keep complete type hints and NumPy-style public docstrings. Test observable
  behavior and failure cleanup; avoid arbitrary test quotas and timing limits.

## Documentation and version are part of every change

- Assess documentation impact before finishing **every task**. Update affected
  docstrings, README examples/setup, maintenance instructions, and changelog
  entries in the same change as the implementation.
- Put new notable changes under `CHANGELOG.md`'s `Unreleased` heading. Preserve
  published history; never tag or publish as an incidental maintenance step.
- Always update documentation based on the actual changes. Every completed
  changeset needs accurate release notes, including internal maintenance when
  public usage is unchanged. Do not invent cosmetic edits to pass CI; reviewers
  must assess accuracy, not just filenames.
- Always update `pyutils_collection/_version.py` once per completed changeset,
  including documentation/tooling changes. Compare the baseline and current
  version first; do not bump again for individual files, retries, or continuations
  of the same changeset. Default to a patch increment for fixes/docs/tooling, a
  minor increment for new public capabilities, and an appropriate breaking-change
  increment. Keep metadata, release notes, and documented versions synchronized.
- Version updates do not authorize tagging, pushing, merging, or publication.
- Tie measured claims to a commit, environment, and report. Distinguish passes,
  skips, unavailable services, and historical evidence.
- Update these instructions when commands or conventions change. Tool adapters
  reference this file; do not duplicate policy in every AI folder.

## Verification

Install with `python -m pip install -e ".[dev,playwright]"`. Where PyYAML C wheels
are unavailable, set `PYYAML_FORCE_LIBYAML=0` for its supported pure-Python build.
Select the interpreter explicitly; the host default may be older.

```bash
python -m ruff check pyutils_collection scripts
python -m ruff format --check pyutils_collection scripts
python -m mypy pyutils_collection
python -m pytest pytest/unit -ra --cov=pyutils_collection
python -m pip check
python -m bandit -r pyutils_collection -ll -ii
python -m pip_audit --local
```

Run focused regressions during development and relevant broader gates before
handoff. Do not weaken thresholds, exclusions, or assertions to get green.
Keep generated artifacts in ignored `.major-check/<run>/` directories.

## Shared workflows

- Full audits and measured optimizations:
  [.agents/skills/major-check/SKILL.md](.agents/skills/major-check/SKILL.md).
- Documentation, releases, AI instructions, and documentation CI:
  [.agents/skills/documentation-maintenance/SKILL.md](.agents/skills/documentation-maintenance/SKILL.md).
- Current evidence: [MAINTENANCE_PLAN.md](MAINTENANCE_PLAN.md).
- Contributor setup and documentation CI: [CONTRIBUTING.md](CONTRIBUTING.md).
