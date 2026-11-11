# Current maintenance record

## 0.2.2 release preparation — 2026-11-09

Publication and merging through a pull request are authorized for this release.
The existing **0.2.2** patch bump from published **0.2.1** is retained. Historical
audit sections below describe their original scope and results; their earlier
no-publication statements do not describe this release preparation.

- Candidate branch: `codex/release-0.2.2`, based on
  `92153c303ef2aa55c05bf0fe2e82ad8b36ed4f9c` (`v0.2.1`). Remote `main` was
  `ba8510a69d7ac2fe99de9ed7f9b8a6bc1d42374a`; all its commits are ancestors
  of the published 0.2.1 package source. This release brings the intervening
  maintenance history and the new fixes into `main` together.
- README setup runs editable installation from the repository root, names
  0.2.2 and Python 3.15+, records 0.1.5's earlier Python declaration, and counts
  top-level exported names consistently. Mathematics and environment utility
  descriptions match the implemented exports. Changelog release notes are
  dated, with an empty `Unreleased` heading retained.
- Fresh evidence is recorded under `.major-check/2026-11-08-release/` (ignored),
  using Windows and CPython 3.15.2 with standard-library Zstandard 1.5.7 and
  native numerical-library thread counts limited to one. Public signature,
  decorator, constructor, and export AST contracts match the 0.2.1 baseline
  across all 603 package sources.
- The fresh Windows run on 2026-11-08 passes **5,963 unit cases, five skips,
  12 warnings**, plus **92 focused cases**, **seven real HTTP/Chromium integration
  cases**, and **20 affected-module doctest examples**. Coverage is
  **13,751 / 15,133 lines (90.87%)**. The inventory covers all 31 utility
  families; filename gaps are review prompts, not test quotas. Skips cover unavailable
  Windows symlink privileges, Unix ownership, and a package without `__all__`.
- Ruff, formatting, strict Mypy, Bandit, dependency consistency, README export
  counts, six README examples, and local documentation links pass. The dependency
  vulnerability scan reports no known vulnerabilities; the unpublished 0.2.2
  project itself is explicitly skipped by the registry lookup.
- Publication requires clean wheel/source metadata and installed-package probes,
  successful final-revision Windows/Linux/macOS CI and configured integrations,
  then verification of PyPI hashes, Python requirements, and release documentation.
  Final remote evidence belongs to the release's pull request, Actions runs, and
  [0.2.2 release](https://github.com/MForofontov/pyutils-collection/releases/tag/v0.2.2).
  Earlier results below remain historical evidence. No new performance claim is
  introduced.

## Main maintenance audit — 2026-11-02, 0.2.2 unreleased

This is a new local maintenance changeset. Version **0.2.2** applies one patch
increment from baseline **0.2.1**. No push, merge to main, tag, publication, or
remote workflow launch is part of this audit. Release authorization recorded in
older sections below applies to that earlier release only.

### Continued smoothing audit — 2026-11-03

- Further source review found that moving-average smoothing overwrote its final
  complete window for even widths and could return too many samples for an
  oversized window. Five new regression cases failed before repair; three
  preservation cases passed. All **67 data-transformer cases pass** after repair.
- `smooth_timeseries` now retains every complete moving average using the same
  user-selected left alignment as rolling statistics. Only boundary positions
  without a complete window retain original values. Oversized moving-average
  windows raise the documented `ValueError`; exponential smoothing still accepts
  larger windows. Odd widths, single-sample windows, dtype, and caller-owned
  input data are preserved.
- Evidence for this continuation is retained under
  `.major-check/2026-11-03-smoothing-audit/`. The existing **0.2.2** version bump
  is retained for this same uncommitted changeset. No speedup is claimed for
  this correctness repair.
- The final full invocation passes **5,963 cases, five skips, 12 warnings** in
  300.75 seconds. Coverage is **13,751 / 15,133 lines (90.87%)**. Ruff,
  formatting, strict Mypy, Bandit, dependency consistency, and the affected
  module's doctests pass. The source/test/configuration snapshot contains
  **1,177 files**; the inventory still covers all 31 families.
- Clean wheel/sdist archives match all **603 package sources** byte for byte.
  Both isolated installed-package probes verify **603 sources, 790 exports,
  six README examples**, metadata, and `py.typed`; dependency consistency passes.
  The previous separate virtualenv environments are reused with forced package
  replacement and no dependency resolution. Public signatures and exports are
  preserved; the package baseline comparison now covers seven modified modules
  by AST and 596 unchanged package sources by Git.
- Only `smooth_timeseries.py` changed in the package since the preceding
  validated candidate. The earlier seven HTTP/Chromium passes and 2026-11-03
  advisory scan are retained as references for unchanged integration code and
  dependencies; they were not rerun for this smoothing-only repair. Live service
  checks, other operating systems, and remote CI remain unverified.

### Numerical and logging candidate — validated 2026-11-03

- A second full recheck passed **5,934 cases, five skips, 12 warnings**, with
  **90.85% coverage**, seven HTTP/Chromium integration passes, and successful
  quality, security, package, and ten-workload benchmark checks. Evidence is in
  `.major-check/2026-11-02-full-recheck/`. Targeted probes still found numerical
  and logging behavior gaps that the existing tests did not detect.
- Even rolling-statistics windows now contain exactly the requested sample
  count. The user-selected alignment puts the extra sample on the left of the
  current sample. Odd windows, clipped edges, output shapes, and population
  standard deviation are preserved; all five statistics have value regressions.
- `power` rejects negative bases with fractional exponents rather than returning
  complex values. Arithmetic overflow and zero-to-negative-power failures now
  raise the documented `ValueError`, retaining their arithmetic causes. Existing
  bounds, valid result types, and integer precision are preserved.
- Contextual exception logging now retains active exception/traceback information
  by default. `exc_info` is forwarded as a logging control, including explicit
  suppression and saved exception tuples. Context/extra/keyword precedence and
  public signatures are unchanged.
- **Eleven new regression cases failed before repair; ten preservation cases
  passed. All 102 focused cases pass after repair.** The first after-fix run had
  one test expecting None for suppressed exception information; standard logging
  stores False. The corrected test asserts False and absence of the formatted
  exception. Original reports are retained. An earlier invocation interrupted
  before producing a report is not counted as a passing or completed check.
- That candidate passed **5,955 unit cases, five skips, 12 warnings** in one
  completed invocation (455.58 seconds). Coverage is **13,747 / 15,129 lines
  (90.87%)**. All **seven real HTTP/Chromium integration cases pass** (104.83
  seconds). The existing platform/capability skips remain distinct from passes.
- Final evidence is in `.major-check/2026-11-03-followup-final/`; earlier focused
  and diagnostic evidence remains in `.major-check/2026-11-02-followup/`.
  **1,176 source/test/configuration file hashes** match the frozen snapshot.
  Public signatures, decorators, constructors, and exports remain unchanged:
  six modified package files were compared by AST, and the other 597 package
  sources are unchanged by Git. The family inventory covers all 31 families.
- Ruff, formatting, strict Mypy, Bandit, and dependency consistency checks pass
  against this same source snapshot. A fresh 2026-11-03 dependency vulnerability
  audit reports no known vulnerabilities. Affected module doctests, all six
  README examples, nine local documentation links, and working-tree
  documentation-impact classification pass. The committed-change documentation
  CLI remains deferred because these changes are uncommitted.
- An earlier build exceeded its operational deadline. Its incremental retry
  produced archives containing an empty `strings_utility/replace_tabs.py`;
  installed-source equality correctly rejected them even though metadata checks
  had passed. The working source remained intact. The build cache was archived,
  absence of old sdist staging was checked, and clean wheel/sdist builds passed
  byte-for-byte preflight comparisons for all **603 sources**.
- Both clean artifacts pass Twine checks and isolated installation probes for
  **603 sources, 790 exports, six README examples**, metadata, and `py.typed`.
  They were force-installed without dependency resolution into the earlier
  separate virtualenv environments; dependency consistency also passes. Failed
  artifacts, the failed installed-source probe, build/browser deadlines, and
  interrupted full-suite attempts are retained separately, not counted as final
  passes. No interrupted report was combined with the final full-suite result.
- Docker health was rechecked on 2026-11-03 and exceeded its 30-second deadline;
  no Compose project was started. Live PostgreSQL/MySQL/SSH checks, Linux/macOS,
  and remote CI remain unverified for this local changeset.
- This is the same uncommitted changeset, so its existing **0.2.2** patch bump is
  retained. No additional runtime optimization or new performance claim is
  introduced by the numerical and logging repairs.

### Baseline and review

- Fetched origin, switched to `main`, and pulled with `--ff-only`: already up to
  date at `ba8510a69d7ac2fe99de9ed7f9b8a6bc1d42374a`. Created
  `codex/main-maintenance-audit` and fast-forwarded the four preserved maintenance
  commits from `codex/major-check-validation`. Main remains at its original head.
- Combined audit/benchmark baseline:
  `92153c303ef2aa55c05bf0fe2e82ad8b36ed4f9c`. Reports, source hashes, environment,
  profiles, package artifacts, and a detached baseline checkout are retained
  under `.major-check/2026-11-02-main-audit/` (ignored).
- Windows 10, CPython 3.15.2, standard-library Zstandard 1.5.7. Validation uses
  `.venv315/Scripts/python.exe` explicitly; the host default is Python 3.8.
  Native BLAS/OpenMP thread counts are limited to one without changing assertions.
- Inventory and selected source review cover all **31 utility families**.
  `review-register.json` records representative paths and test outcomes. This is
  risk-based review, not exhaustive certification of every function. The hostname
  filename gap is covered by `test_network_get_hostname.py`; four root SSH modules
  are compatibility re-exports of tested local helpers.
- Public signatures, public decorators, class bases, constructors, and export
  declarations match the baseline across **603 sources**; no sources were removed.
  Runtime dependency pins are unchanged.

### Changes and regressions

- Both cache decorators now distinguish keyword insertion order, preserving the
  result of functions that observe `**kwargs` order. Wrapped `TypeError` instances
  propagate unchanged, and failed calls are not cached. Expiring caches use a
  monotonic clock to avoid premature expiration or extended lifetimes after
  system-clock changes. Existing zero-lifetime behavior is retained.
- Five regression cases failed before the fixes. All **34 focused cache cases**
  pass afterward, including unhashable argument rejection before execution,
  uncached failures, keyword ordering, elapsed-time boundaries, and cached `None`.
- Profiling identified redundant cache-hit lookups. Each decorator now validates
  hashability through one dictionary lookup, with wrapped execution outside the
  argument-error handler. Docstrings, the README, and Unreleased notes describe
  the implemented behavior.

### Validation and measurements

- Ruff lint/formatting and strict Mypy pass; Bandit reports no issues at the
  required severity/confidence gates. `pip check` and `pip-audit --local` pass.
- **Seven real HTTP/Chromium integration cases pass.** Initial browser failures
  were caused by a missing Chromium executable. The first installation exceeded
  its 180-second deadline; installation with a longer deadline and the test retry
  succeeded. Original failure reports remain alongside the retry.
- All **ten standard paired benchmark workloads** completed with five alternating
  samples, matching output digests, and separate profiles/allocation/RSS data.
  Their implementations are unchanged; noisy timing differences are not claimed
  as runtime improvements. Additional cache-hit measurements are retained in
  `cache-benchmarks*.json`, separate from the standard workloads.
- A longer cache-hit repeat uses **one million calls per sample**, five
  alternating samples per version, matching results, and separate profiles and
  memory measurements. Median baseline/candidate ratios are **1.49 / 1.39** for
  plain cache hits with zero/eight keyword arguments and **1.22 / 1.35** for
  expiring-cache hits. Traced Python allocation peaks fall from **328–1,112 bytes
  to 112–488 bytes** across these cases; sampled RSS remains comparable. These
  are cache-hit microbenchmarks on this Windows host, not application-wide or
  portable speedup claims. Shorter samples taken during other validation were
  noisier, including a slower zero-keyword plain-cache case; their reports are
  preserved separately. Both runs improve the eight-keyword hit cases.
- Wheel and sdist for **0.2.2** build and pass Twine metadata checks. Standard
  `venv` creation failed because this embedded Python lacks bootstrap modules;
  fresh `virtualenv` environments are used for installed-package validation.
- An intermediate unit invocation passed **5,932 cases, five skips, 12 warnings**.
  Regressions were added during its collection, so this is intermediate evidence,
  not a pristine baseline or final-code certification. Dedicated clean-baseline
  and final-code invocations retain their own reports.
- The pristine baseline passes **5,925 cases, five skips, 12 warnings** in one
  invocation. The cache-only 0.2.2 candidate passes **5,934 cases, five skips, 12 warnings**
  in one invocation. Its coverage is **13,737 / 15,120 lines (90.85%)**. The
  skips are three Windows symlink-privilege cases, one Unix ownership case, and
  one legacy compression package without `__all__`; its functions are exercised.
- Wheel and sdist each install with freshly resolved dependencies in separate
  isolated environments. Both probes verify all **603 sources, 790 exports,
  six README examples**,
  version/Python/dependency metadata, and `py.typed`. Dependency consistency and
  resolved dependency vulnerability checks pass. The unpublished 0.2.2 project
  itself is explicitly skipped by the PyPI vulnerability lookup, not certified
  by that lookup. The cache doctest and nine modified-document local links pass.

### Local limitations

- Docker's health query exceeded its **30-second deadline**. PostgreSQL/MySQL/SSH
  service checks are unavailable locally; the service runner was not started and
  no Compose resources were created.
- Linux/macOS and remote CI remain unverified for this unpushed changeset. Earlier
  CI outcomes cannot certify these local changes. The five platform/capability
  skips must remain distinct from passing tests.

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
