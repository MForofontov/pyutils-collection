"""Find source files without corresponding test files."""

from pathlib import Path
from typing import NamedTuple


class MissingTest(NamedTuple):
    """
    Represents a source file without a corresponding test.

    Attributes
    ----------
    source_file : str
        Relative path to the source file, using forward slashes on every platform.
    expected_test_file : str
        Expected relative path for the test file, using forward slashes.
    module : str
        Module name the source file belongs to.
    """

    source_file: str
    expected_test_file: str
    module: str


class CoverageReport(NamedTuple):
    """
    Contains test coverage analysis results.

    Attributes
    ----------
    total_source_files : int
        Total number of source files analyzed.
    files_with_tests : int
        Number of source files with corresponding tests.
    missing_tests : list[MissingTest]
        List of source files without tests.
    coverage_percentage : float
        Percentage of files with test coverage.
    """

    total_source_files: int
    files_with_tests: int
    missing_tests: list[MissingTest]
    coverage_percentage: float


def find_missing_tests(
    project_path: str | Path,
    source_dirs: list[str] | None = None,
    test_base_dir: str = "pytest/unit",
    exclude_init: bool = True,
) -> CoverageReport:
    """
    Find all source files without corresponding test files.

    Analyzes Python source files in specified directories and checks if each
    has a corresponding test file following the test_*.py naming convention.

    Parameters
    ----------
    project_path : str | Path
        Path to the project root directory.
    source_dirs : list[str] | None, optional
        List of source directories to analyze (by default None, auto-detects).
    test_base_dir : str, optional
        Base directory for test files (by default 'pytest/unit').
    exclude_init : bool, optional
        Whether to exclude __init__.py files (by default True).

    Returns
    -------
    CoverageReport
        Named tuple containing coverage analysis results.

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    FileNotFoundError
        If project_path doesn't exist.
    ValueError
        If project_path is not a directory.

    Examples
    --------
    >>> report = find_missing_tests('my_project/')  # doctest: +SKIP
    >>> print(f"Coverage: {report.coverage_percentage:.1f}%")  # doctest: +SKIP
    Coverage: 85.5%
    >>> for missing in report.missing_tests[:5]:  # doctest: +SKIP
    ...     print(f"Missing: {missing.source_file}")

    Notes
    -----
    - Follows pytest naming convention (test_*.py)
    - Automatically detects *_functions directories
    - Handles nested module structures
    - Excludes __init__.py by default

    Complexity
    ----------
    Time: O(n), Space: O(n)
    where n is the number of source files
    """
    # Input validation
    if not isinstance(project_path, (str, Path)):
        raise TypeError(
            f"project_path must be str or Path, got {type(project_path).__name__}"
        )
    if source_dirs is not None and not isinstance(source_dirs, list):
        raise TypeError(
            f"source_dirs must be list or None, got {type(source_dirs).__name__}"
        )
    if not isinstance(test_base_dir, str):
        raise TypeError(
            f"test_base_dir must be str, got {type(test_base_dir).__name__}"
        )
    if not isinstance(exclude_init, bool):
        raise TypeError(f"exclude_init must be bool, got {type(exclude_init).__name__}")

    project_path = Path(project_path)

    if not project_path.exists():
        raise FileNotFoundError(f"Project path does not exist: {project_path}")

    if not project_path.is_dir():
        raise ValueError(f"Project path must be a directory: {project_path}")

    # Auto-detect source directories if not provided
    if source_dirs is None:
        source_dirs = _auto_detect_source_dirs(project_path)

    missing_tests: list[MissingTest] = []
    total_files = 0

    for source_dir in source_dirs:
        source_path = project_path / source_dir
        if not source_path.exists():
            continue

        # Find all Python files
        for py_file in source_path.rglob("*.py"):
            # Skip __init__.py if requested
            if exclude_init and py_file.name == "__init__.py":
                continue

            total_files += 1

            # Calculate relative path from source_dir
            rel_path = py_file.relative_to(source_path)

            # Construct expected test file path
            test_file_name = f"test_{py_file.stem}.py"
            test_path = (
                project_path
                / test_base_dir
                / source_dir
                / rel_path.parent
                / test_file_name
            )

            if not test_path.exists():
                missing_tests.append(
                    MissingTest(
                        source_file=py_file.relative_to(project_path).as_posix(),
                        expected_test_file=test_path.relative_to(
                            project_path
                        ).as_posix(),
                        module=source_dir,
                    )
                )

    # Calculate coverage
    files_with_tests = total_files - len(missing_tests)
    coverage_percentage = (
        (files_with_tests / total_files * 100) if total_files > 0 else 0.0
    )

    return CoverageReport(
        total_source_files=total_files,
        files_with_tests=files_with_tests,
        missing_tests=missing_tests,
        coverage_percentage=coverage_percentage,
    )


def _auto_detect_source_dirs(project_path: Path) -> list[str]:
    """Auto-detect source directories in the project."""
    source_dirs = []

    # Common patterns for source directories
    patterns = ["*_functions", "decorators", "data_types", "data_validation"]

    for pattern in patterns:
        for directory in project_path.glob(pattern):
            if directory.is_dir() and not directory.name.startswith("."):
                source_dirs.append(directory.name)

    return sorted(source_dirs)


def format_coverage_report(
    report: CoverageReport,
    verbose: bool = True,
    show_limit: int = 20,
) -> str:
    """
    Format test coverage report as readable text.

    Parameters
    ----------
    report : CoverageReport
        Coverage report to format.
    verbose : bool, optional
        Include detailed missing test list (by default True).
    show_limit : int, optional
        Maximum number of missing tests to show (by default 20).

    Returns
    -------
    str
        Formatted coverage report.

    Raises
    ------
    TypeError
        If parameters are of wrong type.

    Examples
    --------
    >>> report = find_missing_tests('my_project/')  # doctest: +SKIP
    >>> formatted = format_coverage_report(report)  # doctest: +SKIP
    >>> print(formatted)  # doctest: +SKIP

    Complexity
    ----------
    Time: O(n), Space: O(n)
    where n is the number of missing tests
    """
    if not isinstance(report, CoverageReport):
        raise TypeError(f"report must be CoverageReport, got {type(report).__name__}")
    if not isinstance(verbose, bool):
        raise TypeError(f"verbose must be bool, got {type(verbose).__name__}")
    if not isinstance(show_limit, int):
        raise TypeError(f"show_limit must be int, got {type(show_limit).__name__}")

    lines = [
        "Test Coverage Report",
        "=" * 60,
        "",
        f"Total Source Files: {report.total_source_files:,}",
        f"Files with Tests: {report.files_with_tests:,}",
        f"Missing Tests: {len(report.missing_tests):,}",
        f"Coverage: {report.coverage_percentage:.1f}%",
        "",
    ]

    if report.missing_tests and verbose:
        # Group by module
        by_module: dict[str, list[MissingTest]] = {}
        for missing in report.missing_tests:
            if missing.module not in by_module:
                by_module[missing.module] = []
            by_module[missing.module].append(missing)

        lines.append("Missing Tests by Module:")
        lines.append("-" * 60)

        for module in sorted(by_module.keys()):
            missing_list = by_module[module]
            lines.append(f"\n{module}: {len(missing_list)} missing")

            # Show up to show_limit items per module
            for missing in missing_list[:show_limit]:
                lines.append(f"  ✗ {missing.source_file}")
                if verbose:
                    lines.append(f"    → {missing.expected_test_file}")

            if len(missing_list) > show_limit:
                lines.append(f"  ... and {len(missing_list) - show_limit} more")

    return "\n".join(lines)


__all__ = [
    "find_missing_tests",
    "format_coverage_report",
    "MissingTest",
    "CoverageReport",
]
