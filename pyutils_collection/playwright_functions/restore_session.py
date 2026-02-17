"""
Browser session restoration for reusing authentication.

This module provides utilities for restoring browser session state from
saved JSON files, enabling continuation of authenticated sessions.
"""

import json
import logging
from pathlib import Path
from typing import Any

from playwright.sync_api import BrowserContext


def restore_session(
    context: BrowserContext,
    session_file: str,
    url: str | None = None,
    logger: logging.Logger | None = None,
) -> None:
    """
    Restore browser session state from file.

    Restores cookies, localStorage, and sessionStorage from previously saved
    session file. Enables continuing authenticated sessions without re-login.

    Parameters
    ----------
    context : BrowserContext
        Playwright BrowserContext to restore session into.
    session_file : str
        Path to session JSON file.
    url : str | None, optional
        URL to navigate to for setting storage (by default None).
        Required if session file contains localStorage/sessionStorage.
    logger : logging.Logger | None, optional
        Logger instance for debugging (by default None).

    Raises
    ------
    ImportError
        If playwright is not installed.
    TypeError
        If parameters are of wrong type.
    ValueError
        If parameters have invalid values.
    FileNotFoundError
        If session file doesn't exist.
    RuntimeError
        If session restoration fails.

    Examples
    --------
    >>> from playwright.sync_api import sync_playwright
    >>> with sync_playwright() as p:
    ...     browser = p.chromium.launch()
    ...     context = browser.new_context()
    ...     restore_session(context, "session.json", url="https://example.com")
    ...     page = context.new_page()
    ...     page.goto("https://example.com")
    ...     # Session restored, user already logged in

    Notes
    -----
    - Cookies are restored at context level (work for all pages)
    - localStorage/sessionStorage require navigating to URL first
    - URL must match the domain where storage was saved
    - Some sites may require additional validation after restoration

    Complexity
    ----------
    Time: O(n) where n is number of cookies/storage items, Space: O(n)
    """
    # Input validation
    if not isinstance(session_file, str):
        raise TypeError(f"session_file must be a string, got {type(session_file).__name__}")
    if not session_file:
        raise ValueError("session_file cannot be empty")

    if url is not None and not isinstance(url, str):
        raise TypeError(f"url must be a string or None, got {type(url).__name__}")

    if logger is not None and not isinstance(logger, logging.Logger):
        raise TypeError("logger must be an instance of logging.Logger or None")

    # Check file exists
    session_path = Path(session_file)
    if not session_path.exists():
        raise FileNotFoundError(f"Session file not found: {session_file}")

    try:
        if logger:
            logger.debug(f"Restoring session from: {session_file}")

        # Load session data
        with open(session_path) as f:
            session_data = json.load(f)

        # Restore cookies
        cookies = session_data.get("cookies", [])
        if cookies:
            context.add_cookies(cookies)
            if logger:
                logger.debug(f"Restored {len(cookies)} cookies")

        # Restore storage if present
        storage = session_data.get("storage", {})
        local_storage = storage.get("localStorage", {})
        session_storage = storage.get("sessionStorage", {})

        if (local_storage or session_storage) and not url:
            raise ValueError("url is required to restore localStorage/sessionStorage")

        if local_storage or session_storage:
            # Need to navigate to URL to set storage
            if url is None:
                raise ValueError("url must be provided when restoring local_storage or session_storage")
            
            pages = context.pages
            if not pages:
                page = context.new_page()
            else:
                page = pages[0]

            if logger:
                logger.debug(f"Navigating to {url} to set storage")
            page.goto(url)

            # Set localStorage
            if local_storage:
                for key, value in local_storage.items():
                    page.evaluate(f"localStorage.setItem({json.dumps(key)}, {json.dumps(value)})")
                if logger:
                    logger.debug(f"Restored {len(local_storage)} localStorage items")

            # Set sessionStorage
            if session_storage:
                for key, value in session_storage.items():
                    page.evaluate(f"sessionStorage.setItem({json.dumps(key)}, {json.dumps(value)})")
                if logger:
                    logger.debug(f"Restored {len(session_storage)} sessionStorage items")

        if logger:
            logger.info(f"Session restored successfully from: {session_file}")

    except Exception as e:
        error_msg = f"Failed to restore session: {e}"
        if logger:
            logger.error(error_msg, exc_info=True)
        raise RuntimeError(error_msg) from e


__all__ = ["restore_session"]
