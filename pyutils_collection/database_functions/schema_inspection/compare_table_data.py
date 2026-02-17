"""
Compare data between two tables for differences.
"""

import logging
from typing import Any

from sqlalchemy import MetaData, func, select, text

logger = logging.getLogger(__name__)


def compare_table_data(
    source_connection: Any,
    target_connection: Any,
    source_table: str,
    target_table: str | None = None,
    source_schema: str | None = None,
    target_schema: str | None = None,
    compare_columns: list[str] | None = None,
    sample_differences: int = 10,
) -> dict[str, Any]:
    """
    Compare data between two tables for differences.

    Identifies differences in row counts, checksums, and sample data between
    source and target tables. Useful for data migration validation.

    Parameters
    ----------
    source_connection : Any
        Source database connection.
    target_connection : Any
        Target database connection (can be same as source).
    source_table : str
        Source table name.
    target_table : str | None, optional
        Target table name (by default None, uses source_table).
    source_schema : str | None, optional
        Source schema name (by default None).
    target_schema : str | None, optional
        Target schema name (by default None).
    compare_columns : list[str] | None, optional
        Specific columns to compare (by default None for all common columns).
    sample_differences : int, optional
        Number of different rows to sample (by default 10).

    Returns
    -------
    dict[str, Any]
        Comparison results with:
        - source_count: int
        - target_count: int
        - count_match: bool
        - common_columns: list[str]
        - column_checksums: dict (column -> checksum match status)
        - sample_differences: list[dict] (if differences found)

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If source_table is empty.

    Examples
    --------
    >>> result = compare_table_data(src_conn, tgt_conn, "users")
    >>> if not result['count_match']:
    ...     print(f"Row count mismatch: {result['source_count']} vs {result['target_count']}")

    Notes
    -----
    Critical for data migration validation and replication verification.
    Checksum comparison is database-specific and may not work across different DB types.
    Large tables may take significant time to compare.

    Complexity
    ----------
    Time: O(n) where n is rows, Space: O(s) where s is sample size
    """
    # Input validation
    if source_connection is None:
        raise TypeError("source_connection cannot be None")
    if target_connection is None:
        raise TypeError("target_connection cannot be None")
    if not isinstance(source_table, str):
        raise TypeError(f"source_table must be str, got {type(source_table).__name__}")
    if not source_table.strip():
        raise ValueError("source_table cannot be empty")
    if target_table is not None and not isinstance(target_table, str):
        raise TypeError(
            f"target_table must be str or None, got {type(target_table).__name__}"
        )
    if source_schema is not None and not isinstance(source_schema, str):
        raise TypeError(
            f"source_schema must be str or None, got {type(source_schema).__name__}"
        )
    if target_schema is not None and not isinstance(target_schema, str):
        raise TypeError(
            f"target_schema must be str or None, got {type(target_schema).__name__}"
        )
    if compare_columns is not None and not isinstance(compare_columns, list):
        raise TypeError(
            f"compare_columns must be list or None, got {type(compare_columns).__name__}"
        )
    if not isinstance(sample_differences, int):
        raise TypeError(
            f"sample_differences must be int, got {type(sample_differences).__name__}"
        )
    if sample_differences < 0:
        raise ValueError("sample_differences must be non-negative")

    # Default target table to source table
    if target_table is None:
        target_table = source_table

    # Verify tables exist before reflecting
    from sqlalchemy import inspect

    source_inspector = inspect(source_connection)
    target_inspector = inspect(target_connection)

    source_tables = source_inspector.get_table_names(schema=source_schema)
    target_tables = target_inspector.get_table_names(schema=target_schema)

    if source_table not in source_tables:
        raise ValueError(f"Source table {source_table} not found")
    if target_table not in target_tables:
        raise ValueError(f"Target table {target_table} not found")

    # Reflect source and target tables
    source_metadata = MetaData()
    source_metadata.reflect(
        bind=source_connection, schema=source_schema, only=[source_table]
    )

    target_metadata = MetaData()
    target_metadata.reflect(
        bind=target_connection, schema=target_schema, only=[target_table]
    )

    if source_table not in source_metadata.tables:
        raise ValueError(f"Source table {source_table} not found in metadata")
    if target_table not in target_metadata.tables:
        raise ValueError(f"Target table {target_table} not found")

    src_table = source_metadata.tables[source_table]
    tgt_table = target_metadata.tables[target_table]

    # Find common columns
    src_columns = {col.name for col in src_table.columns}
    tgt_columns = {col.name for col in tgt_table.columns}
    common_columns = list(src_columns & tgt_columns)

    if compare_columns:
        # Validate requested columns exist
        for col in compare_columns:
            if col not in common_columns:
                raise ValueError(f"Column {col} not found in both tables")
        common_columns = compare_columns

    if not common_columns:
        raise ValueError("No common columns found between tables")

    result: dict[str, Any] = {
        "source_count": 0,
        "target_count": 0,
        "count_match": False,
        "common_columns": common_columns,
        "column_checksums": {},
        "sample_differences": [],
    }

    # Compare row counts
    try:
        src_count_query = select(func.count()).select_from(src_table)
        src_result = source_connection.execute(src_count_query)
        result["source_count"] = src_result.scalar() or 0

        tgt_count_query = select(func.count()).select_from(tgt_table)
        tgt_result = target_connection.execute(tgt_count_query)
        result["target_count"] = tgt_result.scalar() or 0

        result["count_match"] = result["source_count"] == result["target_count"]

    except Exception as e:
        logger.error(f"Error comparing row counts: {e}")
        return result

    # Compare column checksums (if possible)
    db_dialect = source_connection.dialect.name.lower()
    tgt_dialect = target_connection.dialect.name.lower()

    for col_name in common_columns:
        try:
            if db_dialect == "postgresql" and tgt_dialect == "postgresql":
                # PostgreSQL MD5 checksum
                src_checksum_query = text(f"""
                    SELECT MD5(STRING_AGG(CAST({col_name} AS TEXT), ',' ORDER BY {col_name}))
                    FROM {source_table}
                """)
                tgt_checksum_query = text(f"""
                    SELECT MD5(STRING_AGG(CAST({col_name} AS TEXT), ',' ORDER BY {col_name}))
                    FROM {target_table}
                """)

                src_checksum = source_connection.execute(src_checksum_query).scalar()
                tgt_checksum = target_connection.execute(tgt_checksum_query).scalar()

                result["column_checksums"][col_name] = {
                    "match": src_checksum == tgt_checksum,
                    "source_checksum": src_checksum,
                    "target_checksum": tgt_checksum,
                }
            elif db_dialect == "mysql" and tgt_dialect == "mysql":
                # MySQL MD5 checksum with GROUP_CONCAT
                src_checksum_query = text(f"""
                    SELECT MD5(GROUP_CONCAT(CAST({col_name} AS CHAR) ORDER BY {col_name} SEPARATOR ','))
                    FROM {source_table}
                """)
                tgt_checksum_query = text(f"""
                    SELECT MD5(GROUP_CONCAT(CAST({col_name} AS CHAR) ORDER BY {col_name} SEPARATOR ','))
                    FROM {target_table}
                """)

                src_checksum = source_connection.execute(src_checksum_query).scalar()
                tgt_checksum = target_connection.execute(tgt_checksum_query).scalar()

                result["column_checksums"][col_name] = {
                    "match": src_checksum == tgt_checksum,
                    "source_checksum": src_checksum,
                    "target_checksum": tgt_checksum,
                }
            elif db_dialect in ("mssql", "microsoft") and tgt_dialect in (
                "mssql",
                "microsoft",
            ):
                # SQL Server CHECKSUM_AGG (approximate)
                src_checksum_query = text(f"""
                    SELECT CHECKSUM_AGG(CHECKSUM({col_name}))
                    FROM {source_table}
                """)
                tgt_checksum_query = text(f"""
                    SELECT CHECKSUM_AGG(CHECKSUM({col_name}))
                    FROM {target_table}
                """)

                src_checksum = source_connection.execute(src_checksum_query).scalar()
                tgt_checksum = target_connection.execute(tgt_checksum_query).scalar()

                result["column_checksums"][col_name] = {
                    "match": src_checksum == tgt_checksum,
                    "source_checksum": src_checksum,
                    "target_checksum": tgt_checksum,
                    "note": "SQL Server CHECKSUM may have collisions",
                }
            elif db_dialect == "oracle" and tgt_dialect == "oracle":
                # Oracle STANDARD_HASH (12c+)
                try:
                    src_checksum_query = text(f"""
                        SELECT STANDARD_HASH(LISTAGG(TO_CHAR({col_name}), ',') WITHIN GROUP (ORDER BY {col_name}), 'MD5')
                        FROM {source_table}
                    """)
                    tgt_checksum_query = text(f"""
                        SELECT STANDARD_HASH(LISTAGG(TO_CHAR({col_name}), ',') WITHIN GROUP (ORDER BY {col_name}), 'MD5')
                        FROM {target_table}
                    """)

                    src_checksum = source_connection.execute(
                        src_checksum_query
                    ).scalar()
                    tgt_checksum = target_connection.execute(
                        tgt_checksum_query
                    ).scalar()

                    result["column_checksums"][col_name] = {
                        "match": src_checksum == tgt_checksum,
                        "source_checksum": src_checksum,
                        "target_checksum": tgt_checksum,
                    }
                except Exception as oracle_err:
                    # Fallback for older Oracle versions
                    logger.debug(f"Oracle STANDARD_HASH failed: {oracle_err}")
                    result["column_checksums"][col_name] = {
                        "match": None,
                        "note": "Oracle checksum requires 12c+ with STANDARD_HASH",
                    }
            else:
                # Different database types or unsupported
                result["column_checksums"][col_name] = {
                    "match": None,
                    "note": f"Checksum comparison between {db_dialect} and {tgt_dialect} not supported",
                }

        except Exception as e:
            logger.debug(f"Error comparing checksums for {col_name}: {e}")
            result["column_checksums"][col_name] = {
                "match": None,
                "error": str(e),
            }

    # If counts match and all checksums match, we're done
    all_checksums_match = all(
        v.get("match")
        for v in result["column_checksums"].values()
        if v.get("match") is not None
    )

    if result["count_match"] and all_checksums_match:
        logger.info("Tables match exactly")
        return result

    # Sample differences (if primary key exists)
    try:
        src_pk_cols = [col for col in src_table.primary_key.columns]
        tgt_pk_cols = [col for col in tgt_table.primary_key.columns]

        if src_pk_cols and tgt_pk_cols and len(src_pk_cols) == len(tgt_pk_cols):
            # Get sample IDs from source not in target
            src_pk = src_pk_cols[0]
            tgt_pk = tgt_pk_cols[0]

            # Get sample source IDs
            src_ids_query = select(src_pk).limit(sample_differences * 2)
            src_ids_result = source_connection.execute(src_ids_query)
            src_ids = [row[0] for row in src_ids_result]

            # Check which exist in target
            for src_id in src_ids[:sample_differences]:
                tgt_exists_query = (
                    select(func.count()).select_from(tgt_table).where(tgt_pk == src_id)
                )
                tgt_exists = target_connection.execute(tgt_exists_query).scalar()

                if not tgt_exists:
                    result["sample_differences"].append(
                        {
                            "type": "missing_in_target",
                            "primary_key": src_id,
                        }
                    )

    except Exception as e:
        logger.debug(f"Error sampling differences: {e}")

    return result


__all__ = ["compare_table_data"]
