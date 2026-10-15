"""Command-line tools. Local runs read secrets from .env (see .env.example)."""

from __future__ import annotations

import argparse
import json
import sys

import boto3
from dotenv import load_dotenv

from . import airtable_client as at
from . import schema
from .config import Settings, get_secret


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
            f"{rec['id']}  {f.get(at.F_TITLE, '?')} | {f.get(at.F_PLATFORM, '-')} | "
            f"{f.get(at.F_STATUS, '-')} | {f.get(at.F_RATING, '-')}"
        )
        count += 1
    print(f"{count} games")
    return 0


def add_game(argv: list[str] | None = None, client: at.AirtableClient | None = None) -> int:
    p = argparse.ArgumentParser(description="Add a game")
    p.add_argument("--title", required=True)
    p.add_argument("--platform")
    p.add_argument("--genre")
    p.add_argument("--status", help="Completion Status option, e.g. 'Backlog'")
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
) -> int:
    """Invoke the cover-art Lambda for every game with an empty Cover Art URL."""
    p = argparse.ArgumentParser(description="Fetch cover art for games without any")
    p.add_argument("--dry-run", action="store_true", help="only list what would be invoked")
    args = p.parse_args(argv)
    load_dotenv()
    settings = Settings.from_env()
    client = client or _client(settings)
    todo = list(client.list_records(formula=f"{{{at.F_COVER_URL}}} = ''", fields=[at.F_TITLE]))
    print(f"{len(todo)} games need cover art")
    if args.dry_run:
        return 0
    lam = lambda_client or boto3.client("lambda")
    failures = 0
    for rec in todo:
        resp = lam.invoke(
            FunctionName=settings.function_name,
            Payload=json.dumps({"record_id": rec["id"]}).encode(),
        )
        result = json.loads(resp["Payload"].read())
        title = rec["fields"].get(at.F_TITLE, rec["id"])
        if result.get("statusCode") == 200 and "url" in result:
            print(f"ok    {title}")
        else:
            failures += 1
            print(f"FAIL  {title}: {result.get('error', result)}", file=sys.stderr)
    return 1 if failures else 0


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
