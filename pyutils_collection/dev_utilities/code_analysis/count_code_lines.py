"""Count lines of code in Python files."""

import tokenize
from pathlib import Path
from typing import NamedTuple


class CodeLineCount(NamedTuple):
    """
    Container for code line count results.

    Attributes
    ----------
    total_lines : int
        Total number of lines in the file.
    source_lines : int
        Number of source code lines (excluding comments and blank lines).
    comment_lines : int
        Number of comment lines (lines starting with #).
    blank_lines : int
        Number of blank lines (lines with only whitespace).
    docstring_lines : int
        Number of lines in docstrings.
    """

    total_lines: int
    source_lines: int
    comment_lines: int
    blank_lines: int
    docstring_lines: int


def count_code_lines(file_path: str | Path) -> CodeLineCount:
    """
    Count different types of lines in a Python file.

    Uses the tokenize module to accurately count source lines, comments,
    blank lines, and docstrings in Python files.

    Parameters
    ----------
    file_path : str | Path
        Path to the Python file to analyze.

    Returns
    -------
    CodeLineCount
        Named tuple containing line counts for different categories.

    Raises
    ------
    TypeError
        If file_path is not str or Path.
    FileNotFoundError
        If file_path doesn't exist.
    ValueError
        If file_path is not a .py file.

    Examples
    --------
    >>> counts = count_code_lines('my_module.py')  # doctest: +SKIP
    >>> print(f"Source lines: {counts.source_lines}")  # doctest: +SKIP
    Source lines: 42
    >>> print(f"Comments: {counts.comment_lines}")  # doctest: +SKIP
    Comments: 15

    Notes
    -----
    - Uses Python's tokenize module for accurate parsing
    - Distinguishes between comments and docstrings
    - Blank lines are lines containing only whitespace
    - Source lines exclude comments, blanks, and docstrings

    Complexity
    ----------
    Time: O(n), Space: O(1)
    where n is the number of lines in the file
    """
    # Input validation
    if not isinstance(file_path, (str, Path)):
        raise TypeError(
            f"file_path must be str or Path, got {type(file_path).__name__}"
        )

    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"File does not exist: {file_path}")

    if file_path.suffix != ".py":
        raise ValueError(f"File must be a Python (.py) file, got {file_path.suffix}")

    if not file_path.is_file():
        raise ValueError(f"Path must be a file, not a directory: {file_path}")

    # Initialize counters
    total_lines = 0
    source_lines = 0
    comment_lines = 0
    blank_lines = 0
    docstring_lines = 0

    # Read file to count total lines and blank lines
    with open(file_path, "rb") as f:
        content = f.read()

    # Count total and blank lines
    lines = content.decode("utf-8", errors="ignore").splitlines()
    total_lines = len(lines)
    blank_lines = sum(1 for line in lines if not line.strip())

    # Use tokenize to identify comments and docstrings
    try:
        with open(file_path, "rb") as f:
            tokens = list(tokenize.tokenize(f.readline))

        comment_line_numbers: set[int] = set()
        docstring_line_numbers: set[int] = set()

        for i, token in enumerate(tokens):
            # Count comments
            if token.type == tokenize.COMMENT:
                comment_line_numbers.add(token.start[0])

            # Count docstrings (STRING tokens that are the first statement)
            elif token.type == tokenize.STRING:
                # Check if this is likely a docstring by looking at previous tokens
                # Docstrings typically appear after INDENT, NEWLINE, or at module level
                if i > 0:
                    prev_token = tokens[i - 1]
                    # Look for patterns indicating docstring
                    if prev_token.type in (
                        tokenize.INDENT,
                        tokenize.NEWLINE,
                        tokenize.NL,
                    ):
                        # Count all lines in the docstring
                        start_line = token.start[0]
                        end_line = token.end[0]
                        for line_num in range(start_line, end_line + 1):
                            docstring_line_numbers.add(line_num)

        comment_lines = len(comment_line_numbers)
        docstring_lines = len(docstring_line_numbers)

        # Source lines = total - blank - comments - docstrings
        # We need to be careful not to double-count
        non_source_lines = blank_lines + comment_lines + docstring_lines
        source_lines = max(0, total_lines - non_source_lines)

    except tokenize.TokenError, UnicodeDecodeError:
        # If tokenization fails, fall back to simple counting
        source_lines = total_lines - blank_lines

    return CodeLineCount(
        total_lines=total_lines,
        source_lines=source_lines,
        comment_lines=comment_lines,
        blank_lines=blank_lines,
        docstring_lines=docstring_lines,
    )


def count_code_lines_directory(
    directory_path: str | Path,
    recursive: bool = True,
) -> dict[str, CodeLineCount]:
    """
    Count lines of code for all Python files in a directory.

    Parameters
    ----------
    directory_path : str | Path
        Path to the directory to analyze.
    recursive : bool, optional
        Whether to recursively scan subdirectories (by default True).

    Returns
    -------
    dict[str, CodeLineCount]
        Dictionary mapping file paths to their line counts.

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    FileNotFoundError
        If directory doesn't exist.
    ValueError
        If path is not a directory.

    Examples
    --------
    >>> counts = count_code_lines_directory('my_project')  # doctest: +SKIP
    >>> total_source = sum(c.source_lines for c in counts.values())  # doctest: +SKIP
    >>> print(f"Total source lines: {total_source}")  # doctest: +SKIP
    Total source lines: 1234

    Complexity
    ----------
    Time: O(n * m), Space: O(n)
    where n is number of files and m is average file size
    """
    # Input validation
    if not isinstance(directory_path, (str, Path)):
        raise TypeError(
            f"directory_path must be str or Path, got {type(directory_path).__name__}"
        )
    if not isinstance(recursive, bool):
        raise TypeError(f"recursive must be bool, got {type(recursive).__name__}")

    directory_path = Path(directory_path)

    if not directory_path.exists():
        raise FileNotFoundError(f"Directory does not exist: {directory_path}")

    if not directory_path.is_dir():
        raise ValueError(f"Path must be a directory: {directory_path}")

    # Collect Python files
    if recursive:
        python_files = directory_path.rglob("*.py")
    else:
        python_files = directory_path.glob("*.py")

    # Count lines for each file
    results: dict[str, CodeLineCount] = {}
    for py_file in python_files:
        try:
            counts = count_code_lines(py_file)
            results[str(py_file)] = counts
        except ValueError, FileNotFoundError:
            # Skip files that can't be processed
            continue

    return results


__all__ = ["count_code_lines", "count_code_lines_directory", "CodeLineCount"]
