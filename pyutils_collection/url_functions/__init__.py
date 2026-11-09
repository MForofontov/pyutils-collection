"""
URL utilities for SEO, normalization, and manipulation.

This module provides advanced URL handling that adds workflow logic on top of
battle-tested packages like urllib. Includes slugification, normalization,
query parameter manipulation, template expansion, and pattern matching.
"""

from .expand_url_template import expand_url_template
from .match_url_pattern import match_url_pattern, validate_url_format
from .merge_query_params import merge_query_params
from .normalize_url import normalize_url
from .remove_query_params import remove_query_params
from .slugify_url import slugify_url

__all__ = [
    "remove_query_params",
    "slugify_url",
    "normalize_url",
    "merge_query_params",
    "expand_url_template",
    "match_url_pattern",
    "validate_url_format",
]
