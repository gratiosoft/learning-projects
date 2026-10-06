"""Settings and secret loading.

Secrets resolve in this order: environment variable (local dev, from .env),
then SSM Parameter Store (Lambda). The Lambda role may only read /game-tracker/*.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

import boto3

SSM_PREFIX = os.environ.get("SSM_PREFIX", "/game-tracker")


class MissingSecretError(RuntimeError):
    pass


def get_secret(name: str, ssm_client=None) -> str:
    """Return secret `name` from the environment, falling back to SSM (SecureString)."""
    value = os.environ.get(name)
    if value:
        return value
    ssm = ssm_client or boto3.client("ssm")
    try:
        resp = ssm.get_parameter(Name=f"{SSM_PREFIX}/{name}", WithDecryption=True)
    except ssm.exceptions.ParameterNotFound as exc:
        raise MissingSecretError(f"{name} not set in env or SSM") from exc
    value = resp["Parameter"]["Value"]
    if not value or value == "CHANGE_ME":
        raise MissingSecretError(f"{name} in SSM is still the placeholder")
    return value


@dataclass(frozen=True)
class Settings:
    airtable_base_id: str
    airtable_table: str
    covers_bucket: str
    cover_base_url: str  # CloudFront domain, e.g. https://dxxxx.cloudfront.net
    function_name: str

    @classmethod
    def from_env(cls) -> Settings:
        def need(key: str) -> str:
            value = os.environ.get(key)
            if not value:
                raise MissingSecretError(f"{key} is not set")
            return value

        return cls(
            airtable_base_id=need("AIRTABLE_BASE_ID"),
            airtable_table=os.environ.get("AIRTABLE_TABLE", "Games"),
            covers_bucket=os.environ.get("COVERS_BUCKET", ""),
            cover_base_url=os.environ.get("COVER_BASE_URL", "").rstrip("/"),
            function_name=os.environ.get("LAMBDA_FUNCTION_NAME", "game-tracker-cover-art"),
        )
