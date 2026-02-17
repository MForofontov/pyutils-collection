"""
Get storage size information for database tables.
"""

import logging
from typing import Any

from sqlalchemy import MetaData, text

logger = logging.getLogger(__name__)


def get_table_sizes(
    connection: Any,
    tables: list[str] | None = None,
    schema: str | None = None,
    include_indexes: bool = True,
) -> list[dict[str, Any]]:
    """
    Get storage size information for database tables.

    Reports disk space usage for tables and their indexes across different
    database systems (PostgreSQL, MySQL, SQLite, etc.).

    Parameters
    ----------
    connection : Any
        Database connection.
    tables : list[str] | None, optional
        Specific tables to check (by default None for all tables).
    schema : str | None, optional
        Schema name (by default None).
    include_indexes : bool, optional
        Include index sizes in results (by default True).

    Returns
    -------
    list[dict[str, Any]]
        List of tables with size information:
        - table_name: str
        - row_count: int
        - data_size_bytes: int
        - index_size_bytes: int (if include_indexes)
        - total_size_bytes: int
        - data_size_mb: float
        - total_size_mb: float

    Raises
    ------
    TypeError
        If parameters are of wrong type.

    Examples
    --------
    >>> sizes = get_table_sizes(conn, schema="public")
    >>> for table in sizes:
    ...     print(f"{table['table_name']}: {table['total_size_mb']:.2f} MB")

    Notes
    -----
    Results vary by database system. SQLite provides approximate sizes.
    Useful for capacity planning and identifying large tables.

    Complexity
    ----------
    Time: O(n) where n is tables, Space: O(n)
    """
    # Input validation
    if connection is None:
        raise TypeError("connection cannot be None")
    if tables is not None and not isinstance(tables, list):
        raise TypeError(f"tables must be list or None, got {type(tables).__name__}")
    if schema is not None and not isinstance(schema, str):
        raise TypeError(f"schema must be str or None, got {type(schema).__name__}")
    if not isinstance(include_indexes, bool):
        raise TypeError(
            f"include_indexes must be bool, got {type(include_indexes).__name__}"
        )

    # Reflect metadata to get table list
    metadata = MetaData()
    if tables:
        # Verify tables exist before reflecting
        from sqlalchemy import inspect

        inspector = inspect(connection)
        available_tables = inspector.get_table_names(schema=schema)
        existing_tables = [t for t in tables if t in available_tables]
        if existing_tables:
            metadata.reflect(bind=connection, schema=schema, only=existing_tables)
        table_names = existing_tables
    else:
        metadata.reflect(bind=connection, schema=schema)
        table_names = [t for t in metadata.tables.keys()]

    # Detect database type
    db_dialect = connection.dialect.name.lower()

    results = []

    for table_name in table_names:
        table_info = {
            "table_name": table_name,
            "row_count": 0,
            "data_size_bytes": 0,
            "index_size_bytes": 0,
            "total_size_bytes": 0,
        }

        try:
            # Get row count (database-agnostic)
            if table_name in metadata.tables:
                metadata.tables[table_name]
                count_query = text(f"SELECT COUNT(*) FROM {table_name}")
                result = connection.execute(count_query)
                table_info["row_count"] = result.scalar() or 0

            # Get size information (database-specific)
            if db_dialect == "postgresql":
                # PostgreSQL size queries
                schema_prefix = f"{schema}." if schema else ""
                full_table_name = f"{schema_prefix}{table_name}"

                size_query = text(f"""
                    SELECT 
                        pg_table_size('{full_table_name}') as data_size,
                        pg_indexes_size('{full_table_name}') as index_size,
                        pg_total_relation_size('{full_table_name}') as total_size
                """)
                result = connection.execute(size_query)
                row = result.fetchone()
                if row:
                    table_info["data_size_bytes"] = row[0] or 0
                    table_info["index_size_bytes"] = row[1] or 0
                    table_info["total_size_bytes"] = row[2] or 0

            elif db_dialect == "mysql":
                # MySQL size queries
                schema_name = schema or connection.engine.url.database
                size_query = text("""
                    SELECT 
                        data_length as data_size,
                        index_length as index_size,
                        data_length + index_length as total_size
                    FROM information_schema.tables
                    WHERE table_schema = :schema
                    AND table_name = :table
                """)
                result = connection.execute(
                    size_query, {"schema": schema_name, "table": table_name}
                )
                row = result.fetchone()
                if row:
                    table_info["data_size_bytes"] = row[0] or 0
                    table_info["index_size_bytes"] = row[1] or 0
                    table_info["total_size_bytes"] = row[2] or 0

            elif db_dialect == "sqlite":
                # SQLite - approximate size based on page count
                try:
                    page_count_query = text("PRAGMA page_count")
                    page_size_query = text("PRAGMA page_size")

                    page_count_result = connection.execute(page_count_query)
                    page_size_result = connection.execute(page_size_query)

                    page_count = page_count_result.scalar() or 0
                    page_size = page_size_result.scalar() or 0

                    # This is database-wide, not per-table
                    # Approximate by dividing by number of tables
                    table_info["total_size_bytes"] = (page_count * page_size) // len(
                        table_names
                    )
                    table_info["data_size_bytes"] = table_info["total_size_bytes"]
                except Exception as e:
                    logger.debug(f"SQLite size query failed: {e}")

            elif db_dialect == "oracle":
                # Oracle size queries
                schema_name = schema or connection.engine.url.username.upper()
                size_query = text("""
                    SELECT 
                        SUM(bytes) as total_size
                    FROM dba_segments
                    WHERE owner = :schema
                    AND segment_name = :table
                """)
                try:
                    result = connection.execute(
                        size_query, {"schema": schema_name, "table": table_name.upper()}
                    )
                    row = result.fetchone()
                    if row and row[0]:
                        table_info["total_size_bytes"] = row[0]
                        table_info["data_size_bytes"] = row[0]
                except Exception as e:
                    # Fallback to user_segments if dba_segments not accessible
                    logger.debug(
                        f"Oracle dba_segments failed, trying user_segments: {e}"
                    )
                    try:
                        size_query = text("""
                            SELECT 
                                SUM(bytes) as total_size
                            FROM user_segments
                            WHERE segment_name = :table
                        """)
                        result = connection.execute(
                            size_query, {"table": table_name.upper()}
                        )
                        row = result.fetchone()
                        if row and row[0]:
                            table_info["total_size_bytes"] = row[0]
                            table_info["data_size_bytes"] = row[0]
                    except Exception as e2:
                        logger.debug(f"Oracle user_segments failed: {e2}")

            elif db_dialect in ("mssql", "microsoft", "pyodbc"):
                # SQL Server size queries
                schema_name = schema or "dbo"
                size_query = text("""
                    SELECT 
                        SUM(a.total_pages) * 8 * 1024 as total_size,
                        SUM(a.used_pages) * 8 * 1024 as data_size,
                        (SUM(a.total_pages) - SUM(a.used_pages)) * 8 * 1024 as unused_size
                    FROM sys.tables t
                    INNER JOIN sys.indexes i ON t.object_id = i.object_id
                    INNER JOIN sys.partitions p ON i.object_id = p.object_id AND i.index_id = p.index_id
                    INNER JOIN sys.allocation_units a ON p.partition_id = a.container_id
                    INNER JOIN sys.schemas s ON t.schema_id = s.schema_id
                    WHERE t.name = :table
                    AND s.name = :schema
                    GROUP BY t.name
                """)
                result = connection.execute(
                    size_query, {"schema": schema_name, "table": table_name}
                )
                row = result.fetchone()
                if row:
                    table_info["total_size_bytes"] = row[0] or 0
                    table_info["data_size_bytes"] = row[1] or 0
                    # For SQL Server, estimate index size as difference
                    if include_indexes:
                        table_info["index_size_bytes"] = max(
                            0, (row[0] or 0) - (row[1] or 0)
                        )

            else:
                # Fallback: estimate based on row count
                estimated_bytes = int(table_info["row_count"]) * 1000  # type: ignore[call-overload]  # rough estimate
                table_info["total_size_bytes"] = estimated_bytes
                table_info["data_size_bytes"] = estimated_bytes
                logger.warning(
                    f"Size estimation not supported for {db_dialect}, using rough estimate"
                )

            # Calculate MB values
            table_info["data_size_mb"] = int(table_info["data_size_bytes"]) / (1024 * 1024)  # type: ignore[call-overload]
            table_info["total_size_mb"] = int(table_info["total_size_bytes"]) / (1024 * 1024)  # type: ignore[call-overload]

            # Remove index size if not requested
            if not include_indexes:
                del table_info["index_size_bytes"]
            else:
                table_info["index_size_mb"] = int(table_info["index_size_bytes"]) / (  # type: ignore[call-overload]
                    1024 * 1024
                )

            results.append(table_info)

        except Exception as e:
            logger.error(f"Error getting size for table {table_name}: {e}")
            results.append(table_info)

    # Sort by total size descending
    results.sort(key=lambda x: int(x["total_size_bytes"]), reverse=True)  # type: ignore[call-overload]

    return results


__all__ = ["get_table_sizes"]
