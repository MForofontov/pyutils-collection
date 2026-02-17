"""Unit tests for smart_screenshot function."""

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

try:
    from pyutils_collection.playwright_functions.smart_screenshot import smart_screenshot
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    smart_screenshot = None  # type: ignore

pytestmark = [
    pytest.mark.unit,
    pytest.mark.playwright_functions,
    pytest.mark.skipif(not PLAYWRIGHT_AVAILABLE, reason="playwright not installed"),
]


def test_smart_screenshot_basic_success(tmp_path: Path) -> None:
    """
    Test case 1: Basic screenshot with default parameters.
    """
    # Arrange
    mock_page = MagicMock()
    screenshot_path = str(tmp_path / "test.png")
    mock_page.screenshot.return_value = None
    
    # Act
    result = smart_screenshot(mock_page, screenshot_path)
    
    # Assert
    assert result == screenshot_path
    mock_page.screenshot.assert_called_once()
    assert Path(screenshot_path).parent.exists()


def test_smart_screenshot_with_selector(tmp_path: Path) -> None:
    """
    Test case 2: Screenshot of specific element using selector.
    """
    # Arrange
    mock_page = MagicMock()
    mock_element = MagicMock()
    mock_locator = MagicMock()
    mock_locator.first = mock_element
    mock_page.locator.return_value = mock_locator
    screenshot_path = str(tmp_path / "element.png")
    
    # Act
    result = smart_screenshot(
        mock_page,
        screenshot_path,
        selector="#main-content"
    )
    
    # Assert
    assert result == screenshot_path
    mock_page.locator.assert_called_once_with("#main-content")
    mock_element.screenshot.assert_called_once()


def test_smart_screenshot_wait_for_selector(tmp_path: Path) -> None:
    """
    Test case 3: Screenshot with waiting for selector.
    """
    # Arrange
    mock_page = MagicMock()
    screenshot_path = str(tmp_path / "loaded.png")
    
    # Act
    result = smart_screenshot(
        mock_page,
        screenshot_path,
        wait_for_selector="#content",
        wait_timeout=5000
    )
    
    # Assert
    assert result == screenshot_path
    mock_page.wait_for_selector.assert_called_once_with("#content", timeout=5000)


def test_smart_screenshot_full_page(tmp_path: Path) -> None:
    """
    Test case 4: Full page screenshot.
    """
    # Arrange
    mock_page = MagicMock()
    screenshot_path = str(tmp_path / "fullpage.png")
    
    # Act
    result = smart_screenshot(mock_page, screenshot_path, full_page=True)
    
    # Assert
    assert result == screenshot_path
    call_args = mock_page.screenshot.call_args
    assert call_args[1]["full_page"] is True


def test_smart_screenshot_jpeg_with_quality(tmp_path: Path) -> None:
    """
    Test case 5: JPEG screenshot with quality setting.
    """
    # Arrange
    mock_page = MagicMock()
    screenshot_path = str(tmp_path / "image.jpeg")
    
    # Act
    result = smart_screenshot(
        mock_page,
        screenshot_path,
        image_type="jpeg",
        quality=85
    )
    
    # Assert
    assert result == screenshot_path
    call_args = mock_page.screenshot.call_args
    assert call_args[1]["type"] == "jpeg"
    assert call_args[1]["quality"] == 85


def test_smart_screenshot_retry_success(tmp_path: Path) -> None:
    """
    Test case 6: Successful screenshot after retry.
    """
    # Arrange
    mock_page = MagicMock()
    screenshot_path = str(tmp_path / "retry.png")
    # Fail twice, then succeed
    mock_page.screenshot.side_effect = [Exception("Timeout"), Exception("Render error"), None]
    
    # Act
    result = smart_screenshot(
        mock_page,
        screenshot_path,
        retries=3,
        retry_delay=0.1
    )
    
    # Assert
    assert result == screenshot_path
    assert mock_page.screenshot.call_count == 3


def test_smart_screenshot_invalid_path_type() -> None:
    """
    Test case 7: TypeError for non-string path.
    """
    # Arrange
    mock_page = MagicMock()
    
    # Act & Assert
    with pytest.raises(TypeError, match="path must be a string"):
        smart_screenshot(mock_page, 123)  # type: ignore


def test_smart_screenshot_empty_path() -> None:
    """
    Test case 8: ValueError for empty path.
    """
    # Arrange
    mock_page = MagicMock()
    
    # Act & Assert
    with pytest.raises(ValueError, match="path cannot be empty"):
        smart_screenshot(mock_page, "")


def test_smart_screenshot_invalid_selector_type(tmp_path: Path) -> None:
    """
    Test case 9: TypeError for invalid selector type.
    """
    # Arrange
    mock_page = MagicMock()
    screenshot_path = str(tmp_path / "test.png")
    
    # Act & Assert
    with pytest.raises(TypeError, match="selector must be a string or None"):
        smart_screenshot(mock_page, screenshot_path, selector=123)  # type: ignore


def test_smart_screenshot_invalid_timeout(tmp_path: Path) -> None:
    """
    Test case 10: ValueError for negative timeout.
    """
    # Arrange
    mock_page = MagicMock()
    screenshot_path = str(tmp_path / "test.png")
    
    # Act & Assert
    with pytest.raises(ValueError, match="wait_timeout must be positive"):
        smart_screenshot(mock_page, screenshot_path, wait_timeout=-100)


def test_smart_screenshot_invalid_image_type(tmp_path: Path) -> None:
    """
    Test case 11: ValueError for invalid image type.
    """
    # Arrange
    mock_page = MagicMock()
    screenshot_path = str(tmp_path / "test.gif")
    
    # Act & Assert
    with pytest.raises(ValueError, match="image_type must be 'png' or 'jpeg'"):
        smart_screenshot(mock_page, screenshot_path, image_type="gif")  # type: ignore


def test_smart_screenshot_quality_without_jpeg(tmp_path: Path) -> None:
    """
    Test case 12: ValueError for quality parameter with non-jpeg format.
    """
    # Arrange
    mock_page = MagicMock()
    screenshot_path = str(tmp_path / "test.png")
    
    # Act & Assert
    with pytest.raises(ValueError, match="quality parameter only applies to jpeg format"):
        smart_screenshot(mock_page, screenshot_path, image_type="png", quality=80)


def test_smart_screenshot_invalid_quality_range(tmp_path: Path) -> None:
    """
    Test case 13: ValueError for quality out of range.
    """
    # Arrange
    mock_page = MagicMock()
    screenshot_path = str(tmp_path / "test.jpeg")
    
    # Act & Assert
    with pytest.raises(ValueError, match="quality must be between 0-100"):
        smart_screenshot(mock_page, screenshot_path, image_type="jpeg", quality=150)


def test_smart_screenshot_negative_retries(tmp_path: Path) -> None:
    """
    Test case 14: ValueError for negative retries.
    """
    # Arrange
    mock_page = MagicMock()
    screenshot_path = str(tmp_path / "test.png")
    
    # Act & Assert
    with pytest.raises(ValueError, match="retries must be non-negative"):
        smart_screenshot(mock_page, screenshot_path, retries=-1)


def test_smart_screenshot_creates_parent_directory(tmp_path: Path) -> None:
    """
    Test case 15: Automatically creates parent directories.
    """
    # Arrange
    mock_page = MagicMock()
    screenshot_path = str(tmp_path / "nested" / "dir" / "test.png")
    
    # Act
    result = smart_screenshot(mock_page, screenshot_path)
    
    # Assert
    assert result == screenshot_path
    assert Path(screenshot_path).parent.exists()


def test_smart_screenshot_with_logger(tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
    """
    Test case 16: Screenshot with logging enabled.
    """
    # Arrange
    import logging
    logger = logging.getLogger("test_logger")
    mock_page = MagicMock()
    screenshot_path = str(tmp_path / "logged.png")
    
    # Act
    with caplog.at_level(logging.DEBUG):
        result = smart_screenshot(mock_page, screenshot_path, logger=logger)
    
    # Assert
    assert result == screenshot_path
    assert "Preparing screenshot" in caplog.text


def test_smart_screenshot_all_retries_exhausted(tmp_path: Path) -> None:
    """
    Test case 17: RuntimeError when all retries fail.
    """
    # Arrange
    mock_page = MagicMock()
    screenshot_path = str(tmp_path / "fail.png")
    mock_page.screenshot.side_effect = Exception("Persistent error")
    
    # Act & Assert
    with pytest.raises(RuntimeError, match="Screenshot failed after"):
        smart_screenshot(mock_page, screenshot_path, retries=2, retry_delay=0.01)


def test_smart_screenshot_network_idle_timeout_continues(tmp_path: Path) -> None:
    """
    Test case 18: Continues when network idle times out (non-critical).
    """
    # Arrange
    mock_page = MagicMock()
    screenshot_path = str(tmp_path / "test.png")
    mock_page.wait_for_load_state.side_effect = Exception("Timeout")
    
    # Act
    result = smart_screenshot(mock_page, screenshot_path)
    
    # Assert - should still succeed
    assert result == screenshot_path
    mock_page.screenshot.assert_called_once()
