---
name: major-check
description: Audit pyutils-collection correctness, security, packaging, portability, and measured performance. Use for broad maintenance or release-readiness checks; routine focused fixes need only their relevant checks.
---

# Major check

Read root `AGENTS.md` and the current `MAINTENANCE_PLAN.md` first.

1. Record Git status, exact revision, Python/platform, dependency versions, and
   baseline results in a fresh ignored `.major-check/<run>/` directory. Preserve
   unrelated work. Fetch/merge only when requested; never reset existing fixes.
2. Run the full unit suite with JUnit and coverage through
   `scripts/run_with_deadline.py`. Run `scripts/audit_inventory.py <junit.xml>`;
   review all families and conventional test gaps without inventing tests solely
   to match filenames. Prioritize cleanup, mutation on failure, cancellation,
   transport security, bound SQL, filesystem containment, and numerical boundaries.
3. Reproduce defects, add behavior regressions, then repair them without changing
   public interfaces unnecessarily. Compare exports/signatures with the baseline.
4. Profile before optimizing. Use `scripts/benchmark_audit_pair.py --baseline-ref
   <commit> --output .major-check/<run>/benchmarks.json --samples 5 --profile`.
   Compare equivalent outputs and separate timing, Python allocation peaks, and RSS.
   Retain improvements only with repeatable evidence; report neutral results honestly.
5. Run Ruff, strict Mypy, Bandit, `pip check`, and installed dependency audits.
   Dependency changes need demonstrated compatibility/security/correctness reasons.
6. Exercise `pytest/integration/test_http_loopback.py`; opt into real browsers with
   `PYUTILS_BROWSER_TESTS=1` after installing Chromium. Run
   `scripts/run_service_integration.py --report-dir .major-check/<run>/services`
   for disposable PostgreSQL/MySQL/SSH. Record startup failures separately and
   verify cleanup of only task-owned resources.
7. Build wheel and sdist; install each in isolated environments and invoke
   `python -I scripts/check_installed_distribution.py <checkout>` with each installed
   interpreter. Check metadata, source equality, exports, README examples and typing.
8. Always update documentation based on the changes and update the package version
   once per completed changeset under root AGENTS.md's versioning policy. Preserve
   a version bump already made for the same changeset. Record actual results, warnings, skips,
   reviewed gaps, artifact hashes, and outstanding platform checks. Remote CI must
   match the final pushed commit; earlier green runs cannot certify local changes.

Do not push, merge, tag, publish, or launch recurring work unless requested.
