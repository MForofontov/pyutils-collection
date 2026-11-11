# 🛠️ Pyutils Collection

[![PyPI version](https://img.shields.io/pypi/v/pyutils-collection.svg)](https://pypi.org/project/pyutils-collection/)
[![Python versions](https://img.shields.io/pypi/pyversions/pyutils-collection.svg)](https://pypi.org/project/pyutils-collection/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Python utilities** - 500+ functions across 31 specialized modules for async operations, data processing, file handling, security, and more.

## 🎯 What is This?

A collection of **500+ utility functions** across **31 specialized modules**, designed for **copy-paste reuse** or **pip install**. Functions include type hints, docstrings, and focused tests.

**Philosophy:**
- 📋 **Copy-paste friendly** - Copy utilities with their imports and supporting helpers
- 🔒 **Type-safe** - Complete type hints (Python 3.15+)
- 📝 **Self-documenting** - NumPy-style docstrings with examples
- ✅ **Tested** - 5,500+ unit tests; measured coverage and skips are recorded in the maintenance plan
- 🎨 **Optional browser support** - Install the Playwright extra for browser utilities

## 📦 Quick Start

Version **0.2.2** requires **Python 3.15+** with `compression.zstd`. Release
0.1.5 declared Python 3.10+ support. See the
[changelog](CHANGELOG.md) for release history. The PyPI badges show the published
package; development checkouts may contain changes listed under `Unreleased`.


```bash
# Install from PyPI
python -m pip install pyutils-collection==0.2.2

# Or clone and copy what you need
git clone https://github.com/MForofontov/pyutils-collection.git
cd pyutils-collection
# Copy utilities from the pyutils_collection/ directory as needed.

# Or install the checked-out version for development
python -m pip install -e ".[dev,playwright]"
```

## 📦 Modules Overview

### Companion utilities

```python
from datetime import date

from pyutils_collection.iterable_functions import unique_by, unflatten_dict, deep_delete
from pyutils_collection.datetime_functions import date_range
from pyutils_collection.url_functions import remove_query_params
from pyutils_collection.file_functions import atomic_write_file
from pyutils_collection.asyncio_functions import async_map_limited
from pyutils_collection.env_config_functions import validate_env_vars

unique_by(["Ada", "ADA", "Grace"], str.lower)  # ["Ada", "Grace"]
data = unflatten_dict({"user_name": "Ada", "user_age": 36})
deep_delete(data, "user.age")  # data is now {"user": {"name": "Ada"}}
list(date_range(date(2026, 1, 1), date(2026, 1, 4)))  # Stop is exclusive
remove_query_params("/search?q=python&utm_source=mail", ["utm_source"])
atomic_write_file("settings.json", '{"enabled": true}')
config = validate_env_vars(
    {"PORT": int, "DEBUG": bool},
    defaults={"PORT": 8080, "DEBUG": False},
)

async def double(value: int) -> int:
    return value * 2

# In an async function: await async_map_limited(double, range(100), limit=5)
```

`unflatten_dict` rejects conflicting paths and uses the same separator as
`flatten_dict`. `atomic_write_file` requires an existing parent directory and
uses temporary-file permissions. Environment defaults are already-converted
values; malformed present values raise an error instead of using a default.

### Selected utility families

Counts below are public names exported by each family's top-level module,
including classes and submodules, excluding `__version__`. Some families also
provide utilities through nested modules. Playwright exports require its extra.

| Module | Exports | Description |
|--------|-------|-------------|
| 🔄 **asyncio_functions** | 20 | Async/await, connection pools, rate limiting, HTTP |
| 🗜️ **compression_functions** | 27 | GZIP, BZ2, LZMA, Snappy, Zstandard, polyline encoding |
| 🗄️ **database_functions** | 14 | SQLAlchemy utils, transactions, schema inspection |
| 📅 **datetime_functions** | 27 | Timezone conversion, business days, humanization |
| 🎨 **decorators** | 31 | Caching, retry, timeout, type checking, profiling |
| 📁 **file_functions** | 33 | I/O, hashing, search, temp files, format conversion |
| 🌐 **http_functions** | 9 | REST operations, downloads, query strings |
| 🔄 **iterable_functions** | 58 | Chunking, filtering, grouping, flattening |
| 🧮 **mathematical_functions** | 5 | Real-valued powers and random sampling |
| 🔐 **security_functions** | 12 | Encryption (AES/RSA), hashing, JWT tokens |
| 📊 **serialization_functions** | 28 | CSV, Excel, Parquet with streaming & conversion |
| 🔌 **ssh_functions** | 6 | SSH commands and local/remote implementation modules |
| 🧪 **testing_functions** | 29 | Fixtures, mocks, assertions, test data generators |
| 🌍 **network_functions** | 19 | IP utilities, DNS, port scanning, connectivity |
| 🌐 **web_scraping_functions** | 18 | HTML/CSS/XPath parsing, table extraction |
| 🎭 **playwright_functions** | 6 | Browser automation, screenshots, session management |
| 🔗 **url_functions** | 7 | Parse, build, validate, normalize URLs |
|  **regex_functions** | 5 | Email/phone/URL validation & extraction |
| ⚙️ **cli_functions** | 15 | System info, process management, environment vars |
| 📝 **logger_functions** | 7 | Logger setup, function logging, rotation |
| 🔄 **multiprocessing_functions** | 13 | Parallel processing, pool management |
| 🔧 **batch_processing_functions** | 3 | Chunked processing, streaming aggregation |
| 🌿 **env_config_functions** | 7 | Environment validation and config loading (env, YAML, TOML, INI) |
| ✅ **data_validation** | 7 | Type/schema validation, Pydantic/Cerberus support |

## 🔑 Key Features

### Database-Agnostic Design
All database functions use **SQLAlchemy** for maximum portability:
- ✅ PostgreSQL
- ✅ MySQL / MariaDB
- ✅ SQLite
- ✅ Oracle
- ✅ SQL Server

### Type Safety
- Complete type hints using modern Python syntax (`list[str]`, `dict[str, Any]`)
- Runtime type checking with decorators
- mypy-compliant codebase

### Comprehensive Testing
- Package coverage reports include paths not exercised on the current platform
- 5,500+ unit tests across the utility families
- Pytest-based testing framework
- Comprehensive edge case coverage

### Documentation
- NumPy-style docstrings for all functions
- Examples in docstrings
- Time/space complexity notes for algorithms
- Comprehensive README with usage examples

## 📚 Usage Examples

### Database Operations
```python
from sqlalchemy import create_engine, text
from pyutils_collection.database_functions import atomic_transaction
from pyutils_collection.database_functions.schema_inspection import (
    get_table_info, find_duplicate_rows,
)

engine = create_engine("sqlite:///:memory:")
try:
    with engine.connect() as conn:
        with atomic_transaction(conn):
            conn.execute(text("CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT)"))
            conn.execute(
                text("INSERT INTO users (email) VALUES (:email)"),
                [{"email": "ada@example.com"}, {"email": "ada@example.com"}],
            )
        print(get_table_info(conn, "users"))
        print(find_duplicate_rows(conn, "users", ["email"]))
finally:
    engine.dispose()
```

### Async Operations
```python
import asyncio
from pyutils_collection.asyncio_functions import async_batch, async_map_limited

async def double_batch(items: list[int]) -> list[int]:
    return [item * 2 for item in items]

async def double(item: int) -> int:
    return item * 2

async def main() -> None:
    print(await async_batch(double_batch, list(range(5)), batch_size=2))
    print(await async_map_limited(double, range(5), limit=2))

asyncio.run(main())
```

### Decorators
```python
from pyutils_collection.decorators import cache, retry, timeout, enforce_types

@cache
@retry(max_retries=3, delay=0.01)
@timeout(seconds=30)
@enforce_types()
def fetch_user_data(user_id: int) -> dict:
    # Function logic here
    return {"id": user_id, "name": "John"}
```

`cache` and `cache_with_expiration` require hashable arguments and treat keyword
insertion order as part of the call. Wrapped exceptions propagate unchanged and
are not cached. Expiring caches use monotonic elapsed seconds, so changing the
system clock does not change cache lifetimes; a zero lifetime disables reuse.

### Numerical Results and Diagnostics

`calculate_moving_statistics` uses exactly the requested width. Even widths place
the extra sample on the left of the current sample; edges use partial windows.
Standard deviation uses the population definition. `power` returns real numbers
and raises `ValueError` for negative bases with fractional exponents, overflow,
and zero raised to negative exponents.

`smooth_timeseries` also places the extra sample on the left for even moving
averages, preserving original boundary values where a complete window cannot
fit. Moving-average windows must fit the series; exponential smoothing allows
larger windows because its window controls the smoothing factor.

`ContextualLogger.exception()` includes the active exception and traceback by
default. Pass `exc_info=False` to suppress them, or supply saved exception
information using `exc_info`. Context and additional metadata remain attached.

### File Operations
```python
from pathlib import Path
from tempfile import TemporaryDirectory
from pyutils_collection.file_functions import (
    atomic_write_file, read_lines, calculate_sha256_hash, find_files_by_pattern,
)

with TemporaryDirectory() as directory:
    path = Path(directory) / "data.txt"
    atomic_write_file(str(path), "first line\nsecond line\n")
    print(read_lines(str(path)))
    print(calculate_sha256_hash(str(path)))
    print(find_files_by_pattern(directory, "*.txt"))
```

### Data Serialization
```python
from pathlib import Path
from tempfile import TemporaryDirectory
from pyutils_collection.serialization_functions import stream_csv_chunks, csv_to_parquet

with TemporaryDirectory() as directory:
    source = Path(directory) / "scores.csv"
    destination = Path(directory) / "scores.parquet"
    source.write_text("name,score\nAda,10\nGrace,12\n", encoding="utf-8")
    for chunk in stream_csv_chunks(str(source), chunk_size=1):
        print(chunk)
    print(csv_to_parquet(str(source), str(destination), compression="snappy"))
```

## 📋 Requirements

- **Python**: 3.15+
- Use a Python build that includes `compression.zstd`; official CPython builds
  provide it. Zstandard helpers now use this standard-library implementation,
  preserving support for previously compressed data.
- A package installation installs the dependencies declared in `pyproject.toml`, including scientific, database, SSH, and security libraries.
- Browser automation is optional: install with `pip install '.[playwright]'` from a checkout or `pip install 'pyutils-collection[playwright]'` from PyPI.

### Maintenance behavior changes

Paramiko SSH helpers verify server keys against `~/.ssh/known_hosts` and reject unknown or changed keys. CLI SSH helpers use the system client's host-key policy and reject option-like destinations. HTTP helpers accept only HTTP(S) URLs and redirects, stripping credentials when a redirect changes origin. Bcrypt hashing rejects passwords over 72 UTF-8 bytes, and verification returns `False` for those passwords. Parquet partitioning preserves null groups and raises `ValueError` before writing files when partition values produce colliding filenames.

Security dependency updates require modern SSH algorithms; Paramiko 5 no longer supports SHA-1 signatures/key exchange or DSA keys. Python 3.15 is now the minimum supported version. Installations on older Python versions are intentionally rejected. See the maintenance plan for migration evidence and remaining release checks.

Public function parameters remain unchanged. See [CHANGELOG.md](CHANGELOG.md) for the full list of corrections.

Async downloads preserve existing destinations on failure. Async-pool capacity
includes checked-out connections; duplicate registration and foreign or duplicate
release raise `ValueError`. ZIP extraction rejects unsafe member paths and
existing symlink escapes; TAR extraction preflights members before writing.

`savepoint_context` releases its owned savepoint after rollback or ignored body
errors without committing the caller's outer transaction. Ignore mode retains
partial body work, but setup/release failures propagate. Cancellation and process
interruptions always attempt rollback and release before propagating.

## 🧪 Testing

```bash
# Install development dependencies
python -m pip install -e '.[dev,playwright]'

# Unit tests and package coverage
python scripts/run_with_deadline.py --seconds 900 --log .major-check/unit.log -- python -m pytest pytest/unit --cov=pyutils_collection --cov-report=html --junitxml=.major-check/unit.xml

# Separate performance checks and optional stress tests
python -m pytest pytest/performance -m 'performance and not slow'
python -m pytest pytest/performance -m 'performance and slow'

# Isolated local HTTP integration checks
python -m pytest pytest/integration/test_http_loopback.py -q

# Real browser checks (install Chromium first, then set PYUTILS_BROWSER_TESTS=1)
python -m playwright install chromium --only-shell
python -m pytest pytest/integration/test_browser_lifecycle.py -q

# Disposable PostgreSQL, MySQL, and SSH/SFTP checks (requires Docker Compose)
python scripts/run_service_integration.py --report-dir .major-check/services

# Audit inventory, Python 3.15 wheels, and repeatable async-map benchmarks
python scripts/audit_inventory.py .major-check/unit.xml
python scripts/check_python315_wheels.py
python scripts/benchmark_async_map.py
python scripts/benchmark_sqlite_migration.py

# Static checks
python -m ruff check pyutils_collection scripts
python -m ruff format --check pyutils_collection scripts
python -m mypy pyutils_collection --install-types --non-interactive
```

See [MAINTENANCE_PLAN.md](MAINTENANCE_PLAN.md) for verified results, platform coverage, and outstanding audit work. Skipped tests and unavailable integration checks are listed separately from passes.

## 🤝 Contributing

Read [CONTRIBUTING.md](CONTRIBUTING.md) for setup, validation, and the PR
documentation-impact check. [AGENTS.md](AGENTS.md) holds shared AI guidance and
links to reusable maintenance and documentation skills. Update documentation and
release notes alongside changes, including internal maintenance, and update the
package version once per completed changeset under the policy in `AGENTS.md`.
CI exception support does not waive that repository policy. Public utilities use complete type hints
and NumPy-style docstrings with examples. Test meaningful behavior and failure
paths; current measured coverage belongs in the maintenance record.

## 📄 License

MIT © 2026 [Mykyta Forofontov](https://github.com/MForofontov)

See [LICENSE](LICENSE) for the full license text.

## 👤 Author

**Mykyta Forofontov**
- GitHub: [@MForofontov](https://github.com/MForofontov)

## 🔗 Links

- **Repository**: https://github.com/MForofontov/pyutils-collection
- **Issues**: https://github.com/MForofontov/pyutils-collection/issues
- **Documentation**: https://github.com/MForofontov/pyutils-collection#readme

---

⭐ **Star this repository** if you find it useful!
