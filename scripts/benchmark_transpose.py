"""Paired comparison of transpose allocation strategies with identical staging."""

import argparse
import json
import platform
import statistics
import sys
import tempfile
import time
import tracemalloc
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import openpyxl

from pyutils_collection.serialization_functions._staged_output import staged_output
from pyutils_collection.serialization_functions.excel_operations.transpose_excel_data import (
    transpose_excel_data,
)


def previous(source, destination):
    """Prior allocation strategy, with the same safe publishing as current."""
    workbook = openpyxl.load_workbook(source, data_only=True)
    try:
        data = list(workbook.active.iter_rows(values_only=True))
    finally:
        workbook.close()
    columns = max((len(row) for row in data), default=0)
    padded = [list(row) + [None] * (columns - len(row)) for row in data]
    transposed = list(zip(*padded, strict=False)) if padded else []
    output = openpyxl.Workbook()
    try:
        output.active.title = "Transposed"
        for row in transposed:
            output.active.append(row)
        with staged_output(destination) as temporary:
            output.save(temporary)
    finally:
        output.close()
    return len(data), columns


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = {
        "python": sys.version,
        "platform": platform.platform(),
        "samples": 5,
        "cases": {},
    }
    with tempfile.TemporaryDirectory() as directory:
        source, destination = (
            Path(directory) / "source.xlsx",
            Path(directory) / "output.xlsx",
        )
        for rows, columns in ((50, 10), (2_000, 20)):
            expected = [
                tuple(row * columns + column for column in range(columns))
                for row in range(rows)
            ]
            workbook = openpyxl.Workbook()
            for row in expected:
                workbook.active.append(row)
            workbook.save(source)
            workbook.close()
            samples = {
                name: {"seconds": [], "python_peak_bytes": []}
                for name in ("previous", "current")
            }
            for sample in range(5):
                # Alternate order to reduce warm-cache and background-load bias.
                functions = [("previous", previous), ("current", transpose_excel_data)]
                for name, operation in functions[:: 1 if sample % 2 else -1]:
                    started = time.perf_counter()
                    assert operation(source, destination) == (rows, columns)
                    samples[name]["seconds"].append(time.perf_counter() - started)
                    tracemalloc.start()
                    try:
                        assert operation(source, destination) == (rows, columns)
                        samples[name]["python_peak_bytes"].append(
                            tracemalloc.get_traced_memory()[1]
                        )
                    finally:
                        tracemalloc.stop()
                    output = openpyxl.load_workbook(
                        destination, data_only=True, read_only=True
                    )
                    try:
                        assert list(output.active.iter_rows(values_only=True)) == list(
                            zip(*expected, strict=True)
                        )
                    finally:
                        output.close()
            report["cases"][f"{rows}x{columns}"] = {
                name: {
                    "median_seconds": statistics.median(values["seconds"]),
                    "median_python_peak_bytes": statistics.median(
                        values["python_peak_bytes"]
                    ),
                    "samples": values,
                }
                for name, values in samples.items()
            }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
