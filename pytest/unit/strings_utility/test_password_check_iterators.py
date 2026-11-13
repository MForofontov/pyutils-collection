"""Custom password rules must run for one-shot iterables."""

from collections.abc import Callable

import pytest

from pyutils_collection.strings_utility import verify_password

pytestmark = [pytest.mark.unit, pytest.mark.strings_utility]


@pytest.mark.parametrize("accepted", [True, False])
def test_generator_rule_runs_once(accepted: bool) -> None:
    calls: list[str] = []

    def check(password: str) -> bool:
        calls.append(password)
        return accepted

    rules = (rule for rule in [check])
    assert verify_password("Password123!", custom_checks=rules) is accepted
    assert calls == ["Password123!"]


def test_rules_short_circuit_in_iteration_order() -> None:
    calls: list[str] = []

    def reject(password: str) -> bool:
        calls.append("reject")
        return False

    def accept(password: str) -> bool:
        calls.append("accept")
        return True

    rules: list[Callable[[str], bool]] = [reject, accept]
    assert not verify_password("Password123!", iter(rules))
    assert calls == ["reject"]
