"""
Find duplicate and redundant indexes for optimization.
"""

import logging
from typing import Any

from sqlalchemy import inspect

logger = logging.getLogger(__name__)


def find_duplicate_indexes(
    connection: Any,
    schema: str | None = None,
) -> dict[str, Any]:
    """
    Find duplicate and redundant indexes across tables.

    Identifies exact duplicates and left-prefix redundancies. Useful for
    database optimization and reducing index maintenance overhead.

    Parameters
    ----------
    connection : Any
        Database connection.
    schema : str | None, optional
        Schema name to analyze (by default None).

    Returns
    -------
    dict[str, Any]
        Dictionary with:
        - 'exact_duplicates': List of exact duplicate index groups
        - 'redundant': List of redundant indexes (prefix of another)
        - 'summary': Dict with count statistics

    Raises
    ------
    TypeError
        If parameters are of wrong type.

    Examples
    --------
    >>> result = find_duplicate_indexes(conn)
    >>> for dup_group in result['exact_duplicates']:
    ...     print(f"Duplicates: {[idx['name'] for idx in dup_group]}")
    ...     print(f"Consider dropping all but one")

    Notes
    -----
    Removing unnecessary indexes improves write performance and reduces
    storage. Always verify with query analysis before dropping.

    Complexity
    ----------
    Time: O(n^2) where n is number of indexes, Space: O(n)
    """
    # Input validation
    if connection is None:
        raise TypeError("connection cannot be None")
    if schema is not None and not isinstance(schema, str):
        raise TypeError(f"schema must be str or None, got {type(schema).__name__}")

    inspector = inspect(connection)
    tables = inspector.get_table_names(schema=schema)

    all_indexes: list[dict[str, Any]] = []

    # Collect all indexes with their details
    for table in tables:
        indexes = inspector.get_indexes(table, schema=schema)
        for idx in indexes:
            all_indexes.append(
                {
                    "table": table,
                    "name": idx.get("name", "unnamed"),
                    "columns": tuple(idx.get("column_names", [])),
                    "unique": idx.get("unique", False),
                }
            )

    # Find exact duplicates (same columns, same order)
    exact_duplicates: list[list[dict[str, Any]]] = []
    seen_combinations: dict[tuple[Any, ...], Any] = {}

    for idx in all_indexes:
        key = (idx["table"], idx["columns"], idx["unique"])
        if key in seen_combinations:
            # Found duplicate
            existing_group = seen_combinations[key]
            if isinstance(existing_group, list):
                existing_group.append(idx)
            else:
                duplicate_group = [existing_group, idx]
                exact_duplicates.append(duplicate_group)
                seen_combinations[key] = duplicate_group
        else:
            seen_combinations[key] = idx

    # Find redundant indexes (one is prefix of another)
    redundant: list[dict[str, Any]] = []

    for i, idx1 in enumerate(all_indexes):
        for idx2 in all_indexes[i + 1 :]:
            # Only compare indexes on same table
            if idx1["table"] != idx2["table"]:
                continue

            cols1 = idx1["columns"]
            cols2 = idx2["columns"]

            # Check if one is prefix of another
            if cols1 != cols2:
                if tuple(cols2[: len(cols1)]) == cols1:
                    redundant.append(
                        {
                            "redundant_index": idx1["name"],
                            "covers_by": idx2["name"],
                            "table": idx1["table"],
                            "redundant_columns": list(cols1),
                            "covering_columns": list(cols2),
                            "reason": f"Index {idx1['name']} is redundant - {idx2['name']} starts with same columns",
                        }
                    )
                elif tuple(cols1[: len(cols2)]) == cols2:
                    redundant.append(
                        {
                            "redundant_index": idx2["name"],
                            "covers_by": idx1["name"],
                            "table": idx2["table"],
                            "redundant_columns": list(cols2),
                            "covering_columns": list(cols1),
                            "reason": f"Index {idx2['name']} is redundant - {idx1['name']} starts with same columns",
                        }
                    )

    return {
        "exact_duplicates": exact_duplicates,
        "redundant": redundant,
        "summary": {
            "total_indexes": len(all_indexes),
            "duplicate_groups": len(exact_duplicates),
            "redundant_count": len(redundant),
        },
    }


__all__ = ["find_duplicate_indexes"]
