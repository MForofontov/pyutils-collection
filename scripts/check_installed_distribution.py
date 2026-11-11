"""Run with an isolated, installed-package interpreter (python -I)."""

import ast
import importlib
import importlib.metadata
import os
import pkgutil
import re
import sys
import tempfile
import tomllib
from pathlib import Path

from packaging.requirements import Requirement

import pyutils_collection


def main() -> None:
    root = Path(sys.argv[1]).resolve()
    installed = Path(pyutils_collection.__file__).resolve()
    assert installed.is_relative_to(Path(sys.prefix).resolve()), installed
    assert not installed.is_relative_to(root / "pyutils_collection"), installed
    assert (installed.parent / "py.typed").is_file()
    # Verify the artifact was built from this checkout, including private helpers.
    source_count = 0
    for source in (root / "pyutils_collection").rglob("*.py"):
        relative = source.relative_to(root / "pyutils_collection")
        packaged = installed.parent / relative
        assert packaged.is_file(), f"Missing packaged source: {relative}"
        assert packaged.read_bytes() == source.read_bytes(), (
            f"Packaged source differs from checkout: {relative}"
        )
        source_count += 1
    project = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8"))[
        "project"
    ]
    metadata = importlib.metadata.metadata("pyutils-collection")
    assert metadata["Version"] == pyutils_collection.__version__
    assert metadata["Requires-Python"] == ">=3.15"
    runtime = [Requirement(item) for item in metadata.get_all("Requires-Dist", [])]
    runtime = [
        item
        for item in runtime
        if item.marker is None or "extra" not in str(item.marker)
    ]
    assert set(runtime) == {Requirement(item) for item in project["dependencies"]}
    count = 0
    for info in pkgutil.walk_packages(
        pyutils_collection.__path__, "pyutils_collection."
    ):
        if info.ispkg:
            module = importlib.import_module(info.name)
            for name in getattr(module, "__all__", []):
                assert hasattr(module, name), (info.name, name)
                count += 1
    examples = re.findall(
        r"```python\n(.*?)```", (root / "README.md").read_text(encoding="utf-8"), re.S
    )
    previous = Path.cwd()
    try:
        with tempfile.TemporaryDirectory() as directory:
            os.chdir(directory)
            for index, example in enumerate(examples, 1):
                ast.parse(example)
                exec(
                    compile(example, f"README example {index}", "exec"),
                    {"__name__": "__main__"},
                )
            os.chdir(previous)
    finally:
        os.chdir(previous)
    print(
        f"Verified {source_count} sources, {count} exports, {len(examples)} README examples, metadata, and typing marker: {installed}"
    )


if __name__ == "__main__":
    main()
