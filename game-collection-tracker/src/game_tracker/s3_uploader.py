"""Upload cover images to S3 and build their public (CloudFront) URL."""

from __future__ import annotations

import re

import boto3
from botocore.exceptions import ClientError

EXTENSIONS = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp"}


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "game"


class CoverUploader:
    def __init__(self, bucket: str, base_url: str, s3_client=None):
        self.bucket = bucket
        self.base_url = base_url.rstrip("/")
        self.s3 = s3_client or boto3.client("s3")

    def key_for(self, name: str, content_type: str = "image/jpeg") -> str:
        # Key derives from the record id (or title slug), so re-runs overwrite
        # the same object instead of piling up duplicates.
        return f"covers/{name}.{EXTENSIONS.get(content_type, 'jpg')}"

    def url_for(self, key: str) -> str:
        return f"{self.base_url}/{key}"

    def key_from_url(self, url: str) -> str | None:
        prefix = f"{self.base_url}/"
        return url[len(prefix) :] if url.startswith(prefix) else None

    def exists(self, key: str) -> bool:
        try:
            self.s3.head_object(Bucket=self.bucket, Key=key)
            return True
        except ClientError as exc:
            if exc.response["Error"]["Code"] in ("404", "NoSuchKey", "NotFound"):
                return False
            raise

    def upload(self, name: str, data: bytes, content_type: str) -> str:
        key = self.key_for(name, content_type)
        self.s3.put_object(Bucket=self.bucket, Key=key, Body=data, ContentType=content_type)
        return self.url_for(key)
