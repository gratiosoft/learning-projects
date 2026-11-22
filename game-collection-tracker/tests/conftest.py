import os

import pytest


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    """Tests must never see real secrets or touch real AWS."""
    for key in ("AIRTABLE_TOKEN", "RAWG_API_KEY"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")
    os.environ.pop("AWS_PROFILE", None)
