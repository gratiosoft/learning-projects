"""Command-line tools. Local runs read secrets from .env (see .env.example)."""

from __future__ import annotations

import argparse
import json
import sys
from urllib.parse import urlparse

import boto3
from dotenv import load_dotenv

from . import airtable_client as at
from . import schema
from .backfill import MAX_CONSECUTIVE_ERRORS, run_backfill
from .config import Settings, get_secret
from .rawg_client import GameNotFoundError, RawgClient, UpstreamError


def _client(settings: Settings) -> at.AirtableClient:
    return at.AirtableClient(
        get_secret("AIRTABLE_TOKEN"), settings.airtable_base_id, settings.airtable_table
    )


def list_games(argv: list[str] | None = None, client: at.AirtableClient | None = None) -> int:
    argparse.ArgumentParser(description="List all games").parse_args(argv)
    load_dotenv()
    client = client or _client(Settings.from_env())
    count = 0
    for rec in client.list_records():
        f = rec["fields"]
        print(
            f"{rec['id']}  {f.get(at.F_TITLE, '?')} | "
            f"{', '.join(f.get(at.F_PLATFORM, [])) or '-'} | "
            f"{f.get(at.F_STATUS, '-')} | {f.get(at.F_RATING, '-')}"
        )
        count += 1
    print(f"{count} games")
    return 0


def add_game(argv: list[str] | None = None, client: at.AirtableClient | None = None) -> int:
    p = argparse.ArgumentParser(description="Add a game")
    p.add_argument("--title", required=True)
    p.add_argument("--platform", action="append", help="repeatable; must be an existing option")
    p.add_argument("--genre", action="append", help="repeatable; must be an existing option")
    p.add_argument("--status", help="Completion status option, e.g. 'Not played'")
    p.add_argument("--rating", type=int, choices=range(1, 6))
    args = p.parse_args(argv)
    load_dotenv()
    fields = {
        at.F_TITLE: args.title,
        at.F_PLATFORM: args.platform,
        at.F_GENRE: args.genre,
        at.F_STATUS: args.status,
        at.F_RATING: args.rating,
    }
    fields = {k: v for k, v in fields.items() if v is not None}
    client = client or _client(Settings.from_env())
    rec = client.create_records([fields])[0]
    print(f"created {rec['id']}")
    return 0


def backfill(
    argv: list[str] | None = None,
    client: at.AirtableClient | None = None,
    lambda_client=None,
    rawg=None,
) -> int:
    """Invoke the cover-art Lambda for every game with an empty Cover art URL."""
    p = argparse.ArgumentParser(description="Fetch cover art for games without any")
    p.add_argument("--dry-run", action="store_true", help="only list what would be invoked")
    p.add_argument(
        "--preview",
        action="store_true",
        help="look each title up on RAWG and print the match; no S3, no Lambda, no Airtable writes",
    )
    args = p.parse_args(argv)
    load_dotenv()
    settings = Settings.from_env()
    client = client or _client(settings)
    # Skip blank rows (Airtable bases start with empty placeholder records).
    formula = f"AND({{{at.F_TITLE}}} != '', {{{at.F_COVER_URL}}} = '')"
    todo = list(client.list_records(formula=formula, fields=[at.F_TITLE]))
    print(f"{len(todo)} games need cover art")
    if args.dry_run:
        return 0
    if args.preview:
        rawg = rawg or RawgClient(get_secret("RAWG_API_KEY"))
        for rec in todo:
            title = rec["fields"][at.F_TITLE]
            try:
                cover = rawg.find_cover(title)
                print(f"{title!r} -> {cover.name!r}  {urlparse(cover.image_url).hostname}")
            except (GameNotFoundError, UpstreamError) as exc:
                print(f"{title!r} -> {exc}")
        return 0
    lam = lambda_client or boto3.client("lambda")

    def enrich(rec: dict) -> dict:
        resp = lam.invoke(
            FunctionName=settings.function_name,
            Payload=json.dumps({"record_id": rec["id"]}).encode(),
        )
        return json.loads(resp["Payload"].read())

    def show(rec: dict, result: dict) -> None:
        title = rec["fields"].get(at.F_TITLE, rec["id"])
        if result.get("statusCode") == 200 and "url" in result:
            print(f"ok    {title}")
        else:
            print(f"FAIL  {title}: {result.get('error', result)}", file=sys.stderr)

    out = run_backfill(todo, enrich, on_result=show)
    if out.stopped_early:
        print(
            f"stopped after {MAX_CONSECUTIVE_ERRORS} consecutive upstream errors; "
            f"{out.remaining} games not attempted. Re-run later.",
            file=sys.stderr,
        )
    return 1 if (out.errors or out.not_found) else 0


def setup_base(argv: list[str] | None = None, ensure=schema.ensure_games_table) -> int:
    """Create the Games table (with colored select options) in the configured base."""
    argparse.ArgumentParser(description="Create the Games table").parse_args(argv)
    load_dotenv()
    settings = Settings.from_env()
    table = ensure(get_secret("AIRTABLE_TOKEN"), settings.airtable_base_id)
    print(f"table {table['name']} id={table['id']}")
    for f in table["fields"]:
        print(f"  {f['id']}  {f['name']} ({f['type']})")
    return 0
