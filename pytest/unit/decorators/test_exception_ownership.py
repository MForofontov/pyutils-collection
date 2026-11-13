"""Decorator machinery must distinguish its failures from body failures."""

import importlib
from unittest.mock import MagicMock, patch

import pytest

from pyutils_collection.decorators import conditional_execute, timeout

pytestmark = [pytest.mark.unit, pytest.mark.decorators]


def test_conditional_body_exception_keeps_identity() -> None:
    error = ValueError("body failed")

    @conditional_execute(lambda: True)
    def function() -> None:
        raise error

    with pytest.raises(ValueError) as caught:
        function()
    assert caught.value is error


def test_predicate_error_still_wraps_with_cause() -> None:
    error = ValueError("predicate failed")

    def predicate() -> bool:
        raise error

    @conditional_execute(predicate)
    def function() -> None:
        pytest.fail("body must not run")

    with pytest.raises(RuntimeError) as caught:
        function()
    assert caught.value.__cause__ is error


@pytest.mark.parametrize("error", [ValueError("body failed"), TimeoutError("body timeout")])
def test_timeout_body_exception_keeps_identity(error: Exception) -> None:
    @timeout(seconds=1)
    def function() -> None:
        raise error

    with pytest.raises(type(error)) as caught:
        function()
    assert caught.value is error


def test_timeout_submit_failure_shuts_down_executor() -> None:
    module = importlib.import_module("pyutils_collection.decorators.timeout")
    executor = MagicMock()
    error = RuntimeError("submit failed")
    executor.submit.side_effect = error
    with patch.object(module, "ThreadPoolExecutor", return_value=executor):
        with pytest.raises(RuntimeError) as caught:
            timeout(seconds=1)(lambda: None)()
    assert caught.value is error
    executor.shutdown.assert_called_once_with(wait=False, cancel_futures=True)
