"""Guards against committing real secrets in tracked example files."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SECRET_KEYS = {"AIRTABLE_TOKEN", "RAWG_API_KEY"}
PAT = re.compile(r"pat[A-Za-z0-9]{14}\.[a-f0-9]{16,}")
HEX32 = re.compile(r"\b[a-f0-9]{32}\b")


def _env_lines():
    for line in (ROOT / ".env.example").read_text().splitlines():
        if "=" in line and not line.lstrip().startswith("#"):
            key, _, value = line.partition("=")
            yield key.strip(), value.strip()


def test_env_example_secret_keys_are_empty():
    values = dict(_env_lines())
    assert SECRET_KEYS <= values.keys()
    for key in SECRET_KEYS:
        assert values[key] == "", f"{key} in .env.example must be empty"


def test_env_example_has_no_token_shaped_text():
    text = (ROOT / ".env.example").read_text()
    assert not PAT.search(text), "looks like a real Airtable token"
    assert not HEX32.search(text), "looks like a real API key"


def test_env_example_has_no_inline_comments_after_values():
    # dotenv keeps "value#comment" as one value; comments belong on their own line.
    for key, value in _env_lines():
        assert "#" not in value, f"{key} has an inline comment"


def test_tfvars_example_has_no_real_base_id():
    text = (ROOT / "infra" / "terraform.tfvars.example").read_text()
    assert "appXXXXXXXXXXXXXX" in text
