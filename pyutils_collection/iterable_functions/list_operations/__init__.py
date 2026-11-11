"""
List operation utilities.

Functions for manipulating and working with lists, including chunking,
finding duplicates, handling subsets, and list transformations.
"""

from .add_strings_to_subsets import add_strings_to_subsets
from .check_if_all_elements_are_duplicates import check_if_all_elements_are_duplicates
from .divide_list_into_n_chunks import divide_list_into_n_chunks
from .find_duplicates import find_duplicates
from .get_duplicates import get_duplicates
from .get_unique_sublists import get_unique_sublists
from .group_by import group_by
from .is_nested_list_empty import is_nested_list_empty
from .repeat_strings_in_a_list import repeat_strings_in_a_list
from .sliding_window import sliding_window
from .unique_by import unique_by

__all__ = [
    "unique_by",
    "add_strings_to_subsets",
    "check_if_all_elements_are_duplicates",
    "divide_list_into_n_chunks",
    "find_duplicates",
    "get_duplicates",
    "get_unique_sublists",
    "group_by",
    "is_nested_list_empty",
    "repeat_strings_in_a_list",
    "sliding_window",
]
