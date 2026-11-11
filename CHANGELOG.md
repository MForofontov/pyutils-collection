# Changelog

## Live-service follow-up — 2026-10-29

### Fixed
- Run SQLAlchemy connection health queries through its driver-SQL interface and
  close failed health-check connections and temporary results before retrying.
- Multiplex SSH stdin, stdout, and stderr to prevent shared-window deadlocks
  with large stderr or scripts that produce output before reading all input.
  Enforce a finite input/output collection deadline and reject non-finite
  timeouts before creating remote SSH clients.

### Validation
- Add disposable PostgreSQL, MySQL, and OpenSSH/SFTP protocol tests, isolated
  loopback ports, fixture trust stores, pinned optional test drivers, diagnostic
  logs, process-tree deadlines, and cleanup of task-owned Docker resources.
- Add a dedicated service integration CI job alongside HTTP/browser checks.

## Statistical follow-up — 2026-10-29

### Fixed
- Match independent t-test confidence intervals to the selected equal-variance
  or Welch model and the two-sided, less, or greater alternative. Report Welch's
  fractional degrees of freedom without changing the result keys or signature.
- Collapse descriptive mean intervals to the mean for zero-variance samples.
- Reject NaN confidence/significance levels consistently in descriptive
  statistics, correlation analysis, and independent t-tests.

## Major-check follow-up — 2026-10-28

### Fixed
- Preserve CSV transform, Parquet append/partition, and Excel transpose
  destinations on callback, writer, sync, or replacement failures through
  sibling-file staging. Existing permission bits are retained; destination
  symlinks are replaced rather than followed. CSV transforms support in-place use.
- Retain NaN-valued Parquet partition rows alongside null groups.
- Reject malformed JWT JSON objects, invalid base64 characters, and boolean or
  non-finite expiration claims with predictable validation errors.
- Correct central first derivatives on uneven grids and accept two-point
  inputs for the gradient method.
- Close multicast sockets on setup errors, isolate logger scope metadata, and
  preserve memory-tracing sessions owned by a caller.
- Wait for resource-sampling completion with an event after reproducing a stall
  inside a timed native thread join on the local Windows runtime.
- Reuse managed SQLite test engines so validation tests close their pooled
  connections; the database suite also passes with warnings treated as errors.

### Performance and validation
- Read Excel transpose sources in read-only mode, close workbooks reliably,
  and avoid padded and transposed list copies. A five-sample paired 2,000×20-cell
  benchmark with identical staged writes reduced median time from 2.49 s to
  1.85 s and traced Python peak allocation from 27.05 MB to 13.06 MB. Every output
  cell matched. These are local measurements, not CI timing thresholds.
- Add repeatable small/large workload measurements for async mapping,
  multiprocessing, file listing, serialization, and SQLite mappings. Memory
  figures exclude native buffers and child-process RSS.
- Add opt-in real Chromium lifecycle tests and an isolated Ubuntu CI job.
- Preserve current audit evidence and the per-family review register in
  `MAINTENANCE_PLAN.md`; remote platform and disposable service gaps remain explicit.

## Unreleased — Python 3.15 migration

### Breaking compatibility
- Require Python 3.15 or newer; update dependency pins, tooling targets, and the
  Windows/Linux/macOS CI matrix. Remove Python 3.10 dependency markers and the
  obsolete Pydantic v1 configuration branch.
- Replace the third-party zstandard dependency with Python's `compression.zstd`.
  Public helper signatures and legacy frame compatibility are retained; Python
  builds must include that standard-library extension. PyYAML 6.0.3 lacks 3.15
  wheels, so CI uses its supported pure-Python build (`PYYAML_FORCE_LIBYAML=0`).

### Fixed
- Reject unsafe ZIP destinations and preflight TAR members before writes.
- Stage async downloads before replacement; reject ignored, mismatched, or
  truncated parallel ranges and await sibling cleanup on failure.
- Accept futures in `gather_with_timeout` and clean up on worker, iterator, timeout,
  and cancellation failures. Reject nested synchronous event-loop execution
  before creating an unawaited coroutine.
- Count checked-out connections toward async-pool capacity and reject duplicate
  registration, duplicate release, and foreign connections.
- Use SQLAlchemy's savepoint handle without committing an outer transaction;
  validate SQL savepoint identifiers, including trailing newlines.
- Bind ID-migration values and quote reflected identifiers; preserve SQLite's
  foreign-key policy after success or rollback and clean up temporary mappings.
- Restrict HTTP redirects to HTTP(S) and remove authorization/cookie headers on
  origin changes without modifying urllib's global opener.
- Fix CLI SSH script text input, validate destinations and finite deadlines,
  disambiguate SCP paths/IPv6, and share fixes with legacy import paths.
- Replace a reproduced scheduler-sensitive retry test with requested-delay checks.
- Bound resource-monitor shutdown, use interruptible sampling waits and
  nonblocking CPU samples, respect disabled monitors, and read GC counters
  without forcing collections. Execution time excludes monitor shutdown.

### Performance and verification
- Store ordered async-map results directly in a list. Repeatable small/large
  benchmarks compare results, time, and traced memory with the prior algorithm.
- Replace quadratic SQLite batch CASE scans with indexed temporary mappings.
  A local three-sample median for 10,000 rows improved from 1.81 s to 0.10 s;
  the 100-row case had about 0.17 ms additional overhead.
- Add family/export/test inventory, dependency-wheel checks, clean-distribution
  smoke checks, and a deadline runner that terminates spawned worker processes.
- Record current evidence and remaining release gates in `MAINTENANCE_PLAN.md`.

All notable changes to this package will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- Replace vulnerable dependency pins with patched releases and update the pytest/asyncio plugin pair together; retain the documented dnspython 2.8 exception for Python 3.10.
- Save browser sessions through a temporary file and atomic replacement so serialization or replacement failures preserve existing sessions.
- Reject bcrypt passwords longer than 72 UTF-8 bytes consistently across bcrypt versions; verification returns false instead of accepting a truncated password.
- Preserve null Parquet partition rows, sanitize Windows filenames, and reject filename collisions before writing partition files.
- Handle empty gateway output and command timeouts; measure download speed with a monotonic high-resolution clock.
- Verify SSH server keys using the user's known-hosts file and close clients when host-key setup fails.
- Restrict HTTP helpers to HTTP(S) initial URLs before filesystem or network operations.
- Propagate test and checker failures through CI and the shell runner; scan the actual package and reject missing or erroneous security reports.
- Recheck async rate-limit capacity after early timer wakeups; reject non-finite limits.
- Preserve existing download destinations on failures and detect truncated transfers.
- Return already-converted environment defaults unchanged when variables are absent.
- Normalize missing-test report paths across operating systems and stabilize JSON diff order.
- Reject non-finite cleanup ages and patterns that traverse outside the selected directory.
- Report free disk space on systems without statvfs and skip inaccessible file metadata.

### Changed
- Make plain pytest invocations collect unit tests only; performance and stress suites require an explicit path.
- Bound default `parallel_map` workers by input size and avoid starting a pool for empty input; explicit process counts are preserved.
- Synchronize runtime and development dependency declarations, retain Python 3.10-compatible NumPy/SciPy pins, and require a build backend supporting the package's license metadata.
- Run pull-request unit checks on Windows and Linux with Python 3.10–3.13, alongside lint, type, and security checks.
- Correct mixed-value result typing and platform-specific attribute access; apply the configured package formatting rules.
- Mark MD5 and SHA-1 file checksums as non-security uses and document narrow scanner exceptions for intentional command execution and multicast/route constants.
- Use cached directory-entry metadata for listings and one stat call per temporary file.
- Make command, Unicode, temporary-file, and Unix-specific tests portable across platforms.
- Add MAINTENANCE_PLAN.md with phased checks and remaining validation blockers.

### Added
- Include the PEP 561 `py.typed` marker in distributions so installed-package type hints are discoverable.
- Order-preserving `unique_by`, `unflatten_dict`, and nested `deep_delete` utilities.
- Lazy `date_range` with ascending and descending date or datetime steps.
- `remove_query_params` with preservation of retained query encoding.
- `atomic_write_file` for text or binary file replacement with failure cleanup.
- `async_map_limited` with ordered results, bounded workers, and cancellation cleanup.
- `validate_env_vars` with converters, defaults, boolean parsing, and grouped errors.

### Tests
- Execute CI checker pipelines and final-status/report-validation scripts with simulated failures to verify that failed tools and missing scans cannot produce passing pull-request checks.
- Validate a 1,000-record Pydantic payload without a wall-clock deadline and test browser-session write failures without assuming a particular path is unwritable.
- Add regression coverage for shell exit codes and quoting, dependency declaration parity, bounded worker counts, gateway failures, UTF-8 bcrypt limits, Parquet partition safety, HTTP schemes, and SSH host-key verification.
- Replace scheduler-dependent periodic/backoff timing assertions with controlled clocks and recorded sleeps; simulate compression permission metadata consistently across platforms.

### Documentation
- Correct installed-package import examples and remove the malformed duplicate README appendix; replace outdated coverage and module-count claims with measured maintenance results.
- Document security behavior corrections and separate unit, performance, and stress-test commands; record validation progress in MAINTENANCE_PLAN.md.

## [0.1.5] - 2026-08-04

### Fixed
- Export hygiene: `get_current_datetime_iso`, playwright `__version__`
- Security: constant-time PBKDF2 verification
- Decorators: thread-safe cache/rate-limit/throttle, non-blocking timeout, RLock for recursive cache
- Datetime: reject bool offsets in `modify_months`/`modify_years`
- Iterable: `safe_cast` string wrapping, `try_convert_to_type` bool strings, `merge_dicts_recursive` deep copy
- ML: bootstrap refit, estimator cloning, overfitting severity, model report validation
- Database: nested transaction savepoint rollback, managed connection exception handling
- SSH: connection cleanup, interpreter allowlist
- HTTP: `http_get` returns error dict on HTTPError (consistent with `http_post`)
- Network: `ping_host` macOS timeout flag
- Compression: polyline precision scaling
- Multiprocessing: preserve `None` results in `parallel_gather_errors`

### Added
- `scikit-learn` as declared dependency for `machine_learning_functions`
- ML unit tests (8 modules), package export validation test, decorator regression tests

## [0.1.4] - 2026-02-17

Initial release with comprehensive Python utilities library containing 200+ reusable functions, classes, and decorators organized into specialized modules.

### Added
- **asyncio_functions** - Asynchronous programming utilities including async_batch, fetch_all, retry with backoff
- **batch_processing_functions** - Batch processing utilities for data pipelines
- **cli_functions** - CLI and system utilities
- **compression_functions** - Data compression algorithms including binary and file compression
- **data_validation** - Data validation utilities with type checking
- **data_visualization_functions** - Data visualization helpers
- **database_functions** - Database utilities and helpers
- **datetime_functions** - Date and time manipulation utilities
- **decorators** - Function enhancement decorators (retry, cache, logging, etc.)
- **dev_utilities** - Development utilities and helpers
- **env_config_functions** - Environment configuration management
- **file_functions** - File system operations and utilities
- **formatting_functions** - Data formatting utilities
- **http_functions** - HTTP client utilities and helpers
- **iterable_functions** - Iterator and list operations
- **json_functions** - JSON manipulation utilities
- **logger_functions** - Logging utilities and helpers
- **mathematical_functions** - Mathematical operations and algorithms
- **multiprocessing_functions** - Parallel processing utilities
- **network_functions** - Network utilities and helpers
- **playwright_functions** - Browser automation utilities
- **print_functions** - Enhanced print utilities
- **regex_functions** - Regular expression utilities
- **scientific_computing_functions** - Scientific computing helpers
- **security_functions** - Security utilities including hashing and encryption
- **serialization_functions** - Data serialization utilities
- **ssh_functions** - SSH connection and operation utilities
- **strings_utility** - String manipulation utilities
- **testing_functions** - Testing utilities and helpers
- **url_functions** - URL manipulation and validation
- **web_scraping_functions** - Web scraping utilities

### Documentation
- Comprehensive NumPy-style docstrings for all functions
- Type hints for all parameters and returns
- Examples and complexity notes in docstrings

### Tests
- 200+ unit tests with >95% coverage
- Comprehensive test scenarios including normal operation, edge cases, and error handling
- Performance tests for critical functions
