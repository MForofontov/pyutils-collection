# Current maintenance record

## Release validation — 2026-11-02

Version **0.2.1** is the release target. The existing changeset's patch bump is
retained; publication does not add another version increment. The 0.2.1 changelog
is prepared with the release date, preserving all published 0.2.0 history.

Fresh local results and source/environment manifests are recorded under
`.major-check/2026-11-02-release-validation/` (ignored). Native BLAS thread counts
are limited to one for local validation to avoid the resource exhaustion recorded
below; test assertions and thresholds remain unchanged.

The release gate is the final pushed commit's documentation, lint/type, security,
and test workflows, including full Windows/Linux/macOS units, clean wheel/sdist
installation on all three systems, real Chromium/HTTP, and disposable
PostgreSQL/MySQL/OpenSSH checks. Exact head-specific outcomes are available in
[PR #534 checks](https://github.com/MForofontov/pyutils-collection/pull/534/checks).
Earlier CI or local reports cannot certify a different revision.

Publication is authorized for this release and uses the repository's existing
PyPI trusted-publishing workflow only after the required checks pass. An immutable
version tag pins the validated commit for publishing. Upload hashes and the final
registry response are retained with the release evidence. Historical limitations
and measurements below remain dated evidence, not current release-gate outcomes.

## Local maintenance baseline — 2026-11-01

- At completion of local maintenance on 2026-11-01, **0.2.1** was unreleased;
  Python support remains **3.15+**. The patch
  bump follows the repository's once-per-changeset version policy. Published
  0.2.0 notes and tags were unchanged. No commit, push, PR merge, tag, or
  publication had been performed at that point.
- Baseline: `e78db025b189fb130fb285f70e639ef8ea2a0935` (published `v0.2.0`).
  Origin was fetched and `origin/main` merged on 2026-10-30: already up to date.
- Baseline evidence: `.major-check/2026-10-30-maintenance/`. Continuation and final
  evidence: `.major-check/2026-11-01-maintenance/` (both ignored). `summary.json`
  and `api-comparison.json` record source/diff/artifact hashes, report provenance,
  environment and limits.
- Environment: Windows 10, CPython 3.15.2. The original baseline completed with
  **5,860 passed, 5 skipped, 12 warnings** in 480 seconds.

## Changes and review

- Fix `savepoint_context` ownership: release after rollback or ignored body
  failures, preserve the caller's outer transaction, propagate setup/release
  failures, and retain original body exceptions when cleanup fails. Cancellation,
  KeyboardInterrupt and SystemExit always attempt rollback and propagate.
  Six lifecycle regressions and six interruption regressions failed before their
  respective fixes; all 13 lifecycle/interruption cases now pass.
- Correct the numerical-derivative docstring's endpoint results. Its four doctest
  statements pass; numerical behavior is unchanged.
- Root `AGENTS.md` is canonical. Two shared skills plus native Cursor, Claude,
  Gemini, and Copilot entry points replace outdated duplicated instructions.
  Documentation and one version update are required per completed changeset.
- Read-only documentation-impact CI compares the true merge base, checks both
  sides of renames, rejects deleted/generated docs as evidence, and reads PR text
  as data. **52 policy regressions pass**, including fork/null bodies, commented
  examples, exception reasons, deletions and real Git histories. Reviewers still
  assess semantic accuracy; the CI exception does not waive repository policy.
- Review covers inventories and test outcomes for **all 31 utility families**,
  plus selected source paths for ownership, cancellation, filesystem/archive
  containment, transport security, bound SQL, numerical boundaries and cloning.
  `inventory.json` and `review-register.json` retain per-family evidence. This is
  a risk-based review, not exhaustive manual certification of every function.
- Public signatures and export declarations match the baseline across **603
  package sources**. Runtime dependency pins are unchanged.

## Verification completed on 2026-11-01

- **5,925 unique unit cases have passing final outcomes; 5 remain skipped.**
  Verification used disjoint shards and an explicit plotting/export retry;
  it is not a claim that one uninterrupted full-suite invocation passed.
- The non-decorator shard initially recorded 5,632 passes, one Matplotlib
  `MemoryError: bad allocation`, five skips and 12 existing numerical warnings.
  The plotting file and package exports then passed **93 cases, one skip** in
  isolation with BLAS threads limited to one. Original failure XML is retained;
  `effective-tests.xml` is a derived latest-outcome index with source-report links.
- Other decorator tests passed **287 cases**. The five resource-monitor cases
  each passed in their own process after the single-process suite stalled inside
  Python's native `Thread.start()` wait. `native-stack.log` preserves the sampled
  stack. Assertions, internal timeouts, coverage exclusions and thresholds were
  not weakened. A single-process rerun on another host remains desirable.
- Combined coverage: **13,733 / 15,116 lines (90.85%)**. The five skips are three
  Windows symlink-privilege cases, one Unix ownership case, and one legacy
  binary-compression package lacking `__all__`; compression functions are exercised.
- Ruff lint/formatting, strict Mypy over 603 sources, Bandit, installed dependency
  consistency and vulnerability audits pass. Fresh resolved artifact dependencies
  also have no known vulnerabilities. Both shared skills validate; 24 local links,
  adapter imports and the documentation workflow structure were checked.
- **Seven real Chromium/HTTP loopback integration cases pass.** An earlier browser
  deadline interruption is preserved separately from the successful retry.
- Wheel and sdist for **0.2.1** build and pass Twine metadata checks. Isolated
  installed-package probes verify all 603 source files, 790 exports, six README
  examples, version/Python/dependency metadata and `py.typed`. Fresh environments
  first resolved dependencies independently, then installed the patch artifacts.
  An initial parallel probe exhausted OpenBLAS memory; successful probes ran
  sequentially, limiting BLAS threads to one where needed.
- The behavior suite ran before the metadata-only 0.2.1 bump; package exports,
  exact installed sources and artifact metadata were rechecked after the bump.

## Performance evidence

The existing benchmark runner completed all **ten small/large workload cases**
with five alternating samples per version, matching output digests, zero RSS
sampling errors, and ten separate candidate profiles. Families are async mapping,
process mapping, directory listing, Excel transpose, and SQLite ID mapping.
Reports/profiles are in the baseline evidence directory under `benchmarks*`.

These workload implementations are unchanged from the baseline. No new runtime
optimization or portable speedup is claimed from noisy timing differences. Earlier
validated optimizations remain in place; Python allocation peaks and sampled
parent/child RSS remain distinct measurements with the runner's documented limits.

## Outstanding checks recorded on 2026-11-01

- Live PostgreSQL/MySQL/SSH integration is **unavailable locally**: Docker's health
  query exceeded its 30-second deadline. The service runner was not started and
  created no service resources in this run. Four new database-service cases are
  collected for the savepoint lifecycle but require real services before release.
- Remote Windows/Linux/macOS CI must run against the final pushed candidate.
  Baseline e78db025 passed [test-check](https://github.com/MForofontov/pyutils-collection/actions/runs/41040791538),
  [lint-check](https://github.com/MForofontov/pyutils-collection/actions/runs/41040791495),
  and [security-check](https://github.com/MForofontov/pyutils-collection/actions/runs/41040791666).
  Those runs do not certify the current uncommitted changes.
- Recheck single-process Windows/Python 3.15.2 native thread startup on a host with
  adequate resources; preserve this run's stall and memory diagnostics.

## Historical evidence and reusable procedure

- [Historical maintenance records](docs/history/maintenance-through-0.2.0.md)
  preserve earlier scopes, measurements, skips, and platform evidence.
- [Major-check workflow](.agents/skills/major-check/SKILL.md) defines repeatable
  verification without treating old logs as fresh certification.
- [Contributor guide](CONTRIBUTING.md) covers setup, versioning and documentation CI.
