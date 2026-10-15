"""Create the `Games` table through the Airtable Meta API (scope: schema.bases:write).

Select options need a distinct color each and the API cannot recolor them later
(ADR 0006), so colors are fixed here. Forms, interfaces and automations are not
exposed by the public API; see docs/manual-steps.md.
"""

from __future__ import annotations

import requests

META = "https://api.airtable.com/v0/meta/bases"

# One color per option, never repeated within a field.
_PALETTE = [
    "blueBright", "cyanBright", "tealBright", "greenBright", "yellowBright",
    "orangeBright", "redBright", "pinkBright", "purpleBright", "grayBright",
]  # fmt: skip


def _select(name: str, options: list[str]) -> dict:
    assert len(options) <= len(_PALETTE)
    return {
        "name": name,
        "type": "singleSelect",
        "options": {"choices": [{"name": o, "color": _PALETTE[i]} for i, o in enumerate(options)]},
    }


def games_table(name: str = "Games") -> dict:
    return {
        "name": name,
        "description": "Video game collection",
        "fields": [
            {"name": "Title", "type": "singleLineText"},  # first field = primary
            _select(
                "Platform",
                [
                    "PC",
                    "PlayStation 5",
                    "PlayStation 4",
                    "Xbox Series X|S",
                    "Nintendo Switch",
                    "Other",
                ],
            ),
            _select(
                "Genre",
                [
                    "Action",
                    "Adventure",
                    "RPG",
                    "Strategy",
                    "Shooter",
                    "Puzzle",
                    "Platformer",
                    "Sports",
                    "Simulation",
                    "Other",
                ],
            ),  # fmt: skip
            _select("Completion Status", ["Backlog", "Playing", "Completed", "Dropped"]),
            {
                "name": "Rating",
                "type": "rating",
                "options": {"max": 5, "icon": "star", "color": "yellowBright"},
            },
            {"name": "Cover Art URL", "type": "url"},
            _select("Review Status", ["Unreviewed", "Reviewed"]),
            {"name": "Cover Art Attachment", "type": "multipleAttachments"},
        ],
    }


def ensure_games_table(token: str, base_id: str, session: requests.Session | None = None) -> dict:
    """Create the table unless a table with that name exists. Returns the table JSON."""
    s = session or requests.Session()
    headers = {"Authorization": f"Bearer {token}"}
    spec = games_table()
    resp = s.get(f"{META}/{base_id}/tables", headers=headers, timeout=30)
    resp.raise_for_status()
    for table in resp.json()["tables"]:
        if table["name"] == spec["name"]:
            return table  # already there: do nothing
    resp = s.post(f"{META}/{base_id}/tables", headers=headers, json=spec, timeout=30)
    if not resp.ok:
        raise RuntimeError(f"Airtable {resp.status_code}: {resp.text[:200]}")
    return resp.json()
