"""Compare a local Git revision and checkout with alternating paired workloads."""

import argparse
import asyncio
import cProfile
import hashlib
import importlib
import json
import platform
import statistics
import subprocess
import sys
import tempfile
import threading
import time
import tracemalloc
import types
from pathlib import Path

import openpyxl
import psutil
from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def square(value):
    return value * value


async def async_square(value):
    return square(value)


def versions(reference, module_name, name):
    path = module_name.replace(".", "/") + ".py"
    source = subprocess.run(
        ["git", "show", f"{reference}:{path}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        encoding="utf-8",
    ).stdout
    baseline = types.ModuleType("audit_baseline")
    exec(compile(source, f"{reference}:{path}", "exec"), baseline.__dict__)
    return {
        "baseline": getattr(baseline, name),
        "candidate": getattr(importlib.import_module(module_name), name),
    }


def memory_sample(operation, sample_children):
    """Sample absolute RSS separately from timing; trace only Python allocations."""
    done = threading.Event()
    process = psutil.Process()
    peaks = {"parent_rss": 0, "children_rss": 0}
    errors = []

    tracemalloc.start()
    try:
        result = operation()
        python_peak = tracemalloc.get_traced_memory()[1]
    finally:
        tracemalloc.stop()

    def monitor():
        while not done.is_set():
            try:
                peaks["parent_rss"] = max(
                    peaks["parent_rss"], process.memory_info().rss
                )
                children = 0
                for child in (
                    process.children(recursive=True) if sample_children else []
                ):
                    try:
                        children += child.memory_info().rss
                    except psutil.Error, OSError:
                        pass
                peaks["children_rss"] = max(peaks["children_rss"], children)
            except (psutil.Error, OSError) as exc:
                errors.append(str(exc))
                break
            done.wait(0.05)

    worker = threading.Thread(target=monitor, daemon=True)
    worker.start()
    try:
        rss_result = operation()
    finally:
        done.set()
        worker.join(timeout=5)
    assert rss_result == result
    if worker.is_alive():
        errors.append("RSS sampler did not finish within five seconds")
    return result, {"python_peak_bytes": python_peak, **peaks, "rss_errors": errors}


def paired(functions, operation, samples, sample_children=False):
    records = {name: [] for name in functions}
    digest = None
    for sample in range(samples):
        order = list(functions.items())[:: 1 if sample % 2 else -1]
        for name, function in order:
            started = time.perf_counter()
            result = operation(function)
            elapsed = time.perf_counter() - started
            traced_result, memory = memory_sample(
                lambda f=function: operation(f), sample_children
            )
            assert result == traced_result
            current_digest = hashlib.sha256(repr(result).encode()).hexdigest()
            if digest is None:
                digest = current_digest
            assert current_digest == digest, "baseline/candidate output differs"
            records[name].append({"seconds": elapsed, **memory})
            print(f"{name} sample {sample + 1}: {elapsed:.6f}s", flush=True)
    return {
        "output_sha256": digest,
        "versions": {
            name: {
                "samples": values,
                "medians": {
                    key: statistics.median(row[key] for row in values)
                    for key in (
                        "seconds",
                        "python_peak_bytes",
                        "parent_rss",
                        "children_rss",
                    )
                },
            }
            for name, values in records.items()
        },
    }


def sqlite_workload(function, size):
    engine = create_engine("sqlite://")
    try:
        with engine.begin() as connection:
            connection.exec_driver_sql("CREATE TABLE items (id TEXT PRIMARY KEY)")
            batch = [(f"new-{i}", f"old-{i}") for i in range(size)]
            connection.execute(
                text("INSERT INTO items VALUES (:id)"),
                [{"id": old} for _, old in batch],
            )
            assert function(connection, "items", "id", batch) == size
            result = sorted(
                connection.exec_driver_sql("SELECT id FROM items").scalars()
            )
            assert result == sorted(new for new, _ in batch)
            return result
    finally:
        engine.dispose()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-ref", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--samples", type=int, default=5)
    parser.add_argument(
        "--profile",
        action="store_true",
        help="Profile a separate candidate invocation per workload.",
    )
    parser.add_argument(
        "--workload",
        action="append",
        choices=[
            "async_map",
            "parallel_map",
            "list_files",
            "transpose_excel",
            "sqlite_mapping",
        ],
        help="Select workload families; repeat to select several (default: all).",
    )
    args = parser.parse_args()
    if args.samples < 1:
        parser.error("samples must be positive")
    revision = subprocess.run(
        ["git", "rev-parse", "--verify", f"{args.baseline_ref}^{{commit}}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    workloads = {}

    def record(name, functions, operation):
        if args.workload and name.split("/", 1)[0] not in args.workload:
            return
        print(name, flush=True)
        workloads[name] = paired(
            functions, operation, args.samples, name.startswith("parallel_map/")
        )
        args.output.parent.mkdir(parents=True, exist_ok=True)
        if args.profile:
            profiler = cProfile.Profile()
            profiler.runcall(operation, functions["candidate"])
            profile = args.output.with_name(
                f"{args.output.stem}-{name.replace('/', '-')}.pstats"
            )
            profiler.dump_stats(profile)
            workloads[name]["profile_file"] = str(profile)
        args.output.write_text(
            json.dumps(
                {
                    "baseline_commit": revision,
                    "python": sys.version,
                    "platform": platform.platform(),
                    "samples": args.samples,
                    "memory_scope": "Timing, Python tracemalloc peak, and sampled RSS use three separate invocations. Absolute parent RSS sampled every 50ms; child RSS sampled for multiprocessing only. RSS includes native allocations, can miss short peaks, and double-counts shared pages. Samples with rss_errors have incomplete RSS. SQLite timings include setup and validation.",
                    "workloads": workloads,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    functions = versions(
        revision,
        "pyutils_collection.asyncio_functions.async_map_limited",
        "async_map_limited",
    )
    for size in (100, 100_000):
        record(
            f"async_map/{size}",
            functions,
            lambda f, size=size: asyncio.run(f(async_square, range(size))),
        )
    functions = versions(
        revision,
        "pyutils_collection.multiprocessing_functions.parallel_map",
        "parallel_map",
    )
    for size in (8, 10_000):
        record(
            f"parallel_map/{size}",
            functions,
            lambda f, size=size: f(square, list(range(size)), num_processes=2),
        )
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        functions = versions(
            revision, "pyutils_collection.cli_functions.list_files", "list_files"
        )
        for size in (100, 5_000):
            folder = root / str(size)
            folder.mkdir()
            for index in range(size):
                (folder / f"{index}.txt").touch()
            record(
                f"list_files/{size}", functions, lambda f, folder=folder: f(str(folder))
            )
        functions = versions(
            revision,
            "pyutils_collection.serialization_functions.excel_operations.transpose_excel_data",
            "transpose_excel_data",
        )
        for rows, columns in ((50, 10), (2_000, 20)):
            source, destination = root / "input.xlsx", root / "output.xlsx"
            expected = [
                tuple(r * columns + c for c in range(columns)) for r in range(rows)
            ]
            workbook = openpyxl.Workbook()
            for row in expected:
                workbook.active.append(row)
            workbook.save(source)
            workbook.close()

            def transpose(
                function,
                source=source,
                destination=destination,
                rows=rows,
                columns=columns,
                expected=expected,
            ):
                assert function(source, destination) == (rows, columns)
                checked = openpyxl.load_workbook(
                    destination, read_only=True, data_only=True
                )
                try:
                    result = list(checked.active.iter_rows(values_only=True))
                    assert result == list(zip(*expected, strict=True))
                    return result
                finally:
                    checked.close()

            record(f"transpose_excel/{rows}x{columns}", functions, transpose)
    functions = versions(
        revision,
        "pyutils_collection.database_functions.schema_inspection.migrate_id_type",
        "_execute_batch_update",
    )
    for size in (100, 5_000):
        record(
            f"sqlite_mapping/{size}",
            functions,
            lambda f, size=size: sqlite_workload(f, size),
        )


if __name__ == "__main__":
    main()
