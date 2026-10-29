"""Redirects must not change protocols or forward credentials to another origin."""

import urllib.request
from email.message import Message

import pytest

from pyutils_collection.http_functions._transport import HttpOnlyRedirectHandler

pytestmark = [pytest.mark.unit, pytest.mark.http_functions]


@pytest.mark.parametrize(
    "url", ["ftp://example.com/file", "file:///etc/passwd", "data:text/plain,secret"]
)
def test_redirect_rejects_non_http_protocols(url):
    handler = HttpOnlyRedirectHandler()
    request = urllib.request.Request("https://example.com")
    with pytest.raises(ValueError, match="Redirect URL"):
        handler.redirect_request(request, None, 302, "Found", Message(), url)


@pytest.mark.parametrize(
    "url",
    [
        "https://other.example/path",
        "http://example.com/path",
        "https://example.com:444/path",
    ],
)
def test_redirect_strips_sensitive_headers_on_origin_change(url):
    handler = HttpOnlyRedirectHandler()
    request = urllib.request.Request(
        "https://example.com",
        headers={
            "Authorization": "Bearer secret",
            "Cookie": "session=secret",
            "Host": "example.com",
            "X-Trace": "trace",
        },
    )
    redirected = handler.redirect_request(request, None, 302, "Found", Message(), url)
    assert redirected.get_header("Authorization") is None
    assert redirected.get_header("Cookie") is None
    assert redirected.get_header("Host") is None
    assert redirected.get_header("X-trace") == "trace"


def test_same_origin_redirect_keeps_authorization():
    handler = HttpOnlyRedirectHandler()
    request = urllib.request.Request(
        "https://example.com", headers={"Authorization": "Bearer secret"}
    )
    redirected = handler.redirect_request(
        request, None, 302, "Found", Message(), "https://example.com:443/path"
    )
    assert redirected.get_header("Authorization") == "Bearer secret"
