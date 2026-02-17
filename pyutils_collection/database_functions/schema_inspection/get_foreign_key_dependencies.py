"""
Get table dependency order based on foreign key relationships.
"""

import logging
from typing import Any

from sqlalchemy import inspect

logger = logging.getLogger(__name__)


def get_foreign_key_dependencies(
    connection: Any,
    schema: str | None = None,
) -> dict[str, Any]:
    """
    Get table dependency graph based on foreign key relationships.

    Returns tables in safe deletion/truncation order (dependencies first).
    Useful for cleanup scripts, test fixtures, and data migration.

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
        - 'ordered_tables': List of tables in safe drop order
        - 'dependencies': Dict of table -> list of tables it depends on
        - 'dependents': Dict of table -> list of tables that depend on it
        - 'circular': List of tables involved in circular dependencies

    Raises
    ------
    TypeError
        If parameters are of wrong type.

    Examples
    --------
    >>> deps = get_foreign_key_dependencies(conn)
    >>> # Safe order to drop/truncate tables
    >>> for table in reversed(deps['ordered_tables']):
    ...     conn.execute(f"DELETE FROM {table}")

    Notes
    -----
    Critical for avoiding FK constraint violations during cleanup.
    Detects circular dependencies that require special handling.

    Complexity
    ----------
    Time: O(n^2) where n is number of tables, Space: O(n^2)
    """
    # Input validation
    if connection is None:
        raise TypeError("connection cannot be None")
    if schema is not None and not isinstance(schema, str):
        raise TypeError(f"schema must be str or None, got {type(schema).__name__}")

    inspector = inspect(connection)
    tables = inspector.get_table_names(schema=schema)

    # Build dependency graph
    dependencies: dict[str, set[str]] = {table: set() for table in tables}
    dependents: dict[str, set[str]] = {table: set() for table in tables}

    for table in tables:
        fks = inspector.get_foreign_keys(table, schema=schema)
        for fk in fks:
            referred_table = fk.get("referred_table")
            if referred_table and referred_table in tables:
                dependencies[table].add(referred_table)
                dependents[referred_table].add(table)

    # Topological sort to get safe order
    ordered: list[str] = []
    visited: set[str] = set()
    temp_visited: set[str] = set()
    circular: set[str] = set()

    def visit(table: str) -> None:
        if table in temp_visited:
            # Circular dependency detected
            circular.add(table)
            return
        if table in visited:
            return

        temp_visited.add(table)

        for dep in dependencies[table]:
            visit(dep)

        temp_visited.remove(table)
        visited.add(table)
        ordered.append(table)

    for table in tables:
        if table not in visited:
            visit(table)

    return {
        "ordered_tables": ordered,
        "dependencies": {k: list(v) for k, v in dependencies.items()},
        "dependents": {k: list(v) for k, v in dependents.items()},
        "circular": list(circular),
    }


__all__ = ["get_foreign_key_dependencies"]
