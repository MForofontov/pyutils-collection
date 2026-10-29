"""
Browser lifecycle management with context manager for Playwright.

This module provides a context manager for managing Playwright browser
instances with automatic cleanup, error handling, and smart configuration.
"""

import logging
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Literal

from playwright.sync_api import (
    Browser,
    BrowserContext,
    Page,
    sync_playwright,
)

BrowserType = Literal["chromium", "firefox", "webkit"]


@contextmanager
def managed_browser(
    browser_type: BrowserType = "chromium",
    headless: bool = True,
    viewport_width: int = 1920,
    viewport_height: int = 1080,
    user_agent: str | None = None,
    downloads_path: str | None = None,
    timeout: float = 30000,
    logger: logging.Logger | None = None,
) -> Generator[tuple[Browser, BrowserContext, Page]]:
    """
    Context manager for Playwright browser with automatic lifecycle management.

    Provides automatic setup and teardown of browser, context, and page with
    error handling and resource cleanup. Includes smart defaults for common
    scraping scenarios.

    Parameters
    ----------
    browser_type : BrowserType, optional
        Browser to launch: 'chromium', 'firefox', or 'webkit' (by default "chromium").
    headless : bool, optional
        Whether to run in headless mode (by default True).
    viewport_width : int, optional
        Browser viewport width in pixels (by default 1920).
    viewport_height : int, optional
        Browser viewport height in pixels (by default 1080).
    user_agent : str | None, optional
        Custom user agent string (by default None, uses Playwright default).
    downloads_path : str | None, optional
        Path for downloaded files (by default None, uses temp directory).
    timeout : float, optional
        Default timeout in milliseconds for operations (by default 30000).
    logger : logging.Logger | None, optional
        Logger instance for debugging (by default None).

    Yields
    ------
    tuple[Browser, BrowserContext, Page]
        Tuple of (browser, context, page) instances for scraping.

    Raises
    ------
    ImportError
        If playwright is not installed.
    TypeError
        If parameters are of wrong type.
    ValueError
        If parameters have invalid values.
    RuntimeError
        If browser fails to launch or initialize.

    Examples
    --------
    >>> with managed_browser() as (browser, context, page):
    ...     page.goto("https://example.com")
    ...     content = page.content()
    >>> # Browser automatically closed

    >>> with managed_browser(browser_type="firefox", headless=False) as (_, _, page):
    ...     page.goto("https://example.com")
    ...     page.screenshot(path="screenshot.png")

    Notes
    -----
    - Automatically cleans up all resources (page, context, browser, playwright)
    - Logs errors and warnings for debugging
    - Sets sensible defaults for web scraping
    - Handles crashes and connection failures gracefully

    Complexity
    ----------
    Time: O(1) for setup/teardown, Space: O(1)
    """
    # Input validation
    if not isinstance(browser_type, str):
        raise TypeError(
            f"browser_type must be a string, got {type(browser_type).__name__}"
        )
    if browser_type not in ("chromium", "firefox", "webkit"):
        raise ValueError(
            f"browser_type must be 'chromium', 'firefox', or 'webkit', got {browser_type}"
        )

    if not isinstance(headless, bool):
        raise TypeError(f"headless must be a boolean, got {type(headless).__name__}")

    if not isinstance(viewport_width, int):
        raise TypeError(
            f"viewport_width must be an integer, got {type(viewport_width).__name__}"
        )
    if viewport_width <= 0:
        raise ValueError(f"viewport_width must be positive, got {viewport_width}")

    if not isinstance(viewport_height, int):
        raise TypeError(
            f"viewport_height must be an integer, got {type(viewport_height).__name__}"
        )
    if viewport_height <= 0:
        raise ValueError(f"viewport_height must be positive, got {viewport_height}")

    if user_agent is not None and not isinstance(user_agent, str):
        raise TypeError(
            f"user_agent must be a string or None, got {type(user_agent).__name__}"
        )

    if downloads_path is not None and not isinstance(downloads_path, str):
        raise TypeError(
            f"downloads_path must be a string or None, got {type(downloads_path).__name__}"
        )

    if not isinstance(timeout, (int, float)):
        raise TypeError(f"timeout must be a number, got {type(timeout).__name__}")
    if timeout <= 0:
        raise ValueError(f"timeout must be positive, got {timeout}")

    if logger is not None and not isinstance(logger, logging.Logger):
        raise TypeError("logger must be an instance of logging.Logger or None")

    # Initialize resources
    playwright_instance = None
    browser = None
    context = None
    page = None

    try:
        # Launch Playwright
        playwright_instance = sync_playwright().start()
        if logger:
            logger.debug(f"Playwright started, launching {browser_type} browser")

        # Get browser launcher
        browser_launcher = getattr(playwright_instance, browser_type)

        # Launch browser
        browser = browser_launcher.launch(headless=headless)
        if logger:
            logger.debug(f"Browser launched (headless={headless})")

        # Create context with configuration
        context_options: dict[str, Any] = {
            "viewport": {"width": viewport_width, "height": viewport_height},
        }

        if user_agent:
            context_options["user_agent"] = user_agent

        if downloads_path:
            Path(downloads_path).mkdir(parents=True, exist_ok=True)
            context_options["accept_downloads"] = True

        context = browser.new_context(**context_options)
        context.set_default_timeout(timeout)

        if logger:
            logger.debug(
                f"Context created with viewport {viewport_width}x{viewport_height}"
            )

        # Create page
        page = context.new_page()
        if logger:
            logger.debug("Page created, ready for navigation")

        # Yield control to user code
        yield browser, context, page

    except Exception as e:
        if logger:
            logger.error(f"Error in managed_browser: {e}", exc_info=True)
        raise RuntimeError(f"Browser management failed: {e}") from e

    finally:
        # Cleanup in reverse order
        if logger:
            logger.debug("Cleaning up browser resources")

        if page:
            try:
                page.close()
                if logger:
                    logger.debug("Page closed")
            except Exception as e:
                if logger:
                    logger.warning(f"Error closing page: {e}")

        if context:
            try:
                context.close()
                if logger:
                    logger.debug("Context closed")
            except Exception as e:
                if logger:
                    logger.warning(f"Error closing context: {e}")

        if browser:
            try:
                browser.close()
                if logger:
                    logger.debug("Browser closed")
            except Exception as e:
                if logger:
                    logger.warning(f"Error closing browser: {e}")

        if playwright_instance:
            try:
                playwright_instance.stop()
                if logger:
                    logger.debug("Playwright stopped")
            except Exception as e:
                if logger:
                    logger.warning(f"Error stopping Playwright: {e}")


__all__ = ["managed_browser"]
