"""
Transform CSV file with column mapping and filtering.
"""

import csv
from collections.abc import Callable, Sequence
from pathlib import Path
from typing import Any

from pyutils_collection.serialization_functions._staged_output import staged_output


def transform_csv_columns(
    input_file: str | Path,
    output_file: str | Path,
    *,
    column_mapping: dict[str, str] | None = None,
    select_columns: Sequence[str] | None = None,
    transformers: dict[str, Callable[[Any], Any]] | None = None,
    filter_func: Callable[[dict[str, Any]], bool] | None = None,
    encoding: str = "utf-8",
    **kwargs: Any,
) -> int:
    """
    Transform CSV file with column renaming, selection, and value transformations.

    Provides flexible CSV transformation including column mapping, filtering,
    and per-column value transformations in a single pass.

    Parameters
    ----------
    input_file : str | Path
        Path to input CSV file.
    output_file : str | Path
        Path to output CSV file.
    column_mapping : dict[str, str] | None, optional
        Map old column names to new names (by default None).
    select_columns : Sequence[str] | None, optional
        Only include these columns in output (by default None for all).
    transformers : dict[str, Callable[[Any], Any]] | None, optional
        Functions to transform values in specific columns (by default None).
    filter_func : Callable[[dict[str, Any]], bool] | None, optional
        Function to filter rows - returns True to include (by default None).
    encoding : str, optional
        File encoding (by default 'utf-8').
    **kwargs : Any
        Additional arguments for csv.DictReader/DictWriter.

    Returns
    -------
    int
        Number of rows written to output file.

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    FileNotFoundError
        If input file doesn't exist.
    ValueError
        If column names are invalid.

    Examples
    --------
    >>> # Rename columns
    >>> mapping = {'first_name': 'name', 'user_age': 'age'}
    >>> transform_csv_columns('input.csv', 'output.csv', column_mapping=mapping)
    100

    >>> # Select specific columns
    >>> transform_csv_columns('input.csv', 'output.csv', select_columns=['id', 'name'])
    100

    >>> # Transform values
    >>> transformers = {
    ...     'age': int,
    ...     'email': str.lower,
    ...     'salary': lambda x: float(x) * 1.1
    ... }
    >>> transform_csv_columns('input.csv', 'output.csv', transformers=transformers)
    100

    >>> # Filter rows
    >>> filter_func = lambda row: int(row['age']) >= 18
    >>> transform_csv_columns('input.csv', 'adults.csv', filter_func=filter_func)
    73

    >>> # Combine all transformations
    >>> transform_csv_columns(
    ...     'input.csv',
    ...     'output.csv',
    ...     column_mapping={'user_id': 'id'},
    ...     select_columns=['id', 'name', 'age'],
    ...     transformers={'age': int},
    ...     filter_func=lambda row: row['name'] != ''
    ... )
    95

    Notes
    -----
    Operations are applied in order: mapping → selection → transformation → filtering.
    Transformers receive string values from CSV and should handle conversion.
    Output is staged beside the destination and replaced only after success,
    allowing input_file and output_file to be the same path. Existing permission
    bits are preserved; a destination symlink is replaced rather than followed.

    Complexity
    ----------
    Time: O(n*m) where n=rows, m=avg columns per row
    Space: O(1)
    """
    # Type validation
    if not isinstance(input_file, (str, Path)):
        raise TypeError(
            f"input_file must be str or Path, got {type(input_file).__name__}"
        )
    if not isinstance(output_file, (str, Path)):
        raise TypeError(
            f"output_file must be str or Path, got {type(output_file).__name__}"
        )
    if column_mapping is not None and not isinstance(column_mapping, dict):
        raise TypeError(
            f"column_mapping must be dict or None, got {type(column_mapping).__name__}"
        )
    if select_columns is not None and not isinstance(select_columns, (list, tuple)):
        raise TypeError(
            f"select_columns must be sequence or None, got {type(select_columns).__name__}"
        )
    if transformers is not None and not isinstance(transformers, dict):
        raise TypeError(
            f"transformers must be dict or None, got {type(transformers).__name__}"
        )
    if filter_func is not None and not callable(filter_func):
        raise TypeError("filter_func must be callable or None")
    if not isinstance(encoding, str):
        raise TypeError(f"encoding must be str, got {type(encoding).__name__}")

    # Value validation
    if not Path(input_file).exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")

    rows_written = 0

    with (
        staged_output(output_file) as temporary,
        open(input_file, encoding=encoding, newline="") as infile,
    ):
        reader = csv.DictReader(infile, **kwargs)

        if reader.fieldnames is None:
            raise ValueError("Input CSV file has no header")

        # Build output fieldnames
        input_fieldnames = list(reader.fieldnames)
        output_fieldnames = input_fieldnames.copy()

        # Apply column mapping
        if column_mapping:
            output_fieldnames = [
                column_mapping.get(col, col) for col in output_fieldnames
            ]

        # Apply column selection
        if select_columns:
            selected = list(select_columns)
            # Validate all selected columns exist
            for col in selected:
                if col not in output_fieldnames:
                    raise ValueError(
                        f"Selected column '{col}' not found in output columns {output_fieldnames}"
                    )
            output_fieldnames = selected

        with open(temporary, "w", encoding=encoding, newline="") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=output_fieldnames, **kwargs)
            writer.writeheader()

            for row in reader:
                # Apply column mapping to row
                if column_mapping:
                    mapped_row = {column_mapping.get(k, k): v for k, v in row.items()}
                else:
                    mapped_row = row.copy()

                # Apply column selection
                if select_columns:
                    selected_row = {
                        k: v for k, v in mapped_row.items() if k in select_columns
                    }
                else:
                    selected_row = mapped_row

                # Apply transformers
                if transformers:
                    for col, transformer in transformers.items():
                        if col in selected_row:
                            try:
                                selected_row[col] = transformer(selected_row[col])
                            except Exception as e:
                                raise ValueError(
                                    f"Error transforming column '{col}': {e}"
                                ) from e

                # Apply filter
                if filter_func:
                    try:
                        if not filter_func(selected_row):  # type: ignore[arg-type]
                            continue
                    except Exception as e:
                        raise ValueError(f"Error in filter function: {e}") from e

                writer.writerow(selected_row)
                rows_written += 1

    return rows_written


__all__ = ["transform_csv_columns"]
