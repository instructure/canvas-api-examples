import os
from pathlib import Path
from urllib.parse import urlsplit

import pytest

from canvaslib.client import CanvasClient

CANVAS_VARS = (
    "CANVAS_BASE_URL",
    "CANVAS_TOKEN",
    "CANVAS_CLIENT_ID",
    "CANVAS_CLIENT_SECRET",
    "CANVAS_REFRESH_TOKEN",
    "CANVAS_COURSE_ID",
    "CANVAS_ENROLL_USER_ID",
)

# (method, path) of every endpoint the recipes chose during this test session.
# scripts/list_apis.py reads them to build used-apis.txt.
SENT_REQUESTS = set()


@pytest.fixture(autouse=True)
def clean_canvas_env(request, monkeypatch):
    """Mocked tests never see the developer's real Canvas settings.

    Live tests are the exception: they need those settings.
    """
    if request.node.get_closest_marker("live"):
        return
    for name in CANVAS_VARS:
        monkeypatch.delenv(name, raising=False)


CLIENT_METHODS = {"get": "GET", "get_all": "GET", "post": "POST", "put": "PUT", "delete": "DELETE"}


@pytest.fixture(autouse=True)
def record_sent_requests(monkeypatch):
    """Remember the endpoints recipes call. Only ones we call, not ones Canvas sends back or redirects to.
    """

    def recording(original, http_method):
        def call(self, path, *args, **kwargs):
            if not path.startswith(("http://", "https://")):
                SENT_REQUESTS.add((http_method, urlsplit(self._url(path)).path))
            return original(self, path, *args, **kwargs)

        return call

    for name, http_method in CLIENT_METHODS.items():
        monkeypatch.setattr(CanvasClient, name, recording(getattr(CanvasClient, name), http_method))


def pytest_sessionfinish(session):
    """When USED_APIS_RECORD names a file, write the recorded requests there."""
    target = os.environ.get("USED_APIS_RECORD")
    if target:
        lines = sorted(f"{method} {path}" for method, path in SENT_REQUESTS)
        Path(target).write_text("".join(f"{line}\n" for line in lines))
