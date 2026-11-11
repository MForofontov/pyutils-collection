"""Generate dependency graph for Python modules."""

import ast
from pathlib import Path


def generate_dependency_graph(
    project_path: str | Path,
    output_format: str = "dot",
    include_external: bool = False,
) -> str:
    """
    Generate a dependency graph for Python modules in a project.

    Analyzes Python files to extract import statements and creates a dependency
    graph showing relationships between modules. Supports DOT format for Graphviz
    visualization.

    Parameters
    ----------
    project_path : str | Path
        Path to the project directory to analyze.
    output_format : str, optional
        Output format for the graph ('dot', 'json', 'text') (by default 'dot').
    include_external : bool, optional
        Include external dependencies (by default False).

    Returns
    -------
    str
        Dependency graph in the specified format.

    Raises
    ------
    TypeError
        If parameters are of wrong type.
    ValueError
        If project_path doesn't exist or output_format is invalid.
    FileNotFoundError
        If project_path directory doesn't exist.

    Examples
    --------
    >>> graph = generate_dependency_graph('my_project')  # doctest: +SKIP
    >>> print(graph)  # doctest: +SKIP
    digraph dependencies {
        "module_a" -> "module_b";
        "module_b" -> "module_c";
    }

    Notes
    -----
    - Only analyzes Python (.py) files
    - Parses import statements using AST
    - Can export to DOT format for Graphviz visualization
    - Filters out standard library imports by default

    Complexity
    ----------
    Time: O(n * m), Space: O(n * m)
    where n is number of files and m is average imports per file
    """
    # Input validation
    if not isinstance(project_path, (str, Path)):
        raise TypeError(
            f"project_path must be str or Path, got {type(project_path).__name__}"
        )
    if not isinstance(output_format, str):
        raise TypeError(
            f"output_format must be str, got {type(output_format).__name__}"
        )
    if not isinstance(include_external, bool):
        raise TypeError(
            f"include_external must be bool, got {type(include_external).__name__}"
        )

    valid_formats = {"dot", "json", "text"}
    if output_format not in valid_formats:
        raise ValueError(
            f"output_format must be one of {valid_formats}, got '{output_format}'"
        )

    project_path = Path(project_path)
    if not project_path.exists():
        raise FileNotFoundError(f"Project path does not exist: {project_path}")
    if not project_path.is_dir():
        raise ValueError(f"Project path must be a directory: {project_path}")

    # Collect all Python files
    python_files = list(project_path.rglob("*.py"))

    # Build dependency map
    dependencies: dict[str, set[str]] = {}
    modules_in_project: set[str] = set()

    # First pass: collect all module names in project
    for py_file in python_files:
        rel_path = py_file.relative_to(project_path)
        module_name = rel_path.with_suffix("").as_posix().replace("/", ".")
        if module_name.endswith(".__init__"):
            module_name = module_name[:-9]
        modules_in_project.add(module_name)

    # Second pass: extract imports
    for py_file in python_files:
        rel_path = py_file.relative_to(project_path)
        module_name = rel_path.with_suffix("").as_posix().replace("/", ".")
        if module_name.endswith(".__init__"):
            module_name = module_name[:-9]

        try:
            with open(py_file, encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=str(py_file))

            imports: set[str] = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imported_module = alias.name.split(".")[0]
                        if include_external or imported_module in modules_in_project:
                            imports.add(imported_module)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imported_module = node.module.split(".")[0]
                        if include_external or imported_module in modules_in_project:
                            imports.add(imported_module)

            if imports:
                dependencies[module_name] = imports

        except SyntaxError, UnicodeDecodeError:
            # Skip files with syntax errors or encoding issues
            continue

    # Generate output in requested format
    if output_format == "dot":
        return _generate_dot_format(dependencies)
    elif output_format == "json":
        return _generate_json_format(dependencies)
    else:  # text
        return _generate_text_format(dependencies)


def _generate_dot_format(dependencies: dict[str, set[str]]) -> str:
    """Generate DOT format for Graphviz."""
    lines = ["digraph dependencies {", '    rankdir="LR";', "    node [shape=box];", ""]

    for module, imports in sorted(dependencies.items()):
        for imported in sorted(imports):
            lines.append(f'    "{module}" -> "{imported}";')

    lines.append("}")
    return "\n".join(lines)


def _generate_json_format(dependencies: dict[str, set[str]]) -> str:
    """Generate JSON format."""
    import json

    # Convert sets to lists for JSON serialization
    json_deps = {
        module: sorted(list(imports)) for module, imports in dependencies.items()
    }
    return json.dumps(json_deps, indent=2)


def _generate_text_format(dependencies: dict[str, set[str]]) -> str:
    """Generate plain text format."""
    lines = ["Module Dependencies", "=" * 50, ""]

    for module, imports in sorted(dependencies.items()):
        lines.append(f"{module}:")
        for imported in sorted(imports):
            lines.append(f"  -> {imported}")
        lines.append("")

    return "\n".join(lines)


__all__ = ["generate_dependency_graph"]
