"""
Analyze column cardinality for optimization insights.

Identifies low and high cardinality columns to guide indexing,
partitioning, and data modeling decisions.
"""

import logging
from typing import Any

from sqlalchemy import MetaData, func, select

logger = logging.getLogger(__name__)


def analyze_column_cardinality(
    connection: Any,
    tables: list[str] | None = None,
    schema: str | None = None,
    sample_size: int | None = None,
    low_cardinality_threshold: float = 0.01,
    high_cardinality_threshold: float = 0.95,
) -> list[dict[str, Any]]:
    """
    Analyze column cardinality for optimization insights.

    Identifies columns with low cardinality (good candidates for indexing,
    enum types, or partitioning keys) and high cardinality columns
    (potential primary keys or unique identifiers).

    Parameters
    ----------
    connection : Any
        Database connection.
    tables : list[str] | None, optional
        Specific tables to analyze (by default None for all tables).
    schema : str | None, optional
        Schema name (by default None).
    sample_size : int | None, optional
        Limit analysis to N rows (by default None for full scan).
    low_cardinality_threshold : float, optional
        Ratio below which column is considered low cardinality (by default 0.01).
    high_cardinality_threshold : float, optional
        Ratio above which column is considered high cardinality (by default 0.95).

    Returns
    -------
    list[dict[str, Any]]
        List of cardinality analysis results:
        - 'table_name': Table name
        - 'column_name': Column name
        - 'total_rows': Total row count
        - 'distinct_values': Number of distinct values
        - 'cardinality_ratio': distinct/total ratio (0-1)
        - 'cardinality_category': 'low', 'medium', or 'high'
        - 'null_count': Number of NULL values
        - 'null_percentage': Percentage of NULLs
        - 'top_values': Most common values (for low cardinality)
        - 'recommendations': Suggested optimizations

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If thresholds are invalid.

    Examples
    --------
    >>> from sqlalchemy import create_engine
    >>> engine = create_engine("sqlite:///:memory:")
    >>> with engine.connect() as conn:
    ...     results = analyze_column_cardinality(conn, low_cardinality_threshold=0.01)
    >>> results[0]['cardinality_category']
    'low'

    Notes
    -----
    - Low cardinality (<1%): Good for indexing, enums, partitioning
    - High cardinality (>95%): Likely unique, consider unique constraints
    - Medium cardinality: Standard columns, evaluate case-by-case
    - Sampling can significantly speed up analysis on large tables

    Complexity
    ----------
    Time: O(n*m) where n=tables, m=columns, Space: O(n*m)
    """
    # Input validation
    if connection is None:
        raise TypeError("connection cannot be None")
    if tables is not None and not isinstance(tables, list):
        raise TypeError(f"tables must be list or None, got {type(tables).__name__}")
    if schema is not None and not isinstance(schema, str):
        raise TypeError(f"schema must be str or None, got {type(schema).__name__}")
    if sample_size is not None:
        if not isinstance(sample_size, int):
            raise TypeError(
                f"sample_size must be int or None, got {type(sample_size).__name__}"
            )
        if sample_size <= 0:
            raise ValueError(f"sample_size must be positive, got {sample_size}")
    if not isinstance(low_cardinality_threshold, (int, float)):
        raise TypeError(
            f"low_cardinality_threshold must be float, got {type(low_cardinality_threshold).__name__}"
        )
    if not isinstance(high_cardinality_threshold, (int, float)):
        raise TypeError(
            f"high_cardinality_threshold must be float, got {type(high_cardinality_threshold).__name__}"
        )
    if not 0 < low_cardinality_threshold < 1:
        raise ValueError(
            f"low_cardinality_threshold must be between 0 and 1, got {low_cardinality_threshold}"
        )
    if not 0 < high_cardinality_threshold <= 1:
        raise ValueError(
            f"high_cardinality_threshold must be between 0 and 1, got {high_cardinality_threshold}"
        )
    if low_cardinality_threshold >= high_cardinality_threshold:
        raise ValueError(
            "low_cardinality_threshold must be less than high_cardinality_threshold"
        )

    # Reflect metadata
    metadata = MetaData()
    metadata.reflect(bind=connection, schema=schema, only=tables)

    table_names = tables if tables else [t for t in metadata.tables.keys()]

    results = []

    for table_name in table_names:
        if table_name not in metadata.tables:
            continue

        table = metadata.tables[table_name]

        # Get total row count
        count_query = select(func.count()).select_from(table)
        if sample_size:
            count_query = count_query.limit(sample_size)

        result = connection.execute(count_query)
        total_rows = result.scalar() or 0

        if total_rows == 0:
            logger.debug(f"Table {table_name} is empty, skipping")
            continue

        for column in table.columns:
            try:
                # Skip primary keys - they're always high cardinality
                if column.primary_key:
                    continue

                # Count NULLs
                null_query = (
                    select(func.count()).select_from(table).where(column.is_(None))
                )
                if sample_size:
                    null_query = null_query.limit(sample_size)
                result = connection.execute(null_query)
                null_count = result.scalar() or 0

                # Count distinct values
                distinct_query = select(func.count(func.distinct(column))).select_from(
                    table
                )
                if sample_size:
                    distinct_query = distinct_query.limit(sample_size)
                result = connection.execute(distinct_query)
                distinct_count = result.scalar() or 0

                # Calculate cardinality ratio
                non_null_rows = total_rows - null_count
                if non_null_rows == 0:
                    continue

                cardinality_ratio = (
                    distinct_count / non_null_rows if non_null_rows > 0 else 0
                )
                null_percentage = (null_count / total_rows) * 100

                # Categorize cardinality
                if cardinality_ratio <= low_cardinality_threshold:
                    category = "low"
                    recommendations = [
                        "Consider creating an index on this column",
                        "Good candidate for ENUM type or lookup table",
                        "Suitable for partitioning key",
                    ]
                elif cardinality_ratio >= high_cardinality_threshold:
                    category = "high"
                    recommendations = [
                        "Consider unique constraint if values should be unique",
                        "Potential candidate for primary key or alternate key",
                        "Not suitable for indexing unless required for joins",
                    ]
                else:
                    category = "medium"
                    recommendations = [
                        "Standard cardinality - evaluate indexing based on query patterns",
                    ]

                # Get top values for low cardinality columns
                top_values = None
                if category == "low":
                    try:
                        top_query = (
                            select(column, func.count().label("count"))
                            .group_by(column)
                            .order_by(func.count().desc())
                            .limit(5)
                        )
                        result = connection.execute(top_query)
                        top_values = [
                            {"value": str(row[0]), "count": row[1]} for row in result
                        ]
                    except Exception as e:
                        logger.debug(
                            f"Could not get top values for {table_name}.{column.name}: {e}"
                        )

                results.append(
                    {
                        "table_name": table_name,
                        "column_name": column.name,
                        "total_rows": total_rows,
                        "distinct_values": distinct_count,
                        "cardinality_ratio": round(cardinality_ratio, 4),
                        "cardinality_category": category,
                        "null_count": null_count,
                        "null_percentage": round(null_percentage, 2),
                        "top_values": top_values,
                        "recommendations": recommendations,
                    }
                )

            except Exception as e:
                logger.warning(
                    f"Could not analyze cardinality for {table_name}.{column.name}: {e}"
                )
                continue

    # Sort by category (low first for actionable insights) then by cardinality ratio
    category_order = {"low": 0, "medium": 1, "high": 2}
    results.sort(
        key=lambda x: (
            category_order[str(x["cardinality_category"])],
            float(x["cardinality_ratio"]),  # type: ignore[arg-type]
        )
    )

    return results


__all__ = ["analyze_column_cardinality"]
