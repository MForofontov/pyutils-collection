"""Unit tests for extract_dynamic_content function."""

from unittest.mock import MagicMock, Mock

import pytest

try:
    from pyutils_collection.playwright_functions.extract_dynamic_content import extract_dynamic_content
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    extract_dynamic_content = None  # type: ignore

pytestmark = [
    pytest.mark.unit,
    pytest.mark.playwright_functions,
    pytest.mark.skipif(not PLAYWRIGHT_AVAILABLE, reason="playwright not installed"),
]


def test_extract_dynamic_content_basic_success() -> None:
    """
    Test case 1: Basic content extraction with default settings.
    """
    # Arrange
    mock_page = MagicMock()
    mock_page.url = "https://example.com"
    mock_page.title.return_value = "Example Page"
    mock_page.evaluate.return_value = "Page content text"
    
    mock_response = MagicMock()
    mock_response.status = 200
    mock_page.goto.return_value = mock_response
    
    # Act
    result = extract_dynamic_content(mock_page, "https://example.com")
    
    # Assert
    assert result["url"] == "https://example.com"
    assert result["title"] == "Example Page"
    assert result["text"] == "Page content text"
    assert result["html"] is None
    assert result["status"] == 200


def test_extract_dynamic_content_with_html() -> None:
    """
    Test case 2: Extract both text and HTML.
    """
    # Arrange
    mock_page = MagicMock()
    mock_page.url = "https://example.com"
    mock_page.title.return_value = "Test"
    mock_page.evaluate.return_value = "Text content"
    mock_page.content.return_value = "<html>content</html>"
    
    mock_response = MagicMock()
    mock_response.status = 200
    mock_page.goto.return_value = mock_response
    
    # Act
    result = extract_dynamic_content(
        mock_page,
        "https://example.com",
        extract_text=True,
        extract_html=True
    )
    
    # Assert
    assert result["text"] == "Text content"
    assert result["html"] == "<html>content</html>"


def test_extract_dynamic_content_wait_selector() -> None:
    """
    Test case 3: Wait for specific selector before extraction.
    """
    # Arrange
    mock_page = MagicMock()
    mock_page.url = "https://example.com"
    mock_page.title.return_value = "Loaded"
    mock_page.evaluate.return_value = "Content"
    
    mock_response = MagicMock()
    mock_response.status = 200
    mock_page.goto.return_value = mock_response
    
    # Act
    result = extract_dynamic_content(
        mock_page,
        "https://example.com",
        wait_strategy="selector",
        wait_selector="#content"
    )
    
    # Assert
    assert result["text"] == "Content"
    mock_page.wait_for_selector.assert_called_once_with("#content", timeout=30000)


def test_extract_dynamic_content_wait_function() -> None:
    """
    Test case 4: Wait for custom JavaScript function.
    """
    # Arrange
    mock_page = MagicMock()
    mock_page.url = "https://example.com"
    mock_page.title.return_value = "Ready"
    mock_page.evaluate.return_value = "Data"
    
    mock_response = MagicMock()
    mock_response.status = 200
    mock_page.goto.return_value = mock_response
    
    # Act
    result = extract_dynamic_content(
        mock_page,
        "https://example.com",
        wait_strategy="function",
        wait_function="() => window.loaded === true"
    )
    
    # Assert
    assert result["text"] == "Data"
    mock_page.wait_for_function.assert_called_once_with(
        "() => window.loaded === true",
        timeout=30000
    )


def test_extract_dynamic_content_extract_selector() -> None:
    """
    Test case 5: Extract content from specific element only.
    """
    # Arrange
    mock_page = MagicMock()
    mock_page.url = "https://example.com"
    mock_page.title.return_value = "Page"
    
    mock_element = MagicMock()
    mock_element.text_content.return_value = "Element text"
    mock_locator = MagicMock()
    mock_locator.first = mock_element
    mock_page.locator.return_value = mock_locator
    
    mock_response = MagicMock()
    mock_response.status = 200
    mock_page.goto.return_value = mock_response
    
    # Act
    result = extract_dynamic_content(
        mock_page,
        "https://example.com",
        extract_selector="#main"
    )
    
    # Assert
    assert result["text"] == "Element text"
    mock_page.locator.assert_called_with("#main")


def test_extract_dynamic_content_no_url_provided() -> None:
    """
    Test case 6: Extract from current page without navigation.
    """
    # Arrange
    mock_page = MagicMock()
    mock_page.url = "https://current.com"
    mock_page.title.return_value = "Current"
    mock_page.evaluate.return_value = "Current content"
    
    # Act
    result = extract_dynamic_content(mock_page, url=None)
    
    # Assert
    assert result["url"] == "https://current.com"
    assert result["text"] == "Current content"
    mock_page.goto.assert_not_called()


def test_extract_dynamic_content_networkidle_strategy() -> None:
    """
    Test case 7: Use networkidle wait strategy.
    """
    # Arrange
    mock_page = MagicMock()
    mock_page.url = "https://example.com"
    mock_page.title.return_value = "Test"
    mock_page.evaluate.return_value = "Text"
    
    mock_response = MagicMock()
    mock_response.status = 200
    mock_page.goto.return_value = mock_response
    
    # Act
    result = extract_dynamic_content(
        mock_page,
        "https://example.com",
        wait_strategy="networkidle"
    )
    
    # Assert
    assert result["text"] == "Text"
    call_args = mock_page.goto.call_args
    assert call_args[1]["wait_until"] == "networkidle"


def test_extract_dynamic_content_invalid_url_type() -> None:
    """
    Test case 8: TypeError for invalid URL type.
    """
    # Arrange
    mock_page = MagicMock()
    
    # Act & Assert
    with pytest.raises(TypeError, match="url must be a string or None"):
        extract_dynamic_content(mock_page, url=123)  # type: ignore


def test_extract_dynamic_content_invalid_wait_strategy() -> None:
    """
    Test case 9: ValueError for invalid wait strategy.
    """
    # Arrange
    mock_page = MagicMock()
    
    # Act & Assert
    with pytest.raises(ValueError, match="wait_strategy must be one of"):
        extract_dynamic_content(mock_page, "https://example.com", wait_strategy="invalid")  # type: ignore


def test_extract_dynamic_content_selector_strategy_missing_selector() -> None:
    """
    Test case 10: ValueError when selector strategy lacks wait_selector.
    """
    # Arrange
    mock_page = MagicMock()
    
    # Act & Assert
    with pytest.raises(ValueError, match="wait_selector is required"):
        extract_dynamic_content(
            mock_page,
            "https://example.com",
            wait_strategy="selector"
        )


def test_extract_dynamic_content_function_strategy_missing_function() -> None:
    """
    Test case 11: ValueError when function strategy lacks wait_function.
    """
    # Arrange
    mock_page = MagicMock()
    
    # Act & Assert
    with pytest.raises(ValueError, match="wait_function is required"):
        extract_dynamic_content(
            mock_page,
            "https://example.com",
            wait_strategy="function"
        )


def test_extract_dynamic_content_invalid_timeout() -> None:
    """
    Test case 12: ValueError for non-positive timeout.
    """
    # Arrange
    mock_page = MagicMock()
    
    # Act & Assert
    with pytest.raises(ValueError, match="timeout must be positive"):
        extract_dynamic_content(mock_page, "https://example.com", timeout=-1000)


def test_extract_dynamic_content_invalid_extract_text_type() -> None:
    """
    Test case 13: TypeError for invalid extract_text type.
    """
    # Arrange
    mock_page = MagicMock()
    
    # Act & Assert
    with pytest.raises(TypeError, match="extract_text must be a boolean"):
        extract_dynamic_content(mock_page, "https://example.com", extract_text="yes")  # type: ignore


def test_extract_dynamic_content_custom_timeout() -> None:
    """
    Test case 14: Custom timeout value.
    """
    # Arrange
    mock_page = MagicMock()
    mock_page.url = "https://example.com"
    mock_page.title.return_value = "Test"
    mock_page.evaluate.return_value = "Content"
    
    mock_response = MagicMock()
    mock_response.status = 200
    mock_page.goto.return_value = mock_response
    
    # Act
    result = extract_dynamic_content(
        mock_page,
        "https://example.com",
        timeout=60000
    )
    
    # Assert
    assert result["text"] == "Content"
    call_args = mock_page.goto.call_args
    assert call_args[1]["timeout"] == 60000


def test_extract_dynamic_content_with_logger(caplog: pytest.LogCaptureFixture) -> None:
    """
    Test case 15: Content extraction with logging enabled.
    """
    # Arrange
    import logging
    logger = logging.getLogger("test_logger")
    mock_page = MagicMock()
    mock_page.url = "https://example.com"
    mock_page.title.return_value = "Test"
    mock_page.evaluate.return_value = "Content"
    
    mock_response = MagicMock()
    mock_response.status = 200
    mock_page.goto.return_value = mock_response
    
    # Act
    with caplog.at_level(logging.DEBUG):
        result = extract_dynamic_content(mock_page, "https://example.com", logger=logger)
    
    # Assert
    assert result["text"] == "Content"
    assert "Navigating to" in caplog.text


def test_extract_dynamic_content_navigation_failure() -> None:
    """
    Test case 16: RuntimeError on navigation failure.
    """
    # Arrange
    mock_page = MagicMock()
    mock_page.goto.side_effect = Exception("Navigation failed")
    
    # Act & Assert
    with pytest.raises(RuntimeError, match="Failed to extract dynamic content"):
        extract_dynamic_content(mock_page, "https://example.com")


def test_extract_dynamic_content_only_html_no_text() -> None:
    """
    Test case 17: Extract only HTML without text.
    """
    # Arrange
    mock_page = MagicMock()
    mock_page.url = "https://example.com"
    mock_page.title.return_value = "Page"
    mock_page.content.return_value = "<html><body>Content</body></html>"
    
    mock_response = MagicMock()
    mock_response.status = 200
    mock_page.goto.return_value = mock_response
    
    # Act
    result = extract_dynamic_content(
        mock_page,
        "https://example.com",
        extract_text=False,
        extract_html=True
    )
    
    # Assert
    assert result["text"] is None
    assert result["html"] == "<html><body>Content</body></html>"


def test_extract_dynamic_content_load_strategy() -> None:
    """
    Test case 18: Use 'load' wait strategy.
    """
    # Arrange
    mock_page = MagicMock()
    mock_page.url = "https://example.com"
    mock_page.title.return_value = "Test"
    mock_page.evaluate.return_value = "Content"
    
    mock_response = MagicMock()
    mock_response.status = 200
    mock_page.goto.return_value = mock_response
    
    # Act
    result = extract_dynamic_content(
        mock_page,
        "https://example.com",
        wait_strategy="load"
    )
    
    # Assert
    assert result["text"] == "Content"
    call_args = mock_page.goto.call_args
    assert call_args[1]["wait_until"] == "load"
