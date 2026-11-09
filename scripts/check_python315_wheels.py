"""Check pinned dependency wheels on the supported Python 3.15 platforms.

Run with a Python environment containing packaging. Results are evidence of
direct wheel availability, not a substitute for a complete pip resolution.
"""

import concurrent.futures
import json
import sys
import tomllib
import urllib.request
from compression import zstd
from pathlib import Path

from packaging.requirements import Requirement
from packaging.tags import compatible_tags, cpython_tags, mac_platforms
from packaging.utils import parse_wheel_filename

ROOT = Path(__file__).resolve().parents[1]
NATIVE_REQUIRED = {
    "cramjam",
    "psutil",
    "numpy",
    "matplotlib",
    "aiohttp",
    "bcrypt",
    "cryptography",
    "lxml",
    "pyarrow",
    "scipy",
    "scikit-learn",
    "playwright",
    "mypy",
    "ruff",
}
PLATFORMS = {
    "windows-x64": ["win_amd64"],
    "linux-x64": [
        "manylinux_2_28_x86_64",
        "manylinux_2_27_x86_64",
        "manylinux_2_17_x86_64",
        "manylinux2014_x86_64",
        "manylinux2010_x86_64",
        "manylinux1_x86_64",
    ],
    "macos-arm64": list(mac_platforms((15, 0), "arm64")),
}


def inspect(requirement: str) -> dict:
    req = Requirement(requirement)
    pin = next(iter(req.specifier)).version
    with urllib.request.urlopen(
        f"https://pypi.org/pypi/{req.name}/{pin}/json", timeout=30
    ) as response:
        data = json.load(response)
    wheels = []
    for entry in data["urls"]:
        if entry["filename"].endswith(".whl") and not entry.get("yanked"):
            wheels.append(parse_wheel_filename(entry["filename"])[3])
    availability = {}
    for platform, names in PLATFORMS.items():
        tags = set(cpython_tags((3, 15), abis=["cp315"], platforms=names))
        tags.update(compatible_tags((3, 15), interpreter="cp315", platforms=names))
        availability[platform] = any(tags.intersection(wheel) for wheel in wheels)
    return {
        "requirement": requirement,
        "native_wheel_required": req.name.lower() in NATIVE_REQUIRED,
        "wheels": availability,
    }


def main() -> int:
    project = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))[
        "project"
    ]
    requirements = (
        project["dependencies"]
        + project["optional-dependencies"]["dev"]
        + project["optional-dependencies"]["playwright"]
    )
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(inspect, requirements))
    target = ROOT / ".major-check" / "python315-wheels.json"
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")
    blockers = [item for item in results if not all(item["wheels"].values())]
    print(json.dumps(blockers, indent=2))
    print(f"Checked {len(results)} requirements; {len(blockers)} have wheel gaps.")
    required_gaps = [item for item in blockers if item["native_wheel_required"]]
    print(
        f"{len(required_gaps)} required native-wheel gaps. Optional accelerators may build from source."
    )
    print(f"Standard-library Zstandard: {zstd.zstd_version}")
    return int(bool(required_gaps))


if __name__ == "__main__":
    sys.exit(main())
