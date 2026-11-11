"""Opt-in real Chromium lifecycle checks using generated content only."""

import os

import pytest
from pyutils_collection.playwright_functions.managed_browser import managed_browser

pytestmark = [
    pytest.mark.integration,
    pytest.mark.playwright_functions,
    pytest.mark.skipif(
        os.environ.get("PYUTILS_BROWSER_TESTS") != "1",
        reason="set PYUTILS_BROWSER_TESTS=1 after installing Playwright Chromium",
    ),
]


def test_real_browser_content_and_cleanup():
    with managed_browser(headless=True) as (browser, context, page):
        page.set_content("<main><button>Ready</button></main>")
        page.locator("button").evaluate("button => button.textContent = 'Done'")
        assert page.locator("button").inner_text() == "Done"
        assert browser.is_connected()
        assert len(context.pages) == 1
    assert page.is_closed()
    assert not browser.is_connected()


def test_real_browser_cleanup_after_user_error():
    with pytest.raises(RuntimeError, match="intentional failure"):
        with managed_browser(headless=True) as (browser, context, page):
            page.set_content("<p>Temporary page</p>")
            raise ValueError("intentional failure")
    assert page.is_closed()
    assert not browser.is_connected()
