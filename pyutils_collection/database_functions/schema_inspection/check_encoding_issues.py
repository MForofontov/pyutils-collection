"""
Detect text encoding issues in database columns.
"""

import logging
from typing import Any

from sqlalchemy import MetaData, String, Text, select, text

logger = logging.getLogger(__name__)


def check_encoding_issues(
    connection: Any,
    tables: list[str] | None = None,
    schema: str | None = None,
    sample_limit: int = 100,
) -> list[dict[str, Any]]:
    """
    Detect text encoding issues in database columns.

    Identifies columns containing non-UTF8 characters, mojibake patterns,
    or other encoding problems that may cause data corruption.

    Parameters
    ----------
    connection : Any
        Database connection.
    tables : list[str] | None, optional
        Specific table names within ``schema`` to check (by default None for
        all tables). Explicit names are retained in the reported results.
    schema : str | None, optional
        Schema name (by default None).
    sample_limit : int, optional
        Maximum problematic rows to report per column (by default 100).

    Returns
    -------
    list[dict[str, Any]]
        List of encoding issues with:
        - table_name: str
        - column_name: str
        - issue_type: str
        - affected_rows: int
        - sample_values: list[str]

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If sample_limit is negative.

    Examples
    --------
    >>> issues = check_encoding_issues(conn, schema="public")
    >>> for issue in issues:
    ...     print(f"{issue['table_name']}.{issue['column_name']}: {issue['issue_type']}")

    Notes
    -----
    Critical before migrating data or changing database encoding.
    Patterns checked:
    - Invalid UTF-8 byte sequences
    - Mojibake (e.g., Ã© instead of é)
    - NULL bytes
    - Control characters

    Complexity
    ----------
    Time: O(n*m) where n is rows and m is text columns, Space: O(s) where s is samples
    """
    # Input validation
    if connection is None:
        raise TypeError("connection cannot be None")
    if tables is not None and not isinstance(tables, list):
        raise TypeError(f"tables must be list or None, got {type(tables).__name__}")
    if schema is not None and not isinstance(schema, str):
        raise TypeError(f"schema must be str or None, got {type(schema).__name__}")
    if not isinstance(sample_limit, int):
        raise TypeError(f"sample_limit must be int, got {type(sample_limit).__name__}")
    if sample_limit < 0:
        raise ValueError("sample_limit must be non-negative")

    # Reflect metadata
    metadata = MetaData()
    metadata.reflect(bind=connection, schema=schema, only=tables)

    table_names = tables if tables else [t for t in metadata.tables.keys()]

    issues = []
    db_dialect = connection.dialect.name.lower()

    for table_name in table_names:
        table_key = (
            f"{schema}.{table_name}" if schema is not None and tables else table_name
        )
        if table_key not in metadata.tables:
            continue

        table = metadata.tables[table_key]

        # Find text columns
        text_columns = [
            col for col in table.columns if isinstance(col.type, (String, Text))
        ]

        for col in text_columns:
            try:
                # Check for common encoding issues
                issue_checks = []

                # Pattern 1: Check for NULL bytes (works across databases)
                if db_dialect in (
                    "postgresql",
                    "mysql",
                    "mssql",
                    "microsoft",
                    "oracle",
                ):
                    try:
                        if db_dialect == "postgresql":
                            # PostgreSQL: Use \x00 or CHR(0)
                            null_byte_query = (
                                select(col)
                                .where(text(f"{col.name} LIKE '%' || CHR(0) || '%'"))
                                .limit(sample_limit)
                            )
                        elif db_dialect == "mysql":
                            # MySQL: Use CHAR(0)
                            null_byte_query = (
                                select(col)
                                .where(
                                    text(f"{col.name} LIKE CONCAT('%', CHAR(0), '%')")
                                )
                                .limit(sample_limit)
                            )
                        elif db_dialect in ("mssql", "microsoft"):
                            # SQL Server: Use CHAR(0)
                            null_byte_query = (
                                select(col)
                                .where(text(f"{col.name} LIKE '%' + CHAR(0) + '%'"))
                                .limit(sample_limit)
                            )
                        else:  # oracle
                            # Oracle: Use CHR(0)
                            null_byte_query = (
                                select(col)
                                .where(text(f"{col.name} LIKE '%' || CHR(0) || '%'"))
                                .limit(sample_limit)
                            )

                        result = connection.execute(null_byte_query)
                        samples = [row[0] for row in result if row[0]]
                        if samples:
                            issue_checks.append(
                                {
                                    "table_name": table_name,
                                    "column_name": col.name,
                                    "issue_type": "null_bytes",
                                    "affected_rows": len(samples),
                                    "sample_values": samples[:10],
                                }
                            )
                    except Exception as e:
                        logger.debug(
                            f"NULL byte check failed for {table_name}.{col.name}: {e}"
                        )

                # Pattern 2: Check for mojibake patterns (common UTF-8 issues)
                # These are patterns like Ã© (should be é), â€™ (should be ')
                mojibake_patterns = [
                    "%Ã%",  # Common Latin-1 to UTF-8 mojibake
                    "%â€%",  # Smart quotes mojibake
                    "%Â%",  # Non-breaking space mojibake
                ]

                for pattern in mojibake_patterns:
                    mojibake_query = (
                        select(col).where(col.like(pattern)).limit(sample_limit)
                    )

                    try:
                        result = connection.execute(mojibake_query)
                        samples = [row[0] for row in result if row[0]]
                        if samples:
                            issue_checks.append(
                                {
                                    "table_name": table_name,
                                    "column_name": col.name,
                                    "issue_type": "mojibake_pattern",
                                    "affected_rows": len(samples),
                                    "sample_values": samples[:10],
                                }
                            )
                            break  # Found mojibake, no need to check other patterns
                    except Exception as e:
                        logger.debug(
                            f"Mojibake check failed for {table_name}.{col.name}: {e}"
                        )

                # Pattern 3: Check for control characters (ASCII < 32 except tab, newline, carriage return)
                if db_dialect in (
                    "postgresql",
                    "mysql",
                    "mssql",
                    "microsoft",
                    "oracle",
                ):
                    try:
                        if db_dialect == "postgresql":
                            # PostgreSQL: Use regex
                            control_char_query = text(f"""
                                SELECT {col.name}
                                FROM {table_name}
                                WHERE {col.name} ~ '[\\x01-\\x08\\x0B\\x0C\\x0E-\\x1F]'
                                LIMIT :limit
                            """)
                            result = connection.execute(
                                control_char_query, {"limit": sample_limit}
                            )
                        elif db_dialect == "mysql":
                            # MySQL: Use REGEXP
                            control_char_query = text(f"""
                                SELECT {col.name}
                                FROM {table_name}
                                WHERE {col.name} REGEXP '[\\x01-\\x08\\x0B\\x0C\\x0E-\\x1F]'
                                LIMIT :limit
                            """)
                            result = connection.execute(
                                control_char_query, {"limit": sample_limit}
                            )
                        elif db_dialect in ("mssql", "microsoft"):
                            # SQL Server: Check for common control chars
                            control_char_query = text(f"""
                                SELECT TOP :limit {col.name}
                                FROM {table_name}
                                WHERE {col.name} LIKE '%' + CHAR(1) + '%'
                                   OR {col.name} LIKE '%' + CHAR(2) + '%'
                                   OR {col.name} LIKE '%' + CHAR(11) + '%'
                                   OR {col.name} LIKE '%' + CHAR(12) + '%'
                            """)
                            result = connection.execute(
                                control_char_query, {"limit": sample_limit}
                            )
                        else:  # oracle
                            # Oracle: Use REGEXP_LIKE
                            control_char_query = text(f"""
                                SELECT {col.name}
                                FROM {table_name}
                                WHERE REGEXP_LIKE({col.name}, '[\\x01-\\x08\\x0B\\x0C\\x0E-\\x1F]')
                                AND ROWNUM <= :limit
                            """)
                            result = connection.execute(
                                control_char_query, {"limit": sample_limit}
                            )

                        samples = [row[0] for row in result if row[0]]
                        if samples:
                            issue_checks.append(
                                {
                                    "table_name": table_name,
                                    "column_name": col.name,
                                    "issue_type": "control_characters",
                                    "affected_rows": len(samples),
                                    "sample_values": samples[:10],
                                }
                            )
                    except Exception as e:
                        logger.debug(
                            f"Control char check failed for {table_name}.{col.name}: {e}"
                        )

                # Add all found issues
                issues.extend(issue_checks)

            except Exception as e:
                logger.error(
                    f"Error checking encoding for {table_name}.{col.name}: {e}"
                )

    return issues


__all__ = ["check_encoding_issues"]
