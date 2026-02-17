"""Unit tests for managed_browser context manager."""

from unittest.mock import MagicMock, Mock, patch

import pytest

try:
    from pyutils_collection.playwright_functions.managed_browser import managed_browser
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    managed_browser = None  # type: ignore

pytestmark = [
    pytest.mark.unit,
    pytest.mark.playwright_functions,
    pytest.mark.skipif(not PLAYWRIGHT_AVAILABLE, reason="playwright not installed"),
]


@patch("pyutils_collection.playwright_functions.managed_browser.sync_playwright")
def test_managed_browser_basic_success(mock_sync_playwright: Mock) -> None:
    """
    Test case 1: Basic browser management with default settings.
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
    
    # Act
    with managed_browser() as (browser, context, page):
        assert browser == mock_browser
        assert context == mock_context
        assert page == mock_page
    
    # Assert
    mock_playwright.chromium.launch.assert_called_once_with(headless=True)
    mock_browser.close.assert_called_once()
    mock_playwright.stop.assert_called_once()


@patch("pyutils_collection.playwright_functions.managed_browser.sync_playwright")
def test_managed_browser_firefox_browser(mock_sync_playwright: Mock) -> None:
    """
    Test case 2: Launch Firefox browser.
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
    
    # Act
    with managed_browser(browser_type="firefox") as (browser, context, page):
        pass
    
    # Assert
    mock_playwright.firefox.launch.assert_called_once_with(headless=True)


@patch("pyutils_collection.playwright_functions.managed_browser.sync_playwright")
def test_managed_browser_headless_false(mock_sync_playwright: Mock) -> None:
    """
    Test case 3: Launch browser in non-headless mode.
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
    
    # Act
    with managed_browser(headless=False) as (browser, context, page):
        pass
    
    # Assert
    mock_playwright.chromium.launch.assert_called_once_with(headless=False)


@patch("pyutils_collection.playwright_functions.managed_browser.sync_playwright")
def test_managed_browser_custom_viewport(mock_sync_playwright: Mock) -> None:
    """
    Test case 4: Custom viewport dimensions.
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
    
    # Act
    with managed_browser(viewport_width=1280, viewport_height=720) as (browser, context, page):
        pass
    
    # Assert
    call_args = mock_browser.new_context.call_args
    assert call_args[1]["viewport"]["width"] == 1280
    assert call_args[1]["viewport"]["height"] == 720


@patch("pyutils_collection.playwright_functions.managed_browser.sync_playwright")
def test_managed_browser_custom_user_agent(mock_sync_playwright: Mock) -> None:
    """
    Test case 5: Custom user agent string.
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
    
    user_agent = "CustomBot/1.0"
    
    # Act
    with managed_browser(user_agent=user_agent) as (browser, context, page):
        pass
    
    # Assert
    call_args = mock_browser.new_context.call_args
    assert call_args[1]["user_agent"] == user_agent


@patch("pyutils_collection.playwright_functions.managed_browser.sync_playwright")
def test_managed_browser_custom_timeout(mock_sync_playwright: Mock) -> None:
    """
    Test case 6: Custom default timeout.
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
    
    # Act
    with managed_browser(timeout=60000) as (browser, context, page):
        pass
    
    # Assert
    mock_context.set_default_timeout.assert_called_once_with(60000)


@patch("pyutils_collection.playwright_functions.managed_browser.sync_playwright")
def test_managed_browser_cleanup_on_error(mock_sync_playwright: Mock) -> None:
    """
    Test case 7: Proper cleanup when error occurs during usage.
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
    
    # Act & Assert
    with pytest.raises(RuntimeError, match="Browser management failed"):
        with managed_browser() as (browser, context, page):
            raise ValueError("Test error")
    
    # Cleanup should still happen
    mock_page.close.assert_called_once()
    mock_context.close.assert_called_once()
    mock_browser.close.assert_called_once()
    mock_playwright.stop.assert_called_once()


def test_managed_browser_invalid_browser_type() -> None:
    """
    Test case 8: ValueError for invalid browser type.
    """
    # Act & Assert
    with pytest.raises(ValueError, match="browser_type must be"):
        with managed_browser(browser_type="safari"):  # type: ignore
            pass


def test_managed_browser_invalid_viewport_width() -> None:
    """
    Test case 9: ValueError for non-positive viewport width.
    """
    # Act & Assert
    with pytest.raises(ValueError, match="viewport_width must be positive"):
        with managed_browser(viewport_width=0):
            pass


def test_managed_browser_invalid_viewport_height() -> None:
    """
    Test case 10: ValueError for non-positive viewport height.
    """
    # Act & Assert
    with pytest.raises(ValueError, match="viewport_height must be positive"):
        with managed_browser(viewport_height=-100):
            pass


def test_managed_browser_invalid_timeout() -> None:
    """
    Test case 11: ValueError for non-positive timeout.
    """
    # Act & Assert
    with pytest.raises(ValueError, match="timeout must be positive"):
        with managed_browser(timeout=-1000):
            pass


def test_managed_browser_invalid_headless_type() -> None:
    """
    Test case 12: TypeError for invalid headless type.
    """
    # Act & Assert
    with pytest.raises(TypeError, match="headless must be a boolean"):
        with managed_browser(headless="yes"):  # type: ignore
            pass


@patch("pyutils_collection.playwright_functions.managed_browser.sync_playwright")
def test_managed_browser_with_logger(mock_sync_playwright: Mock, caplog: pytest.LogCaptureFixture) -> None:
    """
    Test case 13: Browser management with logging enabled.
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
    
    # Act
    with caplog.at_level(logging.DEBUG):
        with managed_browser(logger=logger) as (browser, context, page):
            pass
    
    # Assert
    assert "Playwright started" in caplog.text
    assert "Browser launched" in caplog.text


@patch("pyutils_collection.playwright_functions.managed_browser.sync_playwright")
def test_managed_browser_webkit_browser(mock_sync_playwright: Mock) -> None:
    """
    Test case 14: Launch WebKit browser.
    """
    # Arrange
    mock_playwright = MagicMock()
    mock_browser = MagicMock()
    mock_context = MagicMock()
    mock_page = MagicMock()
    
    mock_sync_playwright.return_value.start.return_value = mock_playwright
    mock_playwright.webkit.launch.return_value = mock_browser
    mock_browser.new_context.return_value = mock_context
    mock_context.new_page.return_value = mock_page
    
    # Act
    with managed_browser(browser_type="webkit") as (browser, context, page):
        pass
    
    # Assert
    mock_playwright.webkit.launch.assert_called_once_with(headless=True)


@patch("pyutils_collection.playwright_functions.managed_browser.sync_playwright")
@patch("pyutils_collection.playwright_functions.managed_browser.Path")
def test_managed_browser_with_downloads_path(mock_path: Mock, mock_sync_playwright: Mock) -> None:
    """
    Test case 15: Browser with downloads path configured.
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
    
    mock_path_instance = MagicMock()
    mock_path.return_value = mock_path_instance
    
    # Act
    with managed_browser(downloads_path="/tmp/downloads") as (browser, context, page):
        pass
    
    # Assert
    mock_path_instance.mkdir.assert_called_once_with(parents=True, exist_ok=True)
    call_args = mock_browser.new_context.call_args
    assert call_args[1]["accept_downloads"] is True


@patch("pyutils_collection.playwright_functions.managed_browser.sync_playwright")
def test_managed_browser_launch_failure(mock_sync_playwright: Mock) -> None:
    """
    Test case 16: RuntimeError when browser launch fails.
    """
    # Arrange
    mock_playwright = MagicMock()
    mock_sync_playwright.return_value.start.return_value = mock_playwright
    mock_playwright.chromium.launch.side_effect = Exception("Launch failed")
    
    # Act & Assert
    with pytest.raises(RuntimeError, match="Browser management failed"):
        with managed_browser() as (browser, context, page):
            pass


@patch("pyutils_collection.playwright_functions.managed_browser.sync_playwright")
def test_managed_browser_invalid_logger_type(mock_sync_playwright: Mock) -> None:
    """
    Test case 17: TypeError for invalid logger type.
    """
    # Arrange
    mock_playwright = MagicMock()
    mock_browser = MagicMock()
    mock_sync_playwright.return_value.start.return_value = mock_playwright
    mock_playwright.chromium.launch.return_value = mock_browser
    
    # Act & Assert
    with pytest.raises(TypeError, match="logger must be an instance of logging.Logger"):
        with managed_browser(logger="not_a_logger"):  # type: ignore
            pass
