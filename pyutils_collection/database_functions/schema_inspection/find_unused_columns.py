"""
Identify columns that are rarely or never used.
"""

import logging
from typing import Any

from sqlalchemy import MetaData, func, select

logger = logging.getLogger(__name__)


def find_unused_columns(
    connection: Any,
    tables: list[str] | None = None,
    schema: str | None = None,
    null_threshold: float = 0.95,
) -> list[dict[str, Any]]:
    """
    Identify columns that are rarely or never used.

    Finds columns with very high NULL percentages that may be candidates
    for removal or archival. Useful for database optimization.

    Parameters
    ----------
    connection : Any
        Database connection.
    tables : list[str] | None, optional
        Specific tables to check (by default None for all tables).
    schema : str | None, optional
        Schema name (by default None).
    null_threshold : float, optional
        Minimum NULL percentage to flag as unused (by default 0.95 = 95%).

    Returns
    -------
    list[dict[str, Any]]
        List of potentially unused columns with:
        - table_name: str
        - column_name: str
        - null_count: int
        - total_rows: int
        - null_percentage: float
        - distinct_values: int (if not all NULL)

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If null_threshold is not between 0 and 1.

    Examples
    --------
    >>> unused = find_unused_columns(conn, null_threshold=0.90)
    >>> for col in unused:
    ...     print(f"{col['table_name']}.{col['column_name']}: {col['null_percentage']:.1%} NULL")

    Notes
    -----
    Critical before schema changes or data archival decisions.
    Consider checking query logs for actual column access patterns.
    High NULL percentage doesn't always mean unused - could be optional data.

    Complexity
    ----------
    Time: O(n*m) where n is rows and m is columns, Space: O(c) where c is candidates
    """
    # Input validation
    if connection is None:
        raise TypeError("connection cannot be None")
    if tables is not None and not isinstance(tables, list):
        raise TypeError(f"tables must be list or None, got {type(tables).__name__}")
    if schema is not None and not isinstance(schema, str):
        raise TypeError(f"schema must be str or None, got {type(schema).__name__}")
    if not isinstance(null_threshold, (int, float)):
        raise TypeError(
            f"null_threshold must be float, got {type(null_threshold).__name__}"
        )
    if not 0 <= null_threshold <= 1:
        raise ValueError(
            f"null_threshold must be between 0 and 1, got {null_threshold}"
        )

    # Reflect metadata
    metadata = MetaData()
    metadata.reflect(bind=connection, schema=schema, only=tables)

    table_names = tables if tables else [t for t in metadata.tables.keys()]

    unused_columns = []

    for table_name in table_names:
        table_key = (
            f"{schema}.{table_name}" if schema is not None and tables else table_name
        )
        if table_key not in metadata.tables:
            continue

        table = metadata.tables[table_key]

        # Get total row count first
        total_rows_query = select(func.count()).select_from(table)
        result = connection.execute(total_rows_query)
        total_rows = result.scalar() or 0

        if total_rows == 0:
            logger.debug(f"Table {table_name} is empty, skipping")
            continue

        # Check each column
        for col in table.columns:
            try:
                # Skip primary key columns
                if col.primary_key:
                    continue

                # Count NULL values
                null_count_query = (
                    select(func.count()).select_from(table).where(col.is_(None))
                )
                result = connection.execute(null_count_query)
                null_count = result.scalar() or 0

                null_percentage = null_count / total_rows

                # Check if exceeds threshold
                if null_percentage >= null_threshold:
                    col_info = {
                        "table_name": table_name,
                        "column_name": col.name,
                        "null_count": null_count,
                        "total_rows": total_rows,
                        "null_percentage": null_percentage,
                    }

                    # If not all NULL, get distinct value count
                    if null_count < total_rows:
                        try:
                            distinct_query = (
                                select(func.count(func.distinct(col)))
                                .select_from(table)
                                .where(col.is_not(None))
                            )
                            result = connection.execute(distinct_query)
                            distinct_count = result.scalar() or 0
                            col_info["distinct_values"] = distinct_count

                            # Add cardinality info
                            non_null_count = total_rows - null_count
                            if non_null_count > 0:
                                col_info["cardinality_ratio"] = (
                                    distinct_count / non_null_count
                                )
                        except Exception as e:
                            logger.debug(
                                f"Could not get distinct count for {table_name}.{col.name}: {e}"
                            )

                    unused_columns.append(col_info)

            except Exception as e:
                logger.error(f"Error checking column {table_name}.{col.name}: {e}")

    # Sort by null percentage descending
    unused_columns.sort(key=lambda x: x["null_percentage"], reverse=True)

    return unused_columns


__all__ = ["find_unused_columns"]
