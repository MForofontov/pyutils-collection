"""
Dictionary operation utilities.

Functions for working with dictionaries, including structure analysis,
value identification, recursive operations, sorting, and advanced utilities.
"""

from .deep_delete import deep_delete
from .deep_get import deep_get
from .deep_set import deep_set
from .dict_structural_difference import dict_structural_difference
from .dict_value_difference import dict_value_difference
from .filter_dict_by_keys import filter_dict_by_keys
from .flatten_dict import flatten_dict
from .identify_dict_structure import identify_dict_structure
from .identify_string_in_dict_lists_regex import (
    identify_string_in_dict_lists_regex,
)
from .identify_value_in_dict_get_key import identify_value_in_dict_get_key
from .invert_dict import invert_dict
from .merge_dicts_recursive import merge_dicts_recursive
from .remove_empty_dicts_recursive import remove_empty_dicts_recursive
from .sort_subdict_by_tuple import sort_subdict_by_tuple
from .unflatten_dict import unflatten_dict

__all__ = [
    "deep_delete",
    "unflatten_dict",
    "identify_dict_structure",
    "identify_string_in_dict_lists_regex",
    "identify_value_in_dict_get_key",
    "remove_empty_dicts_recursive",
    "sort_subdict_by_tuple",
    "merge_dicts_recursive",
    "flatten_dict",
    "filter_dict_by_keys",
    "invert_dict",
    "deep_get",
    "deep_set",
    "dict_structural_difference",
    "dict_value_difference",
]
