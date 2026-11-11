"""
Append data to existing Parquet file.
"""

from pathlib import Path
from typing import Any

import pyarrow as pa
import pyarrow.parquet as pq

from pyutils_collection.serialization_functions._staged_output import staged_output


def append_parquet(
    data: list[dict[str, Any]],
    file_path: str,
    compression: str = "snappy",
) -> None:
    """
    Append data to existing Parquet file or create new one.

    Parameters
    ----------
    data : list[dict[str, Any]]
        List of dictionaries to append.
    file_path : str
        Path to Parquet file.
    compression : str, optional
        Compression codec (by default "snappy").

    Returns
    -------
    None

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If data is empty or schema mismatch.
    ImportError
        If pyarrow is not installed.

    Examples
    --------
    >>> data = [{'name': 'Charlie', 'age': 35}]
    >>> append_parquet(data, 'people.parquet')

    Notes
    -----
    Requires pyarrow package.
    Schema must match existing file.
    Creates file if it doesn't exist.
    A failed write leaves an existing destination unchanged. Output is staged
    beside the destination; existing permission bits are preserved and a
    destination symlink is replaced rather than followed.

    Complexity
    ----------
    Time: O(n*m), Space: O(n*m), where n is total rows, m is columns
    """
    if not isinstance(data, list):
        raise TypeError(f"data must be a list, got {type(data).__name__}")

    if not data:
        raise ValueError("data cannot be empty")

    if not all(isinstance(item, dict) for item in data):
        raise TypeError("all elements in data must be dictionaries")

    if not isinstance(file_path, str):
        raise TypeError(f"file_path must be a string, got {type(file_path).__name__}")

    if not isinstance(compression, str):
        raise TypeError(
            f"compression must be a string, got {type(compression).__name__}"
        )

    # Create parent directories
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)

    # Convert new data to table
    try:
        new_table = pa.Table.from_pylist(data)
    except Exception as e:
        raise ValueError(f"Failed to convert data to Arrow table: {e}") from e

    # Check if file exists
    file_exists = Path(file_path).exists()

    if file_exists:
        # Read existing data
        existing_table = pq.read_table(file_path)

        # Validate schema compatibility
        if existing_table.schema.names != new_table.schema.names:
            raise ValueError(
                f"Schema mismatch. Existing: {existing_table.schema.names}, "
                f"New: {new_table.schema.names}"
            )

        # Concatenate tables
        combined_table = pa.concat_tables([existing_table, new_table])
    else:
        combined_table = new_table

    # Write combined table
    with staged_output(file_path) as temporary:
        pq.write_table(
            combined_table,
            temporary,
            compression=compression.upper() if compression != "none" else None,
        )


__all__ = ["append_parquet"]
