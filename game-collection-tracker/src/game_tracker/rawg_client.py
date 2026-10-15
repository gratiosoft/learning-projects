"""RAWG client: find a game by title and download its cover image.

RAWG takes the API key as a query parameter, so never log request URLs.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urlparse

import requests

API_ROOT = "https://api.rawg.io/api"
# RAWG serves images from this host only. We refuse anything else so a bad or
# tampered API response cannot make the Lambda fetch arbitrary URLs (SSRF).
IMAGE_HOSTS = frozenset({"media.rawg.io"})


class GameNotFoundError(LookupError):
    pass


class UpstreamError(RuntimeError):
    """RAWG (or the image host) failed: 5xx, network error or bad response."""


@dataclass(frozen=True)
class Cover:
    name: str
    image_url: str


def normalize(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


class RawgClient:
    def __init__(self, api_key: str, session: requests.Session | None = None):
        self.api_key = api_key
        self.session = session or requests.Session()

    def _get(self, url: str, **kwargs) -> requests.Response:
        try:
            resp = self.session.get(url, timeout=30, **kwargs)
        except requests.RequestException as exc:
            # Don't chain the original: its message can contain the URL with the key.
            raise UpstreamError(f"request failed: {type(exc).__name__}") from None
        if resp.status_code >= 500:
            raise UpstreamError(f"upstream returned {resp.status_code}")
        if resp.status_code >= 300:  # includes un-followed redirects
            raise UpstreamError(f"unexpected status {resp.status_code}")
        return resp

    def find_cover(self, title: str) -> Cover:
        resp = self._get(
            f"{API_ROOT}/games",
            params={"search": title, "page_size": 5, "key": self.api_key},
        )
        results = [r for r in resp.json().get("results", []) if r.get("background_image")]
        if not results:
            raise GameNotFoundError(f"no cover found for {title!r}")
        wanted = normalize(title)
        # Exact normalized title wins; otherwise trust RAWG's relevance order.
        best = next((r for r in results if normalize(r["name"]) == wanted), results[0])
        return Cover(name=best["name"], image_url=best["background_image"])

    def download(self, image_url: str) -> tuple[bytes, str]:
        parsed = urlparse(image_url)
        if parsed.scheme != "https" or parsed.hostname not in IMAGE_HOSTS:
            raise UpstreamError(f"refusing to fetch image from {parsed.hostname!r}")
        # No redirects: a redirect could point outside the allowed host.
        resp = self._get(image_url, allow_redirects=False)
        content_type = resp.headers.get("Content-Type", "image/jpeg").split(";")[0]
        return resp.content, content_type
