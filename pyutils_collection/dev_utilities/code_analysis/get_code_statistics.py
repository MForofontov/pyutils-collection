"""Get code statistics and metrics for Python projects."""

import ast
from pathlib import Path
from typing import NamedTuple

from .count_code_lines import count_code_lines_directory


class CodeStatistics(NamedTuple):
    """
    Container for comprehensive code statistics.

    Attributes
    ----------
    total_files : int
        Total number of Python files.
    total_lines : int
        Total number of lines across all files.
    source_lines : int
        Total source code lines.
    comment_lines : int
        Total comment lines.
    blank_lines : int
        Total blank lines.
    docstring_lines : int
        Total docstring lines.
    total_functions : int
        Total number of functions defined.
    total_classes : int
        Total number of classes defined.
    total_methods : int
        Total number of methods in classes.
    total_imports : int
        Total number of import statements.
    avg_lines_per_file : float
        Average lines per file.
    avg_functions_per_file : float
        Average functions per file.
    """

    total_files: int
    total_lines: int
    source_lines: int
    comment_lines: int
    blank_lines: int
    docstring_lines: int
    total_functions: int
    total_classes: int
    total_methods: int
    total_imports: int
    avg_lines_per_file: float
    avg_functions_per_file: float


def get_code_statistics(
    project_path: str | Path,
    exclude_patterns: list[str] | None = None,
) -> CodeStatistics:
    """
    Generate comprehensive code statistics for a Python project.

    Analyzes all Python files in a project to gather metrics about code
    structure, including counts of files, lines, functions, classes, and imports.

    Parameters
    ----------
    project_path : str | Path
        Path to the project directory to analyze.
    exclude_patterns : list[str] | None, optional
        List of glob patterns to exclude (by default None).

    Returns
    -------
    CodeStatistics
        Named tuple containing comprehensive code statistics.

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
    >>> stats = get_code_statistics('my_project')  # doctest: +SKIP
    >>> print(f"Total files: {stats.total_files}")  # doctest: +SKIP
    Total files: 42
    >>> print(f"Functions: {stats.total_functions}")  # doctest: +SKIP
    Functions: 156

    Notes
    -----
    - Recursively analyzes all Python files
    - Uses AST parsing for accurate analysis
    - Provides both absolute and average metrics
    - Can exclude files matching patterns (e.g., '**/test_*.py')

    Complexity
    ----------
    Time: O(n * m), Space: O(n)
    where n is number of files and m is average file size
    """
    # Input validation
    if not isinstance(project_path, (str, Path)):
        raise TypeError(
            f"project_path must be str or Path, got {type(project_path).__name__}"
        )
    if exclude_patterns is not None and not isinstance(exclude_patterns, list):
        raise TypeError(
            f"exclude_patterns must be list or None, got {type(exclude_patterns).__name__}"
        )
    if exclude_patterns is not None:
        if not all(isinstance(p, str) for p in exclude_patterns):
            raise TypeError("All exclude_patterns must be strings")

    project_path = Path(project_path)

    if not project_path.exists():
        raise FileNotFoundError(f"Project path does not exist: {project_path}")

    if not project_path.is_dir():
        raise ValueError(f"Project path must be a directory: {project_path}")

    # Get line counts for all files
    line_counts = count_code_lines_directory(project_path, recursive=True)

    # Filter excluded patterns
    if exclude_patterns:
        filtered_counts = {}
        for file_path, counts in line_counts.items():
            path = Path(file_path)
            excluded = False
            for pattern in exclude_patterns:
                if path.match(pattern):
                    excluded = True
                    break
            if not excluded:
                filtered_counts[file_path] = counts
        line_counts = filtered_counts

    # Initialize counters
    total_files = len(line_counts)
    total_lines = sum(c.total_lines for c in line_counts.values())
    source_lines = sum(c.source_lines for c in line_counts.values())
    comment_lines = sum(c.comment_lines for c in line_counts.values())
    blank_lines = sum(c.blank_lines for c in line_counts.values())
    docstring_lines = sum(c.docstring_lines for c in line_counts.values())

    total_functions = 0
    total_classes = 0
    total_methods = 0
    total_imports = 0

    # Analyze AST for each file
    for file_path in line_counts.keys():
        try:
            with open(file_path, encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=file_path)

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Check if this is a method (inside a class)
                    is_method = False
                    for parent in ast.walk(tree):
                        if isinstance(parent, ast.ClassDef):
                            if node in ast.walk(parent):
                                is_method = True
                                break
                    if is_method:
                        total_methods += 1
                    else:
                        total_functions += 1
                elif isinstance(node, ast.ClassDef):
                    total_classes += 1
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    total_imports += 1

        except SyntaxError, UnicodeDecodeError:
            # Skip files with errors
            continue

    # Calculate averages
    avg_lines_per_file = total_lines / total_files if total_files > 0 else 0.0
    avg_functions_per_file = (
        (total_functions + total_methods) / total_files if total_files > 0 else 0.0
    )

    return CodeStatistics(
        total_files=total_files,
        total_lines=total_lines,
        source_lines=source_lines,
        comment_lines=comment_lines,
        blank_lines=blank_lines,
        docstring_lines=docstring_lines,
        total_functions=total_functions,
        total_classes=total_classes,
        total_methods=total_methods,
        total_imports=total_imports,
        avg_lines_per_file=round(avg_lines_per_file, 2),
        avg_functions_per_file=round(avg_functions_per_file, 2),
    )


def format_statistics(stats: CodeStatistics, title: str = "Code Statistics") -> str:
    """
    Format code statistics as a readable text report.

    Parameters
    ----------
    stats : CodeStatistics
        Statistics to format.
    title : str, optional
        Title for the report (by default "Code Statistics").

    Returns
    -------
    str
        Formatted statistics report.

    Raises
    ------
    TypeError
        If parameters are of wrong type.

    Examples
    --------
    >>> stats = get_code_statistics('my_project')  # doctest: +SKIP
    >>> report = format_statistics(stats)  # doctest: +SKIP
    >>> print(report)  # doctest: +SKIP
    Code Statistics
    ===============
    Files: 42
    ...

    Complexity
    ----------
    Time: O(1), Space: O(1)
    """
    if not isinstance(stats, CodeStatistics):
        raise TypeError(f"stats must be CodeStatistics, got {type(stats).__name__}")
    if not isinstance(title, str):
        raise TypeError(f"title must be str, got {type(title).__name__}")

    lines = [
        title,
        "=" * len(title),
        "",
        "File Metrics:",
        f"  Total Files: {stats.total_files:,}",
        "",
        "Line Metrics:",
        f"  Total Lines: {stats.total_lines:,}",
        f"  Source Lines: {stats.source_lines:,}",
        f"  Comment Lines: {stats.comment_lines:,}",
        f"  Blank Lines: {stats.blank_lines:,}",
        f"  Docstring Lines: {stats.docstring_lines:,}",
        "",
        "Code Structure:",
        f"  Functions: {stats.total_functions:,}",
        f"  Classes: {stats.total_classes:,}",
        f"  Methods: {stats.total_methods:,}",
        f"  Imports: {stats.total_imports:,}",
        "",
        "Averages:",
        f"  Lines per File: {stats.avg_lines_per_file:.2f}",
        f"  Functions per File: {stats.avg_functions_per_file:.2f}",
    ]

    return "\n".join(lines)


__all__ = ["get_code_statistics", "format_statistics", "CodeStatistics"]
