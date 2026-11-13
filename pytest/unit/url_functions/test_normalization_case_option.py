import pytest

from pyutils_collection.url_functions import normalize_url

pytestmark = [pytest.mark.unit, pytest.mark.url_functions]


@pytest.mark.parametrize(
    "url, expected",
    [
        ("HTTP://EXAMPLE.COM:80/a", "HTTP://EXAMPLE.COM/a"),
        ("HtTpS://EXAMPLE.COM:443/a", "HtTpS://EXAMPLE.COM/a"),
        ("HTTPS://EXAMPLE.COM:8443/a", "HTTPS://EXAMPLE.COM:8443/a"),
        ("/a", "/a"),
    ],
)
def test_disabling_case_normalization_preserves_scheme(
    url: str, expected: str
) -> None:
    assert normalize_url(url, lowercase_scheme_host=False) == expected


def test_default_case_normalization_still_removes_default_port() -> None:
    assert normalize_url("HtTpS://EXAMPLE.COM:443/a") == "https://example.com/a"
