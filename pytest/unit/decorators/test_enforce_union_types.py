"""Runtime checking of Any and union annotations."""

from typing import Any

import pytest

from pyutils_collection.decorators import enforce_types

pytestmark = [pytest.mark.unit, pytest.mark.decorators]


@pytest.mark.parametrize("value", [None, 1, "text", [1]])
def test_any_annotation_accepts_values(value: Any) -> None:
    @enforce_types()
    def identity(item: Any) -> Any:
        return item

    assert identity(value) is value


@pytest.mark.parametrize("value", [None, 1, "text"])
def test_union_annotation_accepts_each_member(value: Any) -> None:
    @enforce_types()
    def identity(item: int | str | None) -> int | str | None:
        return item

    assert identity(value) is value


def test_nested_union_still_rejects_invalid_members() -> None:
    @enforce_types()
    def identity(items: list[int | None]) -> list[int | None]:
        return items

    valid = [1, None]
    assert identity(valid) is valid
    with pytest.raises(TypeError):
        identity(["invalid"])
