"""Exception logging retains tracebacks and contextual metadata."""

import logging
import sys

import pytest
from pyutils_collection.logger_functions.contextual_logger import (
    LogContext,
    contextual_logger,
)

pytestmark = [pytest.mark.unit, pytest.mark.logger_functions]


def test_exception_retains_active_exception_and_context(
    caplog: pytest.LogCaptureFixture,
) -> None:
    logger = contextual_logger("audit.exception", LogContext(user_id="context"))
    error = ValueError("original failure")
    with caplog.at_level(logging.ERROR):
        try:
            raise error
        except ValueError:
            logger.exception(
                "operation failed",
                extra={"user_id": "extra", "custom": 1},
                user_id="keyword",
            )
    (record,) = caplog.records
    assert record.exc_info is not None
    assert record.exc_info[0] is ValueError
    assert record.exc_info[1] is error
    assert record.exc_info[2] is error.__traceback__
    assert record.user_id == "keyword"
    assert record.custom == 1
    assert "ValueError: original failure" in caplog.text


def test_exception_can_suppress_traceback(caplog: pytest.LogCaptureFixture) -> None:
    logger = contextual_logger("audit.suppressed")
    with caplog.at_level(logging.ERROR):
        try:
            raise ValueError("suppressed")
        except ValueError:
            logger.exception("message only", exc_info=False)
    (record,) = caplog.records
    assert record.exc_info is False
    assert record.getMessage() == "message only"
    assert "ValueError: suppressed" not in caplog.text


def test_error_accepts_explicit_exception_tuple(
    caplog: pytest.LogCaptureFixture,
) -> None:
    logger = contextual_logger("audit.explicit")
    try:
        raise RuntimeError("saved failure")
    except RuntimeError:
        saved = sys.exc_info()
    with caplog.at_level(logging.ERROR):
        logger.error("later", exc_info=saved, task="upload")
    (record,) = caplog.records
    assert record.exc_info == saved
    assert record.task == "upload"


def test_exception_without_active_error_matches_logging(
    caplog: pytest.LogCaptureFixture,
) -> None:
    with caplog.at_level(logging.ERROR):
        contextual_logger("audit.outside").exception("outside handler")
        logging.getLogger("audit.standard").exception("outside handler")
    actual, standard = caplog.records
    assert actual.exc_info == standard.exc_info
