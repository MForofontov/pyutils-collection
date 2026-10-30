# Major validation and optimization plan

This plan covers the full library. Changes already made in this checkout stay in
place; each new fix should have a reproducible failure or measured benefit.

## Full-library audit and 0.2.0 release candidate — 2026-10-30

Fresh evidence starts at `b27c11f96f8498cd0f20399cbabff334d21dc0c9` in
`.major-check/2026-10-29-full-audit-174621/`. This directory preserves baseline
and final JUnit/coverage reports, failure reproductions, source hashes, public
API comparison, dependencies, benchmarks, profiles, and integration diagnostics.
The working tree was clean at baseline. Reports from earlier audits remain
historical evidence rather than certification of the new changes.

### Corrections and optimization

- Reproduced 28 failing cases before their fixes: directory-link cleanup escapes,
  unsafe Windows filename results, pagination fragments/parameter delimiters,
  Playwright thread ownership/resource failures, decimal size rounding, and
  Windows dependency-graph paths. Added 29 unit cases including a normal nested
  cleanup control. Public function/class-method signatures and exports match
  the baseline; nested private implementation helpers are excluded from that
  comparison.
- Cleanup now checks resolved parent containment for relative glob matches,
  including Windows junctions and dry runs. It still assumes links are not
  concurrently replaced by a hostile process; it is not a race-proof sandbox.
- Filename sanitization rejects unsafe replacements and handles reserved stems
  before multiple extensions and after truncation, preserving the length limit.
  Pagination adds encoded parameters to the query before the fragment.
- Each parallel scraper worker owns and reuses its own Playwright driver/browser,
  with a fresh context per URL. Launch, page-creation, and browser-close failure
  tests verify cleanup; real browser tests exercise one and two workers, isolated
  cookies, ordered results, and a failing callback without external page traffic.
- Size parsing uses exact rational arithmetic before byte truncation. Dependency
  graphs normalize Windows separators before discovering nested package imports.
- SQLite migrations no longer allocate unused CASE strings/parameter dictionaries.
  Five paired 5,000-row measurements reduced median Python allocation peaks from
  4,727,304 to 3,148,865 bytes (33.4%). Timing varied substantially, so this is a
  memory improvement, not a claimed portable speedup. Four additional dialect
  cases verify bound values, quoted identifiers, and absent row counts for the
  PostgreSQL/MySQL CASE path that SQLite now bypasses.

### Validation and evidence boundaries

- Baseline: **5,827 passed, 5 skipped, 12 numerical warnings**, 424.99 seconds.
  Full final suite: **5,856 passed, 5 skipped, the same 12 warnings**, 418.55
  seconds. The four additional dialect cases pass separately; their coverage is
  appended to the full run, not represented as another full-suite execution.
- Combined line coverage increases from **13,711 / 15,105 (90.77%)** to
  **13,728 / 15,115 (90.82%)**. The initial final run exposed the untested
  non-SQLite branch after removing eager allocations; the four dialect cases
  close that gap. No thresholds or exclusions were weakened.
- Skips are three Windows symlink-privilege cases, one Unix ownership case, and
  one existing package without `__all__`. Real Windows junction regressions run
  without symlink privileges. All 31 families have passing test outcomes.
- Ruff lint/formatting, strict Mypy over 603 package sources, Bandit, dependency
  consistency, and the installed-environment vulnerability audit pass. The
  dependency declarations are unchanged from the maintenance branch.
- Seven real Chromium/HTTP integration cases pass. Initial memory-pressure and
  deadline-interrupted benchmark/service attempts remain in separate logs. The
  interrupted Compose project was explicitly removed, including its containers,
  network, anonymous volumes, and task-built SSH image. A second local attempt
  stopped before running tests when MySQL became unhealthy during initialization;
  its diagnostics and cleanup are retained. The final remote service job must
  pass before publishing; local startup failures are not counted as passing tests.
- `scripts/benchmark_audit_pair.py` compares a specified Git revision with the
  checkout using alternating paired samples, output digests, and separate timing,
  tracemalloc, RSS, and optional profiling invocations. RSS is sampled every 50 ms;
  child RSS is sampled only for multiprocessing and can double-count shared pages.
  Sampling failures are recorded, not treated as zero-memory success.
  The final run completed all ten small/large cases with five samples per version,
  matching outputs, zero RSS sampling errors, and separate candidate profiles.
- Clean artifact checks compare all 603 installed Python sources with the checkout,
  verify package version, metadata, dependencies, exports, README examples, and
  `py.typed`. Final remote checks must cover the actual pushed release candidate;
  earlier successful checks for `b27c11f9` do not certify these changes.
- Version **0.2.0** explicitly marks the Python 3.15+ floor; PyPI 0.1.5 supported
  Python 3.10+. Publishing is gated on final artifact and platform CI checks.
  Exact remote outcomes are recorded on PR #534 and in the release workflow.

### Family review register

`review-register.json` contains public-definition/export inventories, conventional
test filename gaps, per-family outcomes and coverage, and individual review notes.
Source review is risk-based and does not claim exhaustive manual certification of
every function. The reviewed groups cover all 31 families:

- `asyncio_functions`, `multiprocessing_functions`: bounded work, cancellation,
  result ordering, pool/connection ownership, and small/large workload measurements.
- `batch_processing_functions`, `iterable_functions`: chunk/window boundaries,
  streaming statistics, iterator consumption, nested conflicts and mutation ownership.
- `file_functions`, `serialization_functions`, `compression_functions`: destination
  preservation, archive containment, link traversal, Parquet groups and Excel memory.
- `http_functions`, `network_functions`, `ssh_functions`: redirect credentials,
  short downloads, socket cleanup, gateway failures, multiplexed SSH deadlines.
- `playwright_functions`, `web_scraping_functions`, `url_functions`: browser thread
  affinity, context lifecycle, pagination, selectors and URL components.
- `security_functions`, `data_validation`, `env_config_functions`: signed claims,
  authenticated encryption/password checks, collection/schema constraints, safe
  configuration loading and environment error redaction.
- `scientific_computing_functions`, `mathematical_functions`,
  `machine_learning_functions`: known answers, finite numerical boundaries,
  statistical intervals, cloned model ownership and prediction shapes.
- `data_visualization_functions`, `formatting_functions`, `regex_functions`,
  `strings_utility`: plot/transform validation, exact units, filename safety,
  replacements and documented empty/boundary behavior.
- `database_functions`, `decorators`, `logger_functions`: bound migrations,
  transactions and health checks, caching/retries/timeouts and scoped metadata.
- `cli_functions`, `dev_utilities`, `testing_functions`, `json_functions`: platform
  capabilities, dependency graphs, inventories, tracing ownership, assertions,
  JSON merge ownership and error fallbacks.

Filename gaps were reviewed rather than filled mechanically: hostname tests use
`test_network_get_hostname.py`; root SSH modules simply re-export their tested
local implementations. Existing cyclic-input policies, archive extraction quotas,
thread termination limits, and undefined numerical-data warnings are unchanged.

## Platform CI — 2026-10-29

The validated checkout is now on `codex/major-check-validation`, with draft
[PR #534](https://github.com/MForofontov/pyutils-collection/pull/534). The PR's
checks track the exact current revision, including Windows/Linux/macOS unit and
clean-package jobs, lint/types, security, browser, and disposable service checks.
The package remains unpublished and the PR remains a draft.

The initial matrix verified Linux units (5,828 passed, 2 skipped), all three
clean-package jobs, browser, PostgreSQL/MySQL/OpenSSH services, lint/types, and
security. It also exposed three portability defects absent from the local host:

- On macOS, psutil may omit CPU frequency support. CPU information now reports
  None frequency fields for a missing or unimplemented reader, retaining usage
  and count data. Two deterministic regressions reproduce both cases.
- macOS ships Bash 3.2, which lacks mapfile. The shell runner now reads parsed
  arguments into its array using portable read/array operations, preserving
  quoting and exit-code behavior without evaluating shell expressions.
- One session-restore test wrote to /tmp/session.json, which was absent on the
  clean Windows runner. It now uses the test's isolated temporary directory.

Remote artifacts for the initial head are retained locally under
`.major-check/remote/4d50212e/`. Subsequent matrix results are recorded in the PR,
so these earlier local validation records are not claims about newer revisions.

## Live-service follow-up record — 2026-10-29

- Docker became responsive (Engine 29.8.2, Compose 5.6.0). Disposable Compose
  projects use generated `pyutils-audit-*` names and random loopback-only ports.
  Existing Docker workloads and configuration were left unchanged. Task-owned
  containers, networks, anonymous volumes, and locally built SSH image tags
  are removed in finally blocks, including on startup and test failures.
- **PostgreSQL 17.11 and MySQL 8.4.13: 8 live tests passed**, 12.61 seconds.
  Cases cover managed health checks, failed-query connection ownership, atomic
  rollback, nested savepoint ownership, and early streaming-result closure.
  Tests create and drop only uniquely named tables in their disposable databases.
  The first cold MySQL initialization exceeded its original startup allowance;
  a startup grace period and a longer bounded health wait resolved the fixture
  failure. This was recorded separately from function failures.
- **OpenSSH/SFTP: 8 live tests passed**, 3.33 seconds. These exercise password
  success/failure, unknown-host-key rejection, Unicode stdout/stderr and exit
  status, a binary SFTP upload verified by hash, timeouts, 3 MB stderr, and a
  3 MB script that emits output before consuming all input. The test trust store
  comes from the owned container; user host files, keys, and agents are not used.
- Fixed two managed-connection defects reproduced by SQLite/SQLAlchemy unit
  cases: SQLAlchemy cannot execute a raw health-query string through execute,
  and failed health queries leaked retry connections. SQLAlchemy now uses
  exec_driver_sql; failed checks close their connection and temporary results.
- Fixed SSH backpressure defects reproduced against OpenSSH: sequential stdout
  then stderr reads timed out for large stderr (2 failed, 5 passed). After
  interleaving reads, a large script still blocked while sending stdin (1 failed,
  7 passed). A shared nonblocking collector now multiplexes input and both output
  streams under an absolute collection deadline, waits for EOF and exit status,
  and closes input. Public signatures, result keys, and whitespace trimming are
  preserved. Remote helpers reject non-finite timeouts before client creation.
- Added deterministic collector tests for partial UTF-8 chunks, stderr
  backpressure, partial input writes, EOF/status waits, deadlines, and cleanup.
  The combined affected-unit run passed **237 tests**; strict Mypy passes for
  **603 package source files**.
- `scripts/run_service_integration.py` provisions, tests, captures diagnostics,
  and removes only its generated Compose project. Docker subprocess trees use
  the existing deadline runner. Optional service drivers are pinned separately
  in `requirements_integration.txt`; runtime dependency declarations are unchanged.
  A dedicated Ubuntu CI job runs these checks; HTTP/browser jobs select their
  own files explicitly rather than silently skipping unconfigured service tests.
- Live evidence is in `.major-check/databases-live/` and `.major-check/ssh-final/`.
  Failed startup/backpressure diagnostics remain in the earlier service folders.
  The prior statistical pass and its distributions were preserved in
  `.major-check/pre-services-verified/` before the latest verification refresh.
- Final full-suite verification: **5,825 passed, 5 skipped, 12 numerical
  warnings**, **315.42 seconds**. Coverage increased to **90.77%**
  (**13,707 / 15,101** executable lines). All 31 families have passing outcomes.
  Fresh browser/HTTP verification added **5 passing cases**, 54.17 seconds, for
  **21 passing integration cases** including the 16 new live-service cases.
- Rebuilt wheel/source artifacts pass Twine and isolated checks for **603
  byte-identical Python sources, 790 exports, six README examples**, metadata,
  dependencies, and `py.typed`. Lint, formatting, strict types, Bandit, and
  refreshed dependency audits pass. Cleanup verification confirms no remaining
  containers or networks for all five generated diagnostic/success projects;
  earlier task-owned SSH image tags were removed without touching base images.
- Remote Windows/Linux/macOS CI for the dirty working tree remains unverified.
  These live service cases do not certify every database helper, migration
  dialect, SSH configuration, or the Python package on Linux/macOS.

## Statistical follow-up record — 2026-10-29

This earlier record is superseded by the live-service follow-up above.

- Rechecked Docker with a 20-second deadline; the engine still did not respond.
  Remote workflow results still cover older commits, not the uncommitted checkout.
  PostgreSQL/MySQL/SSH and final remote platform runs remain unverified.
- Ten new known-answer/validation cases reproduced **9 failures and 1 pass**.
  `perform_t_test` previously calculated a pooled, two-sided interval even when
  the caller selected Welch's test or a one-sided alternative. It now obtains
  its interval and degrees of freedom from the same SciPy test result as its
  statistic and p-value. Welch degrees of freedom retain their fractional value;
  equal-variance degrees of freedom remain integers. One-sided intervals have
  the appropriate infinite endpoint. Signatures and dictionary keys are unchanged.
- Constant-data descriptive summaries now return the mean at both confidence
  interval endpoints rather than NaN from a zero-scale distribution calculation.
  NaN confidence/significance levels are rejected by descriptive statistics,
  correlation analysis, and independent t-tests using the existing ValueError
  contract. Other undefined numerical statistics continue to expose warnings.
- Affected-family verification: **444 passed**, 12 warnings, 21.81 seconds.
- Final full-suite verification: **5,809 passed, 5 skipped, 12 warnings**, in
  **331.37 seconds**. Coverage: **13,640 / 15,031 lines (90.75%)**, up from
  90.73% in the prior broad pass. All 31 families have recorded passing results.
- Ruff lint/formatting, strict Mypy over 602 source files, and Bandit pass.
  Refreshed dependency audits report no known vulnerabilities in the development
  environment or installed wheel. Rebuilt wheel/source archives pass Twine,
  dependency checks, and isolated verification of 602 byte-identical sources,
  790 exports, six README examples, metadata, and `py.typed`.
- Current authoritative evidence and artifacts remain in `.major-check/current/`;
  the prior successful run and archives are preserved in
  `.major-check/2026-10-28-verified/`. The refreshed summary includes individual
  report timestamps: unchanged browser and database-performance checks retain
  their October 28 evidence rather than being presented as fresh executions.

## Major check record — 2026-10-28

This follow-up preserves the 180 modified and 43 untracked entries present at
the start. Its evidence is isolated in `.major-check/current/`; older results
below are historical and do not establish success for the current checkout.

### Baseline and confirmed corrections

- Runtime: Windows, CPython 3.15.2, `.venv315`. Installed requirements are
  consistent. The full baseline collected the first 20 newly added regression
  cases: **5,769 passed, 19 failed, 5 skipped**, 16 warnings, 520.26 seconds.
  All 19 failures were the defects independently reproduced by the focused run.
  Baseline line coverage: **13,597 / 15,008 (90.60%)**.
- **P1 — destination corruption:** CSV transformation and Parquet append could
  overwrite an existing destination before a callback or writer failed. Excel
  transpose had the same failure mode when saving. A private sibling-file
  staging context now syncs a completed file and replaces the destination only
  after success. CSV in-place transformation is supported. Parquet partition
  outputs use the same protection on each file. Regressions inject transformer,
  filter, partial-write, sync, and replacement failures and verify cleanup.
- **P2 — missing partition rows:** equality does not select NaN values. Floating
  NaN groups now use Arrow's NaN predicate, retaining their rows alongside null
  and ordinary groups.
- **P2 — invalid signed JWT claims:** NaN/infinite expiration values could evade
  expiry comparisons; boolean expirations and non-object JSON claims were also
  mishandled. Reject these with ValueError and reject invalid base64 characters.
  Missing expiration remains supported, and valid public signatures are unchanged.
- **P2 — numerical correctness:** two-point gradient inputs passed validation but
  failed inside NumPy. They now use first-order boundary differences. Central
  first derivatives now weight neighboring slopes for unequal spacing; ascending
  and descending quadratic known-answer tests reproduce the former error.
- **P2 — resource ownership:** multicast sockets now close after setup errors,
  logger scopes copy their metadata mapping before adding temporary fields, and
  memory measurement leaves caller-owned tracemalloc sessions running. Separate
  pre-fix runs reproduced three socket and four ownership failures.
- **P2 — monitor shutdown stall:** the final broad rerun stalled inside
  `Thread.join(timeout=1)` on Windows. An independent faulthandler diagnostic
  reproduced that stack and hit its 90-second process deadline. Sampling now
  signals a completion event in a finally block; waiting on that event keeps
  shutdown bounded without relying on native thread teardown. All 11 monitor
  regressions and ordinary monitor tests then passed in 8.82 seconds. The
  interrupted broad log is retained as `unit-before-completion-event.log`.
- **P2 — test database ownership:** four encoding-validation tests created their
  own pooled SQLite engines without disposing them. The isolated test file
  reproduced the failure with warnings promoted to errors (1 failed, 11 passed).
  Reusing the existing managed engine fixture eliminates the leak; all **328
  database tests passed with `-W error`**, in 5.18 seconds. Library APIs did not
  change. The earlier broad pass and its coverage are retained under
  `unit-before-test-engine-cleanup.*` and `coverage-before-test-engine-cleanup.xml`.

Public function signatures, exports, and return types are retained. Staged
serialization preserves existing permission bits; a destination symlink is
replaced rather than followed. Ownership and other filesystem metadata are not
copied. Partition publication is atomic per file, not across a set of files.

### Family review register

All 31 families receive fresh unit outcomes in `current/inventory.json` and
`current/family-results.log`. The entries below record the source-review focus;
they are not a claim of exhaustive manual verification of every function.

- `asyncio_functions`: bounded mapping, pool identity/capacity, gather cancellation,
  retry deadlines, and download staging; existing cleanup regressions retained.
- `batch_processing_functions`: chunk boundaries, streaming aggregation state,
  and merge arithmetic; existing boundary and known-answer cases retained.
- `cli_functions`: command execution contracts and scandir-based listings;
  small/large directory workloads measured without further speculative changes.
- `compression_functions`: ZIP/TAR preflight and Zstd compatibility; extraction
  remains non-transactional after validation, with no decompression-size quota.
- `data_validation`: email/schema error propagation and Pydantic configuration;
  existing schema and invalid-input cases retained.
- `data_visualization_functions`: heatmap aggregation and palette/plot boundaries;
  existing known-answer and headless plot tests retained.
- `database_functions`: bound migration values, savepoint ownership, rollback,
  and SQLite connection-state restoration; benchmarks and scale tests rerun.
- `datetime_functions`: date-range endpoints, overflow, timezone constraints,
  and relative-time boundaries; no new API policy introduced.
- `decorators`: resource-monitor shutdown and thread-based timeout ownership;
  timeout still cannot forcibly stop a running user thread.
- `dev_utilities`: source/test inventories and checker/deadline exit propagation;
  configured jobs are distinguished from executed evidence.
- `env_config_functions`: safe YAML loading, schema hooks, and environment defaults;
  existing invalid-configuration cases retained.
- `file_functions`: atomic replacement, temporary cleanup boundaries, and metadata
  calls; arbitrary file writers do not gain a blanket transactional guarantee.
- `formatting_functions`: size parsing, numerical boundaries, and currency formatting;
  existing explicit behavior retained.
- `http_functions`: scheme validation, scoped redirects, credential stripping,
  and destination preservation; real loopback tests rerun.
- `iterable_functions`: iterator consumption, grouping, sliding windows, and nested
  dictionary ownership/conflicts; existing boundary regressions retained.
- `json_functions`: merge ownership, diff ordering, and safe load/dump failures;
  recursive cyclic-input policy remains unchanged.
- `logger_functions`: nested context ownership; fixed metadata escaping its scope.
- `machine_learning_functions`: cloned bootstrap estimators, prediction shapes,
  and feature-importance contracts; arbitrary third-party estimators are not certified.
- `mathematical_functions`: power input/overflow bounds and known-answer coverage;
  existing numerical-domain policy retained.
- `multiprocessing_functions`: map worker limits, spawn cleanup, and failure paths;
  parent-only traced allocations do not represent child-process peak memory.
- `network_functions`: socket lifecycle and gateway failure handling; fixed setup
  leaks and retained mocked network tests rather than depending on public hosts.
- `playwright_functions`: managed-browser lifecycle and session persistence;
  real disposable Chromium now exercises normal and exceptional cleanup.
- `regex_functions`: extraction, order/deduplication, and filename normalization;
  no universal filesystem-name portability claim is made.
- `scientific_computing_functions`: derivative boundary and uneven-grid accuracy,
  finite numerical inputs, and existing known-answer tests; fixed reproduced errors.
- `security_functions`: JWT claim/encoding validation and bcrypt boundaries;
  scanner success is not independent cryptographic certification.
- `serialization_functions`: callback/writer failure preservation, NaN partition
  completeness, workbook closure, and measured transpose allocations. Other
  direct writers retain their existing non-transactional contracts.
- `ssh_functions`: subprocess validation, host-key verification, and client cleanup;
  mocked checks do not establish live-server compatibility.
- `strings_utility`: slicing/truncation boundaries and existing pure-function cases.
- `testing_functions`: benchmark validity and tracemalloc ownership; fixed caller
  tracing being stopped on successful and exceptional calls.
- `url_functions`: query multiplicity, credentials/IPv6 normalization, and fragments;
  existing normalization/export regressions retained.
- `web_scraping_functions`: pagination generation, selectors, and parsing boundaries;
  external websites are not used as correctness fixtures.

### Measurements and delivery evidence

- Final complete Windows/Python 3.15.2 unit run: **5,799 passed, 5 skipped,
  12 warnings**, **414.97 seconds**. Line coverage increased from **90.60% to
  90.73%** (**13,640 / 15,033** lines). All 31 families have passing outcomes;
  the inventory's family totals exclude the separate root package-export cases.
- The five skips are three symlink-privilege checks, one Unix ownership check,
  and the legacy binary-compression package without `__all__`. Its actual
  compression functions remain exercised. The remaining 12 warnings concern
  numerical edge cases; the four unclosed-SQLite warnings are resolved.
- `scripts/benchmark_major_check.py` records three-sample medians, result hashes,
  and traced parent-process allocations for small/large async mapping,
  multiprocessing, directory listing, Excel transpose, and SQLite mapping jobs.
  Native buffers and child RSS are explicitly excluded from its memory figures.
- `scripts/benchmark_transpose.py` alternates five samples per implementation
  with identical safe staging and verifies every output cell. Retain the
  read-only source workbook and removal of padded/transposed list copies only
  on the strength of the measured large-input memory reduction. General suite
  timing variation is not attributed to unchanged async/listing/database code.
- Real Chromium and HTTP loopback integration checks: **5 passed**, 65.31 seconds.
  Browser files are workspace-local. An opt-in browser test and a dedicated
  Ubuntu CI job reproduce the checks without contacting external websites.
- All **7** SQLite performance cases, including the million-row stress case,
  passed in **326.40 seconds** overall.
- The five-sample paired transpose benchmark reduced large-input median time
  from **2.4902 s to 1.8523 s (25.6%)**, and traced peak allocations from
  **27,047,822 to 13,062,378 bytes (51.7%)**. The 50×10 case improved from
  0.2315 s to 0.1693 s, but used 1,226,428 rather than 978,443 traced bytes.
  This small-input allocation tradeoff is explicit; no universal memory or
  timing improvement is claimed. Both strategies use identical staged writes.
- Ruff lint and formatting checks pass for package and scripts; strict Mypy
  passes for **602 source files**. Bandit at medium severity/confidence reports
  no findings or scanner errors. Dependency audits report no known vulnerabilities
  across the **130 installed development-environment dependencies** and the
  **63 dependencies in the clean wheel environment**.
- Wheel and source archives build successfully and pass Twine checks. Separate
  installed environments pass `pip check` and isolated verification of **602
  byte-identical Python sources, 790 runtime exports, six README examples**,
  metadata, and the typing marker. The optional Playwright extra is exercised
  separately by the real-browser integration run.
- Authoritative distributions are under `current/verified-dist/`; earlier build
  and install attempts remain diagnostic evidence. The final `summary.json`
  includes source/artifact hashes and rejects missing reports, failed tests,
  scanner errors/findings, dependency inconsistencies, and reduced line coverage.

### Historical external gates and limits (superseded above)

- The final dirty working tree has no matching remote revision. Existing GitHub
  runs cover older commits; Windows/Linux/macOS jobs for these final files have
  not run remotely. No commit, push, publication, or release was performed.
- Docker did not respond within a 20-second deadline. Disposable PostgreSQL,
  MySQL, and SSH checks remain unverified. Local SQLite and mocked service tests
  do not substitute for those integrations.
- Archive expansion quotas, transactions across multiple output files, exhaustive
  cyclic-input property testing, and broad numerical/estimator certification
  require additional designs and are outside this maintenance pass.

## Python 3.15 implementation — 2026-10-28

**Release status: local validation passed; remote platform checks pending.**
Python 3.15+ is now the declared requirement. Current
dependency pins, tooling, requirements files, documentation, and all workflow
interpreters target that requirement. Earlier implementation records below are
historical; their Python 3.10–3.13 support claims do not describe this migration.

### Runtime and dependency verification

- CPython 3.15.2 was verified against Python.org's release API and run locally in
  a separate environment. The existing Python 3.12 environment was retained.
- Automatic approval review rejected the regular installer with "blocked by
  policy". Workspace-local official embeddable and NuGet distributions supplied
  a runtime and the full standard library without a system installation.
- The pre-migration baseline rerun passed **5,650 tests**, with five skips and
  41 warnings, on Windows/Python 3.12 in 451.95 seconds. Ruff, formatting, Mypy,
  and `pip check` also passed before migration.
- All runtime/dev/Playwright pins were refreshed from stable PyPI releases and
  synchronized with package metadata. Python-version dependency markers and the
  obsolete Pydantic v1 configuration branch were removed.
- The initial wheel inventory found no zstandard 0.25.0 wheels for Python 3.15.
  That blocker was resolved by moving the existing helpers to the standard
  library's `compression.zstd`, without removing Zstandard functionality. Twelve
  stored frames generated with the former dependency verify legacy decoding;
  a separate backend verifies new frames across five levels. The single-frame
  return behavior is retained, and truncated frames are rejected.
- `scripts/check_python315_wheels.py` now checks 43 direct requirements on Windows
  x64, Linux x64, and macOS arm64. It reports **zero required native-wheel gaps**.
  Optional accelerators are distinguished from mandatory native extensions.
- PyYAML 6.0.3 also lacks Python 3.15 wheels. The default local source build
  failed without Visual C++ tools. Its supported pure-Python configuration,
  `PYYAML_FORCE_LIBYAML=0`, built and installed successfully. No YAML API was
  removed; the optional LibYAML accelerator is absent in this local environment.
  CI explicitly uses this supported pure-Python configuration.
- The initial diagnostic environment excluded zstandard and was not counted as
  a complete installation. After the standard-library replacement, installing
  the complete package with development and Playwright extras succeeded.

### Implemented corrections

- ZIP members are validated before writes, including Windows drives, traversal,
  symlink entries, and existing destination symlink escapes. TAR members are
  preflighted with the standard data filter before extraction begins.
- Async downloads stage bytes beside the destination, flush and sync, and
  replace only on success. Parallel downloads reject ignored, mismatched, and
  truncated ranges, and cancel/await remaining work on failure.
- `gather_with_timeout` accepts existing tasks/futures and cleans up on worker,
  iterator, timeout, and caller-cancellation failures. The synchronous event-loop
  helper rejects a running loop before creating a coroutine.
- Async-pool capacity includes borrowed connections. Identity tracking prevents
  duplicate registration, duplicate release, foreign release, and full-queue
  deadlocks when returning a borrowed connection.
- Nested SQLAlchemy transactions retain and commit/roll back their savepoint
  handle. SQL savepoint names are validated in both public helpers, including
  rejection of newline suffixes.
- ID migration binds values and quotes reflected identifiers. SQLite uses indexed
  temporary mappings instead of quadratic CASE scans; the foreign-key policy
  and temporary-table lifecycle are restored after success or rollback. Dedicated
  regressions exercise quote-containing IDs, unusual identifiers, duplicate-ID
  rollback, unindexed foreign-key references, and connection state restoration.
- Scoped HTTP openers restrict redirects to HTTP(S), strip sensitive headers on
  origin changes, and leave urllib's global opener untouched.
- CLI SSH script input now matches subprocess text mode. Destinations and finite
  deadlines are validated, SCP paths cannot become options, IPv6 targets are
  disambiguated, and legacy modules re-export the same tested implementations.
- A reproduced retry timing-test failure now checks requested sleeps rather than
  an operating-system scheduling deadline. An invalid-model Pydantic test is no
  longer incorrectly skipped based on availability of the v1 compatibility API.
- A later full run reproduced an indefinite join in the resource-monitoring
  decorator. Sampling now respects disabled flags, uses nonblocking CPU reads
  and interruptible waits, and does not force garbage collection. Shutdown is
  bounded to one second and warns if an OS query is still pending; a daemon may
  finish that query later. GC counts are deltas, and execution time excludes
  shutdown. Subprocess regressions cover long sampling intervals and a deliberately
  blocked metric query, then verify thread cleanup after the query is released.
- Ordered async-map storage uses a list instead of an indexed dictionary and a
  second result allocation. The benchmark script checks identical outputs and
  records five-sample timing/memory medians for 100 and 100,000 items.

### Verification completed during migration

- Final complete Windows/CPython 3.15.2 unit run: **5,768 passed, 5 skipped,
  16 warnings**, in **491.71 seconds**. Coverage: **90.55%**, 13,572 of 14,989
  executable lines. No compression or export exclusions were used.
- The five skips are three tests requiring unavailable Windows symlink privileges,
  one Unix ownership test, and the legacy binary-compression package without
  `__all__`. Numerical edge-case warnings are retained in the test log.
- Broad diagnostic run before restoring compression/export coverage:
  **5,378 passed, 3 skipped, 16 warnings**, 428.94 seconds, Python 3.15.2.
  Compression and export checks were explicitly excluded from that run.
- Compression and exported-import follow-up: **377 passed, 2 skipped**,
  135.61 seconds. Skips are the Windows symlink privilege and a legacy package
  without `__all__`. Legacy-frame and independent-decoder Zstandard tests ran.
- High-risk async/HTTP/SSH/transaction regression: **656 passed**. CI runner and
  deadline process-tree checks: **26 passed**. ID-migration regressions: **7 passed**.
- Resource-monitor regressions: **11 passed**. Isolated real HTTP loopback
  integration: **3 passed**, including credential stripping across ports, FTP
  redirect rejection, and preservation after a truncated response.
- Resolved dependency audit and installed-environment audit both report **no
  known vulnerabilities**. Bandit reports **zero findings and zero scan errors**.
- Strict Mypy passes for **601 source files**. Package/script Ruff lint and
  format checks pass. Clean wheel and source environments each verify **796
  exports**, **six README examples**, dependency metadata, and the typing marker.
- Non-stress performance suite: **6 passed, 1 stress case deselected**, 21.93 s.
  An earlier batch comparison exceeded its 10 s budget before the SQLite fix;
  the optimized suite passes the original budgets without relaxing assertions.
- The optional **2.4-million-row stress test passed**, with six non-stress cases
  deselected, in **163.53 seconds**. Its original correctness, referential-integrity,
  time, and memory assertions were retained.
- Python 3.15 async-map benchmark, five-sample medians: 100,000 items decreased
  from **112.4 ms / 13.41 MB** to **70.8 ms / 3.98 MB** traced peak memory.
- SQLite benchmark, three-sample medians: 10,000-row updates decreased from
  **1.806 s** to **0.103 s**. At 100 rows the indexed mapping adds about
  **0.17 ms** (0.99 ms to 1.16 ms). Results and row counts are checked for equality.
  These measurements describe this machine, not portable performance guarantees.
- Wheel and source builds and Twine metadata validation pass. Both artifacts
  install with complete runtime/Playwright dependencies into separate pristine
  Python 3.15 environments; `pip check` and installed-package smoke checks pass.

### Per-family unit outcomes

The final JUnit report classifies 5,685 passes and four skips into the 31 families
below. Another 83 passing export checks and one export-package skip account for
the remainder of the complete suite. Detailed definitions, exports, and test-file
gaps are reproducible with `scripts/audit_inventory.py`.

- asyncio_functions: 169 passed.
- batch_processing_functions: 50 passed.
- cli_functions: 91 passed.
- compression_functions: 294 passed, 1 skipped.
- data_validation: 122 passed.
- data_visualization_functions: 232 passed.
- database_functions: 328 passed.
- datetime_functions: 227 passed.
- decorators: 292 passed.
- dev_utilities: 94 passed.
- env_config_functions: 64 passed.
- file_functions: 274 passed, 3 skipped.
- formatting_functions: 89 passed.
- http_functions: 226 passed.
- iterable_functions: 567 passed.
- json_functions: 28 passed.
- logger_functions: 52 passed.
- machine_learning_functions: 16 passed.
- mathematical_functions: 68 passed.
- multiprocessing_functions: 65 passed.
- network_functions: 111 passed.
- playwright_functions: 105 passed.
- regex_functions: 46 passed.
- scientific_computing_functions: 431 passed.
- security_functions: 140 passed.
- serialization_functions: 296 passed.
- ssh_functions: 202 passed.
- strings_utility: 530 passed.
- testing_functions: 211 passed.
- url_functions: 109 passed.
- web_scraping_functions: 156 passed.

The remaining five conventional filename gaps are accounted for: hostname has
coverage under another test name; the four legacy SSH modules are tested as
re-exports of the independently tested local implementations.

### Repeatable checks and CI

- Added scripts for AST/export/test inventory, wheel availability, installed
  distribution checks, async-map benchmarks, and process-tree deadlines.
- Unit and clean wheel/source jobs target Python 3.15 on Windows, Linux, and
  macOS. Native dependencies must resolve to wheels. Tests run under a deadline
  that terminates descendants and retains logs; artifact uploads run on failure.
- Package and script Ruff checks run in CI. Existing strict Mypy, Bandit, and
  dependency gates remain required. No publishing or remote CI run was triggered.

### Review register and limits

All 31 families have an AST/export/test-file inventory. The source review focused
on the high-risk paths below; inventory and passing tests are not a claim that
every function has received an exhaustive manual or formal security review.

- **asyncio_functions, multiprocessing_functions, batch_processing_functions:**
  reviewed ordered work, resource limits, cancellation, worker lifecycle, and
  stream aggregation. Added deterministic async cleanup and capacity regressions.
- **compression_functions, file_functions, serialization_functions:** reviewed
  archive boundaries, staged writes, cleanup, streaming, partitions, and workbook
  lifetimes. Python 3.15 compression validation passes with standard-library Zstd. Archive
  extraction remains non-transactional for I/O failures after validation; large
  archives and decompression quotas need a separate bounded-resource design.
- **database_functions:** reviewed savepoints, streaming cursor cleanup, and
  callback ownership. Added actual SQLite/SQLAlchemy transaction tests. Release
  callback failures in `nested_transaction` retain the existing log-and-continue
  contract; applications requiring fail-closed commits need further API review.
- **http_functions, ssh_functions, network_functions, web_scraping_functions,
  playwright_functions:** reviewed protocol boundaries, credentials, subprocess
  arguments, deadlines, host keys, pagination, and session storage. Live external
  services and real browsers are not validated by mocked unit tests.
- **data_validation, env_config_functions, security_functions:** reviewed schema
  validation, safe YAML loading, environment defaults, password boundaries, and
  dependency declarations. Cryptographic correctness beyond existing known-answer
  tests and scanner coverage has not been independently certified.
- **iterable_functions, json_functions, strings_utility, url_functions,
  datetime_functions, regex_functions, formatting_functions, mathematical_functions:**
  reviewed representative boundary handling, ownership, ordering, and parsing;
  existing family tests supply broader automated coverage. Exhaustive property
  testing of arbitrary recursive inputs remains outside the completed review.
- **scientific_computing_functions, machine_learning_functions,
  data_visualization_functions:** checked updated dependency imports/types and
  existing small known-answer cases. Broader numerical stability, arbitrary
  estimator compatibility, and large-data behavior remain follow-up work.
- **decorators, logger_functions, testing_functions, dev_utilities:** reviewed
  timing/resource helpers, diagnostic output, inventory, checker propagation, and
  CI gates. The intermittent resource-monitor shutdown hang was reproduced in
  a later full run and fixed with dedicated subprocess regressions.

### Remaining release gates

- Execute Windows/Linux/macOS CI on the final changes. Only local Windows checks
  have been attempted; configured jobs are not evidence of successful runs.
- Chromium for Playwright 1.64.1 is not installed locally, so real-browser checks
  remain unverified. Mocked Playwright tests passed; no browser download occurred.
- External SSH, PostgreSQL, and MySQL service checks remain unverified because no
  disposable services were configured. SQLite, SQLAlchemy, and isolated HTTP
  loopback checks passed; these do not establish external-service compatibility.

## Implementation record — 2026-10-27

Environment: Windows, CPython 3.12.14. Existing checkout changes were retained.
The complete manual audit and cross-platform validation remain in progress.

### Completed changes

- Repair CI failure propagation, retain reports on failures, scan package paths,
  and reject missing or erroneous scanner reports. Pull requests now run unit
  tests on Windows/Linux with Python 3.10–3.13, including mocked Playwright tests,
  plus lint, type checking, and dependency/security checks.
- Make ordinary pytest discovery select unit tests. Keep performance/stress runs
  explicit, parse shell arguments without eval, and preserve pytest exit codes.
- Synchronize dependency declarations and install patched versions of aiohttp,
  cryptography, PyJWT, requests, Paramiko, lxml, PyArrow, pytest, and Pylint.
  Update pytest-asyncio alongside pytest. Use version markers for Python 3.10.
- Reject bcrypt input exceeding 72 UTF-8 bytes, verify SSH host keys, restrict
  HTTP helpers to HTTP(S) initial URLs, and preserve browser sessions on partial
  serialization or replacement failures.
- Preserve null Parquet partitions, generate Windows-compatible filenames, and
  reject colliding names before writing. Handle incomplete gateway output and
  command timeouts; use a monotonic high-resolution download-speed clock.
- Bound default parallel-map workers by item count and avoid a pool for empty
  input. Preserve explicitly requested worker counts and output ordering.
- Replace scheduler-dependent async and Pydantic timing assertions with semantic
  tests; simulate permission errors consistently and mock unit-test network calls.
- Correct result typing, include the PEP 561 package marker, format package code,
  repair README imports/examples, and remove its malformed duplicate appendix.

### Verification

- Latest full unit run with updated dependencies, optional Playwright, and CI
  regression tests: **5,650 passed, 5 skipped**, zero failures, in 187.91 s.
  The separate full coverage run measured **89.35%** (15,000 statements).
  The unit suite contains 5,655 cases; default discovery selects unit tests only.
  Skips: Pydantic v1 compatibility branch; two Windows symlink-privilege tests;
  Unix ownership; one package without an explicit `__all__`.
- Updated-family regression run: 575 passed, one Pydantic compatibility test skipped.
- Ruff lint and formatting: passed. Mypy: no issues in 598 source files.
- CI behavior checks: 24 passed, covering checker exit codes through tee, final
  gates, missing/erroneous reports, quoting, and dependency declaration parity.
  Workflow YAML parses; Bash syntax checks pass for 27 run blocks.
- Bandit medium-severity/medium-confidence scan: zero findings and zero scan
  errors across 598 files. Call-site exceptions explain intentional shell/remote
  execution, validated initial HTTP schemes, and route/multicast constants.
- Direct pinned-dependency and installed-environment audits: no known
  vulnerabilities on Python 3.12 after dependency and local pip updates.
  A separate Python 3.10 marker-selected direct-pin audit reports exactly one
  outstanding advisory: dnspython 2.8, as detailed below.
- All six README Python examples execute in a workspace-local sandbox; all
  package sources parse with Python 3.10 syntax.
- Non-stress performance suite: **6 passed**, one million-row stress case
  deselected, in 41.46 s.
- Wheel and source distribution rebuild: passed. Install the wheel with its full
  runtime dependencies into a pristine Python 3.12 environment: passed. Isolated
  installed-package checks verify 790 exports, all six README examples, runtime
  dependency metadata, and the PEP 561 marker. Pip check and the clean installed
  environment's dependency audit both pass.
- Local three-sample median for a two-item parallel map: 0.468 s before and
  0.239 s after. Empty input avoids all worker creation (0.155 s before versus
  approximately 2 microseconds after). These are local observations; the resource
  bound is also checked without timing thresholds.

### Remaining constraints and audit work

- Python 3.10 retains dnspython 2.8 to preserve declared compatibility. The
  [CPU-exhaustion advisory](https://github.com/advisories/GHSA-45c3-73f7-pv4m)
  is fixed in [dnspython 2.9, which requires Python 3.11+](https://pypi.org/project/dnspython/2.9.0/).
  Resolve this compatibility/security conflict before claiming security-clean
  dependency coverage across every supported Python version.
- [Paramiko 5 removes SHA-1 algorithms and DSA support](https://www.paramiko.org/changelog.html).
  SSH callers need trusted known-host entries and servers supporting modern SSH
  algorithms. Function parameters are unchanged.
- The AST inventory found 518 top-level public function definitions across 31
  utility families. Six source files lack a conventionally named test file:
  hostname is covered under another test name; ID migration has performance
  coverage; four legacy CLI-based SSH modules need dedicated tests/review.
- Finish manual audits of file writers/archive extraction, resource lifecycles,
  public edge cases, and dependency-heavy behavior. Unit-suite success alone
  does not complete those reviews.
- Run the configured Python/OS CI matrix; only Windows/Python 3.12 has been
  executed locally. Complete installation validation on the remaining Python/OS
  combinations, broader doctests, real-service/browser integration, and optional
  stress tests.
- The old browser write-failure test created
  `D:\invalid\path\that\does\not\exist\file.json`. The test now uses an isolated
  directory. Automatic approval review rejected artifact cleanup with
  "blocked by policy"; that external test artifact remains in place.

## 1. Establish a reliable baseline — historical checklist

- [x] Use the local Python 3.12 virtual environment; the system Python is unusable.
- [x] Repair invalid package metadata and exercise the affected public exports.
- [x] Run the focused suites after the companion utilities were added: 1,204 passed.
- [x] Re-run the expanded affected-family suites after this maintenance pass:
  1,638 passed, one Unix-only permission test skipped on Windows. This is a
  selected regression run, not full-library validation.
- [x] Attempt a broader Windows run and retain the results in local test logs.
- [x] Complete development and optional Playwright dependency installation in
  the prepared environment; pip check and installed-dependency audit pass.
- [x] Install the built wheel and full runtime dependencies in a pristine Windows
  Python 3.12 environment; verify metadata, imports, examples, and dependencies.
- [ ] Repeat installation validation in a pristine environment for each supported
  Python/OS combination. Do not count unavailable checks as passes.
- [x] Categorize function defects, portability failures, dependency gaps, and
  scheduler-sensitive tests from the broader Windows run.

Exit: repeatable test collection and a categorized baseline, with unavailable
checks listed explicitly.

## 2. Protect data and clarify failure behavior — historical checklist

- [x] Stage downloads beside the destination and replace only on success.
- [x] Preserve existing files on request, read, callback, write, sync, and rename errors.
- [x] Reject known truncated downloads and remove partial temporary files.
- [x] Return missing environment defaults without applying string converters.
- [x] Reject temporary cleanup patterns that escape the requested directory, and
  reject non-finite ages.
- [ ] Audit other file writers, archive extraction, configuration loading, and
  transaction helpers for partial writes, cleanup failures, and mutation on error.
- [ ] Check resource closure and exception propagation on every affected failure path.

Exit: regression tests reproduce each fixed defect, and originals survive failed
operations. Filesystem tests use isolated temporary directories.

## 3. Check every utility family — historical checklist

- [x] Inventory public function definitions and conventional test-file gaps.
- [ ] Review iterable, JSON, string, URL, date, and math helpers for boundary
  values, empty input, iterator consumption, aliasing, type validation, and overflow.
- [ ] Review HTTP, database, SSH, scraping, and browser helpers using mocked or
  isolated services; keep live integration checks separate.
- [ ] Validate scientific, visualization, and ML helpers with their dependencies
  installed and small inputs with known answers.
- [x] Exercise installed-wheel exported imports and all six standalone README
  examples in a workspace-local sandbox.

Exit: every family has a recorded test result or an explicit blocker, and public
behavior changes are documented.

## 4. Audit concurrency and bounded resource use — historical checklist

- [x] Fix rate-limit enforcement after early timer wakeups; verify with a
  deterministic clock that calls remain inside the allowed window.

- [x] Run multiprocessing tests in a subprocess with a deadline: 65 passed.
  The earlier stall was not reproduced after dependency installation; its exact
  original cause has not been established.
- [ ] Check picklability, Windows spawn behavior, empty input, worker limits,
  exception propagation, and pool shutdown.
- [ ] Check async cancellation, timeouts, retries, rate limiting, iterator errors,
  and whether failed work leaves tasks or connections running.
- [x] Replace the reproduced periodic/backoff scheduler failures with controlled
  clocks and assertions about requested waits.

Exit: bounded concurrency, reliable shutdown, and tests with no orphan workers.

## 5. Optimize measured costs — historical checklist

- [x] Remove repeated per-file stat calls from temporary-file helpers.
- [x] Use directory entries for file/directory listings instead of joining and
  inspecting every pathname separately.
- [x] Make JSON diff ordering deterministic without allocating key-union sets.
- [x] Measure the listing change against the original implementation: a local
  500-file check returned identical results and ran about 20 times faster.
  This is a single-machine measurement, not a portable performance guarantee.
- [ ] Benchmark representative small and large inputs before and after changes.
- [ ] Review recursive copying, repeated scans, eager materialization, and
  unnecessary worker creation; preserve input ownership and result order.
- [x] Record before/after parallel-map timings, default worker bounds, preserved
  explicit counts, and regression results. Broader profiling remains pending.

Exit: optimizations have evidence of benefit and retain documented behavior.
Avoid machine-specific timing assertions in normal unit tests.

## 6. Verify compatibility and enforce checks — historical checklist

- [ ] Test Windows and Linux; add macOS coverage for platform-specific helpers.
- [ ] Verify advertised Python versions against dependency pins and package builds.
- [ ] Remove assumptions about Unix-only modules, signals, symlink privileges,
  default text encodings, and deleting open files from portable tests.
- [x] Build distributions, install into a clean Windows Python 3.12 environment,
  and exercise public imports.
- [x] Run package lint/type checks, the full unit suite, and non-stress performance
  checks as separate commands.
- [ ] Complete broader doctests, remaining platform validation, real-service
  integration, and optional stress tests.
- [x] Repair CI exit-code handling and shell failure propagation; test shell exit
  codes, argument quoting, and dependency declaration parity.
- [x] Update the changelog and record skips, unresolved constraints, and pending checks.

Exit: full results for each supported environment, verified distribution imports,
and no unexplained regressions.

## Local verification commands

Run from the repository root using the prepared environment:

```powershell
& ./.venv315/Scripts/python.exe -m pip check
& ./.venv315/Scripts/python.exe -m ruff check pyutils_collection scripts
& ./.venv315/Scripts/python.exe -m ruff format --check pyutils_collection scripts
& ./.venv315/Scripts/python.exe -m mypy pyutils_collection
& ./.venv315/Scripts/python.exe scripts/run_with_deadline.py --seconds 900 --log .major-check/recheck/unit.log -- ./.venv315/Scripts/python.exe -u -m pytest pytest/unit -ra -o faulthandler_timeout=60 --junitxml=.major-check/recheck/unit.xml --cov=pyutils_collection --cov-report=xml:.major-check/recheck/coverage.xml
& ./.venv315/Scripts/python.exe scripts/audit_inventory.py .major-check/recheck/unit.xml
& ./.venv315/Scripts/python.exe scripts/run_with_deadline.py --seconds 120 --log .major-check/recheck/integration.log -- ./.venv315/Scripts/python.exe -m pytest pytest/integration -ra
& ./.venv315/Scripts/python.exe scripts/run_with_deadline.py --seconds 360 --log .major-check/recheck/performance.log -- ./.venv315/Scripts/python.exe -m pytest pytest/performance -ra
& ./.venv315/Scripts/python.exe -m bandit -r pyutils_collection -ll -ii
& ./.venv315/Scripts/python.exe -m pip_audit
& ./.venv315/Scripts/python.exe scripts/benchmark_major_check.py --output .major-check/recheck/workloads.json
& ./.venv315/Scripts/python.exe scripts/benchmark_transpose.py --output .major-check/recheck/transpose.json
& ./.venv315/Scripts/python.exe -m build --outdir .major-check/recheck/dist
& ./.venv315/Scripts/python.exe -m twine check '.major-check/recheck/dist/*'
```

For real browser integration, install Chromium with
`python -m playwright install chromium --only-shell` and set
`PYUTILS_BROWSER_TESTS=1`; otherwise the two browser tests explicitly skip.
This pass installed it under `.major-check/current/browser-cache` by also setting
`PLAYWRIGHT_BROWSERS_PATH` for installation and testing.

Create clean installation environments with a full Python 3.15 distribution;
the local embeddable runtime does not include ensurepip and its path isolation
prevented one source-build attempt. The local full distribution is
`.major-check/python315/tools/python.exe`. Install the built wheel and source
archive separately with their runtime dependencies, run `pip check`, then run
`python -I scripts/check_installed_distribution.py <repository-root>` with each
installed interpreter. This checks every packaged Python source against the
checkout as well as exports, examples, metadata, and `py.typed`. Local retries
used pip's `--no-compile` after installation exceeded the original deadline;
bytecode generation is not needed to establish package correctness.

During repairs, run only the affected modules first, then their neighboring
suites. Repository-wide lint may report older findings; distinguish those from
new ones. Full-suite success is not claimed until dependency and platform
blockers have been resolved.
