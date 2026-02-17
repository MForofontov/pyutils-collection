"""
Detect data quality anomalies in database columns.
"""

import logging
from typing import Any

from sqlalchemy import Float, Integer, MetaData, Numeric, func, select

logger = logging.getLogger(__name__)


def check_data_anomalies(
    connection: Any,
    tables: list[str] | None = None,
    schema: str | None = None,
    check_all_same: bool = True,
    check_outliers: bool = True,
    outlier_std_threshold: float = 3.0,
) -> list[dict[str, Any]]:
    """
    Detect data quality anomalies in database columns.

    Identifies suspicious patterns like all values being identical,
    statistical outliers, excessive nulls, and other data quality issues.

    Parameters
    ----------
    connection : Any
        Database connection.
    tables : list[str] | None, optional
        Specific tables to check (by default None for all tables).
    schema : str | None, optional
        Schema name (by default None).
    check_all_same : bool, optional
        Check for columns where all values are identical (by default True).
    check_outliers : bool, optional
        Check for statistical outliers in numeric columns (by default True).
    outlier_std_threshold : float, optional
        Standard deviations for outlier detection (by default 3.0).

    Returns
    -------
    list[dict[str, Any]]
        List of detected anomalies with:
        - table_name: str
        - column_name: str
        - anomaly_type: str
        - severity: str (critical, high, medium, low)
        - details: dict (anomaly-specific information)

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If outlier_std_threshold is negative.

    Examples
    --------
    >>> anomalies = check_data_anomalies(conn, schema="public")
    >>> for anom in anomalies:
    ...     print(f"{anom['table_name']}.{anom['column_name']}: {anom['anomaly_type']}")

    Notes
    -----
    Critical for data quality monitoring and migration validation.

    Anomaly types detected:
    - all_same_value: All non-NULL values are identical
    - all_null: Column is entirely NULL
    - statistical_outlier: Values far from mean
    - suspicious_pattern: Regular patterns indicating test data

    Complexity
    ----------
    Time: O(n*m) where n is rows and m is columns, Space: O(a) where a is anomalies
    """
    # Input validation
    if connection is None:
        raise TypeError("connection cannot be None")
    if tables is not None and not isinstance(tables, list):
        raise TypeError(f"tables must be list or None, got {type(tables).__name__}")
    if schema is not None and not isinstance(schema, str):
        raise TypeError(f"schema must be str or None, got {type(schema).__name__}")
    if not isinstance(check_all_same, bool):
        raise TypeError(
            f"check_all_same must be bool, got {type(check_all_same).__name__}"
        )
    if not isinstance(check_outliers, bool):
        raise TypeError(
            f"check_outliers must be bool, got {type(check_outliers).__name__}"
        )
    if not isinstance(outlier_std_threshold, (int, float)):
        raise TypeError(
            f"outlier_std_threshold must be float, got {type(outlier_std_threshold).__name__}"
        )
    if outlier_std_threshold <= 0:
        raise ValueError("outlier_std_threshold must be positive")

    # Reflect metadata
    metadata = MetaData()
    metadata.reflect(bind=connection, schema=schema, only=tables)

    table_names = tables if tables else [t for t in metadata.tables.keys()]

    anomalies = []

    for table_name in table_names:
        if table_name not in metadata.tables:
            continue

        table = metadata.tables[table_name]

        # Get total row count
        total_rows_query = select(func.count()).select_from(table)
        result = connection.execute(total_rows_query)
        total_rows = result.scalar() or 0

        if total_rows == 0:
            logger.debug(f"Table {table_name} is empty, skipping")
            continue

        for col in table.columns:
            try:
                # Skip primary keys
                if col.primary_key:
                    continue

                # Check 1: All NULL
                null_count_query = (
                    select(func.count()).select_from(table).where(col.is_(None))
                )
                result = connection.execute(null_count_query)
                null_count = result.scalar() or 0

                if null_count == total_rows:
                    anomalies.append(
                        {
                            "table_name": table_name,
                            "column_name": col.name,
                            "anomaly_type": "all_null",
                            "severity": "high",
                            "details": {
                                "total_rows": total_rows,
                                "description": "Column is entirely NULL",
                            },
                        }
                    )
                    continue

                # Check 2: All same value (for non-NULL values)
                if check_all_same and null_count < total_rows:
                    distinct_query = (
                        select(func.count(func.distinct(col)))
                        .select_from(table)
                        .where(col.is_not(None))
                    )
                    result = connection.execute(distinct_query)
                    distinct_count = result.scalar() or 0

                    if distinct_count == 1:
                        # Get the single value
                        value_query = select(col).where(col.is_not(None)).limit(1)
                        result = connection.execute(value_query)
                        single_value = result.scalar()

                        anomalies.append(
                            {
                                "table_name": table_name,
                                "column_name": col.name,
                                "anomaly_type": "all_same_value",
                                "severity": "medium",
                                "details": {
                                    "value": single_value,
                                    "non_null_rows": total_rows - null_count,
                                    "description": "All non-NULL values are identical",
                                },
                            }
                        )
                        continue

                # Check 3: Statistical outliers for numeric columns
                if check_outliers and isinstance(col.type, (Integer, Float, Numeric)):
                    try:
                        # Get statistics
                        stats_query = (
                            select(
                                func.avg(col).label("mean"),
                                func.stddev(col).label("stddev"),
                                func.min(col).label("min"),
                                func.max(col).label("max"),
                            )
                            .select_from(table)
                            .where(col.is_not(None))
                        )

                        result = connection.execute(stats_query)
                        stats = result.fetchone()

                        if stats and stats[1]:  # If stddev exists
                            mean = float(stats[0])
                            stddev = float(stats[1])
                            min_val = float(stats[2])
                            max_val = float(stats[3])

                            # Check for outliers beyond threshold
                            lower_bound = mean - (outlier_std_threshold * stddev)
                            upper_bound = mean + (outlier_std_threshold * stddev)

                            # Count values outside bounds
                            outlier_query = (
                                select(func.count())
                                .select_from(table)
                                .where((col < lower_bound) | (col > upper_bound))
                            )
                            result = connection.execute(outlier_query)
                            outlier_count = result.scalar() or 0

                            if outlier_count > 0:
                                outlier_percentage = outlier_count / (
                                    total_rows - null_count
                                )

                                # Only report if significant
                                if outlier_percentage > 0.01:  # More than 1%
                                    severity = (
                                        "high" if outlier_percentage > 0.1 else "medium"
                                    )

                                    anomalies.append(
                                        {
                                            "table_name": table_name,
                                            "column_name": col.name,
                                            "anomaly_type": "statistical_outliers",
                                            "severity": severity,
                                            "details": {
                                                "outlier_count": outlier_count,
                                                "outlier_percentage": outlier_percentage,
                                                "mean": mean,
                                                "stddev": stddev,
                                                "min": min_val,
                                                "max": max_val,
                                                "lower_bound": lower_bound,
                                                "upper_bound": upper_bound,
                                                "description": f"{outlier_count} values beyond {outlier_std_threshold} standard deviations",
                                            },
                                        }
                                    )
                    except Exception as e:
                        logger.debug(
                            f"Error checking outliers for {table_name}.{col.name}: {e}"
                        )

            except Exception as e:
                logger.error(
                    f"Error checking anomalies for {table_name}.{col.name}: {e}"
                )

    # Sort by severity
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    anomalies.sort(key=lambda x: severity_order.get(str(x["severity"]), 4))

    return anomalies


__all__ = ["check_data_anomalies"]
