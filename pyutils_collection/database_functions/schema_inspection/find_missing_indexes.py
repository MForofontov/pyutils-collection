"""
Suggest missing indexes based on foreign keys and common patterns.
"""

import logging
from typing import Any

from sqlalchemy import MetaData

logger = logging.getLogger(__name__)


def find_missing_indexes(
    connection: Any,
    tables: list[str] | None = None,
    schema: str | None = None,
    check_foreign_keys: bool = True,
    check_nullable_columns: bool = False,
) -> list[dict[str, Any]]:
    """
    Suggest missing indexes based on foreign keys and common patterns.

    Identifies columns that should have indexes but don't, particularly
    foreign key columns and frequently queried columns.

    Parameters
    ----------
    connection : Any
        Database connection.
    tables : list[str] | None, optional
        Specific tables to check (by default None for all tables).
    schema : str | None, optional
        Schema name (by default None).
    check_foreign_keys : bool, optional
        Check if foreign key columns have indexes (by default True).
    check_nullable_columns : bool, optional
        Check nullable columns for potential indexes (by default False).

    Returns
    -------
    list[dict[str, Any]]
        List of missing index recommendations with:
        - table_name: str
        - column_name: str
        - reason: str (why index is recommended)
        - priority: str (high, medium, low)
        - estimated_benefit: str (description)

    Raises
    ------
    TypeError
        If parameters are of wrong type.

    Examples
    --------
    >>> missing = find_missing_indexes(conn, schema="public")
    >>> for idx in missing:
    ...     print(f"Add index on {idx['table_name']}.{idx['column_name']}: {idx['reason']}")

    Notes
    -----
    Critical for query performance optimization.
    Foreign keys without indexes can cause significant performance issues
    on DELETE and UPDATE operations.

    Recommendations should be validated with query patterns before implementation.

    Complexity
    ----------
    Time: O(n*m) where n is tables and m is columns/FKs, Space: O(r) where r is recommendations
    """
    # Input validation
    if connection is None:
        raise TypeError("connection cannot be None")
    if tables is not None and not isinstance(tables, list):
        raise TypeError(f"tables must be list or None, got {type(tables).__name__}")
    if schema is not None and not isinstance(schema, str):
        raise TypeError(f"schema must be str or None, got {type(schema).__name__}")
    if not isinstance(check_foreign_keys, bool):
        raise TypeError(
            f"check_foreign_keys must be bool, got {type(check_foreign_keys).__name__}"
        )
    if not isinstance(check_nullable_columns, bool):
        raise TypeError(
            f"check_nullable_columns must be bool, got {type(check_nullable_columns).__name__}"
        )

    # Reflect metadata
    from sqlalchemy import inspect

    metadata = MetaData()
    inspector = inspect(connection)
    if tables:
        metadata.reflect(bind=connection, schema=schema, only=tables)
    else:
        metadata.reflect(bind=connection, schema=schema)

    table_names = tables if tables else inspector.get_table_names(schema=schema)

    recommendations = []

    for table_name in table_names:
        table_key = f"{schema}.{table_name}" if schema is not None else table_name
        if table_key not in metadata.tables:
            continue

        table = metadata.tables[table_key]

        # Get existing indexes
        try:
            indexes = inspector.get_indexes(table_name, schema=schema)
            indexed_columns = set()
            for idx in indexes:
                # Handle both single and multi-column indexes
                if idx.get("column_names"):
                    # First column of index
                    indexed_columns.add(idx["column_names"][0])

            # Also consider primary key as indexed
            for col in table.primary_key.columns:
                indexed_columns.add(col.name)

        except Exception as e:
            logger.error(f"Error getting indexes for {table_name}: {e}")
            continue

        # Check foreign keys for missing indexes
        if check_foreign_keys:
            try:
                foreign_keys = inspector.get_foreign_keys(table_name, schema=schema)

                for fk in foreign_keys:
                    constrained_columns = fk.get("constrained_columns", [])

                    for col_name in constrained_columns:
                        if col_name not in indexed_columns:
                            recommendations.append(
                                {
                                    "table_name": table_name,
                                    "column_name": col_name,
                                    "reason": f"Foreign key to {fk.get('referred_table', 'unknown')}",
                                    "priority": "high",
                                    "estimated_benefit": "Improves JOIN performance and DELETE/UPDATE on referenced table",
                                }
                            )

            except Exception as e:
                logger.error(f"Error checking foreign keys for {table_name}: {e}")

        # Check nullable columns (optional - can indicate filtering)
        if check_nullable_columns:
            for col in table.columns:
                if (
                    col.name not in indexed_columns
                    and col.nullable
                    and not col.primary_key
                ):
                    # Nullable columns are often used in WHERE clauses (IS NULL, IS NOT NULL)
                    recommendations.append(
                        {
                            "table_name": table_name,
                            "column_name": col.name,
                            "reason": "Nullable column - may be used for filtering",
                            "priority": "low",
                            "estimated_benefit": "May improve WHERE IS NULL/IS NOT NULL queries",
                        }
                    )

    # Sort by priority (high first)
    priority_order = {"high": 0, "medium": 1, "low": 2}
    recommendations.sort(key=lambda x: priority_order.get(x["priority"], 3))

    return recommendations


__all__ = ["find_missing_indexes"]
