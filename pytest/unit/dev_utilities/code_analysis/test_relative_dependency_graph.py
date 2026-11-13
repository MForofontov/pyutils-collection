import json
from pathlib import Path

import pytest

from pyutils_collection.dev_utilities import generate_dependency_graph

pytestmark = [pytest.mark.unit, pytest.mark.dev_utilities]


@pytest.mark.parametrize(
    "module, statement",
    [
        ("consumer.py", "from . import helper\n"),
        ("consumer.py", "from .helper import value\n"),
        ("sub/consumer.py", "from .. import helper\n"),
    ],
)
def test_relative_imports_keep_the_same_internal_root_as_absolute_imports(
    tmp_path: Path, module: str, statement: str
) -> None:
    package = tmp_path / "package"
    package.mkdir()
    (package / "__init__.py").write_text("")
    (package / "helper.py").write_text("value = 1\n")
    consumer = package / module
    consumer.parent.mkdir(exist_ok=True)
    if consumer.parent != package:
        (consumer.parent / "__init__.py").write_text("")
    consumer.write_text(statement)
    key = "package." + module.removesuffix(".py").replace("/", ".")
    assert json.loads(generate_dependency_graph(tmp_path, output_format="json")) == {
        key: ["package"]
    }
    consumer.write_text("from package import helper\n")
    assert json.loads(generate_dependency_graph(tmp_path, output_format="json")) == {
        key: ["package"]
    }


def test_relative_imports_in_package_initializers_and_invalid_contexts(
    tmp_path: Path,
) -> None:
    package = tmp_path / "package"
    package.mkdir()
    (package / "__init__.py").write_text("from . import helper\n")
    (package / "helper.py").write_text("value = 1\n")
    (tmp_path / "orphan.py").write_text("from .. import missing\nimport os\n")
    assert json.loads(
        generate_dependency_graph(tmp_path, output_format="json", include_external=True)
    ) == {"package": ["package"], "orphan": ["os"]}
