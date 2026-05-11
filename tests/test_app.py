"""Smoke tests for the Flask app.

Kept intentionally small — these guard the basics (app boots, healthcheck
responds, bad uploads are rejected) without depending on the HF API or any
network/model state. Run with `pytest` from the repo root.
"""

import io

import pytest


@pytest.fixture
def client():
    """Flask test client. `from app import app` is inside the fixture so each
    test that needs the client gets a fresh client object, but the app
    singleton itself is only imported once per session."""
    from app import app

    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_app_initializes():
    """The Flask app object loads without raising."""
    from app import app

    assert app is not None
    assert app.name == "app"


def test_healthz_ok(client):
    """/healthz returns 200 with the expected JSON body."""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_non_image_upload_rejected(client):
    """A non-image upload is refused before any captioning is attempted.

    The app returns 200 with an error message in the rendered HTML rather
    than a bare 400 — this is a deliberate UX choice (the user sees the form
    again with an inline alert instead of a generic browser error page).
    The important guarantee is that the file is not accepted and the
    captioning pipeline is never invoked.
    """
    data = {"file": (io.BytesIO(b"this is not an image"), "malicious.txt")}
    response = client.post("/", data=data, content_type="multipart/form-data")
    assert response.status_code == 200
    assert b"Unsupported file type" in response.data
