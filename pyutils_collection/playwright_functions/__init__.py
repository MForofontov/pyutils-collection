"""
Playwright utilities for browser automation and web scraping.

This module provides high-value utilities built on top of Playwright,
adding workflow logic, error handling, and convenience features for
common browser automation and web scraping tasks.

Functions
---------
managed_browser : Context manager for browser lifecycle
smart_screenshot : Intelligent screenshot with waiting and retry
extract_dynamic_content : Extract content after JavaScript rendering
save_session : Save browser session state to file
restore_session : Restore browser session from file
parallel_scrape : Scrape multiple URLs in parallel with context pooling
"""

from pyutils_collection._version import __version__

# Import functions (gracefully handle missing playwright)
try:
    from .managed_browser import managed_browser
    from .smart_screenshot import smart_screenshot
    from .extract_dynamic_content import extract_dynamic_content
    from .save_session import save_session
    from .restore_session import restore_session
    from .parallel_scrape import parallel_scrape

    __all__ = [
        "managed_browser",
        "smart_screenshot",
        "extract_dynamic_content",
        "save_session",
        "restore_session",
        "parallel_scrape",
        "__version__",
    ]
except ImportError as e:
    # Playwright not installed - provide helpful error message
    import warnings
    warnings.warn(
        f"playwright_functions requires playwright package. "
        f"Install with: pip install 'pyutils_collection[playwright]'. "
        f"Error: {e}",
        ImportWarning
    )

    __all__ = ["__version__"]
