"""HTTP-only redirects with credentials scoped to the original origin."""

import urllib.parse
import urllib.request
from typing import Any


def _origin(url: str) -> tuple[str, str | None, int | None]:
    parsed = urllib.parse.urlsplit(url)
    return (
        parsed.scheme.lower(),
        parsed.hostname,
        parsed.port or (443 if parsed.scheme.lower() == "https" else 80),
    )


class HttpOnlyRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(
        self, req: Any, fp: Any, code: int, msg: str, headers: Any, newurl: str
    ) -> Any:
        if urllib.parse.urlsplit(newurl).scheme.lower() not in {"http", "https"}:
            raise ValueError("Redirect URL must use http or https")
        redirected = super().redirect_request(req, fp, code, msg, headers, newurl)
        if redirected is not None and _origin(req.full_url) != _origin(newurl):
            for name in list(redirected.headers):
                if name.lower() in {
                    "authorization",
                    "proxy-authorization",
                    "cookie",
                    "host",
                }:
                    redirected.remove_header(name)
        return redirected


def open_http(request: urllib.request.Request, timeout: int) -> Any:
    """Use a scoped opener without changing urllib's global opener."""
    return urllib.request.build_opener(HttpOnlyRedirectHandler()).open(
        request, timeout=timeout
    )  # nosec B310 # Callers validate the initial URL; redirects enforce HTTP(S).
