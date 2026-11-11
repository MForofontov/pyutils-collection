"""Real HTTP transport checks using disposable loopback servers only."""

import threading
import urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

from pyutils_collection.http_functions import download_file, http_get

pytestmark = pytest.mark.integration


@pytest.fixture
def servers():
    recorded = []
    running = []

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_args):
            pass

        def do_GET(self):
            if self.path == "/redirect-other":
                self.send_response(302)
                self.send_header("Location", running[1][0] + "/ok")
                self.end_headers()
                return
            if self.path == "/redirect-ftp":
                self.send_response(302)
                self.send_header("Location", "ftp://127.0.0.1:1/forbidden")
                self.end_headers()
                return
            recorded.append(dict(self.headers))
            body = b"hello"
            self.send_response(200)
            self.send_header(
                "Content-Length", "100" if self.path == "/truncated" else str(len(body))
            )
            self.end_headers()
            self.wfile.write(body)

    try:
        for _ in range(2):
            server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
            thread = threading.Thread(
                target=server.serve_forever, kwargs={"poll_interval": 0.01}, daemon=True
            )
            thread.start()
            running.append((f"http://127.0.0.1:{server.server_port}", server, thread))
        yield running[0][0], recorded
    finally:
        for _, server, thread in running:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)
            assert not thread.is_alive()


def test_real_redirect_strips_credentials_when_port_changes(servers):
    url, recorded = servers
    response = http_get(
        url + "/redirect-other",
        headers={"Authorization": "test-only", "Cookie": "test-only"},
    )
    assert response["content"] == "hello"
    assert "Authorization" not in recorded[-1]
    assert "Cookie" not in recorded[-1]


def test_real_redirect_rejects_ftp_before_connecting(servers):
    url, _ = servers
    with pytest.raises(ValueError, match="Redirect URL"):
        http_get(url + "/redirect-ftp")


def test_real_truncated_download_preserves_existing_file(servers, tmp_path):
    url, _ = servers
    destination = tmp_path / "file"
    destination.write_bytes(b"original")
    with pytest.raises(urllib.error.ContentTooShortError):
        download_file(url + "/truncated", str(destination))
    assert destination.read_bytes() == b"original"
    assert list(tmp_path.iterdir()) == [destination]
