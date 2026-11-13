"""
Check health of sequences and auto-increment columns.

Identifies sequences approaching their maximum values to prevent
ID exhaustion failures in production.
"""

import logging
from typing import Any

from sqlalchemy import MetaData, func, inspect, select

logger = logging.getLogger(__name__)


def check_sequence_health(
    connection: Any,
    tables: list[str] | None = None,
    schema: str | None = None,
    warn_percentage: float = 80.0,
) -> list[dict[str, Any]]:
    """
    Check health of sequences and auto-increment columns.

    Identifies sequences that are approaching their maximum values,
    which could cause INSERT failures. Critical for preventing
    production incidents with high-volume tables.

    Parameters
    ----------
    connection : Any
        Database connection.
    tables : list[str] | None, optional
        Specific tables to check (by default None for all tables).
    schema : str | None, optional
        Schema name (by default None).
    warn_percentage : float, optional
        Warn when sequence usage exceeds this percentage (by default 80.0).

    Returns
    -------
    list[dict[str, Any]]
        List of sequence health information:
        - 'table_name': Table name
        - 'column_name': Column name
        - 'current_value': Current sequence value
        - 'max_value': Maximum possible value
        - 'usage_percentage': Percentage used
        - 'remaining_values': Number of values remaining
        - 'severity': 'critical' (>95%), 'high' (>90%), 'medium' (>80%), 'low' (<80%)
        - 'data_type': Column data type
        - 'is_bigint': Whether column is BIGINT
        - 'recommendation': Suggested action

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If warn_percentage is out of range.

    Examples
    --------
    >>> from sqlalchemy import create_engine
    >>> engine = create_engine("postgresql://user:pass@localhost/db")
    >>> with engine.connect() as conn:
    ...     health = check_sequence_health(conn, warn_percentage=80.0)
    >>> health[0]['severity']
    'medium'

    Notes
    -----
    - INTEGER max: 2,147,483,647 (2^31 - 1)
    - BIGINT max: 9,223,372,036,854,775,807 (2^63 - 1)
    - Some databases use SERIAL/BIGSERIAL which are aliases
    - SQLite auto-increment uses ROWID (different mechanism)

    Complexity
    ----------
    Time: O(n) where n is number of tables, Space: O(n)
    """
    # Input validation
    if connection is None:
        raise TypeError("connection cannot be None")
    if tables is not None and not isinstance(tables, list):
        raise TypeError(f"tables must be list or None, got {type(tables).__name__}")
    if schema is not None and not isinstance(schema, str):
        raise TypeError(f"schema must be str or None, got {type(schema).__name__}")
    if not isinstance(warn_percentage, (int, float)):
        raise TypeError(
            f"warn_percentage must be float, got {type(warn_percentage).__name__}"
        )
    if not 0 < warn_percentage <= 100:
        raise ValueError(
            f"warn_percentage must be between 0 and 100, got {warn_percentage}"
        )

    # Get database dialect
    connection.dialect.name.lower()

    # Reflect metadata
    metadata = MetaData()
    if tables:
        inspector = inspect(connection)
        available_tables = inspector.get_table_names(schema=schema)
        existing_tables = [t for t in tables if t in available_tables]
        if existing_tables:
            metadata.reflect(bind=connection, schema=schema, only=existing_tables)
        table_names = existing_tables
    else:
        metadata.reflect(bind=connection, schema=schema)
        table_names = [t for t in metadata.tables.keys()]

    results = []

    for table_name in table_names:
        table_key = (
            f"{schema}.{table_name}" if schema is not None and tables else table_name
        )
        if table_key not in metadata.tables:
            continue

        table = metadata.tables[table_key]

        # Find auto-increment/serial columns
        for column in table.columns:
            # Check if column has autoincrement
            if not column.autoincrement:
                continue

            # Determine max value based on data type
            type_name = str(column.type).upper()
            is_bigint = "BIGINT" in type_name or "INT8" in type_name

            if is_bigint:
                max_value = 9223372036854775807  # 2^63 - 1
            elif "INT" in type_name:
                max_value = 2147483647  # 2^31 - 1
            else:
                # Non-integer auto-increment (rare), skip
                logger.debug(
                    f"Skipping non-integer auto-increment column: {table_name}.{column.name}"
                )
                continue

            try:
                # Get current maximum value in the column
                max_query = select(func.max(column)).select_from(table)
                result = connection.execute(max_query)
                current_value = result.scalar()

                if current_value is None:
                    current_value = 0

                # Calculate usage
                usage_percentage = (current_value / max_value) * 100
                remaining_values = max_value - current_value

                # Determine severity
                if usage_percentage >= 95:
                    severity = "critical"
                    recommendation = f"URGENT: Migrate to BIGINT immediately! Only {remaining_values:,} IDs remaining."
                elif usage_percentage >= 90:
                    severity = "high"
                    recommendation = f"Plan migration to BIGINT soon. {remaining_values:,} IDs remaining."
                elif usage_percentage >= warn_percentage:
                    severity = "medium"
                    recommendation = (
                        f"Monitor closely. {remaining_values:,} IDs remaining."
                    )
                else:
                    severity = "low"
                    recommendation = f"Healthy. {remaining_values:,} IDs remaining."

                # Only include if above threshold or if critical info
                if usage_percentage >= warn_percentage or severity in [
                    "critical",
                    "high",
                ]:
                    results.append(
                        {
                            "table_name": table_name,
                            "column_name": column.name,
                            "current_value": current_value,
                            "max_value": max_value,
                            "usage_percentage": round(usage_percentage, 2),
                            "remaining_values": remaining_values,
                            "severity": severity,
                            "data_type": type_name,
                            "is_bigint": is_bigint,
                            "recommendation": recommendation,
                        }
                    )

            except Exception as e:
                logger.warning(
                    f"Could not check sequence for {table_name}.{column.name}: {e}"
                )
                continue

    # Sort by severity (critical first) then usage percentage
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    results.sort(key=lambda x: (severity_order[x["severity"]], -x["usage_percentage"]))

    return results


__all__ = ["check_sequence_health"]
