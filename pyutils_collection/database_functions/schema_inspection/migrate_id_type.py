"""
Migrate ID column type in a database table while maintaining referential integrity.

This module provides functionality to convert ID columns from one type to another
(e.g., UUID v4 to UUID v7, integer to UUID, string to UUID, etc.) while automatically
handling all foreign key relationships.
"""

import logging
import uuid
from collections.abc import Callable, Generator
from contextlib import contextmanager
from typing import Any

from sqlalchemy import MetaData, inspect, text
from sqlalchemy.engine import Connection, Engine
from sqlalchemy.exc import SQLAlchemyError


def migrate_id_type(
    engine: Engine,
    table_name: str,
    id_generator: Callable[[], Any],
    id_column: str = "id",
    batch_size: int = 1000,
    value_converter: Callable[[Any], str] | None = None,
    logger: logging.Logger | None = None,
) -> dict[str, Any]:
    """
    Migrate ID column type while maintaining referential integrity.

    This function converts IDs in a table from one type to another (e.g., UUID v4 to v7,
    integer to UUID, string to UUID) and automatically updates all foreign key relationships
    throughout the database.

    Parameters
    ----------
    engine : Engine
        SQLAlchemy engine connected to the database.
    table_name : str
        Name of the table containing the ID column to migrate.
    id_column : str, optional
        Name of the ID column to migrate (by default "id").
    id_generator : Callable[[], Any]
        Function to generate new ID values (e.g., uuid.uuid4, uuid7, lambda: str(uuid.uuid4())).
    batch_size : int, optional
        Number of records to process in each batch (by default 1000).
    value_converter : Callable[[Any], str] | None, optional
        Optional function to convert generated ID to string for SQL operations.
        If None, uses str() (by default None).
    logger : logging.Logger | None, optional
        Logger instance for progress tracking (by default None).

    Returns
    -------
    dict[str, Any]
        Migration summary containing:
        - rows_migrated: Number of rows processed in main table
        - fk_relationships_updated: Total number of foreign key rows updated
        - tables_affected: List of table names that were updated
        - rows_per_table: Dictionary mapping table names to number of rows updated
        - id_mapping: Dictionary mapping old IDs to new IDs

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If parameters have invalid values or schema verification fails.
    SQLAlchemyError
        If database operations fail.

    Examples
    --------
    >>> from sqlalchemy import create_engine
    >>> import uuid
    >>> engine = create_engine("sqlite:///:memory:")
    >>>
    >>> # Example 1: Migrate UUID v4 to v7
    >>> def generate_uuid7():
    ...     from uuid6 import uuid7
    ...     return uuid7()
    >>> result = migrate_id_type(
    ...     engine,
    ...     "users",
    ...     id_generator=generate_uuid7,
    ...     batch_size=1000
    ... )
    >>> result['rows_migrated']
    100
    >>>
    >>> # Example 2: Migrate integer IDs to UUID strings
    >>> result = migrate_id_type(
    ...     engine,
    ...     "products",
    ...     id_column="product_id",
    ...     id_generator=lambda: str(uuid.uuid4())
    ... )
    >>>
    >>> # Example 3: Custom value converter for integer IDs
    >>> result = migrate_id_type(
    ...     engine,
    ...     "orders",
    ...     id_generator=lambda: random.randint(100000, 999999),
    ...     value_converter=str
    ... )

    Notes
    -----
    - **Schema Migration First**: Ensure database schema changes (column type modifications)
      are applied via framework migrations (Alembic, Django, etc.) before running this function
    - **Atomic Operation**: Uses transactions to ensure data consistency
    - **Foreign Keys**: Automatically discovers and updates all FK relationships
    - **Batch Processing**: Handles large datasets efficiently with configurable batch size
    - **Constraint Handling**: Temporarily disables FK constraints during migration
    - **Irreversible**: Original IDs cannot be recovered after migration completes

    Migration Process:
    1. Discover all foreign key relationships
    2. Create ID mapping (old -> new)
    3. Update main table with new IDs
    4. Update all referencing tables with new IDs
    5. Commit transaction and re-enable FK constraints

    Common Use Cases:
    - UUID v4 -> UUID v7 (time-ordered UUIDs)
    - Integer -> UUID (for distributed systems)
    - String -> UUID (standardization)
    - UUID -> String (compatibility)
    - Integer32 -> Integer64 (scaling)

    Complexity
    ----------
    Time: O(n * m) where n is number of rows, m is number of FK relationships
    Space: O(n) for ID mapping storage
    """
    # Input validation
    if not isinstance(engine, Engine):
        raise TypeError(
            f"engine must be an SQLAlchemy Engine, got {type(engine).__name__}"
        )
    if not isinstance(table_name, str):
        raise TypeError(f"table_name must be a string, got {type(table_name).__name__}")
    if not isinstance(id_column, str):
        raise TypeError(f"id_column must be a string, got {type(id_column).__name__}")
    if not callable(id_generator):
        raise TypeError("id_generator must be callable")
    if not isinstance(batch_size, int):
        raise TypeError(
            f"batch_size must be an integer, got {type(batch_size).__name__}"
        )
    if value_converter is not None and not callable(value_converter):
        raise TypeError("value_converter must be callable or None")
    if not isinstance(logger, (logging.Logger, type(None))):
        raise TypeError("logger must be a Logger instance or None")

    if not table_name:
        raise ValueError("table_name cannot be empty")
    if not id_column:
        raise ValueError("id_column cannot be empty")
    if batch_size <= 0:
        raise ValueError(f"batch_size must be positive, got {batch_size}")

    # Set default value converter
    if value_converter is None:
        value_converter = str

    # Initialize logger
    if logger is None:
        logger = logging.getLogger(__name__)

    # Initialize result tracking
    result: dict[str, Any] = {
        "rows_migrated": 0,
        "fk_relationships_updated": 0,
        "tables_affected": [],
        "rows_per_table": {},
        "id_mapping": {},
    }

    try:
        # Get database metadata
        metadata = MetaData()
        metadata.reflect(bind=engine)

        # Validate table exists
        if table_name not in metadata.tables:
            raise ValueError(f"Table '{table_name}' does not exist in database")

        table = metadata.tables[table_name]

        # Validate column exists
        if id_column not in table.columns:
            raise ValueError(
                f"Column '{id_column}' does not exist in table '{table_name}'"
            )

        logger.info(f"Starting ID migration for {table_name}.{id_column}")

        # Discover foreign key relationships
        fk_relationships = _discover_fk_relationships(
            engine, metadata, table_name, id_column
        )
        logger.info(f"Found {len(fk_relationships)} foreign key relationships")

        with _migration_connection(engine) as conn:
            # Disable foreign key constraints (database-specific)
            _disable_fk_constraints(conn, engine.dialect.name)

            try:
                # Step 1: Create ID mapping for all records
                logger.info("Creating ID mapping...")
                id_mapping = _create_id_mapping(
                    conn,
                    table_name,
                    id_column,
                    id_generator,
                    value_converter,
                    batch_size,
                )
                result["id_mapping"] = id_mapping
                logger.info(f"Created mapping for {len(id_mapping)} IDs")

                # Step 2: Update main table
                logger.info(f"Updating {table_name}.{id_column}...")
                rows_updated = _update_main_table(
                    conn, table_name, id_column, id_mapping, batch_size
                )
                result["rows_migrated"] = rows_updated
                result["rows_per_table"][table_name] = rows_updated
                logger.info(f"Updated {rows_updated} rows in {table_name}")

                # Step 3: Update all foreign key relationships
                logger.info("Updating foreign key relationships...")
                for fk_info in fk_relationships:
                    fk_table = fk_info["table"]
                    fk_column = fk_info["column"]

                    logger.info(f"Updating {fk_table}.{fk_column}...")
                    fk_rows = _update_foreign_key_table(
                        conn, fk_table, fk_column, id_mapping, batch_size
                    )

                    result["fk_relationships_updated"] += fk_rows
                    if fk_table not in result["tables_affected"]:
                        result["tables_affected"].append(fk_table)

                    # Track rows per table (accumulate if multiple FK columns in same table)
                    if fk_table in result["rows_per_table"]:
                        result["rows_per_table"][fk_table] += fk_rows
                    else:
                        result["rows_per_table"][fk_table] = fk_rows

                    logger.info(f"Updated {fk_rows} rows in {fk_table}.{fk_column}")

                logger.info("Migration completed successfully")

            finally:
                # Re-enable foreign key constraints
                _enable_fk_constraints(conn, engine.dialect.name)

        return result

    except SQLAlchemyError as e:
        logger.error(f"Database error during migration: {e}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Unexpected error during migration: {e}", exc_info=True)
        raise


def _discover_fk_relationships(
    engine: Engine,
    metadata: MetaData,
    table_name: str,
    id_column: str,
) -> list[dict[str, str]]:
    """
    Discover all foreign key relationships referencing the target column.

    Parameters
    ----------
    engine : Engine
        SQLAlchemy engine.
    metadata : MetaData
        Database metadata.
    table_name : str
        Name of the table being migrated.
    id_column : str
        Name of the ID column.

    Returns
    -------
    list[dict[str, str]]
        List of dictionaries containing 'table' and 'column' keys.
    """
    inspector = inspect(engine)
    relationships = []

    # Iterate through all tables to find foreign keys
    for other_table_name in metadata.tables:
        if other_table_name == table_name:
            continue

        foreign_keys = inspector.get_foreign_keys(other_table_name)

        for fk in foreign_keys:
            if fk["referred_table"] == table_name:
                # Check if this FK references our ID column
                if id_column in fk["referred_columns"]:
                    # Get the corresponding local column
                    idx = fk["referred_columns"].index(id_column)
                    local_column = fk["constrained_columns"][idx]

                    relationships.append(
                        {"table": other_table_name, "column": local_column}
                    )

    return relationships


def _create_id_mapping(
    conn: Any,
    table_name: str,
    id_column: str,
    id_generator: Callable[[], Any],
    value_converter: Callable[[Any], str],
    batch_size: int,
) -> dict[str, str]:
    """
    Create mapping of old IDs to new IDs.

    Parameters
    ----------
    conn : Any
        Database connection.
    table_name : str
        Name of the table.
    id_column : str
        Name of the ID column.
    id_generator : Callable[[], Any]
        Function to generate new IDs.
    value_converter : Callable[[Any], str]
        Function to convert ID to string for SQL.
    batch_size : int
        Batch size for processing.

    Returns
    -------
    dict[str, str]
        Mapping of old ID strings to new ID strings.
    """
    # Fetch all existing IDs
    quote = conn.dialect.identifier_preparer.quote
    query = text(f"SELECT {quote(id_column)} FROM {quote(table_name)}")
    result = conn.execute(query)

    id_mapping = {}
    for row in result:
        old_id = value_converter(row[0])
        new_id = value_converter(id_generator())
        id_mapping[old_id] = new_id

    return id_mapping


def _update_main_table(
    conn: Any,
    table_name: str,
    id_column: str,
    id_mapping: dict[str, str],
    batch_size: int,
) -> int:
    """
    Update main table with new IDs.

    Parameters
    ----------
    conn : Any
        Database connection.
    table_name : str
        Name of the table.
    id_column : str
        Name of the ID column.
    id_mapping : dict[str, str]
        Mapping of old to new IDs.
    batch_size : int
        Batch size for processing.

    Returns
    -------
    int
        Number of rows updated.
    """
    rows_updated = 0
    batch = []

    for old_id, new_id in id_mapping.items():
        batch.append((new_id, old_id))

        if len(batch) >= batch_size:
            rows_updated += _execute_batch_update(conn, table_name, id_column, batch)
            batch = []

    # Update remaining records
    if batch:
        rows_updated += _execute_batch_update(conn, table_name, id_column, batch)

    return rows_updated


def _update_foreign_key_table(
    conn: Any,
    table_name: str,
    fk_column: str,
    id_mapping: dict[str, str],
    batch_size: int,
) -> int:
    """
    Update foreign key references in a table.

    Parameters
    ----------
    conn : Any
        Database connection.
    table_name : str
        Name of the table with foreign keys.
    fk_column : str
        Name of the foreign key column.
    id_mapping : dict[str, str]
        Mapping of old to new IDs.
    batch_size : int
        Batch size for processing.

    Returns
    -------
    int
        Number of rows updated.
    """
    rows_updated = 0
    batch = []

    for old_id, new_id in id_mapping.items():
        batch.append((new_id, old_id))

        if len(batch) >= batch_size:
            rows_updated += _execute_batch_update(conn, table_name, fk_column, batch)
            batch = []

    # Update remaining records
    if batch:
        rows_updated += _execute_batch_update(conn, table_name, fk_column, batch)

    return rows_updated


@contextmanager
def _migration_connection(engine: Engine) -> Generator[Connection]:
    if engine.dialect.name != "sqlite":
        with engine.begin() as connection:
            yield connection
        return
    with engine.connect() as connection:
        original_fk_state = connection.exec_driver_sql(
            "PRAGMA foreign_keys"
        ).scalar_one()
        connection.commit()
        connection.exec_driver_sql("PRAGMA foreign_keys = OFF")
        connection.commit()
        try:
            with connection.begin():
                # Include temporary DDL in the same physical transaction as data.
                connection.exec_driver_sql("BEGIN")
                yield connection
        finally:
            connection.exec_driver_sql(
                "PRAGMA foreign_keys = ON"
                if original_fk_state
                else "PRAGMA foreign_keys = OFF"
            )
            connection.commit()


def _execute_batch_update(
    conn: Any,
    table_name: str,
    column_name: str,
    batch: list[tuple[str, str]],
) -> int:
    """
    Execute batch update of IDs.

    Parameters
    ----------
    conn : Any
        Database connection.
    table_name : str
        Name of the table.
    column_name : str
        Name of the column to update.
    batch : list[tuple[str, str]]
        List of (new_id, old_id) tuples.

    Returns
    -------
    int
        Number of rows updated.
    """
    if not batch:
        return 0
    # Build a bound mapping; IDs must never be interpolated as SQL syntax.
    case_parts = []
    old_ids = []

    parameters: dict[str, str] = {}
    for index, (new_id, old_id) in enumerate(batch):
        case_parts.append(f"WHEN :old_{index} THEN :new_{index}")
        old_ids.append(f":old_{index}")
        parameters[f"old_{index}"] = old_id
        parameters[f"new_{index}"] = new_id

    case_statement = " ".join(case_parts)
    where_clause = ", ".join(old_ids)

    quote = conn.dialect.identifier_preparer.quote
    table_name = quote(table_name)
    column_name = quote(column_name)
    if conn.dialect.name == "sqlite":
        # Indexed lookups avoid a linear CASE scan per matched row, including
        # foreign-key columns without their own index. One bound pair per insert
        # also avoids SQLite's per-statement parameter limit on large batches.
        mapping = quote(f"_pyutils_id_map_{uuid.uuid4().hex}")
        conn.exec_driver_sql(
            f"CREATE TEMP TABLE {mapping} (old_id TEXT PRIMARY KEY, new_id TEXT NOT NULL) WITHOUT ROWID"
        )
        try:
            conn.execute(
                text(
                    f"INSERT INTO {mapping} (old_id, new_id) VALUES (:old_id, :new_id)"
                ),
                [{"old_id": old, "new_id": new} for new, old in batch],
            )
            result = conn.execute(
                text(
                    f"UPDATE {table_name} SET {column_name} = "
                    f"(SELECT new_id FROM {mapping} WHERE old_id = {table_name}.{column_name}) "
                    f"WHERE {column_name} IN (SELECT old_id FROM {mapping})"
                )
            )
            return int(result.rowcount or 0)
        finally:
            conn.exec_driver_sql(f"DROP TABLE {mapping}")
    query = text(
        f"""
        UPDATE {table_name}
        SET {column_name} = CASE {column_name}
            {case_statement}
        END
        WHERE {column_name} IN ({where_clause})
        """
    )

    result = conn.execute(query, parameters)
    return result.rowcount or 0


def _disable_fk_constraints(conn: Any, dialect_name: str) -> None:
    """
    Disable foreign key constraints (database-specific).

    Parameters
    ----------
    conn : Any
        Database connection.
    dialect_name : str
        Name of the database dialect.
    """
    if dialect_name == "sqlite":
        conn.execute(text("PRAGMA foreign_keys = OFF"))
    elif dialect_name == "postgresql":
        conn.execute(text("SET session_replication_role = 'replica'"))
    elif dialect_name == "mysql":
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
    # Add other database-specific commands as needed


def _enable_fk_constraints(conn: Any, dialect_name: str) -> None:
    """
    Re-enable foreign key constraints (database-specific).

    Parameters
    ----------
    conn : Any
        Database connection.
    dialect_name : str
        Name of the database dialect.
    """
    if dialect_name == "sqlite":
        conn.execute(text("PRAGMA foreign_keys = ON"))
    elif dialect_name == "postgresql":
        conn.execute(text("SET session_replication_role = 'origin'"))
    elif dialect_name == "mysql":
        conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
    # Add other database-specific commands as needed


__all__ = ["migrate_id_type"]
