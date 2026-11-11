"""Record public definitions, exports, test-file gaps, and family test results."""

import ast
import json
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    families = {}
    for folder in sorted((ROOT / "pyutils_collection").iterdir()):
        if not folder.is_dir() or folder.name.startswith("_"):
            continue
        definitions, exports, gaps = [], [], []
        for path in sorted(folder.rglob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            relative = path.relative_to(ROOT).as_posix()
            for node in tree.body:
                if isinstance(
                    node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
                ) and not node.name.startswith("_"):
                    definitions.append(f"{relative}:{node.lineno}:{node.name}")
                if isinstance(node, ast.Assign) and any(
                    isinstance(target, ast.Name) and target.id == "__all__"
                    for target in node.targets
                ):
                    try:
                        exports.extend(
                            f"{relative}:{name}"
                            for name in ast.literal_eval(node.value)
                        )
                    except ValueError, TypeError:
                        exports.append(f"{relative}:dynamic __all__")
            if path.name != "__init__.py" and not path.name.startswith("_"):
                conventional = (
                    ROOT / "pytest/unit" / path.relative_to(ROOT / "pyutils_collection")
                )
                if not conventional.with_name(f"test_{path.name}").exists():
                    gaps.append(relative)
        families[folder.name] = {
            "public_definitions": definitions,
            "exports": exports,
            "conventional_test_gaps": gaps,
            "tests": {},
        }
    for argument in sys.argv[1:]:
        report = ET.parse(argument)
        for case in report.iter("testcase"):
            location = case.get("classname", "").replace("\\", ".").replace("/", ".")
            for family, details in families.items():
                if f"unit.{family}." in location:
                    status = (
                        "failed"
                        if case.find("failure") is not None
                        or case.find("error") is not None
                        else "skipped"
                        if case.find("skipped") is not None
                        else "passed"
                    )
                    details["tests"][status] = details["tests"].get(status, 0) + 1
                    break
    output = ROOT / ".major-check/inventory.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(families, indent=2) + "\n", encoding="utf-8")
    for family, details in families.items():
        print(
            f"{family}: {len(details['public_definitions'])} definitions, {len(details['exports'])} exports, "
            f"{len(details['conventional_test_gaps'])} conventional test gaps; {details['tests']}"
        )
    totals = Counter()
    for details in families.values():
        totals.update(details["tests"])
    print(
        f"{len(families)} families; tests: {dict(totals)}. Filename gaps require review, not automatic new tests."
    )


if __name__ == "__main__":
    main()
