import json
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from pyutils_collection.playwright_functions.restore_session import restore_session

pytestmark = [pytest.mark.unit, pytest.mark.playwright_functions]


@pytest.mark.parametrize("existing", [False, True])
@pytest.mark.parametrize("failure", ["goto", "evaluate"])
def test_restore_failure_closes_only_a_page_it_created(
    tmp_path: Path, existing: bool, failure: str
) -> None:
    session = tmp_path / "session.json"
    session.write_text(json.dumps({"storage": {"localStorage": {"key": "value"}}}))
    page = MagicMock()
    context = MagicMock()
    context.pages = [page] if existing else []
    context.new_page.return_value = page
    error = RuntimeError("restore failed")
    getattr(page, failure).side_effect = error
    if not existing and failure == "evaluate":
        page.close.side_effect = RuntimeError("cleanup failed")
    with pytest.raises(RuntimeError) as raised:
        restore_session(context, str(session), url="https://example.test")
    assert raised.value.__cause__ is error
    if existing:
        page.close.assert_not_called()
        context.new_page.assert_not_called()
    else:
        page.close.assert_called_once_with()


def test_successful_restore_retains_new_page_for_session_storage(tmp_path: Path) -> None:
    session = tmp_path / "session.json"
    session.write_text(json.dumps({"storage": {"sessionStorage": {"key": "value"}}}))
    page = MagicMock()
    context = MagicMock()
    context.pages = []
    context.new_page.return_value = page
    restore_session(context, str(session), url="https://example.test")
    context.new_page.assert_called_once_with()
    page.close.assert_not_called()
    page.evaluate.assert_called_once()
