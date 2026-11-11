"""HTTP operations reject local-file and non-HTTP URLs before doing I/O."""

import importlib
from pathlib import Path
from unittest.mock import patch

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.http_functions]


@pytest.mark.parametrize(
    "name", ["http_get", "http_post", "download_file", "upload_file"]
)
@pytest.mark.parametrize(
    "url", ["file:///etc/passwd", "ftp://example.com/file", "data:text/plain,hello"]
)
def test_http_helpers_reject_other_schemes(tmp_path: Path, name: str, url: str) -> None:
    module = importlib.import_module(f"pyutils_collection.http_functions.{name}")
    function = getattr(module, name)
    path = tmp_path / "not-created" / "file.txt"
    arguments = (url, str(path)) if name in {"download_file", "upload_file"} else (url,)
    with patch.object(module.urllib.request, "urlopen") as urlopen:
        with pytest.raises(ValueError, match="URL must use http or https"):
            function(*arguments)
    urlopen.assert_not_called()
    assert not path.parent.exists()
