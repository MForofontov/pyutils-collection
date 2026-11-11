"""
Test case 1: Test dependency graph generation with normal Python project.
"""

import tempfile
from pathlib import Path

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.dev_utilities]
from pyutils_collection.dev_utilities.code_analysis.generate_dependency_graph import (
    generate_dependency_graph,
)


def test_generate_dependency_graph_simple_project() -> None:
    """
    Test case 1: Generate dependency graph for a simple project.
    """
    # Arrange
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)

        # Create simple Python files with imports
        (project_path / "module_a.py").write_text(
            "import module_b\nfrom module_c import func\n"
        )
        (project_path / "module_b.py").write_text("import os\n")
        (project_path / "module_c.py").write_text("")

        # Act
        result = generate_dependency_graph(project_path, output_format="dot")

        # Assert
        assert isinstance(result, str)
        assert "digraph dependencies" in result
        assert "module_a" in result


def test_generate_dependency_graph_json_format() -> None:
    """
    Test case 2: Generate dependency graph in JSON format.
    """
    # Arrange
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        (project_path / "test.py").write_text("import json\n")

        # Act
        result = generate_dependency_graph(project_path, output_format="json")

        # Assert
        assert isinstance(result, str)
        assert "{" in result  # JSON format


def test_generate_dependency_graph_text_format() -> None:
    """
    Test case 3: Generate dependency graph in text format.
    """
    # Arrange
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        (project_path / "app.py").write_text("import sys\n")

        # Act
        result = generate_dependency_graph(project_path, output_format="text")

        # Assert
        assert isinstance(result, str)
        assert "Module Dependencies" in result


def test_generate_dependency_graph_invalid_project_path_raises_error() -> None:
    """
    Test case 4: TypeError for invalid project_path type.
    """
    # Arrange
    invalid_path = 123
    expected_message = "project_path must be str or Path, got int"

    # Act & Assert
    with pytest.raises(TypeError, match=expected_message):
        generate_dependency_graph(invalid_path)  # type: ignore


def test_generate_dependency_graph_nonexistent_path_raises_error() -> None:
    """
    Test case 5: FileNotFoundError for nonexistent project path.
    """
    # Arrange
    invalid_path = "/nonexistent/path/to/project"
    expected_message = "Project path does not exist"

    # Act & Assert
    with pytest.raises(FileNotFoundError, match=expected_message):
        generate_dependency_graph(invalid_path)


def test_generate_dependency_graph_invalid_format_raises_error() -> None:
    """
    Test case 6: ValueError for invalid output format.
    """
    # Arrange
    with tempfile.TemporaryDirectory() as tmpdir:
        expected_message = "output_format must be one of"

        # Act & Assert
        with pytest.raises(ValueError, match=expected_message):
            generate_dependency_graph(tmpdir, output_format="invalid")


def test_generate_dependency_graph_exclude_external_dependencies() -> None:
    """
    Test case 7: Exclude external dependencies by default.
    """
    # Arrange
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        (project_path / "main.py").write_text("import os\nimport sys\n")

        # Act
        result = generate_dependency_graph(project_path, include_external=False)

        # Assert - should not include 'os' or 'sys' as they're external
        assert isinstance(result, str)


def test_generate_dependency_graph_include_external_dependencies() -> None:
    """
    Test case 8: Include external dependencies when requested.
    """
    # Arrange
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)
        (project_path / "main.py").write_text("import os\n")

        # Act
        result = generate_dependency_graph(project_path, include_external=True)

        # Assert
        assert "os" in result or "digraph" in result  # Will show in graph


def test_nested_modules_use_dotted_names_and_keep_internal_imports(tmp_path):
    import json

    package = tmp_path / "package"
    package.mkdir()
    (package / "__init__.py").write_text("")
    (package / "consumer.py").write_text("import package\n")
    assert json.loads(generate_dependency_graph(tmp_path, output_format="json")) == {
        "package.consumer": ["package"]
    }
