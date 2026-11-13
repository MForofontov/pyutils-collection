"""
Merge multiple CSV files into one.
"""

import csv
import os
import tempfile
from collections.abc import Sequence
from pathlib import Path
from typing import Any


def merge_csv_files(
    input_files: Sequence[str | Path],
    output_file: str | Path,
    *,
    has_header: bool = True,
    skip_duplicates: bool = False,
    encoding: str = "utf-8",
    **kwargs: Any,
) -> int:
    """
    Merge multiple CSV files into a single output file.

    Handles header merging, duplicate detection, and consistent formatting.
    All input files must have compatible structures (same columns if has_header=True).

    Parameters
    ----------
    input_files : Sequence[str | Path]
        List of paths to CSV files to merge.
    output_file : str | Path
        Path to output merged CSV file.
    has_header : bool, optional
        Whether CSV files have headers (by default True).
    skip_duplicates : bool, optional
        Skip duplicate rows (by default False). Compares entire row.
    encoding : str, optional
        File encoding (by default 'utf-8').
    **kwargs : Any
        Additional arguments for csv.reader/writer.

    Returns
    -------
    int
        Number of rows written (excluding header).

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If input_files is empty or files have incompatible headers.
    FileNotFoundError
        If any input file doesn't exist.

    Examples
    --------
    >>> from tempfile import TemporaryDirectory
    >>> with TemporaryDirectory() as directory:
    ...     first = Path(directory) / 'first.csv'
    ...     second = Path(directory) / 'second.csv'
    ...     output = Path(directory) / 'merged.csv'
    ...     _ = first.write_text('name\\nAda\\n', encoding='utf-8')
    ...     _ = second.write_text('name\\nAda\\nBob\\n', encoding='utf-8')
    ...     merge_csv_files([first, second], output, skip_duplicates=True)
    2

    Notes
    -----
    When has_header=True, uses the first nonempty file's header and validates
    others match. Empty files are skipped.
    Duplicate detection keeps first occurrence and compares full row content.
    Output is staged beside the destination and replaced only after success;
    failures remove the temporary file and preserve existing output. The output
    may also be an input. Replacement uses temporary-file permissions and replaces
    a destination symlink itself; parent-directory metadata is not synced.

    Complexity
    ----------
    Time: O(n*m) where n=total rows, m=row size (for duplicate check)
    Space: O(n) if skip_duplicates=True, O(1) otherwise
    """
    # Type validation
    if not isinstance(input_files, (list, tuple)):
        raise TypeError(
            f"input_files must be a sequence, got {type(input_files).__name__}"
        )
    if not isinstance(output_file, (str, Path)):
        raise TypeError(
            f"output_file must be str or Path, got {type(output_file).__name__}"
        )
    if not isinstance(has_header, bool):
        raise TypeError(f"has_header must be bool, got {type(has_header).__name__}")
    if not isinstance(skip_duplicates, bool):
        raise TypeError(
            f"skip_duplicates must be bool, got {type(skip_duplicates).__name__}"
        )
    if not isinstance(encoding, str):
        raise TypeError(f"encoding must be str, got {type(encoding).__name__}")

    # Value validation
    if len(input_files) == 0:
        raise ValueError("input_files cannot be empty")

    for file_path in input_files:
        if not isinstance(file_path, (str, Path)):
            raise TypeError(
                f"Each input file must be str or Path, got {type(file_path).__name__}"
            )
        if not Path(file_path).exists():
            raise FileNotFoundError(f"Input file not found: {file_path}")

    # Track seen rows for duplicate detection
    seen_rows: set[tuple[str, ...]] = set() if skip_duplicates else set()
    header: list[str] | None = None
    rows_written = 0

    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding=encoding,
            newline="",
            dir=Path(output_file).parent,
            prefix=".merge-csv-",
            delete=False,
        ) as outfile:
            temporary = Path(outfile.name)
            writer: Any = None

            for input_path in input_files:
                with open(input_path, encoding=encoding, newline="") as infile:
                    reader = csv.reader(infile, **kwargs)

                    # Handle header
                    if has_header:
                        file_header = next(reader, None)
                        if file_header is None:
                            continue  # Skip empty file

                        if header is None:
                            # First nonempty file establishes the header
                            header = file_header
                            writer = csv.writer(outfile, **kwargs)
                            writer.writerow(header)
                        else:
                            # Validate header matches
                            if file_header != header:
                                raise ValueError(
                                    f"Header mismatch in {input_path}. "
                                    f"Expected {header}, got {file_header}"
                                )
                    else:
                        if writer is None:
                            writer = csv.writer(outfile, **kwargs)

                    # Write data rows
                    for row in reader:
                        if skip_duplicates:
                            row_tuple = tuple(row)
                            if row_tuple in seen_rows:
                                continue
                            seen_rows.add(row_tuple)

                        if writer is not None:
                            writer.writerow(row)
                            rows_written += 1
            outfile.flush()
            os.fsync(outfile.fileno())
        os.replace(temporary, output_file)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)

    return rows_written


__all__ = ["merge_csv_files"]
