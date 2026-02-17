"""Unit tests for parallel_scrape function."""

from typing import Any
from unittest.mock import MagicMock, Mock, patch

import pytest

try:
    from pyutils_collection.playwright_functions.parallel_scrape import parallel_scrape
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    parallel_scrape = None  # type: ignore

pytestmark = [
    pytest.mark.unit,
    pytest.mark.playwright_functions,
    pytest.mark.skipif(not PLAYWRIGHT_AVAILABLE, reason="playwright not installed"),
]


@patch("pyutils_collection.playwright_functions.parallel_scrape.sync_playwright")
def test_parallel_scrape_basic_success(mock_sync_playwright: Mock) -> None:
    """
    Test case 1: Basic parallel scraping of multiple URLs.
    """
    # Arrange
    mock_playwright = MagicMock()
    mock_browser = MagicMock()
    mock_context = MagicMock()
    mock_page = MagicMock()
    
    mock_sync_playwright.return_value.start.return_value = mock_playwright
    mock_playwright.chromium.launch.return_value = mock_browser
    mock_browser.new_context.return_value = mock_context
    mock_context.new_page.return_value = mock_page
    
    urls = ["https://example.com/1", "https://example.com/2"]
    
    def scrape_func(page: Any, url: Any) -> dict[str, str]:
        return {"title": f"Page {url}", "content": "test content"}
    
    # Act
    results = parallel_scrape(urls, scrape_func, max_workers=2)
    
    # Assert
    assert len(results) == 2
    assert all(r["success"] for r in results)
    assert results[0]["url"] == urls[0]
    assert results[1]["url"] == urls[1]
    mock_browser.close.assert_called_once()


@patch("pyutils_collection.playwright_functions.parallel_scrape.sync_playwright")
def test_parallel_scrape_single_url(mock_sync_playwright: Mock) -> None:
    """
    Test case 2: Scrape single URL.
    """
    # Arrange
    mock_playwright = MagicMock()
    mock_browser = MagicMock()
    mock_context = MagicMock()
    mock_page = MagicMock()
    
    mock_sync_playwright.return_value.start.return_value = mock_playwright
    mock_playwright.chromium.launch.return_value = mock_browser
    mock_browser.new_context.return_value = mock_context
    mock_context.new_page.return_value = mock_page
    
    urls = ["https://example.com"]
    
    def scrape_func(page: Any, url: Any) -> dict[str, str]:
        return {"data": "scraped"}
    
    # Act
    results = parallel_scrape(urls, scrape_func)
    
    # Assert
    assert len(results) == 1
    assert results[0]["success"] is True
    assert results[0]["data"] == {"data": "scraped"}


@patch("pyutils_collection.playwright_functions.parallel_scrape.sync_playwright")
def test_parallel_scrape_firefox_browser(mock_sync_playwright: Mock) -> None:
    """
    Test case 3: Use Firefox browser for scraping.
    """
    # Arrange
    mock_playwright = MagicMock()
    mock_browser = MagicMock()
    mock_context = MagicMock()
    mock_page = MagicMock()
    
    mock_sync_playwright.return_value.start.return_value = mock_playwright
    mock_playwright.firefox.launch.return_value = mock_browser
    mock_browser.new_context.return_value = mock_context
    mock_context.new_page.return_value = mock_page
    
    urls = ["https://example.com"]
    
    def scrape_func(page: Any, url: Any) -> dict[str, str]:
        return {"data": "test"}
    
    # Act
    results = parallel_scrape(urls, scrape_func, browser_type="firefox")
    
    # Assert
    mock_playwright.firefox.launch.assert_called_once()
    assert results[0]["success"] is True


@patch("pyutils_collection.playwright_functions.parallel_scrape.sync_playwright")
def test_parallel_scrape_headless_false(mock_sync_playwright: Mock) -> None:
    """
    Test case 4: Run browser in non-headless mode.
    """
    # Arrange
    mock_playwright = MagicMock()
    mock_browser = MagicMock()
    mock_context = MagicMock()
    mock_page = MagicMock()
    
    mock_sync_playwright.return_value.start.return_value = mock_playwright
    mock_playwright.chromium.launch.return_value = mock_browser
    mock_browser.new_context.return_value = mock_context
    mock_context.new_page.return_value = mock_page
    
    urls = ["https://example.com"]
    
    def scrape_func(page: Any, url: Any) -> dict[str, str]:
        return {}
    
    # Act
    results = parallel_scrape(urls, scrape_func, headless=False)
    
    # Assert
    call_args = mock_playwright.chromium.launch.call_args
    assert call_args[1]["headless"] is False


@patch("pyutils_collection.playwright_functions.parallel_scrape.sync_playwright")
def test_parallel_scrape_custom_timeout(mock_sync_playwright: Mock) -> None:
    """
    Test case 5: Custom timeout for operations.
    """
    # Arrange
    mock_playwright = MagicMock()
    mock_browser = MagicMock()
    mock_context = MagicMock()
    mock_page = MagicMock()
    
    mock_sync_playwright.return_value.start.return_value = mock_playwright
    mock_playwright.chromium.launch.return_value = mock_browser
    mock_browser.new_context.return_value = mock_context
    mock_context.new_page.return_value = mock_page
    
    urls = ["https://example.com"]
    
    def scrape_func(page: Any, url: Any) -> dict[str, str]:
        return {}
    
    # Act
    results = parallel_scrape(urls, scrape_func, timeout=60000)
    
    # Assert
    mock_context.set_default_timeout.assert_called_once_with(60000)


@patch("pyutils_collection.playwright_functions.parallel_scrape.sync_playwright")
def test_parallel_scrape_error_handling(mock_sync_playwright: Mock) -> None:
    """
    Test case 6: Handle scrape errors gracefully.
    """
    # Arrange
    mock_playwright = MagicMock()
    mock_browser = MagicMock()
    mock_context = MagicMock()
    mock_page = MagicMock()
    
    mock_sync_playwright.return_value.start.return_value = mock_playwright
    mock_playwright.chromium.launch.return_value = mock_browser
    mock_browser.new_context.return_value = mock_context
    mock_context.new_page.return_value = mock_page
    
    urls = ["https://example.com/1", "https://example.com/2"]
    
    def scrape_func(page: Any, url: Any) -> dict[str, str]:
        if "1" in url:
            raise ValueError("Test error")
        return {"data": "success"}
    
    # Act
    results = parallel_scrape(urls, scrape_func)
    
    # Assert
    assert len(results) == 2
    assert results[0]["success"] is False
    assert "Test error" in results[0]["error"]
    assert results[1]["success"] is True


@patch("pyutils_collection.playwright_functions.parallel_scrape.sync_playwright")
def test_parallel_scrape_multiple_workers(mock_sync_playwright: Mock) -> None:
    """
    Test case 7: Scrape with multiple worker threads.
    """
    # Arrange
    mock_playwright = MagicMock()
    mock_browser = MagicMock()
    mock_context = MagicMock()
    mock_page = MagicMock()
    
    mock_sync_playwright.return_value.start.return_value = mock_playwright
    mock_playwright.chromium.launch.return_value = mock_browser
    mock_browser.new_context.return_value = mock_context
    mock_context.new_page.return_value = mock_page
    
    urls = [f"https://example.com/{i}" for i in range(10)]
    
    def scrape_func(page: Any, url: Any) -> dict[str, str]:
        return {"url": url}
    
    # Act
    results = parallel_scrape(urls, scrape_func, max_workers=5)
    
    # Assert
    assert len(results) == 10
    assert all(r["success"] for r in results)
    # Verify order is maintained
    for i, result in enumerate(results):
        assert result["url"] == urls[i]


def test_parallel_scrape_invalid_urls_type() -> None:
    """
    Test case 8: TypeError for non-list URLs.
    """
    # Arrange
    def scrape_func(page: Any, url: Any) -> dict[str, str]:
        return {}
    
    # Act & Assert
    with pytest.raises(TypeError, match="urls must be a list"):
        parallel_scrape("not a list", scrape_func)  # type: ignore


def test_parallel_scrape_empty_urls() -> None:
    """
    Test case 9: ValueError for empty URLs list.
    """
    # Arrange
    def scrape_func(page: Any, url: Any) -> dict[str, str]:
        return {}
    
    # Act & Assert
    with pytest.raises(ValueError, match="urls list cannot be empty"):
        parallel_scrape([], scrape_func)


def test_parallel_scrape_invalid_url_in_list() -> None:
    """
    Test case 10: TypeError when URLs list contains non-strings.
    """
    # Arrange
    urls = ["https://example.com", 123, "https://test.com"]  # Invalid URL
    
    def scrape_func(page: Any, url: Any) -> dict[str, str]:
        return {}
    
    # Act & Assert
    with pytest.raises(TypeError, match="all URLs must be strings"):
        parallel_scrape(urls, scrape_func)  # type: ignore


def test_parallel_scrape_non_callable_scrape_function() -> None:
    """
    Test case 11: TypeError for non-callable scrape_function.
    """
    # Arrange
    urls = ["https://example.com"]
    
    # Act & Assert
    with pytest.raises(TypeError, match="scrape_function must be callable"):
        parallel_scrape(urls, "not_callable")  # type: ignore


def test_parallel_scrape_invalid_max_workers() -> None:
    """
    Test case 12: ValueError for non-positive max_workers.
    """
    # Arrange
    urls = ["https://example.com"]
    
    def scrape_func(page: Any, url: Any) -> dict[str, str]:
        return {}
    
    # Act & Assert
    with pytest.raises(ValueError, match="max_workers must be positive"):
        parallel_scrape(urls, scrape_func, max_workers=0)


def test_parallel_scrape_invalid_browser_type() -> None:
    """
    Test case 13: ValueError for invalid browser type.
    """
    # Arrange
    urls = ["https://example.com"]
    
    def scrape_func(page: Any, url: Any) -> dict[str, str]:
        return {}
    
    # Act & Assert
    with pytest.raises(ValueError, match="browser_type must be"):
        parallel_scrape(urls, scrape_func, browser_type="safari")


def test_parallel_scrape_invalid_timeout() -> None:
    """
    Test case 14: ValueError for non-positive timeout.
    """
    # Arrange
    urls = ["https://example.com"]
    
    def scrape_func(page: Any, url: Any) -> dict[str, str]:
        return {}
    
    # Act & Assert
    with pytest.raises(ValueError, match="timeout must be positive"):
        parallel_scrape(urls, scrape_func, timeout=-1000)


@patch("pyutils_collection.playwright_functions.parallel_scrape.sync_playwright")
def test_parallel_scrape_with_logger(mock_sync_playwright: Mock, caplog: pytest.LogCaptureFixture) -> None:
    """
    Test case 15: Parallel scraping with logging enabled.
    """
    # Arrange
    import logging
    logger = logging.getLogger("test_logger")
    
    mock_playwright = MagicMock()
    mock_browser = MagicMock()
    mock_context = MagicMock()
    mock_page = MagicMock()
    
    mock_sync_playwright.return_value.start.return_value = mock_playwright
    mock_playwright.chromium.launch.return_value = mock_browser
    mock_browser.new_context.return_value = mock_context
    mock_context.new_page.return_value = mock_page
    
    urls = ["https://example.com"]
    
    def scrape_func(page: Any, url: Any) -> dict[str, str]:
        return {"data": "test"}
    
    # Act
    with caplog.at_level(logging.INFO):
        results = parallel_scrape(urls, scrape_func, logger=logger)
    
    # Assert
    assert "Starting parallel scrape" in caplog.text
    assert "Parallel scrape complete" in caplog.text


@patch("pyutils_collection.playwright_functions.parallel_scrape.sync_playwright")
def test_parallel_scrape_context_isolation(mock_sync_playwright: Mock) -> None:
    """
    Test case 16: Each worker gets isolated browser context.
    """
    # Arrange
    mock_playwright = MagicMock()
    mock_browser = MagicMock()
    mock_contexts = [MagicMock() for _ in range(3)]
    mock_pages = [MagicMock() for _ in range(3)]
    
    mock_sync_playwright.return_value.start.return_value = mock_playwright
    mock_playwright.chromium.launch.return_value = mock_browser
    mock_browser.new_context.side_effect = mock_contexts
    for i, ctx in enumerate(mock_contexts):
        ctx.new_page.return_value = mock_pages[i]
    
    urls = ["https://example.com/1", "https://example.com/2", "https://example.com/3"]
    
    def scrape_func(page: Any, url: Any) -> dict[str, str]:
        return {}
    
    # Act
    results = parallel_scrape(urls, scrape_func, max_workers=3)
    
    # Assert
    assert mock_browser.new_context.call_count == 3  # One context per URL
    for ctx in mock_contexts:
        ctx.close.assert_called_once()  # Each context closed


@patch("pyutils_collection.playwright_functions.parallel_scrape.sync_playwright")
def test_parallel_scrape_browser_cleanup_on_error(mock_sync_playwright: Mock) -> None:
    """
    Test case 17: Browser cleaned up even when errors occur.
    """
    # Arrange
    mock_playwright = MagicMock()
    mock_browser = MagicMock()
    mock_context = MagicMock()
    mock_page = MagicMock()
    
    mock_sync_playwright.return_value.start.return_value = mock_playwright
    mock_playwright.chromium.launch.return_value = mock_browser
    mock_browser.new_context.return_value = mock_context
    mock_context.new_page.return_value = mock_page
    
    urls = ["https://example.com"]
    
    def scrape_func(page: Any, url: Any) -> dict[str, str]:
        raise RuntimeError("Critical error")
    
    # Act
    results = parallel_scrape(urls, scrape_func)
    
    # Assert - browser should still be closed despite error
    mock_browser.close.assert_called_once()
    mock_playwright.stop.assert_called_once()
    assert results[0]["success"] is False


def test_parallel_scrape_invalid_logger_type() -> None:
    """
    Test case 18: TypeError for invalid logger type.
    """
    # Arrange
    urls = ["https://example.com"]
    
    def scrape_func(page: Any, url: Any) -> dict[str, str]:
        return {}
    
    # Act & Assert
    with pytest.raises(TypeError, match="logger must be an instance of logging.Logger"):
        parallel_scrape(urls, scrape_func, logger="not_a_logger")  # type: ignore
