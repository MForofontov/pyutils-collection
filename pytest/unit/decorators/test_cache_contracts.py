"""Observable call and failure contracts shared by the cache decorators."""

from collections.abc import Callable
from typing import Any

import pytest
from pyutils_collection.decorators.cache import cache
from pyutils_collection.decorators.cache_with_expiration import cache_with_expiration

pytestmark = [pytest.mark.unit, pytest.mark.decorators]


@pytest.fixture(params=[cache, cache_with_expiration(60)], ids=["cache", "expiration"])
def decorate(request: pytest.FixtureRequest) -> Callable[..., Any]:
    return request.param


def test_keyword_order_is_part_of_the_call(decorate: Callable[..., Any]) -> None:
    calls = []

    @decorate
    def ordered(**kwargs: int) -> tuple[str, ...]:
        calls.append(tuple(kwargs))
        return tuple(kwargs)

    assert ordered(a=1, b=2) == ("a", "b")
    assert ordered(b=2, a=1) == ("b", "a")
    assert ordered(a=1, b=2) == ("a", "b")
    assert calls == [("a", "b"), ("b", "a")]


def test_body_type_error_propagates_unchanged(decorate: Callable[..., Any]) -> None:
    error = TypeError("body failure")
    calls = []

    @decorate
    def failing(value: int) -> None:
        calls.append(value)
        raise error

    for _ in range(2):
        with pytest.raises(TypeError) as caught:
            failing(1)
        assert caught.value is error
    assert calls == [1, 1]


def test_unhashable_arguments_do_not_execute_body(decorate: Callable[..., Any]) -> None:
    calls = []

    @decorate
    def record(value: object) -> None:
        calls.append(value)

    with pytest.raises(TypeError, match="Unhashable arguments"):
        record([])
    with pytest.raises(TypeError, match="Unhashable arguments"):
        record(value=[])
    assert calls == []


def test_none_results_are_cached(decorate: Callable[..., Any]) -> None:
    calls = []

    @decorate
    def calculate() -> None:
        calls.append(None)

    assert calculate() is None
    assert calculate() is None
    assert calls == [None]


def test_expiration_uses_elapsed_time(monkeypatch: pytest.MonkeyPatch) -> None:
    import importlib

    module = importlib.import_module(
        "pyutils_collection.decorators.cache_with_expiration"
    )
    clock = {"wall": 100.0, "elapsed": 0.0}
    monkeypatch.setattr(module.time, "time", lambda: clock["wall"])
    monkeypatch.setattr(module.time, "monotonic", lambda: clock["elapsed"])
    calls = []

    @cache_with_expiration(10)
    def calculate() -> int:
        calls.append(None)
        return len(calls)

    assert calculate() == 1
    clock.update(wall=1000.0, elapsed=5.0)
    assert calculate() == 1
    clock.update(wall=50.0, elapsed=10.0)
    assert calculate() == 2
