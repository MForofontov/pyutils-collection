"""
Iterable functions utilities.

A collection of utilities for working with various iterable data structures
including lists, sets, dictionaries, and type operations.
"""

# Import submodules
from . import (
    dictionary_operations,
    list_comparison,
    list_operations,
    set_operations,
    type_operations,
)

# Explicit imports for all functions listed in __all__
from .dictionary_operations import (
    deep_delete,
    deep_get,
    deep_set,
    dict_structural_difference,
    dict_value_difference,
    filter_dict_by_keys,
    flatten_dict,
    identify_dict_structure,
    identify_string_in_dict_lists_regex,
    identify_value_in_dict_get_key,
    invert_dict,
    merge_dicts_recursive,
    remove_empty_dicts_recursive,
    sort_subdict_by_tuple,
    unflatten_dict,
)
from .list_comparison import (
    all_match_lists,
    any_match_lists,
    contains_sublist,
    find_sublist_index,
    get_common_elements_in_lists,
    partially_contains_fragment_of_list,
    partially_contains_sublist,
)
from .list_operations import (
    add_strings_to_subsets,
    check_if_all_elements_are_duplicates,
    divide_list_into_n_chunks,
    find_duplicates,
    get_duplicates,
    get_unique_sublists,
    group_by,
    is_nested_list_empty,
    repeat_strings_in_a_list,
    sliding_window,
    unique_by,
)
from .set_operations import (
    check_if_all_sets_are_same,
    convert_set_elements_to_strings,
    count_combinations,
    get_combinations,
    get_combinations_with_replacement,
    get_permutations,
    get_set_partitions,
    get_shared_elements,
    get_subsets_of_size,
    get_unique_elements_across_sets,
    partition_set_by_predicate,
    partition_set_by_sizes,
    partition_set_into_n_parts,
    set_cartesian_product,
    set_cartesian_product_as_list,
    set_power_set,
    set_power_set_as_lists,
    set_symmetric_difference,
)
from .type_operations import (
    has_element_of_type,
    try_convert_to_type,
)

__all__ = [
    "deep_delete",
    "unflatten_dict",
    "unique_by",
    # Submodules
    "list_operations",
    "set_operations",
    "list_comparison",
    "dictionary_operations",
    "type_operations",
    # List operations
    "add_strings_to_subsets",
    "check_if_all_elements_are_duplicates",
    "divide_list_into_n_chunks",
    "get_duplicates",
    "get_unique_sublists",
    "group_by",
    "is_nested_list_empty",
    "repeat_strings_in_a_list",
    "find_duplicates",
    "sliding_window",
    # Set operations
    "check_if_all_sets_are_same",
    "convert_set_elements_to_strings",
    "get_shared_elements",
    "set_symmetric_difference",
    "get_unique_elements_across_sets",
    "set_cartesian_product",
    "set_cartesian_product_as_list",
    "set_power_set",
    "set_power_set_as_lists",
    "get_subsets_of_size",
    "partition_set_by_predicate",
    "partition_set_into_n_parts",
    "get_set_partitions",
    "get_combinations",
    "get_combinations_with_replacement",
    "get_permutations",
    "count_combinations",
    "partition_set_by_sizes",
    # List comparison
    "all_match_lists",
    "any_match_lists",
    "contains_sublist",
    "find_sublist_index",
    "get_common_elements_in_lists",
    "partially_contains_fragment_of_list",
    "partially_contains_sublist",
    # Dictionary operations
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
    # Type operations
    "has_element_of_type",
    "try_convert_to_type",
]
