"""Legacy import paths share the tested CLI implementation."""

import importlib
import inspect

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.ssh_functions]


@pytest.mark.parametrize(
    "name",
    [
        "ssh_execute_command",
        "ssh_execute_script",
        "ssh_copy_file",
        "ssh_check_connection",
    ],
)
def test_legacy_module_and_package_export_the_local_helper(name):
    package = importlib.import_module("pyutils_collection.ssh_functions")
    legacy = importlib.import_module(f"pyutils_collection.ssh_functions.{name}")
    local = importlib.import_module(f"pyutils_collection.ssh_functions.local.{name}")
    assert getattr(legacy, name) is getattr(local, name)
    # Importing a dotted module may replace a package attribute with that module;
    # the public object captured by __init__ before import remains the helper.
    exported = getattr(package, name)
    if not inspect.ismodule(exported):
        assert exported is getattr(local, name)
