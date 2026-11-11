"""Verify all subpackage __all__ exports are importable."""

import importlib
import pkgutil

import pytest

import pyutils_collection

pytestmark = pytest.mark.unit

# Discover all subpackages under pyutils_collection
_SUBPACKAGES: list[str] = []
for _importer, _name, _ispkg in pkgutil.walk_packages(
    pyutils_collection.__path__, prefix="pyutils_collection."
):
    if _ispkg:
        _SUBPACKAGES.append(_name)


@pytest.mark.parametrize("package_name", _SUBPACKAGES)
def test_package_exports_are_importable(package_name: str) -> None:
    """Every name in a subpackage __all__ must be accessible via getattr."""
    try:
        package = importlib.import_module(package_name)
    except ImportError as exc:
        pytest.skip(f"Optional dependency missing for {package_name}: {exc}")

    all_names = getattr(package, "__all__", None)
    if not all_names:
        pytest.skip(f"{package_name} has no __all__")

    for name in all_names:
        assert hasattr(package, name), (
            f"{package_name}.{name} is listed in __all__ but not exported"
        )
        getattr(package, name)
