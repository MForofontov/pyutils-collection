"""
Intelligent screenshot capture with automatic waiting and error handling.

This module provides utilities for taking screenshots with smart defaults,
automatic element waiting, viewport adjustments, and retry logic.
"""

import logging
from pathlib import Path
from typing import Any, Literal

from playwright.sync_api import Page

ScreenshotType = Literal["png", "jpeg"]


def smart_screenshot(
    page: Page,
    path: str,
    selector: str | None = None,
    wait_for_selector: str | None = None,
    wait_timeout: float = 30000,
    full_page: bool = False,
    image_type: ScreenshotType = "png",
    quality: int | None = None,
    retries: int = 3,
    retry_delay: float = 1.0,
    logger: logging.Logger | None = None,
) -> str:
    """
    Take screenshot with automatic waiting and intelligent error handling.

    Provides robust screenshot capture with automatic waiting for elements,
    viewport adjustment, retry logic, and error recovery. Handles common
    edge cases like slow loading, dynamic content, and rendering delays.

    Parameters
    ----------
    page : Page
        Playwright Page instance to screenshot.
    path : str
        Output file path for screenshot.
    selector : str | None, optional
        CSS selector for element to screenshot (by default None, captures full viewport).
    wait_for_selector : str | None, optional
        Wait for this selector before taking screenshot (by default None).
    wait_timeout : float, optional
        Timeout in milliseconds for waiting (by default 30000).
    full_page : bool, optional
        Capture full scrollable page (by default False).
    image_type : ScreenshotType, optional
        Output format: 'png' or 'jpeg' (by default "png").
    quality : int | None, optional
        JPEG quality 0-100, only for jpeg (by default None).
    retries : int, optional
        Number of retry attempts on failure (by default 3).
    retry_delay : float, optional
        Delay in seconds between retries (by default 1.0).
    logger : logging.Logger | None, optional
        Logger instance for debugging (by default None).

    Returns
    -------
    str
        Path to the saved screenshot file.

    Raises
    ------
    ImportError
        If playwright is not installed.
    TypeError
        If parameters are of wrong type.
    ValueError
        If parameters have invalid values.
    RuntimeError
        If screenshot fails after all retries.
    FileNotFoundError
        If output directory doesn't exist.

    Examples
    --------
    >>> from playwright.sync_api import sync_playwright
    >>> with sync_playwright() as p:
    ...     browser = p.chromium.launch()
    ...     page = browser.new_page()
    ...     page.goto("https://example.com")
    ...     smart_screenshot(page, "screenshot.png")
    ...     browser.close()
    'screenshot.png'

    >>> # Wait for specific element before screenshot
    >>> smart_screenshot(
    ...     page,
    ...     "loaded.png",
    ...     wait_for_selector="#content",
    ...     full_page=True
    ... )

    >>> # Screenshot specific element
    >>> smart_screenshot(
    ...     page,
    ...     "element.png",
    ...     selector="#main-content"
    ... )

    Notes
    -----
    - Automatically waits for network idle and load events
    - Retries on transient failures (rendering issues, timeouts)
    - Creates parent directories if they don't exist
    - Handles both element and full-page screenshots
    - JPEG quality only applies to jpeg format

    Complexity
    ----------
    Time: O(1) + network/rendering time, Space: O(image size)
    """
    # Input validation
    if not isinstance(path, str):
        raise TypeError(f"path must be a string, got {type(path).__name__}")
    if not path:
        raise ValueError("path cannot be empty")

    if selector is not None and not isinstance(selector, str):
        raise TypeError(
            f"selector must be a string or None, got {type(selector).__name__}"
        )

    if wait_for_selector is not None and not isinstance(wait_for_selector, str):
        raise TypeError(
            f"wait_for_selector must be a string or None, got {type(wait_for_selector).__name__}"
        )

    if not isinstance(wait_timeout, (int, float)):
        raise TypeError(
            f"wait_timeout must be a number, got {type(wait_timeout).__name__}"
        )
    if wait_timeout <= 0:
        raise ValueError(f"wait_timeout must be positive, got {wait_timeout}")

    if not isinstance(full_page, bool):
        raise TypeError(f"full_page must be a boolean, got {type(full_page).__name__}")

    if not isinstance(image_type, str):
        raise TypeError(f"image_type must be a string, got {type(image_type).__name__}")
    if image_type not in ("png", "jpeg"):
        raise ValueError(f"image_type must be 'png' or 'jpeg', got {image_type}")

    if quality is not None:
        if not isinstance(quality, int):
            raise TypeError(
                f"quality must be an integer or None, got {type(quality).__name__}"
            )
        if not 0 <= quality <= 100:
            raise ValueError(f"quality must be between 0-100, got {quality}")
        if image_type != "jpeg":
            raise ValueError("quality parameter only applies to jpeg format")

    if not isinstance(retries, int):
        raise TypeError(f"retries must be an integer, got {type(retries).__name__}")
    if retries < 0:
        raise ValueError(f"retries must be non-negative, got {retries}")

    if not isinstance(retry_delay, (int, float)):
        raise TypeError(
            f"retry_delay must be a number, got {type(retry_delay).__name__}"
        )
    if retry_delay < 0:
        raise ValueError(f"retry_delay must be non-negative, got {retry_delay}")

    if logger is not None and not isinstance(logger, logging.Logger):
        raise TypeError("logger must be an instance of logging.Logger or None")

    # Ensure output directory exists
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if logger:
        logger.debug(
            f"Preparing screenshot: path={path}, selector={selector}, full_page={full_page}"
        )

    # Retry logic
    import time

    last_error = None

    for attempt in range(retries + 1):
        try:
            # Wait for selector if specified
            if wait_for_selector:
                if logger:
                    logger.debug(f"Waiting for selector: {wait_for_selector}")
                page.wait_for_selector(wait_for_selector, timeout=wait_timeout)

            # Additional wait for network idle (helps with dynamic content)
            try:
                page.wait_for_load_state("networkidle", timeout=5000)
            except Exception:
                # Non-critical, continue anyway
                if logger:
                    logger.debug("Network idle timeout, continuing with screenshot")

            # Build screenshot options
            screenshot_options: dict[str, Any] = {
                "path": str(output_path),
                "type": image_type,
                "full_page": full_page,
            }

            if quality is not None and image_type == "jpeg":
                screenshot_options["quality"] = quality

            # Take screenshot
            if selector:
                # Screenshot specific element
                if logger:
                    logger.debug(f"Taking element screenshot: {selector}")
                element = page.locator(selector).first
                element.screenshot(
                    **{k: v for k, v in screenshot_options.items() if k != "full_page"}
                )
            else:
                # Screenshot page
                if logger:
                    logger.debug("Taking page screenshot")
                page.screenshot(**screenshot_options)

            if logger:
                logger.info(f"Screenshot saved successfully: {path}")

            return str(output_path)

        except Exception as e:
            last_error = e
            if logger:
                logger.warning(
                    f"Screenshot attempt {attempt + 1}/{retries + 1} failed: {e}"
                )

            if attempt < retries:
                if logger:
                    logger.debug(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                # Final attempt failed
                error_msg = (
                    f"Screenshot failed after {retries + 1} attempts: {last_error}"
                )
                if logger:
                    logger.error(error_msg)
                raise RuntimeError(error_msg) from last_error

    # Should never reach here, but for type safety
    raise RuntimeError(f"Screenshot failed: {last_error}")


__all__ = ["smart_screenshot"]
