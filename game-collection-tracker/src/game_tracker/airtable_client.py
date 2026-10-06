"""Thin wrapper over the Airtable REST API.

Airtable limits to know about:
- 5 requests/second per base. We space calls and back off on HTTP 429.
- Create/update accept at most 10 records per request, so we batch.
- List responses return at most 100 records and an `offset` token for the next page.
"""

from __future__ import annotations

import time
from collections.abc import Callable, Iterator
from typing import Any

import requests

API_ROOT = "https://api.airtable.com/v0"
BATCH_SIZE = 10
MIN_INTERVAL = 0.2  # 5 req/s

# Field names in the Games table (see README for IDs).
F_TITLE = "Title"
F_PLATFORM = "Platform"
F_GENRE = "Genre"
F_STATUS = "Completion Status"
F_RATING = "Rating"
F_COVER_URL = "Cover Art URL"
F_REVIEW = "Review Status"


class AirtableError(RuntimeError):
    def __init__(self, status: int, message: str):
        super().__init__(f"Airtable {status}: {message}")
        self.status = status


class AirtableClient:
    def __init__(
        self,
        token: str,
        base_id: str,
        table: str = "Games",
        session: requests.Session | None = None,
        max_retries: int = 5,
        sleep: Callable[[float], None] = time.sleep,
        clock: Callable[[], float] = time.monotonic,
    ):
        self.url = f"{API_ROOT}/{base_id}/{table}"
        self.session = session or requests.Session()
        self.session.headers["Authorization"] = f"Bearer {token}"
        self.max_retries = max_retries
        self._sleep = sleep
        self._clock = clock
        self._last_call = float("-inf")

    def _request(self, method: str, url: str, **kwargs: Any) -> dict:
        for attempt in range(self.max_retries + 1):
            wait = MIN_INTERVAL - (self._clock() - self._last_call)
            if wait > 0:
                self._sleep(wait)
            self._last_call = self._clock()
            resp = self.session.request(method, url, timeout=30, **kwargs)
            if resp.status_code == 429 and attempt < self.max_retries:
                # Airtable asks clients to wait 30s after a 429; use Retry-After if given,
                # otherwise exponential backoff (kept short so tests and CLI stay snappy).
                delay = float(resp.headers.get("Retry-After", 0.5 * 2**attempt))
                self._sleep(delay)
                continue
            if not resp.ok:
                raise AirtableError(resp.status_code, resp.text[:200])
            return resp.json()
        raise AirtableError(429, "rate limited, retries exhausted")  # pragma: no cover

    def list_records(
        self, formula: str | None = None, fields: list[str] | None = None
    ) -> Iterator[dict]:
        """Yield every record, following `offset` pagination."""
        params: dict[str, Any] = {"pageSize": 100}
        if formula:
            params["filterByFormula"] = formula
        if fields:
            params["fields[]"] = fields
        while True:
            data = self._request("GET", self.url, params=params)
            yield from data["records"]
            if not data.get("offset"):
                return
            params["offset"] = data["offset"]

    def get_record(self, record_id: str) -> dict:
        return self._request("GET", f"{self.url}/{record_id}")

    def create_records(self, rows: list[dict], typecast: bool = False) -> list[dict]:
        """Create records from a list of field dicts, 10 per request."""
        created: list[dict] = []
        for i in range(0, len(rows), BATCH_SIZE):
            body = {
                "records": [{"fields": r} for r in rows[i : i + BATCH_SIZE]],
                "typecast": typecast,
            }
            created += self._request("POST", self.url, json=body)["records"]
        return created

    def update_records(self, updates: list[dict], typecast: bool = False) -> list[dict]:
        """PATCH records. Each item is {"id": "rec...", "fields": {...}}; 10 per request."""
        updated: list[dict] = []
        for i in range(0, len(updates), BATCH_SIZE):
            body = {"records": updates[i : i + BATCH_SIZE], "typecast": typecast}
            updated += self._request("PATCH", self.url, json=body)["records"]
        return updated
