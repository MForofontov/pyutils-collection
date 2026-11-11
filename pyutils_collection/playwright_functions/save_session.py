"""
Browser session saving for persistent authentication.

This module provides utilities for saving browser session state including
cookies, localStorage, and sessionStorage to JSON files for later restoration.
"""

import json
import logging
import os
import tempfile
from pathlib import Path
from typing import Any

from playwright.sync_api import BrowserContext


def save_session(
    context: BrowserContext,
    session_file: str,
    include_storage: bool = True,
    logger: logging.Logger | None = None,
) -> None:
    """
    Save browser session state (cookies and storage) to file.

    Exports cookies, localStorage, and sessionStorage from browser context
    to JSON file for later restoration. Enables session persistence across
    multiple scraping runs without re-authentication.

    Parameters
    ----------
    context : BrowserContext
        Playwright BrowserContext to save session from.
    session_file : str
        Path to save session JSON file.
    include_storage : bool, optional
        Include localStorage and sessionStorage (by default True).
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
    RuntimeError
        If session save fails.

    Examples
    --------
    >>> from playwright.sync_api import sync_playwright
    >>> with sync_playwright() as p:
    ...     browser = p.chromium.launch()
    ...     context = browser.new_context()
    ...     page = context.new_page()
    ...     page.goto("https://example.com")
    ...     # ... perform login ...
    ...     save_session(context, "session.json")
    ...     browser.close()

    >>> # Session can be restored later
    >>> from playwright_functions import restore_session
    >>> with sync_playwright() as p:
    ...     browser = p.chromium.launch()
    ...     context = browser.new_context()
    ...     restore_session(context, "session.json")
    ...     # Session restored, no need to login again

    Notes
    -----
    - Session file contains sensitive data (cookies, tokens)
    - Store session files securely
    - Session expiration depends on cookie expiry settings
    - localStorage and sessionStorage are page-specific
    - Files are replaced atomically after successful serialization and use
      temporary-file permissions; failures preserve an existing session file

    Complexity
    ----------
    Time: O(n) where n is number of cookies/storage items, Space: O(n)
    """
    # Input validation
    if not isinstance(session_file, str):
        raise TypeError(
            f"session_file must be a string, got {type(session_file).__name__}"
        )
    if not session_file:
        raise ValueError("session_file cannot be empty")

    if not isinstance(include_storage, bool):
        raise TypeError(
            f"include_storage must be a boolean, got {type(include_storage).__name__}"
        )

    if logger is not None and not isinstance(logger, logging.Logger):
        raise TypeError("logger must be an instance of logging.Logger or None")

    try:
        if logger:
            logger.debug(f"Saving session to: {session_file}")

        # Get cookies
        cookies = context.cookies()
        if logger:
            logger.debug(f"Retrieved {len(cookies)} cookies")

        # Initialize session data
        session_data: dict[str, Any] = {
            "cookies": cookies,
            "storage": {},
        }

        # Get storage data if requested
        if include_storage:
            # Get all pages in context
            pages = context.pages
            if pages:
                page = pages[0]  # Use first page

                # Get localStorage
                try:
                    local_storage = page.evaluate("() => Object.entries(localStorage)")
                    session_data["storage"]["localStorage"] = dict(local_storage)
                    if logger:
                        logger.debug(
                            f"Retrieved {len(local_storage)} localStorage items"
                        )
                except Exception as e:
                    if logger:
                        logger.warning(f"Could not retrieve localStorage: {e}")
                    session_data["storage"]["localStorage"] = {}

                # Get sessionStorage
                try:
                    session_storage = page.evaluate(
                        "() => Object.entries(sessionStorage)"
                    )
                    session_data["storage"]["sessionStorage"] = dict(session_storage)
                    if logger:
                        logger.debug(
                            f"Retrieved {len(session_storage)} sessionStorage items"
                        )
                except Exception as e:
                    if logger:
                        logger.warning(f"Could not retrieve sessionStorage: {e}")
                    session_data["storage"]["sessionStorage"] = {}

        # Create parent directory if needed
        session_path = Path(session_file)
        session_path.parent.mkdir(parents=True, exist_ok=True)

        # Stage beside the destination so failed writes preserve the old session.
        temporary_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=session_path.parent,
                prefix=".session-",
                delete=False,
            ) as f:
                temporary_path = Path(f.name)
                json.dump(session_data, f, indent=2)
                f.flush()
                os.fsync(f.fileno())
            os.replace(temporary_path, session_path)
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)

        if logger:
            logger.info(f"Session saved successfully: {session_file}")

    except Exception as e:
        error_msg = f"Failed to save session: {e}"
        if logger:
            logger.error(error_msg, exc_info=True)
        raise RuntimeError(error_msg) from e


__all__ = ["save_session"]
