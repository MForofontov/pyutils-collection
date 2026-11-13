# Current maintenance record

## Final local validation — 2026-11-13

The exhaustive source review and locally available final gates are complete for
the existing uncommitted **0.2.3** changeset. Version 0.2.3 is retained; nothing
was committed, pushed, tagged, published or launched in remote CI.

- All **603 package source files** across the 31 families have review dispositions,
  contracts, test references, findings or explicit no-additional-finding outcomes
  in `.major-check/2026-11-11-exhaustive/review-register.json`. A separate
  `tooling-review-register.json` covers 30 tooling/configuration files.
  `findings-register.json` prioritizes reproduced repairs, measured optimizations
  and unresolved candidates. Per-file manifestations are not independent defect
  counts. Exhaustive source review is not a guarantee that no defects remain.
- Final candidate `final2-candidate-manifest.json` records HEAD
  `46ed7a2e7c948139856cf294495790128f6a34dd`, the uncommitted source hashes,
  Windows 10, CPython 3.15.2 and dependency versions. The final unit invocation
  passes **6,159 tests, five skips, 12 numerical warnings** in 262.25 seconds,
  with **91.15% line coverage**, JUnit, coverage XML and a 31-family inventory.
  `final-evidence.json` verifies no runtime, test, tooling or dependency-config
  hash changed during validation. Documentation-only evidence updates follow it.
- Ruff lint/format, strict Mypy, Bandit, `pip check` and `pip-audit --local` all
  pass. The security-required pin to **Soup Sieve 4.0.1** addresses
  [CVE-2026-126190](https://github.com/facelessuser/soupsieve/security/advisories/GHSA-mmhr-3c5m-f64f).
  The failing advisory report and bounded before/after selector probe are retained;
  all 166 scraping tests and the final full suite pass with the patched version.
  The advisory service cannot audit unpublished local `pyutils-collection 0.2.3`;
  this explicit skip is not a security certification of the package itself.
- Real HTTP/Chromium checks pass **eight tests** in 34.77 seconds. The earlier
  download timeout and passing isolated retry remain separate evidence. Real
  PostgreSQL/OpenSSH checks pass **14 tests**, with **six MySQL cases skipped**.
  MySQL failed its disposable service startup health check; its tests did not run.
  Both task-owned Compose projects have no remaining containers, networks or
  locally built SSH images after cleanup, verified in `final-evidence.json`.
- Clean wheel and sdist builds, Twine metadata checks, separate isolated
  installation/`pip check`, and both installed probes pass. Each probe verifies
  **603 byte-identical sources, 790 exports, six README examples, metadata and
  typing markers**. The build uses installed setuptools 84.2.1, satisfying the
  declared backend requirement. The initial sdist probe setup lacked setuptools;
  its failed install is retained separately, and the corrected setup passes.
  Final artifact hashes are in `final2-artifact-hashes.json`.
- Public function/class signatures and exports match the frozen starting working
  tree across all 603 sources. Forty applicable doctest statements and 18 affected
  local documentation links pass; working-tree documentation policy and its
  repository tests pass. The committed-change checker has no suitable committed
  candidate because commits were explicitly excluded from this task.
- Retained optimizations are the measured SVD reconstruction and one-pass grouped
  dictionary inversion described below. Their measured source hashes still match
  the final implementation. All ten standard paired workloads have equivalent
  output digests and no recorded RSS sampling errors. Timings, Python allocation
  peaks and process memory remain separate; no application-wide speedup is claimed.
- Outstanding platform/infrastructure checks are Linux/macOS, exact-candidate
  remote CI, MySQL, three Windows symlink-privilege cases and Unix ownership.
  The fifth unit skip is a binary-compression module without `__all__`.
  Compatibility-sensitive review candidates remain: dialect-specific raw SQL
  identifier formatting, partial/expression/collation index equivalence,
  caller-owned truncate transactions, advertised solver-mode mismatches,
  ambiguous nested-path/nonfinite/label policies and unverified SSH interpreter
  flags beyond the repaired Node path. They are recorded limitations, not passes
  or newly promised behavior. Illustrative external-service doctests are not
  presented as executed examples.

## Development evidence — 2026-11-11 to 2026-11-13

The checkpoints below describe progress before final selection. Pending work and
intermediate failures in this record are superseded only by the explicit final
results above, while their original reports remain preserved.

This continues the same uncommitted **0.2.3** changeset. Its comparison baseline
is the frozen working tree under `.major-check/2026-11-11-exhaustive/baseline/`,
including the preceding repairs, rather than Git HEAD alone. The baseline
manifest hashes 1,213 tracked files, including all 603 package sources, and
`starting.diff` preserves the original uncommitted changes.

- The frozen baseline passes **5,994 tests, five skips, 12 warnings** in one
  invocation. That result does not certify the newer repairs described below.
- The per-file review register distinguishes completed source-and-test review,
  source review awaiting test review, and pending files. At this checkpoint,
  **all 603 files have completed source-and-test review**, including private
  helpers and exports. The JSON register records literal contracts, tests,
  reviewed behavior, findings and limitations. Tooling/configuration review has
  a separate 30-entry register. Review coverage is not proof of correctness;
  final verification is still in progress.
- The November 13 continuation completes iterable and serialization test review.
  Numeric overflow now follows documented conversion failure behavior (nine
  failures before; 60 type-operation tests pass). Rejecting an export with no
  active figure no longer creates one (one failure before; 250 visualization
  tests pass), while preserving existing empty caller-owned figures.
- Three real SQLite regressions expose incomplete composite/self-referencing
  foreign-key matching and NULL parent keys hiding orphans. Correlated aliased
  `EXISTS` checks now match all key components, exclude nullable child references
  with MATCH SIMPLE semantics, and preserve the first-column report/sample shape.
  Two valid Excel sheet names that normalize identically previously overwrote
  one CSV silently; batch exports now validate eligible destinations before
  writing. Four regressions fail before these repairs, one preservation case
  passes; all **1,154** schema/serialization/iterable tests pass afterward.
- The first frozen candidate passes Ruff lint/format, strict Mypy, Bandit and
  dependency consistency. Its vulnerability audit reports
  **CVE-2026-126190 / GHSA-mmhr-3c5m-f64f** in installed Soup Sieve 3.0.4.
  The [maintainer advisory](https://github.com/facelessuser/soupsieve/security/advisories/GHSA-mmhr-3c5m-f64f)
  identifies 4.0 as patched. A bounded nested-selector probe preserves empty
  results with downloaded 4.0.1; the security-required dependency update and fresh
  candidate validation are pending. No advisory exception or weakened gate is used.
- The first real HTTP/Chromium invocation records seven passes and one download
  click timeout. The isolated retry passes; both reports are preserved. A clean
  combined rerun is required after final candidate selection. Docker now responds,
  and the disposable service runner has started task-owned services. Startup,
  integration and cleanup outcomes remain pending, rather than recorded as passes.
- The November 12 continuation completes asynchronous, development-tool,
  decorator, database, SSH and string-utility test review. New checkpoints pass 271
  asynchronous/development tests, 318 decorator tests, and 239 schema-inspection
  tests. These focused results do not replace final-candidate validation.
- SSH tests pass **217 cases**, including a real local Node probe that failed
  with exit code 9 for the generated `node -s` command and now executes supplied
  stdin using `node -`. This validates interpreter arguments with the SSH
  transport mocked; it does not substitute for the disposable remote service.
  Ruff lint/format and strict Mypy on the 22 files covering the preceding new
  repairs pass after removal of an obsolete type-ignore comment. The public
  contract comparison still matches all 603 frozen sources.
- Dependency graphs now resolve package-relative imports before retaining their
  existing top-level grouping (three failures before; package-initializer and
  invalid-context preservation also pass). Resource monitoring uses counter
  increments and avoids double-counting process bytes in system disk totals;
  deterministic checks cover repeated samples, reused process IDs and an
  unavailable initial counter. Cache tests now isolate cached state: three
  selected cases failed before; all 25 pass with accurate independent counts.
- Twelve real SQLite regressions demonstrate schema-qualified reflection lookup
  failures or silently empty/zero results across analysis helpers. Qualified
  metadata lookup preserves requested result names; row counts and sequence
  maxima use reflected SQL expressions. Cardinality sampling now bounds input
  rows before all aggregates (two failures before, 19 related tests pass).
  Unique-prefix indexes are excluded from prefix-redundancy advice because a
  longer index does not preserve their uniqueness constraint (two failures
  before, 15 related tests pass). Raw SQL in remaining dialect-specific paths
  and partial-index equivalence still need investigation; composite-key and NULL
  matching are now repaired as recorded above.
- An intermediate quality run passes Ruff lint/format, strict Mypy, Bandit,
  dependency consistency and vulnerability checks. Its checks overlap development
  and predate the latest database edits, so it is not final-candidate evidence.
  The dependency advisory audit explicitly skips unpublished local
  `pyutils-collection 0.2.3`; no known vulnerabilities are reported for audited
  dependencies. Fresh final checks and distribution builds remain outstanding.
- New failure reproductions cover timezone-aware default age references, invalid
  accumulation chunk settings before pool startup, caller cancellation and worker
  cleanup, Windows address-family classification, same-file/hard-link
  concatenation, generator-based password rules, socket cleanup/default-timeout
  ownership, compact-number integer zeros, and exact-k set-partition completeness.
  Focused regressions and existing preservation cases pass after each repair.
- Cancellation cleanup now retrieves both owned tasks' outcomes, preserving
  cancellation/timeouts when a worker raises during cleanup. Network probes close
  their sockets on failure; the connectivity timeout no longer changes global
  socket defaults. The old timeout test now requires the socket-local setting and
  explicitly rejects changing the process default.
- Password-rule generators are materialized once so validation cannot consume and
  bypass custom checks. Concatenation rejects source/destination aliases before
  copying. Set-partition tests assert completeness and exact cardinality directly;
  older tests that filtered invalid results are retained alongside them.
- Further reproduced repairs cover explicit case-sensitive filename matching on
  Windows (44 recursive-search tests pass), gzip/bz2/lzma same-file and hard-link
  input preservation, extended to TAR/ZIP creation after four further failure
  reproductions (118 file-compression tests pass, one skip), commit-failure
  accounting and per-row rollback (28 bulk-operation tests pass), assertion helpers
  accepting their own missing-exception failure (14 related tests pass), temporary
  fixture path containment (27 fixture tests pass), and Excel reader failure cleanup
  (25 related tests pass). Each has saved failing-before and passing-after reports.
  Two bulk-operation assertions that expected double counting were corrected;
  independent regressions verify counts, progress, and committed database rows.
- Plot-generation failures close the newly created figure while preserving caller
  figures. Conditional execution and timeout decorators preserve body exceptions;
  timeout executors also shut down after submission failure. Runtime type checks
  accept `Any` and union members in supported containers. Focused before/after and
  adjacent preservation checks are retained for these repairs.
- URL case-normalization opt-out now preserves scheme case while recognizing
  default ports case-insensitively (three failing reproductions; 114 URL tests
  pass). A scoped Cerberus availability-test override preserves the cached module
  identity; an independent isolation probe and all 122 validation tests pass.
- Browser download-directory forwarding has a failing-before regression and 17
  passing manager tests. Eight real HTTP/Chromium integrations pass, including a
  generated download stored in the requested directory and removed at context
  cleanup. Failed session restoration also closes only pages it creates, while
  successful session-storage pages remain usable; 22 related unit tests pass.
- A broad checkpoint invocation passes **6,077 tests, five skips, 12 warnings** in
  292.11 seconds, with JUnit, coverage and the 31-family inventory retained. Its
  collection predates the latest database, assertion, fixture and Excel-reader
  regressions and their repairs; it is **not final-candidate validation**.
- A later development checkpoint records **6,134 passes, one failure, five skips,
  12 warnings** in 462.71 seconds. It overlaps ongoing edits and includes the new
  Node regression before that process used the repair. Its failing JUnit/log and
  coverage are preserved as `checkpoint2-*`; it is not a passing candidate gate.
  Subsequent SSH checks pass all 217 cases. Future final-suite validation must
  run against a frozen implementation without concurrent source edits.
- Seeded bootstrap analysis no longer resets the caller's NumPy random state
  (three failures before, 26 related tests pass). Six comparisons against the
  frozen implementation preserve exact outputs for all three statistics with and
  without explicit seeds; unseeded calls retain legacy global RNG consumption.
  NaN confidence levels now fail validation before resampling (one failure before,
  three preservation cases pass). All 180 statistical-analysis checks pass with
  12 existing numerical warnings; no performance claim is attached to this repair.
- SVD prototype measurements use the frozen source, warmups, five alternating
  samples, and two independent rounds. The larger whole-function workload improves
  in both rounds; the smaller workload is mixed. Traced allocation peaks are
  unchanged. Numerical preservation checks cover tall/wide/square matrices, full
  and reduced decomposition, ranks, output keys, and caller-owned input.
- Dictionary-inversion profiling exposes a quadratic scan of previously created
  groups. The first one-pass prototype increases list allocations and is rejected.
  The refined prototype improves all three workloads in both rounds without
  increasing traced allocation peaks. Both prototype reports and profiles are
  retained; the integrated implementation preserves ordering, independent output
  buckets, input ownership, and duplicate errors in focused checks.
- Prototype timing, traced allocation peaks, and absolute post-call RSS are
  separate measurements. Post-call RSS is **not** a sampled peak. Integrated-code
  confirmation now uses the actual implementations against the frozen sources.
  Inversion improves all three cases in both confirmation rounds with slightly
  lower traced peaks. Whole-function SVD medians for 512x256/rank 256 improve
  roughly 4–7%; the smaller case is near neutral in one round. A separate five-pair
  fresh-process RSS check samples approximately every millisecond: median lifetime
  peaks are 46,198,784 baseline and 46,403,584 candidate bytes. That check includes
  imports, repeated calls and output serialization; it can miss short peaks.
  The approximately 0.4% RSS difference does not establish a meaningful memory
  regression, and no reduced whole-function peak-memory claim is made.
- All ten standard paired workloads also complete against the frozen working tree,
  using five alternating samples, matching output digests, separate allocation/RSS
  measurements, and profiles. An ignored adapter reads frozen files instead of a
  Git revision, avoiding attribution of preceding uncommitted repairs to this pass.
  Public signature/class/export AST comparison matches all 603 frozen sources.
  Package checks and remaining contract/test review are still outstanding; no
  portable or application-wide speedup is claimed.

Evidence and progress are retained under `.major-check/2026-11-11-exhaustive/`.
The previous audit/recheck sections below remain historical evidence.

## Independent full recheck — 2026-11-11

The same uncommitted **0.2.3** changeset was checked again without further
implementation changes or another version increment. Fresh evidence is under
`.major-check/2026-11-11-recheck/`, including source/environment manifests and
independent logs; previous reports were not overwritten.

- One full invocation passes **5,994 tests, five skips, 12 warnings** in 602.02
  seconds. Coverage remains **13,767 / 15,149 lines (90.88%)**. All 31 utility
  families are represented in the refreshed inventory.
- Ruff lint/formatting, strict Mypy, Bandit, dependency consistency, and installed
  dependency vulnerability checks pass. All seven real HTTP/Chromium integration
  cases, 16 doctest statements, and 18 local documentation links pass again.
- Public API comparison still matches baseline `46ed7a2e` across 603 sources.
  Fresh wheel/sdist archives pass metadata checks and installation into the
  separate artifact environments. Both probes verify 603 sources, 790 exports,
  six README examples, metadata, and typing; dependency consistency passes.
- All ten paired benchmark workloads complete again with five alternating samples,
  matching output digests, separate profiles/allocation/RSS measurements, and zero
  RSS sampling errors. Timing variation does not warrant a new speedup claim.
  Manifest comparison confirms the tested implementation, tests, and tooling
  stayed unchanged throughout this recheck.
- Docker health again exceeds its 30-second operational deadline. No service
  project was started. Live PostgreSQL/MySQL/SSH, Linux/macOS, remote CI, and the
  committed-change documentation CLI remain unverified as previously recorded.

## Whole-codebase maintenance audit — 2026-11-10 to 2026-11-11

This local changeset starts from clean revision
`46ed7a2e7c948139856cf294495790128f6a34dd` (0.2.2). Development version
**0.2.3** applies one patch increment for the complete changeset. No push, merge,
tag, publication, or remote workflow launch is part of this audit.

Evidence is retained under `.major-check/2026-11-10-audit/` (ignored): baseline
source hashes, environment/dependencies, JUnit/coverage reports, failure
reproductions, per-family review register, profiles, and distribution probes.
The environment is Windows 10 with CPython 3.15.2 and standard-library Zstandard;
BLAS/OpenMP thread counts are limited to one for full tests and measurements.

### Findings and repairs

- **High priority — file preservation:** folder merging could overwrite an
  existing `_copy` file and traverse an output nested inside its source. Conflicts
  now select an unused `_copy`, `_copy2`, etc.; overlapping source/output roots
  are rejected before traversal. Concurrent writers remain unsupported.
- **High priority — CSV preservation:** header errors left partial output, and
  using an input as output truncated that input. Output is now staged beside the
  destination, synced, and replaced after success, with failure cleanup. Empty
  leading inputs no longer prevent header discovery. Replacement uses temporary
  file permissions and replaces destination symlinks themselves.
- **Correctness — accumulation:** chunk results now combine with the supplied
  associative operation, preserving operand order and avoiding a numeric identity.
  Multiplication and string concatenation regressions cover multiple chunk sizes.
  Associativity and possible floating-point regrouping differences are documented.
- **Correctness — links:** extracted references now resolve against the base
  document URL, including root/parent/network paths, query strings, and fragments.
  Explicit schemes remain unchanged; extraction does not filter navigation targets.
- **Correctness — assertions and matching:** approximate-equality checks reject
  NaN values/tolerances while preserving matching infinities and large integers;
  the email pattern no longer accepts a pipe in the top-level domain.
- **23 unique regression cases fail before repair.** The first repaired focused
  run passes all 69 cases. Eight additional preservation/cleanup cases cover CSV
  syncing/replacement failures, all-empty inputs, infinities, and large integers.
  CSV and accumulation docstring examples are made executable and self-contained.

### Review coverage and evidence

- Inventory and representative risk-based source review cover all **31 utility
  families**, plus deadline, audit, packaging, and workflow tooling. This is not
  exhaustive manual certification of every function. The review register names
  the inspected sources, contracts, and corresponding family test scopes.
- Filename gaps are reviewed: hostname behavior is exercised by
  `test_network_get_hostname.py`; four root SSH modules re-export tested local
  helpers. No tests were added merely to satisfy filename matching.
- The pristine baseline passes **5,963 tests, five skips, 12 warnings** in one
  invocation. The first repaired candidate passes **5,994 tests, five skips,
  12 warnings**. The five skips concern Windows symlink privileges, Unix ownership,
  and one compression package without `__all__`. Numerical warnings are retained,
  not suppressed or counted as failures.
- All **seven real HTTP/Chromium integration cases pass** on the baseline.
  Baseline lint/formatting, strict Mypy, Bandit, dependency consistency, and the
  installed-dependency vulnerability audit pass. The first candidate Mypy check
  identifies an incorrect BeautifulSoup type-ignore; an explicit string cast
  corrects the annotation without changing URL-resolution behavior.
- Initial wheel/sdist builds pass metadata checks and independent fresh-environment
  installations. Both probes verify **603 sources, 790 exports, six README
  examples**, metadata, and `py.typed`. Final artifacts are rebuilt after the
  annotation/docstring corrections and checked against the resulting checkout.

### Final verification and performance review

- The final complete invocation passes **5,994 tests, five skips, 12 warnings**.
  Coverage is **13,767 / 15,149 lines (90.88%)**. Final evidence uses the
  `verified-*` reports; earlier candidate results are retained separately.
  The overnight interruption inflated elapsed wall-clock time; it is not a
  benchmark result. No interrupted unit reports were combined to obtain this pass.
- The corrected source passes Ruff lint/formatting, strict Mypy over all 603
  package sources, Bandit, `pip check`, and `pip-audit --local`. The registry lookup
  explicitly skips the unpublished 0.2.3 project itself; dependencies report no
  known vulnerabilities. All **77 focused cases pass with Allure enabled**.
- All **seven HTTP/Chromium integration cases pass again** against the final
  package source. All **16 affected doctest statements** and **18 local links**
  pass. AST comparison preserves public signatures, constructors, decorators,
  class bases, and exports across all **603 package sources**.
- All **ten paired benchmark workloads** complete with five alternating samples,
  matching output digests, ten separate candidate profiles, and zero RSS sampling
  errors. Timing, Python allocation peaks, and absolute sampled RSS remain separate
  measurements. The benchmarked implementations are unchanged from the baseline;
  observed timing variation does not establish an optimization or regression.
  No speculative optimization or new speedup claim is retained. Profiles include
  process lifecycle, Excel parsing, and database execution costs; these results
  do not establish application-wide performance or certify every utility.
- The final wheel/sdist are rebuilt from a fresh staging directory. The separate
  environments initially resolved dependencies independently; final artifacts
  replace the package without resolving dependencies again. Logs retain the
  initial typing failure and the corrected checks. Long wall-clock durations
  spanning the overnight interruption are not performance measurements.
- Both final installed-distribution probes pass for **603 sources, 790 exports,
  six README examples**, metadata, and typing; both dependency-consistency checks
  pass. Archive SHA-256 values are retained in `final-artifact-hashes.json`.
  `findings.json`, `review-register.json`, and `verified-family-results.json`
  retain the repaired findings and all 31 families' test outcomes. Source and
  report hashes identify this uncommitted candidate independently of its baseline.

### Validation limits

- Docker health exceeded its 30-second operational deadline; no Compose project
  was started and no service resources were created. Live PostgreSQL/MySQL/SSH
  checks are unavailable locally, not passing.
- Linux/macOS and remote CI remain unverified for this unpushed changeset.
  Historical release authorization and green CI do not apply to this audit.
- Committed-change documentation CLI validation is deferred while the changeset
  remains uncommitted; documentation-policy unit tests and local links are checked.

## 0.2.2 release preparation — 2026-11-09

Publication and merging through a pull request are authorized for this release.
The existing **0.2.2** patch bump from published **0.2.1** is retained. Historical
audit sections below describe their original scope and results; their earlier
no-publication statements do not describe this release preparation.

- The first release PR, [#535](https://github.com/MForofontov/pyutils-collection/pull/535),
  merged as `a5d04581a29808c9b00622321352a21c84999753`. Exact-commit manual
  validation then exposed a missing Playwright test extra and six Allure teardown
  errors caused by globally patched filesystem functions. Publication stopped;
  no 0.2.2 tag or registry upload was created from that failed validation.
- The follow-up keeps the same unpublished 0.2.2 version, installs the full test
  extras in the manual workflow and README setup, and restores filesystem mocks
  before reporting-plugin finalizers run. Every destination-preservation and
  cleanup assertion is retained. Local reproduction recorded **56 test-body
  passes and six teardown errors** with Allure enabled, matching the CI defect.
  Follow-up evidence is under `.major-check/2026-11-09-ci-fix/` (ignored).
- After narrowing mock lifetimes, all **56 affected cases pass with Allure
  reporting enabled**. An AST comparison verifies that every assertion and
  expected-exception call in the four adjusted test modules is unchanged.
  Production package sources are unchanged from the first release candidate.
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
- Root `AGENTS.md` is canonical. Two shared skills plus native Claude,
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
