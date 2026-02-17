"""
Suggest data type optimizations for columns.

Identifies columns using inefficient data types and recommends
more appropriate types to reduce storage and improve performance.
"""

import logging
from typing import Any

from sqlalchemy import MetaData, func, select

logger = logging.getLogger(__name__)


def suggest_data_type_optimizations(
    connection: Any,
    tables: list[str] | None = None,
    schema: str | None = None,
    sample_size: int = 1000,
) -> list[dict[str, Any]]:
    """
    Suggest data type optimizations for columns.

    Analyzes actual data to identify columns using unnecessarily large
    or inappropriate data types. Provides recommendations for more
    efficient types to reduce storage and improve query performance.

    Parameters
    ----------
    connection : Any
        Database connection.
    tables : list[str] | None, optional
        Specific tables to analyze (by default None for all tables).
    schema : str | None, optional
        Schema name (by default None).
    sample_size : int, optional
        Number of rows to sample for analysis (by default 1000).

    Returns
    -------
    list[dict[str, Any]]
        List of optimization suggestions:
        - 'table_name': Table name
        - 'column_name': Column name
        - 'current_type': Current data type
        - 'issue': Description of the problem
        - 'suggested_type': Recommended data type
        - 'reasoning': Explanation for suggestion
        - 'potential_savings': Estimated storage savings
        - 'severity': 'high', 'medium', or 'low'

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If sample_size is invalid.

    Examples
    --------
    >>> from sqlalchemy import create_engine
    >>> engine = create_engine("sqlite:///:memory:")
    >>> with engine.connect() as conn:
    ...     suggestions = suggest_data_type_optimizations(conn)
    >>> suggestions[0]['severity']
    'high'

    Notes
    -----
    Common optimization patterns:
    - VARCHAR(500) with max length 20 → VARCHAR(50)
    - VARCHAR storing only numbers → INTEGER or NUMERIC
    - VARCHAR storing boolean values → BOOLEAN
    - TEXT with short content → VARCHAR
    - INTEGER for small numbers → SMALLINT or TINYINT
    - FLOAT for integer data → INTEGER

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
    if not isinstance(sample_size, int):
        raise TypeError(f"sample_size must be int, got {type(sample_size).__name__}")
    if sample_size <= 0:
        raise ValueError(f"sample_size must be positive, got {sample_size}")

    # Reflect metadata
    metadata = MetaData()
    metadata.reflect(bind=connection, schema=schema, only=tables)

    table_names = tables if tables else [t for t in metadata.tables.keys()]

    suggestions = []

    for table_name in table_names:
        if table_name not in metadata.tables:
            continue

        table = metadata.tables[table_name]

        # Get total row count
        count_query = select(func.count()).select_from(table)
        result = connection.execute(count_query)
        total_rows = result.scalar() or 0

        if total_rows == 0:
            logger.debug(f"Table {table_name} is empty, skipping")
            continue

        for column in table.columns:
            try:
                type_str = str(column.type).upper()

                # Check VARCHAR/CHAR columns
                if "VARCHAR" in type_str or "CHAR" in type_str or "TEXT" in type_str:
                    # Get max length of actual data
                    max_len_query = (
                        select(func.max(func.length(column)))
                        .select_from(table)
                        .where(column.is_not(None))
                        .limit(sample_size)
                    )
                    result = connection.execute(max_len_query)
                    actual_max_length = result.scalar() or 0

                    # Extract declared length from type
                    if "VARCHAR" in type_str and "(" in type_str:
                        declared_length = int(type_str.split("(")[1].split(")")[0])

                        # If actual max is much smaller than declared
                        if actual_max_length < declared_length * 0.25:
                            suggested_length = max(
                                actual_max_length * 2, 10
                            )  # 2x headroom, min 10
                            savings_per_row = (
                                declared_length - suggested_length
                            ) * 0.8  # Approximate
                            total_savings_mb = (savings_per_row * total_rows) / (
                                1024 * 1024
                            )

                            suggestions.append(
                                {
                                    "table_name": table_name,
                                    "column_name": column.name,
                                    "current_type": f"VARCHAR({declared_length})",
                                    "issue": f"Declared length {declared_length} but actual max is only {actual_max_length}",
                                    "suggested_type": f"VARCHAR({int(suggested_length)})",
                                    "reasoning": f"Reduce size while keeping 2x headroom. Max actual: {actual_max_length}",
                                    "potential_savings_mb": round(total_savings_mb, 2),
                                    "severity": "medium"
                                    if total_savings_mb > 10
                                    else "low",
                                }
                            )

                    # Check if numeric data stored as string
                    if actual_max_length > 0:
                        # Sample some values to check if they're numeric
                        sample_query = (
                            select(column)
                            .select_from(table)
                            .where(column.is_not(None))
                            .limit(min(100, sample_size))
                        )
                        result = connection.execute(sample_query)
                        sample_values = [row[0] for row in result if row[0]]

                        if sample_values:
                            # Check if all values are numeric
                            all_numeric = all(
                                str(val)
                                .replace("-", "")
                                .replace(".", "")
                                .replace(",", "")
                                .isdigit()
                                for val in sample_values
                            )

                            if all_numeric:
                                has_decimals = any(
                                    "." in str(val) for val in sample_values
                                )
                                suggested_type = (
                                    "NUMERIC" if has_decimals else "INTEGER"
                                )

                                suggestions.append(
                                    {
                                        "table_name": table_name,
                                        "column_name": column.name,
                                        "current_type": type_str,
                                        "issue": "Numeric data stored as string",
                                        "suggested_type": suggested_type,
                                        "reasoning": "Storing numbers as strings wastes space and prevents numeric operations",
                                        "potential_savings_mb": round(
                                            (actual_max_length * total_rows * 0.5)
                                            / (1024 * 1024),
                                            2,
                                        ),
                                        "severity": "high",
                                    }
                                )

                            # Check if boolean data stored as string
                            unique_values = set(
                                str(val).upper() for val in sample_values
                            )
                            if unique_values <= {
                                "TRUE",
                                "FALSE",
                                "T",
                                "F",
                                "YES",
                                "NO",
                                "Y",
                                "N",
                                "1",
                                "0",
                            }:
                                suggestions.append(
                                    {
                                        "table_name": table_name,
                                        "column_name": column.name,
                                        "current_type": type_str,
                                        "issue": "Boolean data stored as string",
                                        "suggested_type": "BOOLEAN",
                                        "reasoning": f"Only contains boolean values: {unique_values}",
                                        "potential_savings_mb": round(
                                            (actual_max_length * total_rows * 0.9)
                                            / (1024 * 1024),
                                            2,
                                        ),
                                        "severity": "medium",
                                    }
                                )

                # Check INTEGER columns for small value ranges
                elif "INTEGER" in type_str or "INT" in type_str:
                    # Get min/max values
                    stats_query = (
                        select(
                            func.min(column).label("min_val"),
                            func.max(column).label("max_val"),
                        )
                        .select_from(table)
                        .where(column.is_not(None))
                    )
                    result = connection.execute(stats_query)
                    stats = result.fetchone()

                    if stats and stats[0] is not None and stats[1] is not None:
                        min_val = stats[0]
                        max_val = stats[1]

                        # Check if SMALLINT would suffice
                        if "INT" in type_str and "BIGINT" not in type_str:
                            if (
                                -32768 <= min_val <= 32767
                                and -32768 <= max_val <= 32767
                            ):
                                savings_mb = round(
                                    (total_rows * 2) / (1024 * 1024), 2
                                )  # 4 bytes -> 2 bytes
                                if savings_mb > 1:
                                    suggestions.append(
                                        {
                                            "table_name": table_name,
                                            "column_name": column.name,
                                            "current_type": "INTEGER",
                                            "issue": f"Value range {min_val} to {max_val} fits in SMALLINT",
                                            "suggested_type": "SMALLINT",
                                            "reasoning": "Values fit in 2 bytes instead of 4 bytes",
                                            "potential_savings_mb": savings_mb,
                                            "severity": "low"
                                            if savings_mb < 10
                                            else "medium",
                                        }
                                    )

            except Exception as e:
                logger.debug(f"Could not analyze {table_name}.{column.name}: {e}")
                continue

    # Sort by severity and potential savings
    severity_order = {"high": 0, "medium": 1, "low": 2}
    suggestions.sort(
        key=lambda x: (severity_order[str(x["severity"])], -float(x.get("potential_savings_mb", 0)))  # type: ignore[arg-type]
    )

    return suggestions


__all__ = ["suggest_data_type_optimizations"]
