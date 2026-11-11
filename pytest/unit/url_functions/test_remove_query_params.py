"""Tests for removing query fields without re-encoding retained values."""

import pytest
from pyutils_collection.url_functions import remove_query_params

pytestmark = [pytest.mark.unit, pytest.mark.url_functions]


@pytest.mark.parametrize(
    "url,keys,expected",
    [
        ("/p?a=1&b=2&a=3#top", ["a"], "/p?b=2#top"),
        ("/p?a=1#top", ["a"], "/p#top"),
        (
            "/p?tag=a%20b&keep=%2f&blank=&flag&drop=1",
            ["drop"],
            "/p?tag=a%20b&keep=%2f&blank=&flag",
        ),
        ("/p?a+b=1&a%20b=2&c=3", ["a b"], "/p?c=3"),
        ("/p?A=1&a=2", ["a"], "/p?A=1"),
        ("/p", ["a"], "/p"),
        ("/p?", [], "/p?"),
        ("/p?a=1&a=2", ["missing"], "/p?a=1&a=2"),
        (
            "HTTP://EXAMPLE.COM/p?drop=1&keep=%2f#",
            ["drop"],
            "HTTP://EXAMPLE.COM/p?keep=%2f#",
        ),
        ("/p?drop=1&#top", ["drop"], "/p?#top"),
    ],
)
def test_remove_query_params(url, keys, expected) -> None:
    assert remove_query_params(url, iter(keys)) == expected


@pytest.mark.parametrize(
    "url,keys,error",
    [
        (1, [], TypeError),
        ("", [], ValueError),
        ("/", "a", TypeError),
        ("/", None, TypeError),
        ("/", [1], TypeError),
    ],
)
def test_invalid_inputs(url, keys, error) -> None:
    with pytest.raises(error):
        remove_query_params(url, keys)
