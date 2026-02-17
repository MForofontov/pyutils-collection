# GitHub Copilot Instructions for Python Utilities Repository

## ⚠️ CRITICAL: CHANGELOG Workflow (MUST FOLLOW)

**ALL changes must be documented in `CHANGELOG.md` immediately after implementation.**

### Development Workflow

1. **Make changes** (add/modify/fix functions)
2. **IMMEDIATELY update CHANGELOG.md** - Add entry to `[Unreleased]` section
3. **When ready to publish** - Move `[Unreleased]` → `[X.Y.Z] - YYYY-MM-DD`

### Update CHANGELOG After Every Change

Add entries to the `[Unreleased]` section using these categories (only include categories with content):

**After creating new functions**:
```markdown
### Added
- **module_name.function_name** - Brief description (include citation if algorithmic)
```

**After modifying existing functions**:
```markdown
### Enhanced
- **module_name.function_name** - What was improved (e.g., "Added retry logic with exponential backoff")
```

**After fixing bugs**:
```markdown
### Fixed
- **module_name.function_name** - What was fixed (e.g., "Fixed race condition in async processing")
```

**After removing functions**:
```markdown
### Removed
- **module_name.function_name** - Reason for removal
```

**After refactoring**:
```markdown
### Changed
- **module_name.function_name** - What changed and why
```

**After adding/updating tests**:
```markdown
### Tests
- Added 15 unit tests for asyncio_functions.async_batch covering edge cases
```

**After updating documentation**:
```markdown
### Documentation
- Updated README with new examples for database_functions
```

### CHANGELOG Structure

```markdown
# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- **new_module.new_function** - Description

### Fixed
- **existing_module.function** - Bug fix description

## [1.0.2] - 2026-02-17
...previous release...
```

**Only include section headers that have content. Remove empty sections.**

### Publishing a New Version

When releasing:

1. **Update `_version.py`**:
   ```python
   __version__ = "1.1.0"  # Follow SemVer: MAJOR.MINOR.PATCH
   ```

2. **Update CHANGELOG.md**:
   - Change `[Unreleased]` → `[1.1.0] - 2026-02-17`
   - Add new empty `[Unreleased]` section at top
   - Remove empty section headers

3. **Commit and tag**:
   ```bash
   git commit -m "Release v1.1.0"
   git tag -a v1.1.0 -m "Release version 1.1.0"
   ```

### Semantic Versioning

- **MAJOR** (X.0.0): Breaking changes, API incompatibility
- **MINOR** (0.X.0): New features, backward compatible
- **PATCH** (0.0.X): Bug fixes, backward compatible

**Remember**: Update CHANGELOG.md in `[Unreleased]` IMMEDIATELY after implementing changes!

---

## Project Overview

This is a comprehensive Python utilities library containing 200+ reusable functions, classes, and decorators organized into 14 specialized modules. The project emphasizes type safety, comprehensive testing, maintainability, and follows Python best practices for enterprise-grade utility libraries.

## Architecture & Structure

### Core Principles
- **Single Responsibility**: Each function/class should have one clear purpose
- **Type Safety**: Complete type hints for all functions and methods
- **Pure Functions**: Prefer pure functions when possible (no side effects)
- **Comprehensive Testing**: Every function must have unit tests with >95% coverage
- **Documentation**: NumPy-style docstrings with examples and complexity notes
- **Error Handling**: Explicit validation with descriptive error messages
- **Use Battle-Tested Packages**: Leverage existing mature libraries as building blocks, don't reimplement their core functionality
- **Add Value, Don't Wrap**: Functions should add meaningful logic (validation, workflows, convenience) beyond simple one-line calls to existing packages

### Directory Structure
```
python-utils/
├── .github/                        # GitHub-specific files and workflows
├── asyncio_functions/              # Asynchronous programming utilities
│   ├── async_batch.py
│   ├── async_retry_with_backoff.py
│   ├── fetch_all.py
│   └── ...
├── compression_functions/          # Data compression algorithms
│   ├── binary_compression/         # Binary data compression
│   ├── files_compression/          # File compression utilities
│   └── polyline_encoding_*.py
├── data_types/                     # Custom data structure implementations
│   ├── binary_tree.py
│   ├── hash_table.py
│   ├── priority_queue.py
│   └── ...
├── datetime_functions/             # Date and time utilities
├── decorators/                     # Function enhancement decorators
├── env_config_functions/           # Environment configuration
├── file_functions/                 # File system operations
├── http_functions/                 # HTTP client utilities
├── iterable_functions/             # Iterator and list operations
├── json_functions/                 # JSON manipulation
├── cli_functions/                  # CLI and system utilities
├── logger_functions/               # Logging utilities
├── mathematical_functions/         # Mathematical operations
├── multiprocessing_functions/      # Parallel processing
├── strings_utility/                # String manipulation
├── pytest/                         # Comprehensive test suites
│   └── unit/                       # Unit tests mirroring src structure
└── __init__.py                     # Main export file
```

## Development Guidelines

### Function Development Standards

#### 1. Function Structure Template
Every function should follow this template:
```python
from typing import TypeVar, Any
from collections.abc import Callable, Iterable

T = TypeVar("T")
R = TypeVar("R")

def function_name(
    param1: int,
    param2: str,
    optional_param: bool = False,
) -> ReturnType:
    """
    Brief description of what the function does.

    Parameters
    ----------
    param1 : int
        Description of param1.
    param2 : str
        Description of param2.
    optional_param : bool, optional
        Description of optional parameter (by default False).

    Returns
    -------
    ReturnType
        Description of return value.

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If parameters have invalid values.

    Examples
    --------
    >>> function_name(42, "hello")
    ExpectedOutput
    >>> function_name(0, "world", True)
    AnotherExpectedOutput

    Notes
    -----
    Any special considerations or implementation details.

    Complexity
    ----------
    Time: O(n), Space: O(1)
    """
    # Input validation
    if not isinstance(param1, int):
        raise TypeError(f"param1 must be an integer, got {type(param1).__name__}")
    if not isinstance(param2, str):
        raise TypeError(f"param2 must be a string, got {type(param2).__name__}")
    if not isinstance(optional_param, bool):
        raise TypeError(f"optional_param must be a boolean, got {type(optional_param).__name__}")
    
    # Additional validation
    if param1 < 0:
        raise ValueError("param1 must be non-negative")
    
    # Function logic here
    result = perform_operation(param1, param2, optional_param)
    
    return result


__all__ = ['function_name']
```

#### 2. Input Validation Standards
- **Type Checking**: Validate all input types with `isinstance()`
- **Value Validation**: Check ranges, constraints, and business logic
- **Descriptive Errors**: Include parameter name and expected/actual types
- **Consistent Messages**: Use format: `"param_name must be <expected>, got <actual>"`

#### 3. Error Handling Patterns
```python
# Type validation
if not isinstance(param, expected_type):
    raise TypeError(f"param must be {expected_type.__name__}, got {type(param).__name__}")

# Value validation  
if param < 0:
    raise ValueError(f"param must be non-negative, got {param}")

# Collection validation
if not isinstance(items, (list, tuple)):
    raise TypeError(f"items must be a list or tuple, got {type(items).__name__}")

if len(items) == 0:
    raise ValueError("items cannot be empty")
```

### Class Development Standards

#### 1. Class Structure Template
```python
from typing import Generic, TypeVar, Any
from collections.abc import Iterator

T = TypeVar("T")

class ClassName(Generic[T]):
    """
    Brief description of the class.

    Attributes
    ----------
    attribute_name : type
        Description of the attribute.

    Parameters
    ----------
    param1 : type
        Description of constructor parameter.

    Examples
    --------
    >>> obj = ClassName(param1_value)
    >>> obj.method()
    expected_result
    """

    def __init__(self, param1: Any) -> None:
        """Initialize the class with validation."""
        if not isinstance(param1, expected_type):
            raise TypeError(f"param1 must be {expected_type.__name__}")
        
        self._attribute = param1

    def __str__(self) -> str:
        """Return string representation."""
        return f"ClassName(attribute={self._attribute})"

    def __repr__(self) -> str:
        """Return detailed string representation."""
        return f"ClassName(attribute={self._attribute!r})"

    def __eq__(self, other: object) -> bool:
        """Check equality with another instance."""
        if not isinstance(other, ClassName):
            return False
        return self._attribute == other._attribute

    def method_name(self, param: T) -> R:
        """
        Method description.

        Parameters
        ----------
        param : T
            Parameter description.

        Returns
        -------
        R
            Return value description.
        """
        # Method implementation
        pass
```

### Decorator Development Standards

#### 1. Decorator Pattern Template
```python
import logging
from functools import wraps
from typing import Callable, TypeVar, ParamSpec, Any

P = ParamSpec("P")
R = TypeVar("R")

def decorator_name(
    param: str,
    logger: logging.Logger | None = None,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Decorator description.
    
    Parameters
    ----------
    param : str
        Description of parameter.
    logger : logging.Logger | None, optional
        Logger instance for debugging (by default None).

    Returns
    -------
    Callable[[Callable[P, R]], Callable[P, R]]
        Decorated function.

    Raises
    ------
    TypeError
        If parameters are of wrong type.

    Examples
    --------
    >>> @decorator_name("config")
    ... def my_function(x: int) -> int:
    ...     return x * 2
    >>> my_function(5)
    10
    """
    # Input validation
    if not isinstance(param, str):
        raise TypeError(f"param must be a string, got {type(param).__name__}")
    if logger is not None and not isinstance(logger, logging.Logger):
        raise TypeError("logger must be an instance of logging.Logger or None")

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            try:
                # Pre-processing logic
                if logger:
                    logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
                
                result = func(*args, **kwargs)
                
                # Post-processing logic
                if logger:
                    logger.debug(f"{func.__name__} returned {result}")
                
                return result
            except Exception as e:
                if logger:
                    logger.error(f"Error in {func.__name__}: {e}", exc_info=True)
                raise
        return wrapper
    return decorator

__all__ = ['decorator_name']
```

### Async Function Standards

#### 1. Async Function Template
```python
import asyncio
from typing import TypeVar, Any, Coroutine
from collections.abc import Awaitable

T = TypeVar("T")

async def async_function_name(
    param: Any,
    timeout: float = 30.0,
) -> T:
    """
    Async function description.
    
    Parameters
    ----------
    param : Any
        Parameter description.
    timeout : float, optional
        Timeout in seconds (by default 30.0).

    Returns
    -------
    T
        Return value description.

    Raises
    ------
    TimeoutError
        If operation times out.
    TypeError
        If parameters are of wrong type.

    Examples
    --------
    >>> import asyncio
    >>> result = asyncio.run(async_function_name("test"))
    >>> result
    expected_output
    """
    # Input validation
    if not isinstance(timeout, (int, float)):
        raise TypeError(f"timeout must be a number, got {type(timeout).__name__}")
    if timeout <= 0:
        raise ValueError(f"timeout must be positive, got {timeout}")

    try:
        async with asyncio.timeout(timeout):
            # Async logic here
            result = await some_async_operation(param)
            return result
    except asyncio.TimeoutError:
        raise TimeoutError(f"Operation timed out after {timeout} seconds")

__all__ = ['async_function_name']
```

### Testing Standards

#### Test File Structure
```python
import pytest
from unittest.mock import Mock, patch
from module_name.function_name import function_name


def test_function_name_normal_operation() -> None:
    """
    Test case 1: Normal operation with valid inputs.
    """
    # Arrange
    input_data = valid_input
    expected = expected_output
    
    # Act
    result = function_name(input_data)
    
    # Assert
    assert result == expected


def test_function_name_typical_use_case() -> None:
    """
    Test case 2: Another typical usage scenario.
    """
    # Arrange
    input_data = another_valid_input
    expected = another_expected_output
    
    # Act
    result = function_name(input_data)
    
    # Assert
    assert result == expected


def test_function_name_empty_input() -> None:
    """
    Test case 3: Edge case with empty input.
    """
    # Arrange
    input_data = empty_input
    expected = expected_edge_result
    
    # Act
    result = function_name(input_data)
    
    # Assert
    assert result == expected


def test_function_name_boundary_conditions() -> None:
    """
    Test case 4: Boundary conditions testing.
    """
    # Test minimum boundary
    result_min = function_name(0)
    assert result_min == expected_min_result
    
    # Test maximum boundary
    result_max = function_name(MAX_VALUE)
    assert result_max == expected_max_result


def test_function_name_performance_large_input() -> None:
    """
    Test case 5: Performance with large input data.
    """
    # Arrange
    large_input = generate_large_test_data(10000)
    
    # Act
    import time
    start_time = time.time()
    result = function_name(large_input)
    elapsed_time = time.time() - start_time
    
    # Assert
    assert result is not None
    assert elapsed_time < 1.0  # Should complete within 1 second

def test_function_name_invalid_type_raises_error() -> None:
    """
    Test case 6: TypeError for invalid input type.
    """
    # Arrange
    invalid_input = "wrong_type"
    expected_message = "param must be int, got str"
    
    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        function_name(invalid_input)


def test_function_name_negative_value_raises_error() -> None:
    """
    Test case 7: ValueError for invalid input value.
    """
    # Arrange
    invalid_input = -1
    expected_message = "param must be non-negative"
    
    # Act & Assert
    with pytest.raises(ValueError, match=expected_message):
        function_name(invalid_input)


@pytest.mark.asyncio
async def test_async_function_normal_operation() -> None:
    """
    Test case 1: Normal async operation.
    """
    # Arrange
    input_data = valid_input
    expected = expected_output
    
    # Act
    result = await async_function_name(input_data)
    
    # Assert
    assert result == expected
```

#### Testing Requirements
- **Minimum 6 test cases** per function covering (in this order):
  1. **Normal/typical usage cases** (2-4 tests): Standard usage scenarios with valid inputs
  2. **Edge cases** (2-3 tests): Empty inputs, boundary values, large inputs, performance considerations
  3. **Error cases** (2-4 tests): Type validation errors, value validation errors, invalid states

- **Naming Convention**: `test_function_name_descriptive_scenario`
  - ✅ GOOD: `test_parse_json_empty_string`, `test_calculate_sum_negative_numbers`, `test_validate_email_invalid_format`
  - ❌ BAD: `test_function_case_1`, `test_parse_json_case_3_edge_case`
  - **Use descriptive names that clearly indicate what scenario is being tested**
  - **Do NOT include case_1, case_2, etc. in function names - be specific and self-documenting**
- **Docstrings**: Every test function must have a descriptive docstring that includes "Test case N:" for tracking
- **Arrange-Act-Assert**: Structure tests clearly with these sections
- **Error Testing**: Use `pytest.raises()` with specific error message matching

### Module Organization Standards

#### 1. __init__.py Structure
```python
"""
Module name: Brief description of module purpose.

This module provides utilities for [specific domain].
"""

from .function1 import function1
from .function2 import function2
from .subfolder.function3 import function3

__all__ = [
    'function1',
    'function2', 
    'function3',
]

# Version - import from central _version.py
from ._version import __version__  # For top-level modules
# OR
from .._version import __version__  # For nested modules
# OR
from ..._version import __version__  # For deeply nested modules
```

#### 2. Import Standards
```python
# Standard library imports (alphabetical)
import asyncio
import logging
import os
from pathlib import Path

# Third-party imports (alphabetical)
import numpy as np
import psutil
from tqdm import tqdm

# Local imports (relative)
from .utils import helper_function
from ..other_module import other_function

# Type-only imports
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from some_module import SomeClass
```

### Code Style & Formatting

#### Type Hints Standards
- **Complete Coverage**: All functions must have type hints for parameters and returns
- **Modern Syntax**: Use `list[str]` instead of `List[str]` (Python 3.9+)
- **Union Types**: Use `int | str` instead of `Union[int, str]` (Python 3.10+)
- **Generic Types**: Use `TypeVar` and `Generic` for reusable generic code
- **Collections**: Import from `collections.abc` for abstract base classes

#### Documentation Standards
- **NumPy Style**: Use NumPy-style docstrings consistently
- **Sections**: Include Parameters, Returns, Raises, Examples, Notes, Complexity
- **Examples**: Provide working code examples in docstrings
- **Complexity**: Document time/space complexity for non-trivial algorithms

### Export Strategy

#### Main __init__.py Management
All functions should be accessible from the root level:
```python
# Import from modules
from .asyncio_functions import *
from .compression_functions import *
from .data_types import *
# ... other modules

# Explicit exports to avoid conflicts
__all__ = [
    # Asyncio functions
    'async_batch',
    'fetch_all',
    # Compression functions  
    'decompress_number',
    # ... continue for all functions
]
```

### Performance Considerations

#### Algorithmic Efficiency
- Document time/space complexity in docstrings
- Prefer O(1) or O(n) algorithms when possible
- Use generators for memory-efficient processing
- Implement chunking for large datasets

#### Memory Management
- Use context managers for resource handling
- Implement proper cleanup in classes
- Consider memory usage in caching decorators
- Use `__slots__` for memory-critical classes

#### Concurrency Patterns
```python
# Async processing
async def process_items_concurrently(items: list[T]) -> list[R]:
    """Process items concurrently with controlled parallelism."""
    semaphore = asyncio.Semaphore(10)  # Limit concurrent operations
    
    async def process_with_semaphore(item: T) -> R:
        async with semaphore:
            return await process_item(item)
    
    tasks = [process_with_semaphore(item) for item in items]
    return await asyncio.gather(*tasks)

# Multiprocessing with proper resource management
def process_parallel(items: list[T], workers: int = 4) -> list[R]:
    """Process items in parallel using multiprocessing."""
    with multiprocessing.Pool(workers) as pool:
        results = pool.map(process_item, items)
    return results
```

### Best Practices for GitHub Copilot

#### When Adding New Functions
1. **Analyze the category**: Determine the correct module based on function purpose
2. **Follow naming conventions**: Use descriptive, snake_case names
3. **Check for duplicates**: Search existing codebase for similar functionality
4. **Consider dependencies**: Minimize external dependencies where possible
5. **Add comprehensive tests**: Create test file in `pytest/unit/` directory
6. **Update exports**: Add function to module's `__all__` list in `__init__.py`
7. **Validate types**: Ensure complete type hint coverage

#### When Adding New Modules/Categories
1. **Create new directory** following naming convention (`category_functions/`)
2. **Create corresponding test directory** in `pytest/unit/category_functions/`
3. **Update documentation**: Include new module in this guide
4. **Consider integration**: Ensure new category doesn't overlap with existing ones
5. **Update main exports**: Add imports to root `__init__.py`

#### When Modifying Existing Functions
1. **Maintain backward compatibility** unless it's a breaking change
2. **Update tests** to reflect changes and add new test cases
3. **Update docstrings** if behavior or parameters change
4. **Run full test suite** to ensure no regressions
5. **Consider performance impact** of modifications
6. **Update type hints** if signatures change

#### Code Review Considerations
- **Type Safety**: Ensure complete type hints for all parameters and returns
- **Test Coverage**: Verify comprehensive test scenarios including edge cases  
- **Documentation**: Check NumPy-style docstring completeness and accuracy
- **Performance**: Consider algorithmic efficiency and memory usage
- **Consistency**: Ensure code follows established project patterns
- **Error Handling**: Validate proper exception types and descriptive messages
- **Dependencies**: Minimize and justify external dependencies

### Common Patterns in the Codebase

#### Resource Management Pattern
```python
from contextlib import contextmanager
from typing import Generator

@contextmanager
def managed_resource(resource_path: str) -> Generator[Resource, None, None]:
    """Context manager for proper resource handling."""
    resource = None
    try:
        resource = open_resource(resource_path)
        yield resource
    except Exception as e:
        logger.error(f"Error managing resource {resource_path}: {e}")
        raise
    finally:
        if resource:
            resource.close()
```

#### Configuration Pattern
```python
from dataclasses import dataclass
from typing import Any

@dataclass
class FunctionConfig:
    """Configuration for function behavior."""
    timeout: float = 30.0
    retries: int = 3
    batch_size: int = 100
    
    def __post_init__(self) -> None:
        """Validate configuration after initialization."""
        if self.timeout <= 0:
            raise ValueError("timeout must be positive")
        if self.retries < 0:
            raise ValueError("retries must be non-negative")

def configurable_function(
    data: Any,
    config: FunctionConfig | None = None,
) -> Any:
    """Function that accepts configuration."""
    if config is None:
        config = FunctionConfig()
    
    # Use config.timeout, config.retries, etc.
    return process_with_config(data, config)
```

#### Validation Helper Pattern
```python
def validate_numeric_input(
    value: Any, 
    name: str, 
    min_value: float | None = None,
    max_value: float | None = None,
) -> None:
    """Helper function for numeric input validation."""
    if not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a number, got {type(value).__name__}")
    
    if isinstance(value, float) and (value != value):  # NaN check
        raise ValueError(f"{name} cannot be NaN")
    
    if min_value is not None and value < min_value:
        raise ValueError(f"{name} must be >= {min_value}, got {value}")
    
    if max_value is not None and value > max_value:
        raise ValueError(f"{name} must be <= {max_value}, got {value}")
```

### Logging Best Practices

#### When to Use Logger Parameters

**✅ DO use logger parameters in:**

1. **Decorators** - Infrastructure code that wraps user functions
   - Users need flexibility to override logging per decorator instance
   - Different contexts require different logging behavior
   - Testing requires injectable mock loggers
   - Example: `@retry(max_retries=3, logger=custom_logger)`

2. **Long-running operations** - Functions with progress tracking
   - Database migrations, batch processing, file operations
   - Users need visibility into operation progress
   - Example: `migrate_id_type(..., logger=progress_logger)`

3. **Integration utilities** - Functions that bridge logging systems
   - Functions that need to work with custom logging frameworks
   - Example: `custom_integration_func(..., logger=app_logger)`

**❌ DON'T use logger parameters in:**

1. **Regular utility functions** - Pure logic functions
   - Use module-level logger: `logger = logging.getLogger(__name__)`
   - No need for per-call logging customization
   - Example: `calculate_sum()`, `parse_json()`, `validate_email()`

2. **Simple transformations** - Data processing functions
   - Focus on single responsibility (transformation)
   - Module-level logging is sufficient
   - Example: `encode_base64()`, `normalize_string()`

#### Logger Parameter Pattern

**Decorators (KEEP logger parameter):**
```python
import logging
from functools import wraps

def retry(
    max_retries: int,
    delay: float = 1.0,
    logger: logging.Logger | None = None,  # ✅ Optional logger for flexibility
) -> Callable:
    """Retry decorator with optional logging override."""
    
    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if logger:  # Only log if logger provided
                        logger.warning(f"Retry {attempt + 1}/{max_retries} failed: {e}")
                    if attempt == max_retries - 1:
                        raise
        return wrapper
    return decorator

# Usage flexibility:
@retry(max_retries=3, logger=critical_logger)  # Detailed logs
def process_payment(): pass

@retry(max_retries=3, logger=None)  # No logs
def internal_helper(): pass
```

**Regular Functions (USE module logger):**
```python
import logging

# Module-level logger
logger = logging.getLogger(__name__)

def calculate_statistics(data: list[float]) -> dict[str, float]:
    """Calculate statistics - uses module logger."""
    logger.debug(f"Calculating statistics for {len(data)} values")
    
    if not data:
        raise ValueError("data cannot be empty")
    
    result = {
        'mean': sum(data) / len(data),
        'min': min(data),
        'max': max(data),
    }
    
    logger.debug(f"Statistics calculated: {result}")
    return result
```

#### Why Decorators Keep Logger Parameters

**1. Multiple contexts with different logging needs:**
```python
# Critical operations need detailed logs
@timeout(seconds=30, logger=critical_logger)
def process_payment(): pass

# Background tasks need minimal logs
@timeout(seconds=10, logger=background_logger)
def sync_cache(): pass

# Internal utilities need no logs
@timeout(seconds=5, logger=None)
def helper(): pass
```

**2. Testing and verification:**
```python
def test_retry_logging():
    """Verify decorator logs retry attempts."""
    mock_logger = Mock()
    
    @retry(max_retries=3, logger=mock_logger)
    def failing_func():
        raise ValueError("Test error")
    
    with pytest.raises(ValueError):
        failing_func()
    
    # Verify logging behavior
    assert mock_logger.warning.call_count == 3
```

**3. Third-party integration:**
```python
# Integrate with company logging system
from company_logging import CompanyLogger

company_logger = CompanyLogger("payments", team="finance")

@handle_error(logger=company_logger.get_logger())
def process_transaction(): pass
```

**4. Decorator reusability across projects:**
```python
# Project A: Uses structlog
@handle_error(logger=structlog_logger)
def project_a_func(): pass

# Project B: Uses standard logging
@handle_error(logger=std_logger)
def project_b_func(): pass
```

**Key Principle**: Decorators are **infrastructure code** that need flexibility. Regular functions are **application code** that use module-level loggers. This is the industry standard pattern used by Flask, Celery, SQLAlchemy, and other major libraries.

### Environment & Dependencies

#### Development Environment
- **Python**: Version 3.9 or later required
- **Virtual Environment**: Use project-specific virtual environment
- **Testing**: pytest with comprehensive coverage
- **Type Checking**: mypy for static type analysis
- **Linting**: pylint for code quality

#### Key Dependencies
- **Core**: No external dependencies for core utilities
- **Testing**: pytest, pytest-cov for testing
- **Async**: aiohttp for HTTP operations
- **System**: psutil for system monitoring
- **Math**: numpy for numerical operations (optional)
- **Compression**: Various compression libraries (cramjam, zstandard, etc.)

#### Development Commands
- **Install dependencies**: `pip install -r requirements_dev.txt`
- **Run tests**: `./pytest.sh` or `python -m pytest`
- **Type checking**: `mypy .`
- **Linting**: `pylint pyutils_collection/`
- **Coverage**: `pytest --cov=pyutils_collection --cov-report=html`

#### Version Management
- **Single source of truth**: All version information is centralized in `_version.py`
- **Update version**: Edit `_version.py` only - all modules import from it
- **pyproject.toml**: Dynamically reads version via `{attr = "_version.__version__"}`
- **Module imports**: Use relative imports (`from ._version import __version__`)
- **Utility script**: Run `python update_versions.py` to update any hardcoded versions

### Package Usage Philosophy

#### When to Use Battle-Tested Packages
This library follows a clear philosophy: **Use battle-tested packages as building blocks, but add meaningful logic on top**.

**DO use existing packages for:**
- HTTP protocol implementation → `requests`, `httpx`, `urllib`
- SSH protocol → `paramiko`, `fabric`
- HTML/XML parsing → `beautifulsoup4`, `lxml`
- JSON/YAML parsing → `json`, `pyyaml`
- Async primitives → `asyncio` stdlib
- Compression algorithms → stdlib (`gzip`, `bz2`, `lzma`) or bindings
- Database connections → `sqlalchemy`, `psycopg2`, `pymongo`
- State machines → `transitions`, `python-statemachine`
- Workflow orchestration → `prefect`, `airflow` (for complex cases)
- Cryptography → **ALWAYS** use `cryptography` package, never implement custom crypto

**DO add value on top with:**
- ✅ **Workflow logic**: Download management, retry strategies, error recovery
- ✅ **Validation & type safety**: Input validation, type hints, runtime checks
- ✅ **Convenience features**: Progress callbacks, smart defaults, context managers
- ✅ **Resource management**: Connection pooling, cleanup, context managers
- ✅ **Common patterns**: Rate limiting, chunking, batching, pagination
- ✅ **Integration**: Combining multiple packages with unified API
- ✅ **Error handling**: Consistent error handling and descriptive messages
- ✅ **Documentation**: Clear examples and comprehensive docstrings

**Examples of Good Patterns:**

```python
# ✅ GOOD: Uses urllib but adds download management logic
def download_file(url, destination, progress_callback=None):
    """Download with chunking, progress tracking, and cleanup."""
    # Uses: urllib.request
    # Adds: chunked reading, progress callbacks, cleanup on error, directory creation
    with urllib.request.urlopen(url) as response:
        # Custom chunking and progress logic here
        pass

# ✅ GOOD: Uses multiprocessing.Pool but adds convenience
def parallel_map(func, data, num_processes=None):
    """Parallel map with smart CPU defaults."""
    # Uses: multiprocessing.Pool
    # Adds: Smart CPU count defaults, error handling, context management
    if num_processes is None:
        num_processes = max(cpu_count() - 1, 1)
    with Pool(processes=num_processes) as pool:
        return pool.map(func, data)

# ✅ GOOD: Uses time but adds rate limiting pattern
@rate_limited_scraper(calls_per_second=2.0)
def fetch_url(url):
    """Fetch with automatic rate limiting."""
    # Uses: time.sleep
    # Adds: Decorator pattern with per-function state tracking
    pass

# ❌ BAD: Just a thin wrapper with no added value
def get_json(filepath):
    """Load JSON file."""
    with open(filepath) as f:
        return json.load(f)  # No validation, no error handling, no value added

# ❌ BAD: Reimplementing HTTP from scratch
def http_request(host, path):
    """Send HTTP request."""
    # Don't reimplement sockets and HTTP protocol!
    sock = socket.socket()
    sock.connect((host, 80))
    # ... manual HTTP implementation
```

**Value Proposition:**
This library provides a **convenience layer with engineering best practices** on top of battle-tested foundations:
1. **Consistent API** across different underlying libraries
2. **Type safety and validation**
3. **Error handling and cleanup**
4. **Convenience features** (progress callbacks, smart defaults)
5. **Good documentation and examples**
6. **Common patterns** (retry, rate limiting, chunking)

#### When Adding New Functionality
Before adding a new function or module, ask:
1. **Does a battle-tested package already solve this?** → Use it as a foundation
2. **What value am I adding?** → Ensure you're adding workflow logic, not just wrapping
3. **Is this a thin wrapper?** → Consider if users should just use the underlying package directly
4. **Am I reimplementing core functionality?** → Don't reimplement protocols, parsers, or algorithms

This document serves as a comprehensive guide for maintaining code quality, consistency, and best practices in the Python utilities repository. It should be updated whenever new patterns or standards are established in the project.