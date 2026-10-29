"""
Parallel web page scraping with browser context pooling.

This module provides utilities for scraping multiple URLs in parallel
using browser context pooling for efficiency and error handling.
"""

import logging
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from playwright.sync_api import sync_playwright


def parallel_scrape(
    urls: list[str],
    scrape_function: Callable[[Any, str], dict[str, Any]],
    max_workers: int = 4,
    browser_type: str = "chromium",
    headless: bool = True,
    timeout: float = 30000,
    logger: logging.Logger | None = None,
) -> list[dict[str, Any]]:
    """
    Scrape multiple URLs in parallel with browser context pooling.

    Launches multiple browser contexts in parallel for efficient scraping.
    Each worker gets its own context but shares the same browser instance,
    reducing resource usage while maintaining isolation.

    Parameters
    ----------
    urls : list[str]
        List of URLs to scrape.
    scrape_function : Callable[[Page, str], dict[str, Any]]
        Function that takes (page, url) and returns scraped data dict.
        This function is called for each URL with a fresh page.
    max_workers : int, optional
        Maximum number of parallel workers/contexts (by default 4).
    browser_type : str, optional
        Browser type: 'chromium', 'firefox', or 'webkit' (by default "chromium").
    headless : bool, optional
        Run browsers in headless mode (by default True).
    timeout : float, optional
        Default timeout in milliseconds for operations (by default 30000).
    logger : logging.Logger | None, optional
        Logger instance for debugging (by default None).

    Returns
    -------
    list[dict[str, Any]]
        List of scraping results, one per URL. Each result dict contains:
        - 'url': str - The scraped URL
        - 'success': bool - Whether scraping succeeded
        - 'data': dict | None - Scraped data (from scrape_function)
        - 'error': str | None - Error message if failed

    Raises
    ------
    ImportError
        If playwright is not installed.
    TypeError
        If parameters are of wrong type.
    ValueError
        If parameters have invalid values.

    Examples
    --------
    >>> def scrape_page(page, url):
    ...     page.goto(url)
    ...     return {
    ...         'title': page.title(),
    ...         'text': page.evaluate("() => document.body.innerText")
    ...     }

    >>> urls = [
    ...     "https://example.com/page1",
    ...     "https://example.com/page2",
    ...     "https://example.com/page3",
    ... ]
    >>> results = parallel_scrape(urls, scrape_page, max_workers=2)
    >>> for result in results:
    ...     if result['success']:
    ...         print(f"Scraped {result['url']}: {result['data']['title']}")

    >>> # Custom scrape function with error handling
    >>> def scrape_with_retry(page, url):
    ...     page.goto(url, wait_until="networkidle")
    ...     page.wait_for_selector("#content")
    ...     return {
    ...         'content': page.locator("#content").text_content(),
    ...         'links': [a.get_attribute('href') for a in page.locator('a').all()]
    ...     }
    >>> results = parallel_scrape(
    ...     urls,
    ...     scrape_with_retry,
    ...     max_workers=5,
    ...     browser_type="firefox"
    ... )

    Notes
    -----
    - Each worker gets isolated browser context (separate cookies/storage)
    - All workers share same browser instance (efficient resource usage)
    - Failed scrapes return error dict instead of raising exception
    - Results maintain order matching input URL list
    - Consider rate limiting for production use

    Complexity
    ----------
    Time: O(n/w) where n is URLs, w is workers, Space: O(n)
    """
    # Input validation
    if not isinstance(urls, list):
        raise TypeError(f"urls must be a list, got {type(urls).__name__}")
    if not urls:
        raise ValueError("urls list cannot be empty")
    if not all(isinstance(url, str) for url in urls):
        raise TypeError("all URLs must be strings")

    if not callable(scrape_function):
        raise TypeError("scrape_function must be callable")

    if not isinstance(max_workers, int):
        raise TypeError(
            f"max_workers must be an integer, got {type(max_workers).__name__}"
        )
    if max_workers <= 0:
        raise ValueError(f"max_workers must be positive, got {max_workers}")

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

    if not isinstance(timeout, (int, float)):
        raise TypeError(f"timeout must be a number, got {type(timeout).__name__}")
    if timeout <= 0:
        raise ValueError(f"timeout must be positive, got {timeout}")

    if logger is not None and not isinstance(logger, logging.Logger):
        raise TypeError("logger must be an instance of logging.Logger or None")

    if logger:
        logger.info(
            f"Starting parallel scrape of {len(urls)} URLs with {max_workers} workers"
        )

    # Launch single browser (shared by all workers)
    playwright_instance = sync_playwright().start()
    browser_launcher = getattr(playwright_instance, browser_type)
    browser = browser_launcher.launch(headless=headless)

    if logger:
        logger.debug(f"{browser_type} browser launched (headless={headless})")

    try:
        # Create result storage (maintains URL order)
        results: list[dict[str, Any]] = [None] * len(urls)  # type: ignore

        # Worker function
        def scrape_url(index: int, url: str) -> tuple[int, dict[str, Any]]:
            """Scrape single URL in isolated context."""
            try:
                if logger:
                    logger.debug(f"Worker starting: {url}")

                # Create isolated context for this worker
                context = browser.new_context()
                context.set_default_timeout(timeout)

                # Create page
                page = context.new_page()

                try:
                    # Call user's scrape function
                    data = scrape_function(page, url)

                    result = {
                        "url": url,
                        "success": True,
                        "data": data,
                        "error": None,
                    }

                    if logger:
                        logger.debug(f"Worker completed successfully: {url}")

                    return index, result

                finally:
                    # Cleanup context (page closes automatically)
                    context.close()

            except Exception as e:
                error_msg = str(e)
                if logger:
                    logger.error(f"Worker failed for {url}: {error_msg}")

                result = {
                    "url": url,
                    "success": False,
                    "data": None,
                    "error": error_msg,
                }

                return index, result

        # Execute scraping in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all jobs
            futures = {
                executor.submit(scrape_url, i, url): i for i, url in enumerate(urls)
            }

            # Collect results as they complete
            for future in as_completed(futures):
                index, result = future.result()
                results[index] = result

                if logger:
                    status = "✓" if result["success"] else "✗"
                    completed = sum(1 for r in results if r is not None)
                    logger.info(f"{status} [{completed}/{len(urls)}] {result['url']}")

    finally:
        # Cleanup browser and playwright
        browser.close()
        playwright_instance.stop()

        if logger:
            logger.debug("Browser closed, playwright stopped")

    # Calculate stats
    successful = sum(1 for r in results if r["success"])
    failed = len(results) - successful

    if logger:
        logger.info(
            f"Parallel scrape complete: {successful} succeeded, {failed} failed"
        )

    return results


__all__ = ["parallel_scrape"]
