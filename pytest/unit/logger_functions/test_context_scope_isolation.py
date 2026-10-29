"""Temporary context metadata must not leak into an enclosing scope."""

import pytest
from pyutils_collection.logger_functions.contextual_logger import (
    LogContext,
    contextual_logger,
)

pytestmark = [pytest.mark.unit, pytest.mark.logger_functions]


def test_nested_metadata_scopes_restore_enclosing_context():
    context = LogContext(metadata={"shared": "original"})
    logger = contextual_logger("scope-isolation", context)
    with logger.context_scope(outer="value"):
        assert logger._get_context().metadata == {"shared": "original", "outer": "value"}
        with logger.context_scope(inner="value", shared="temporary"):
            assert logger._get_context().metadata["shared"] == "temporary"
        assert logger._get_context().metadata == {"shared": "original", "outer": "value"}
    assert context.metadata == {"shared": "original"}


def test_metadata_scope_restores_after_exception():
    context = LogContext(metadata={"original": 1})
    logger = contextual_logger("scope-error", context)
    with pytest.raises(RuntimeError):
        with logger.context_scope(temporary=2):
            raise RuntimeError("failed operation")
    assert logger._get_context() is context
    assert context.metadata == {"original": 1}
