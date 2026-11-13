"""
Get statistical information about table columns for data profiling.
"""

import logging
from typing import Any

from sqlalchemy import MetaData, func, select

logger = logging.getLogger(__name__)


def get_column_statistics(
    connection: Any,
    table_name: str,
    column_name: str | None = None,
    schema: str | None = None,
) -> dict[str, Any]:
    """
    Get statistical information about table columns.

    Provides data profiling metrics: cardinality, NULL percentage,
    min/max values, and top values. Useful for data quality analysis
    and understanding data distribution.

    Parameters
    ----------
    connection : Any
        Database connection.
    table_name : str
        Table name to analyze.
    column_name : str | None, optional
        Specific column, None for all columns (by default None).
    schema : str | None, optional
        Schema name (by default None).

    Returns
    -------
    dict[str, Any]
        Statistics for each column:
        - 'total_rows': Total row count
        - 'null_count': Number of NULL values
        - 'null_percentage': Percentage of NULLs
        - 'distinct_count': Number of distinct values
        - 'cardinality_ratio': distinct/total ratio
        - 'min_value': Minimum value (if applicable)
        - 'max_value': Maximum value (if applicable)
        - 'top_values': Most common values with counts (top 5)

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If table_name is empty.

    Examples
    --------
    >>> stats = get_column_statistics(conn, "users", "email")
    >>> print(f"Cardinality: {stats['email']['cardinality_ratio']}")
    >>> print(f"NULL%: {stats['email']['null_percentage']}")

    Notes
    -----
    Useful for data quality audits, index planning, and anomaly detection.
    Can be slow on large tables - consider sampling for initial analysis.

    Complexity
    ----------
    Time: O(n) where n is rows, Space: O(k) where k is distinct values
    """
    # Input validation
    if connection is None:
        raise TypeError("connection cannot be None")
    if not isinstance(table_name, str):
        raise TypeError(f"table_name must be str, got {type(table_name).__name__}")
    if not table_name.strip():
        raise ValueError("table_name cannot be empty")
    if column_name is not None and not isinstance(column_name, str):
        raise TypeError(
            f"column_name must be str or None, got {type(column_name).__name__}"
        )
    if schema is not None and not isinstance(schema, str):
        raise TypeError(f"schema must be str or None, got {type(schema).__name__}")

    from sqlalchemy import inspect

    inspector = inspect(connection)
    columns = inspector.get_columns(table_name, schema=schema)

    if column_name:
        columns = [c for c in columns if c["name"] == column_name]
        if not columns:
            raise ValueError(f"Column {column_name} not found in table {table_name}")

    # Reflect table metadata for SQLAlchemy queries
    metadata = MetaData()
    metadata.reflect(bind=connection, schema=schema, only=[table_name])

    table_key = f"{schema}.{table_name}" if schema is not None else table_name
    if table_key not in metadata.tables:
        raise ValueError(f"Table {table_name} not found")

    table = metadata.tables[table_key]

    # Get total row count using SQLAlchemy
    total_query = select(func.count()).select_from(table)
    total_rows = connection.execute(total_query).scalar()

    stats = {}

    for col in columns:
        col_name = col["name"]
        col_obj = table.c[col_name]

        col_stats = {
            "total_rows": total_rows,
            "null_count": 0,
            "null_percentage": 0.0,
            "distinct_count": 0,
            "cardinality_ratio": 0.0,
        }

        try:
            # NULL count using SQLAlchemy
            null_query = (
                select(func.count()).select_from(table).where(col_obj.is_(None))
            )
            null_count = connection.execute(null_query).scalar()
            col_stats["null_count"] = null_count
            col_stats["null_percentage"] = (
                (null_count / total_rows * 100) if total_rows > 0 else 0.0
            )

            # Distinct count using SQLAlchemy
            distinct_query = select(func.count(func.distinct(col_obj))).select_from(
                table
            )
            distinct_count = connection.execute(distinct_query).scalar()
            col_stats["distinct_count"] = distinct_count
            col_stats["cardinality_ratio"] = (
                (distinct_count / total_rows) if total_rows > 0 else 0.0
            )

            # Min/Max for numeric/date columns
            try:
                minmax_query = select(func.min(col_obj), func.max(col_obj)).select_from(
                    table
                )
                minmax = connection.execute(minmax_query).fetchone()
                if minmax and minmax[0] is not None:
                    col_stats["min_value"] = str(minmax[0])
                    col_stats["max_value"] = str(minmax[1])
            except Exception:
                # Not applicable for this column type
                pass

            # Top values using SQLAlchemy
            try:
                top_query = (
                    select(col_obj, func.count().label("cnt"))
                    .where(col_obj.isnot(None))
                    .group_by(col_obj)
                    .order_by(func.count().desc())
                    .limit(5)
                )
                top_results = connection.execute(top_query).fetchall()
                col_stats["top_values"] = [
                    {
                        "value": str(row[0]),
                        "count": row[1],
                        "percentage": (row[1] / total_rows * 100),
                    }
                    for row in top_results
                ]
            except Exception as e:
                logger.warning(f"Could not get top values for {col_name}: {e}")
                col_stats["top_values"] = []

        except Exception as e:
            logger.error(f"Error analyzing column {col_name}: {e}")
            col_stats["error"] = str(e)

        stats[col_name] = col_stats

    return stats


__all__ = ["get_column_statistics"]
