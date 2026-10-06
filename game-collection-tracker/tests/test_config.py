import boto3
import pytest
from moto import mock_aws

from game_tracker.config import MissingSecretError, Settings, get_secret


def test_env_wins(monkeypatch):
    monkeypatch.setenv("RAWG_API_KEY", "from-env")
    assert get_secret("RAWG_API_KEY") == "from-env"


@mock_aws
def test_falls_back_to_ssm():
    boto3.client("ssm").put_parameter(
        Name="/game-tracker/RAWG_API_KEY", Value="from-ssm", Type="SecureString"
    )
    assert get_secret("RAWG_API_KEY") == "from-ssm"


@mock_aws
def test_missing_and_placeholder():
    with pytest.raises(MissingSecretError):
        get_secret("RAWG_API_KEY")
    boto3.client("ssm").put_parameter(
        Name="/game-tracker/RAWG_API_KEY", Value="CHANGE_ME", Type="SecureString"
    )
    with pytest.raises(MissingSecretError):
        get_secret("RAWG_API_KEY")


def test_settings_requires_base_id(monkeypatch):
    monkeypatch.delenv("AIRTABLE_BASE_ID", raising=False)
    with pytest.raises(MissingSecretError):
        Settings.from_env()
    monkeypatch.setenv("AIRTABLE_BASE_ID", "appX")
    assert Settings.from_env().airtable_table == "Games"
