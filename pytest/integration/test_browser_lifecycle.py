"""Opt-in real Chromium lifecycle checks using generated content only."""

import os

import pytest
from pyutils_collection.playwright_functions.managed_browser import managed_browser
from pyutils_collection.playwright_functions.parallel_scrape import parallel_scrape

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


@pytest.mark.parametrize("workers", [1, 2])
def test_real_parallel_scrape_thread_ownership_and_context_isolation(workers):
    def scrape(page, url):
        assert page.context.cookies() == []
        page.context.add_cookies([
            {"name": "visited", "value": url, "url": "https://example.test"}
        ])
        if url == "bad":
            raise ValueError("intentional scrape failure")
        page.set_content(f"<title>{url}</title>")
        return {"title": page.title()}

    results = parallel_scrape(["first", "bad", "last"], scrape, max_workers=workers)
    assert [item["url"] for item in results] == ["first", "bad", "last"]
    assert results[0]["data"] == {"title": "first"}
    assert results[2]["data"] == {"title": "last"}
    assert results[1]["success"] is False
    assert "intentional scrape failure" in results[1]["error"]
