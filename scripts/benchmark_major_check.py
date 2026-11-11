"""Repeatable small/large workload measurements; timings are not CI assertions."""

import argparse
import asyncio
import hashlib
import json
import platform
import statistics
import sys
import tempfile
import time
import tracemalloc
from collections.abc import Callable
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import openpyxl

from pyutils_collection.asyncio_functions import async_map_limited
from pyutils_collection.cli_functions.list_files import list_files
from pyutils_collection.multiprocessing_functions.parallel_map import parallel_map
from pyutils_collection.serialization_functions.excel_operations.transpose_excel_data import (
    transpose_excel_data,
)
from scripts.benchmark_sqlite_migration import sample as sqlite_sample


def square(value: int) -> int:
    return value * value


async def async_square(value: int) -> int:
    return square(value)


def measure(operation: Callable[[], Any], samples: int) -> dict[str, Any]:
    timings, peaks, digests = [], [], set()
    for _ in range(samples):
        start = time.perf_counter()
        result = operation()
        timings.append(time.perf_counter() - start)
        digests.add(hashlib.sha256(repr(result).encode()).hexdigest())
        tracemalloc.start()
        try:
            memory_result = operation()
            peaks.append(tracemalloc.get_traced_memory()[1])
        finally:
            tracemalloc.stop()
        assert memory_result == result
    assert len(digests) == 1, "workload outputs changed between samples"
    return {
        "median_seconds": statistics.median(timings),
        "median_python_peak_bytes": statistics.median(peaks),
        "output_sha256": digests.pop(),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--samples", type=int, default=3)
    args = parser.parse_args()
    if args.samples < 1:
        parser.error("samples must be positive")
    results = {}
    for size in (100, 100_000):

        def map_async(size: int = size) -> list[int]:
            result = asyncio.run(async_map_limited(async_square, range(size)))
            assert result == [square(value) for value in range(size)]
            return result

        results[f"async_map/{size}"] = measure(map_async, args.samples)
    for size in (8, 10_000):

        def map_process(size: int = size) -> list[int]:
            result = parallel_map(square, list(range(size)), num_processes=2)
            assert result == [square(value) for value in range(size)]
            return result

        results[f"parallel_map/{size}"] = measure(map_process, args.samples)
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        for size in (100, 5_000):
            folder = root / f"files-{size}"
            folder.mkdir()
            for index in range(size):
                (folder / f"{index:06}.txt").touch()

            def listing(folder: Path = folder, size: int = size) -> list[str]:
                result = sorted(Path(name).name for name in list_files(str(folder)))
                assert len(result) == size
                return result

            results[f"list_files/{size}"] = measure(listing, args.samples)
        for rows, columns in ((50, 10), (2_000, 20)):
            source, output = root / "input.xlsx", root / "output.xlsx"
            workbook = openpyxl.Workbook()
            sheet = workbook.active
            assert sheet is not None
            expected = [
                tuple(row * columns + col for col in range(columns))
                for row in range(rows)
            ]
            for row in expected:
                sheet.append(row)
            workbook.save(source)
            workbook.close()

            def transpose(
                source: Path = source, output: Path = output
            ) -> tuple[int, int]:
                return transpose_excel_data(source, output)

            result = measure(transpose, args.samples)
            checked = openpyxl.load_workbook(output, read_only=True, data_only=True)
            try:
                assert checked.active is not None
                values = list(checked.active.iter_rows(values_only=True))
                assert values == list(zip(*expected, strict=True))
                result["content_sha256"] = hashlib.sha256(
                    repr(values).encode()
                ).hexdigest()
            finally:
                checked.close()
            results[f"transpose_excel/{rows}x{columns}"] = result
    # Existing SQLite benchmark validates affected IDs and uses fresh databases.
    for size in (100, 5_000):
        results[f"sqlite_mapping/{size}"] = measure(
            lambda size=size: sqlite_sample(size, True, repeats=1) is not None,
            args.samples,
        )
    report = {
        "python": sys.version,
        "platform": platform.platform(),
        "samples": args.samples,
        "memory_scope": "tracemalloc Python allocations in the parent process; excludes native buffers and child RSS",
        "workloads": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
