"""
Extract dynamic content from pages after JavaScript execution.

This module provides utilities for extracting content from JavaScript-heavy
pages with smart waiting strategies, automatic detection of content loading,
and flexible extraction patterns.
"""

import logging
from typing import Any, Literal, cast

from playwright.sync_api import Locator, Page


WaitStrategy = Literal["domcontentloaded", "load", "networkidle", "selector", "function"]


def extract_dynamic_content(
    page: Page,
    url: str | None = None,
    wait_strategy: WaitStrategy = "networkidle",
    wait_selector: str | None = None,
    wait_function: str | None = None,
    timeout: float = 30000,
    extract_text: bool = True,
    extract_html: bool = False,
    extract_selector: str | None = None,
    logger: logging.Logger | None = None,
) -> dict[str, Any]:
    """
    Extract content from page after JavaScript rendering with smart waiting.

    Navigates to URL (if provided), waits for content to load using specified
    strategy, then extracts text and/or HTML. Handles complex JavaScript
    applications with multiple loading stages.

    Parameters
    ----------
    page : Page
        Playwright Page instance to extract from.
    url : str | None, optional
        URL to navigate to (by default None, uses current page).
    wait_strategy : WaitStrategy, optional
        Loading strategy: 'domcontentloaded', 'load', 'networkidle',
        'selector', or 'function' (by default "networkidle").
    wait_selector : str | None, optional
        CSS selector to wait for (required if wait_strategy='selector') (by default None).
    wait_function : str | None, optional
        JavaScript function returning boolean (required if wait_strategy='function') (by default None).
    timeout : float, optional
        Timeout in milliseconds for waiting (by default 30000).
    extract_text : bool, optional
        Extract page text content (by default True).
    extract_html : bool, optional
        Extract page HTML (by default False).
    extract_selector : str | None, optional
        Extract only from this selector (by default None, extracts full page).
    logger : logging.Logger | None, optional
        Logger instance for debugging (by default None).

    Returns
    -------
    dict[str, Any]
        Dictionary with keys:
        - 'url': str - Final page URL (after redirects)
        - 'title': str - Page title
        - 'text': str | None - Extracted text (if extract_text=True)
        - 'html': str | None - Extracted HTML (if extract_html=True)
        - 'status': int - HTTP status code

    Raises
    ------
    ImportError
        If playwright is not installed.
    TypeError
        If parameters are of wrong type.
    ValueError
        If parameters have invalid values or missing required parameters.
    RuntimeError
        If navigation or content extraction fails.

    Examples
    --------
    >>> from playwright.sync_api import sync_playwright
    >>> with sync_playwright() as p:
    ...     browser = p.chromium.launch()
    ...     page = browser.new_page()
    ...     result = extract_dynamic_content(
    ...         page,
    ...         "https://example.com",
    ...         wait_strategy="networkidle"
    ...     )
    ...     print(result['title'])
    ...     browser.close()

    >>> # Wait for specific element before extraction
    >>> result = extract_dynamic_content(
    ...     page,
    ...     "https://spa-app.com",
    ...     wait_strategy="selector",
    ...     wait_selector="#loaded-indicator"
    ... )

    >>> # Wait for custom JavaScript condition
    >>> result = extract_dynamic_content(
    ...     page,
    ...     "https://complex-app.com",
    ...     wait_strategy="function",
    ...     wait_function="() => window.dataLoaded === true"
    ... )

    >>> # Extract from specific element only
    >>> result = extract_dynamic_content(
    ...     page,
    ...     "https://example.com",
    ...     extract_selector="#main-content",
    ...     extract_html=True
    ... )

    Notes
    -----
    - 'networkidle' waits for no network activity for 500ms
    - 'load' waits for load event
    - 'domcontentloaded' waits for DOMContentLoaded event
    - 'selector' waits for specific element to appear
    - 'function' waits for custom JavaScript condition
    - Always extracts URL, title, and status regardless of options

    Complexity
    ----------
    Time: O(n) where n is page content size, Space: O(n)
    """
    # Input validation
    if url is not None and not isinstance(url, str):
        raise TypeError(f"url must be a string or None, got {type(url).__name__}")

    if not isinstance(wait_strategy, str):
        raise TypeError(f"wait_strategy must be a string, got {type(wait_strategy).__name__}")
    valid_strategies = ("domcontentloaded", "load", "networkidle", "selector", "function")
    if wait_strategy not in valid_strategies:
        raise ValueError(f"wait_strategy must be one of {valid_strategies}, got {wait_strategy}")

    if wait_strategy == "selector" and wait_selector is None:
        raise ValueError("wait_selector is required when wait_strategy='selector'")

    if wait_strategy == "function" and wait_function is None:
        raise ValueError("wait_function is required when wait_strategy='function'")

    if wait_selector is not None and not isinstance(wait_selector, str):
        raise TypeError(f"wait_selector must be a string or None, got {type(wait_selector).__name__}")

    if wait_function is not None and not isinstance(wait_function, str):
        raise TypeError(f"wait_function must be a string or None, got {type(wait_function).__name__}")

    if not isinstance(timeout, (int, float)):
        raise TypeError(f"timeout must be a number, got {type(timeout).__name__}")
    if timeout <= 0:
        raise ValueError(f"timeout must be positive, got {timeout}")

    if not isinstance(extract_text, bool):
        raise TypeError(f"extract_text must be a boolean, got {type(extract_text).__name__}")

    if not isinstance(extract_html, bool):
        raise TypeError(f"extract_html must be a boolean, got {type(extract_html).__name__}")

    if extract_selector is not None and not isinstance(extract_selector, str):
        raise TypeError(f"extract_selector must be a string or None, got {type(extract_selector).__name__}")

    if logger is not None and not isinstance(logger, logging.Logger):
        raise TypeError("logger must be an instance of logging.Logger or None")

    try:
        # Navigate if URL provided
        response = None
        if url:
            if logger:
                logger.debug(f"Navigating to: {url}")

            # Navigate with specified wait strategy for load events
            if wait_strategy in ("domcontentloaded", "load", "networkidle"):
                response = page.goto(url, wait_until=wait_strategy, timeout=timeout)  # type: ignore
            else:
                # For selector/function strategies, use basic navigation
                response = page.goto(url, wait_until="commit", timeout=timeout)

            if logger:
                status = response.status if response else "unknown"
                logger.debug(f"Navigation complete, status: {status}")

        # Apply wait strategy
        if wait_strategy == "selector" and wait_selector:
            if logger:
                logger.debug(f"Waiting for selector: {wait_selector}")
            page.wait_for_selector(wait_selector, timeout=timeout)

        elif wait_strategy == "function" and wait_function:
            if logger:
                logger.debug(f"Waiting for function: {wait_function}")
            page.wait_for_function(wait_function, timeout=timeout)

        elif wait_strategy in ("domcontentloaded", "load", "networkidle"):
            # Already handled in goto, but wait again for current page if no navigation
            if not url:
                if logger:
                    logger.debug(f"Waiting for load state: {wait_strategy}")
                page.wait_for_load_state(wait_strategy, timeout=timeout)  # type: ignore

        if logger:
            logger.debug("Wait strategy completed successfully")

        # Extract content
        result: dict[str, Any] = {
            "url": page.url,
            "title": page.title(),
            "status": response.status if response else None,
            "text": None,
            "html": None,
        }

        # Determine extraction target
        target: Locator | Page
        if extract_selector:
            if logger:
                logger.debug(f"Extracting from selector: {extract_selector}")
            target = page.locator(extract_selector).first
        else:
            target = page

        # Extract text
        if extract_text:
            if extract_selector:
                # When extract_selector is set, target is always a Locator
                result["text"] = cast(Locator, target).text_content()
            else:
                result["text"] = page.evaluate("() => document.body.innerText")
            if logger:
                text_len = len(result["text"]) if result["text"] else 0
                logger.debug(f"Extracted text: {text_len} characters")

        # Extract HTML
        if extract_html:
            if extract_selector:
                # When extract_selector is set, target is always a Locator
                result["html"] = cast(Locator, target).inner_html()
            else:
                result["html"] = page.content()
            if logger:
                html_len = len(result["html"]) if result["html"] else 0
                logger.debug(f"Extracted HTML: {html_len} characters")

        if logger:
            logger.info(f"Content extracted successfully from {result['url']}")

        return result

    except Exception as e:
        error_msg = f"Failed to extract dynamic content: {e}"
        if logger:
            logger.error(error_msg, exc_info=True)
        raise RuntimeError(error_msg) from e


__all__ = ["extract_dynamic_content"]
