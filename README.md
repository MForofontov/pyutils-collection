# 🛠️ Pyutils Collection

[![PyPI version](https://img.shields.io/pypi/v/pyutils-collection.svg)](https://pypi.org/project/pyutils-collection/)
[![Python versions](https://img.shields.io/pypi/pyversions/pyutils-collection.svg)](https://pypi.org/project/pyutils-collection/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Enterprise-grade Python utilities** - 320+ type-safe, tested functions across 23 specialized modules for async operations, data processing, file handling, security, and more.

## 🎯 What is This?

A curated collection of **320+ utility functions** across **23 specialized modules** - designed for **copy-paste reuse** or **pip install**. Each function is self-contained with type hints, docstrings, and handles its own dependencies gracefully.

**Philosophy:**
- 📋 **Copy-paste friendly** - Functions work standalone
- 🔒 **Type-safe** - Complete type hints (Python 3.10+)
- 📝 **Self-documenting** - NumPy-style docstrings with examples
- ✅ **Well-tested** - 88%+ coverage with 5500+ test cases
- 🎨 **Optional deps** - Functions gracefully handle missing libraries

## 📦 Quick Start

```bash
# Install from PyPI
pip install pyutils-collection

# Or clone and copy what you need
git clone https://github.com/MForofontov/pyutils-collection.git
cd pyutils-collection/pyutils_collection

# Or install for development
pip install -e ".[dev]"
```

## 📦 Modules Overview

### Core Modules (23 categories)

| Module | Count | Description |
|--------|-------|-------------|
| 🔄 **asyncio_functions** | 17 | Async/await, connection pools, rate limiting, HTTP |
| 🗜️ **compression_functions** | 27 | GZIP, BZ2, LZMA, Snappy, Zstandard, polyline encoding |
| 🗄️ **database_functions** | 23 | SQLAlchemy utils, transactions, schema inspection |
| 📅 **datetime_functions** | 27 | Timezone conversion, business days, humanization |
| 🎨 **decorators** | 50+ | Caching, retry, timeout, type checking, profiling |
| 📁 **file_functions** | 32 | I/O, hashing, search, temp files, format conversion |
| 🌐 **http_functions** | 9 | REST operations, downloads, query strings |
| 🔄 **iterable_functions** | 55 | Chunking, filtering, grouping, flattening |
| 🧮 **mathematical_functions** | 5 | GCD, LCM, primes, factorial, fibonacci |
| 🔐 **security_functions** | 12 | Encryption (AES/RSA), hashing, JWT tokens |
| 📊 **serialization_functions** | 28 | CSV, Excel, Parquet with streaming & conversion |
| 🔌 **ssh_functions** | 12 | Remote execution, SFTP, key generation |
| 🧪 **testing_functions** | 24 | Fixtures, mocks, assertions, test data generators |
| 🌍 **network_functions** | 28 | IP utilities, DNS, port scanning, connectivity |
| 🌐 **web_scraping_functions** | 18 | HTML/CSS/XPath parsing, table extraction |
| 🎭 **playwright_functions** | 6 | Browser automation, screenshots, session management |
| 🔗 **url_functions** | 8 | Parse, build, validate, normalize URLs |
|  **regex_functions** | 5 | Email/phone/URL validation & extraction |
| ⚙️ **cli_functions** | 16 | System info, process management, environment vars |
| 📝 **logger_functions** | 7 | Logger setup, function logging, rotation |
| 🔄 **multiprocessing_functions** | 19 | Parallel processing, pool management |
| 🔧 **batch_processing_functions** | 2 | Chunked processing, streaming aggregation |
| 🌿 **env_config_functions** | 6 | Config loading (env, YAML, TOML) |
| ✅ **data_validation** | Many | Type/schema validation, Pydantic/Cerberus support |

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
- 88%+ test coverage
- 150+ test files with 1000+ test cases
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
from database_functions import create_connection, atomic_transaction, execute_query
from database_functions.schema_inspection import (
    get_table_info,
    find_duplicate_rows,
    get_foreign_key_dependencies
)

# Create connection
conn = create_connection("postgresql://user:pass@localhost/db")

# Safe transaction
with atomic_transaction(conn) as trans:
    execute_query(trans, "INSERT INTO users VALUES (:name)", {"name": "John"})

# Schema inspection
table_info = get_table_info(conn, "users")
print(f"Columns: {table_info['columns']}")

# Find duplicates
duplicates = find_duplicate_rows(conn, "users", ["email"])

# Get FK dependencies for safe operations
deps = get_foreign_key_dependencies(conn)
print(f"Safe drop order: {deps['ordered_tables']}")
```

### Async Operations
```python
from asyncio_functions import async_batch, fetch_multiple_urls, AsyncConnectionPool

# Batch processing
async def process_items():
    results = await async_batch(
        items=range(100),
        func=process_item,
        batch_size=10
    )
    return results

# HTTP fetching
urls = ["https://api.example.com/1", "https://api.example.com/2"]
responses = await fetch_multiple_urls(urls, max_concurrent=5)

# Connection pooling
async with AsyncConnectionPool("postgresql://...") as pool:
    async with pool.acquire() as conn:
        result = await conn.fetch("SELECT * FROM users")
```

### Decorators
```python
from decorators import cache, retry, timeout, enforce_types

@cache(maxsize=128, ttl=3600)
@retry(max_attempts=3, backoff=2.0)
@timeout(seconds=30)
@enforce_types
def fetch_user_data(user_id: int) -> dict:
    # Function logic here
    return {"id": user_id, "name": "John"}
```

### File Operations
```python
from file_functions import read_file_lines, hash_file, find_files_by_pattern
from file_functions import temp_file_context

# Read file
lines = read_file_lines("data.txt", encoding="utf-8")

# Hash file
file_hash = hash_file("document.pdf", algorithm="sha256")

# Find files
python_files = find_files_by_pattern("/project", "*.py")

# Temp file context
with temp_file_context(suffix=".txt") as temp_path:
    # Use temp file
    temp_path.write_text("temporary data")
```

### Data Serialization
```python
from serialization_functions import (
    stream_csv_chunks,
    csv_to_parquet,
    read_excel_sheet
)

# Stream large CSV
for chunk in stream_csv_chunks("large_file.csv", chunk_size=10000):
    process_chunk(chunk)

# Convert formats
csv_to_parquet("input.csv", "output.parquet", compression="snappy")

# Read Excel
data = read_excel_sheet("report.xlsx", sheet_name="Sales")
```

## 📋 Requirements

- **Python**: 3.10+
- **Philosophy**: Functions handle missing deps gracefully - install only what you need
- **Common deps**: `numpy`, `aiohttp`, `sqlalchemy`, `psutil`, `tqdm`
- **Optional**: `playwright`, `paramiko`, `bcrypt`, `pydantic`, `cerberus`, etc.

## 🧪 Testing

```bash
# Run all 5500+ tests
python -m pytest

# Coverage report (88%+)
python -m pytest --cov=. --cov-report=html
```

## 🤝 Contributing

See [`.github/copilot-instructions.md`](.github/copilot-instructions.md) for detailed guidelines:
- NumPy-style docstrings with examples
- Complete type hints (Python 3.10+ syntax)
- 95%+ test coverage per function
- Self-contained, copy-paste friendly code

## 📄 License

MIT License - see LICENSE file for details.

## 👤 Author

**MForofontov**
- GitHub: [@MForofontov](https://github.com/MForofontov)

## 🔗 Links

- **Repository**: https://github.com/MForofontov/pyutils-collection
- **Issues**: https://github.com/MForofontov/pyutils-collection/issues
- **Documentation**: https://github.com/MForofontov/pyutils-collection#readme

---

⭐ **Star this repository** if you find it useful!
✨ Key Features

- 🎯 **Self-contained functions** - Copy one file, get everything you need
- 🔒 **Type-safe** - Full type hints with modern Python syntax
- 📝 **Well-documented** - NumPy-style docstrings with examples & complexity
- ✅ **Tested** - 88% coverage, 5500+ test cases across 150+ files
- 🔧 **Graceful degradation** - Optional deps handled automatically
- 🗄️ **DB-agnostic** - SQLAlchemy support for PostgreSQL, MySQL, SQLite, Oracle, SQL Server� Usage Examples

```python
# Import from installed package
from pyutils_collection.decorators import cache, retry, timeout

# Or copy decorators locally and use
from decorators import cache, retry, timeout

@cache(maxsize=128, ttl=3600)
@retry(max_attempts=3, backoff=2.0)
@timeout(seconds=30)
def fetch_user_data(user_id: int) -> dict:
    return {"id": user_id, "name": "John"}

from pyutils_collection.asyncio_functions import async_batch, fetch_multiple_urls

urls = ["https://api.example.com/1", "https://api.example.com/2"]
responses = await fetch_multiple_urls(urls, max_concurrent=5)

from pyutils_collection.database_functions import create_connection, atomic_transaction

conn = create_connection("postgresql://user:pass@localhost/db")
with atomic_transaction(conn) as trans:
    execute_query(trans, "INSERT INTO users VALUES (:name)", {"name": "John"})

from pyutils_collection.serialization_functions import stream_csv_chunks, csv_to_parquet

for chunk in stream_csv_chunks("large.csv", chunk_size=10000):
    process_chunk(chunk)
csv_to_parquet("input.csv", "output.parquet", compression="snappy