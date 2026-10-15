"""Lambda entry point: fetch cover art for a game, store it in S3, link it in Airtable.

Event: {"record_id": "rec..."} or {"title": "..."}, plus optional "force": true to
re-fetch even when the record already has a cover (e.g. after fixing a wrong Title).
Response: {"statusCode": 200, "url": ..., "cached": bool} or
          {"statusCode": 404|400|502, "error": code, "message": ...}.
Errors are returned (not raised) so the backfill CLI can tell "not found" from a crash.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from . import airtable_client as at
from .airtable_client import AirtableClient, AirtableError
from .config import Settings, get_secret
from .rawg_client import GameNotFoundError, RawgClient, UpstreamError
from .s3_uploader import CoverUploader, slugify

log = logging.getLogger()
log.setLevel(logging.INFO)


@dataclass
class Deps:
    airtable: AirtableClient
    rawg: RawgClient
    uploader: CoverUploader


_deps: Deps | None = None


def _build_deps() -> Deps:
    """Build clients once per Lambda container (cold start), reusing them after."""
    global _deps
    if _deps is None:
        s = Settings.from_env()
        _deps = Deps(
            airtable=AirtableClient(
                get_secret("AIRTABLE_TOKEN"), s.airtable_base_id, s.airtable_table
            ),
            rawg=RawgClient(get_secret("RAWG_API_KEY")),
            uploader=CoverUploader(s.covers_bucket, s.cover_base_url),
        )
    return _deps


def _error(status: int, code: str, message: str) -> dict:
    return {"statusCode": status, "error": code, "message": message}


def lambda_handler(event: dict, context=None, deps: Deps | None = None) -> dict:
    d = deps or _build_deps()
    record_id = event.get("record_id")
    title = event.get("title")
    if not record_id and not title:
        return _error(400, "bad_request", "provide record_id or title")

    try:
        if record_id:
            fields = d.airtable.get_record(record_id)["fields"]
            title = fields.get(at.F_TITLE)
            if not title:
                return _error(400, "bad_request", f"record {record_id} has no Title")
            # Idempotency shortcut: already linked to our bucket and the object exists.
            # It does not re-check the title; use force=true after changing a Title.
            current = fields.get(at.F_COVER_URL, "")
            key = d.uploader.key_from_url(current) if current else None
            if key and not event.get("force") and d.uploader.exists(key):
                return {"statusCode": 200, "url": current, "cached": True}

        cover = d.rawg.find_cover(title)
        data, content_type = d.rawg.download(cover.image_url)
        url = d.uploader.upload(record_id or slugify(title), data, content_type)
        if record_id:
            d.airtable.update_records([{"id": record_id, "fields": {at.F_COVER_URL: url}}])
    except GameNotFoundError as exc:
        log.info("game not found: %s", title)
        return _error(404, "game_not_found", str(exc))
    except (UpstreamError, AirtableError) as exc:
        log.error("upstream failure: %s", exc)
        return _error(502, "upstream_error", str(exc))

    log.info("cover stored for %s", record_id or title)
    return {"statusCode": 200, "url": url, "cached": False}
