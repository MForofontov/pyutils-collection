"""Compare ordered async-map storage with the prior dictionary implementation."""

import asyncio
import json
import statistics
import sys
import time
import tracemalloc
from itertools import islice
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pyutils_collection.asyncio_functions import async_map_limited


async def previous(func, items, limit=10):
    indexed = enumerate(items)
    first_items = list(islice(indexed, limit))
    results = {}

    async def worker(first):
        index, item = first
        results[index] = await func(item)
        for index, item in indexed:
            results[index] = await func(item)

    tasks = [asyncio.create_task(worker(first)) for first in first_items]
    try:
        await asyncio.gather(*tasks)
    except BaseException:
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)
        raise
    return [results[index] for index in range(len(results))]


async def identity(value):
    return value


def sample(function, size):
    times, peaks = [], []
    for _ in range(5):
        start = time.perf_counter()
        assert asyncio.run(function(identity, range(size))) == list(range(size))
        times.append(time.perf_counter() - start)
        tracemalloc.start()
        result = asyncio.run(function(identity, range(size)))
        peaks.append(tracemalloc.get_traced_memory()[1])
        tracemalloc.stop()
        assert result == list(range(size))
    return {
        "median_seconds": statistics.median(times),
        "median_peak_bytes": statistics.median(peaks),
    }


if __name__ == "__main__":
    report = {
        "python": sys.version,
        "samples": {
            str(size): {
                "previous": sample(previous, size),
                "current": sample(async_map_limited, size),
            }
            for size in (100, 100_000)
        },
    }
    output = Path(".major-check/async-map-benchmark.json")
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
