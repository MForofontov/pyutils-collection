"""
Find duplicate rows in a table based on specified columns.
"""

import logging
from typing import Any

from sqlalchemy import MetaData, func, select

logger = logging.getLogger(__name__)


def find_duplicate_rows(
    connection: Any,
    table_name: str,
    columns: list[str],
    schema: str | None = None,
    min_duplicates: int = 2,
) -> list[dict[str, Any]]:
    """
    Find duplicate rows in a table based on specified columns.

    Identifies rows that have identical values in the specified columns.
    Useful for data quality checks and duplicate cleanup operations.

    Parameters
    ----------
    connection : Any
        Database connection.
    table_name : str
        Table name to check for duplicates.
    columns : list[str]
        Column names to use for duplicate detection.
    schema : str | None, optional
        Schema name (by default None).
    min_duplicates : int, optional
        Minimum number of duplicates to report (by default 2).

    Returns
    -------
    list[dict[str, Any]]
        List of duplicate groups with:
        - Column values that are duplicated
        - Count of duplicates
        - Sample row IDs (if primary key exists)

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If table_name is empty or columns list is empty.

    Examples
    --------
    >>> dups = find_duplicate_rows(conn, "users", ["email"])
    >>> for dup in dups:
    ...     print(f"Email {dup['email']} appears {dup['count']} times")

    Notes
    -----
    Critical for data cleanup before adding unique constraints.
    Use primary key or unique columns to identify specific duplicate rows.

    Complexity
    ----------
    Time: O(n log n) where n is rows, Space: O(d) where d is duplicates
    """
    # Input validation
    if connection is None:
        raise TypeError("connection cannot be None")
    if not isinstance(table_name, str):
        raise TypeError(f"table_name must be str, got {type(table_name).__name__}")
    if not table_name.strip():
        raise ValueError("table_name cannot be empty")
    if not isinstance(columns, list):
        raise TypeError(f"columns must be list, got {type(columns).__name__}")
    if len(columns) == 0:
        raise ValueError("columns list cannot be empty")
    if not isinstance(min_duplicates, int):
        raise TypeError(
            f"min_duplicates must be int, got {type(min_duplicates).__name__}"
        )
    if min_duplicates < 2:
        raise ValueError("min_duplicates must be at least 2")
    if schema is not None and not isinstance(schema, str):
        raise TypeError(f"schema must be str or None, got {type(schema).__name__}")

    # Reflect table metadata
    metadata = MetaData()
    metadata.reflect(bind=connection, schema=schema, only=[table_name])

    table_key = f"{schema}.{table_name}" if schema is not None else table_name
    if table_key not in metadata.tables:
        raise ValueError(f"Table {table_name} not found")

    table = metadata.tables[table_key]

    # Validate columns exist
    for col_name in columns:
        if col_name not in table.c:
            raise ValueError(f"Column {col_name} not found in table {table_name}")

    # Build duplicate detection query
    col_objs = [table.c[col_name] for col_name in columns]

    # Find groups with duplicates
    dup_query = (
        select(*col_objs, func.count().label("dup_count"))
        .group_by(*col_objs)
        .having(func.count() >= min_duplicates)
        .order_by(func.count().desc())
    )

    result = connection.execute(dup_query)
    duplicates = []

    for row in result:
        dup_info = {
            "count": row[-1],  # Last column is dup_count
        }

        # Add column values
        for i, col_name in enumerate(columns):
            dup_info[col_name] = row[i]

        # Try to get sample IDs if primary key exists
        try:
            pk_cols = [col for col in table.primary_key.columns]
            if pk_cols:
                # Build WHERE clause for this duplicate group
                where_conditions = [
                    table.c[col_name] == row[i] for i, col_name in enumerate(columns)
                ]

                sample_query = select(*pk_cols).where(*where_conditions).limit(10)

                sample_result = connection.execute(sample_query)
                sample_ids = [r[0] for r in sample_result]
                dup_info["sample_ids"] = sample_ids
        except Exception as e:
            logger.debug(f"Could not fetch sample IDs: {e}")

        duplicates.append(dup_info)

    return duplicates


__all__ = ["find_duplicate_rows"]
