"""Compare the former SQLite CASE update with indexed batch mappings."""

import json
import statistics
import sys
import time
from pathlib import Path

from sqlalchemy import Column, MetaData, String, Table, create_engine, select, text

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pyutils_collection.database_functions.schema_inspection.migrate_id_type import (
    _execute_batch_update,
)


def previous(connection, batch):
    # Values in this benchmark are generated numeric suffixes, never caller input.
    cases = " ".join(f"WHEN '{old}' THEN '{new}'" for new, old in batch)
    keys = ", ".join(f"'{old}'" for _, old in batch)
    result = connection.execute(
        text(f"UPDATE items SET id = CASE id {cases} END WHERE id IN ({keys})")
    )
    return result.rowcount


def sample(size, current, repeats=3):
    samples = []
    for _ in range(repeats):
        engine = create_engine("sqlite://")
        metadata = MetaData()
        table = Table("items", metadata, Column("id", String, primary_key=True))
        metadata.create_all(engine)
        batch = [(f"new-{index}", f"old-{index}") for index in range(size)]
        try:
            with engine.begin() as connection:
                connection.execute(table.insert(), [{"id": old} for _, old in batch])
                start = time.perf_counter()
                count = (
                    _execute_batch_update(connection, "items", "id", batch)
                    if current
                    else previous(connection, batch)
                )
                samples.append(time.perf_counter() - start)
                assert count == size
                assert set(connection.execute(select(table.c.id)).scalars()) == {
                    new for new, _ in batch
                }
        finally:
            engine.dispose()
    return statistics.median(samples)


if __name__ == "__main__":
    result = {
        "python": sys.version,
        "median_seconds": {
            str(size): {"previous": sample(size, False), "current": sample(size, True)}
            for size in (100, 10000)
        },
    }
    target = Path(".major-check/sqlite-benchmark.json")
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
