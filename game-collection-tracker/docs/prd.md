# PRD: Game Collection Tracker

Status: draft · Owner: repo owner (junior dev, learning project)

## Problem

I own many video games across platforms and lose track of what I own, what I have finished and what I thought of it. A spreadsheet works but is ugly, has no cover art and can't be shared with friends.

## Goals

1. Keep the collection in an Airtable base (Free plan) with a form, a dashboard and a gallery.
2. Show cover art for every game, stored in my own S3 bucket and linked from Airtable.
3. Learn: Airtable (fields, forms, automations, interfaces, Web API), AWS Lambda + S3, Terraform, testing with mocks.

## Non-goals

- Multi-user accounts, auth or a custom web front end (Airtable interfaces are the UI).
- Price tracking, wishlists, store integrations.
- High availability or scale: this is a personal collection (hundreds of games, not millions).
- Custom domain for cover art.

## Users

- **Owner**: adds and rates games, reads the dashboard, runs scripts and deploys the infra.
- **Friends**: submit games through a shared form (read-only elsewhere).

## Requirements

### Airtable (Phases 1, 2, 5)

| ID | Requirement |
|----|-------------|
| A1 | Base "Game Collection Tracker", table `Games` with `Title`, `Platform`, `Genre`, `Completion status`, `Rating`, `Cover art URL`, `Review status`, `Cover art attachment`. |
| A2 | Every select option has a distinct color. |
| A3 | A form adds games (Title, Platform, Genre, Completion status, Rating). |
| A4 | Dashboard: total games, % completed, average rating. |
| A5 | Gallery page with filters (platform, genre, status). |
| A6 | Automation: notify when a game is added. |
| A7 | Automation: new records get `Review status` = "Unreviewed". |
| A8 | Friends can submit via a shared form. |

Items the Airtable MCP tools cannot do are listed in [manual-steps.md](manual-steps.md).

### Airtable Web API scripts (Phase 3)

| ID | Requirement |
|----|-------------|
| W1 | Client lists all games (pagination via `offset`). |
| W2 | Client creates/updates records in batches of at most 10. |
| W3 | Client respects 5 req/s and retries on HTTP 429 with backoff. |
| W4 | CLI: `list-games`, `add-game`. |

### Cover art pipeline (Phase 4)

| ID | Requirement |
|----|-------------|
| C1 | Lambda input `{record_id}` or `{title}`; looks up the game on RAWG, picks the best match. |
| C2 | Uploads the image to S3 at `covers/<record_id>.jpg` with correct `Content-Type`. |
| C3 | Writes the stable cover URL to the record's `Cover art URL`; returns it. |
| C3b | Also writes `Cover art attachment` (a display copy Airtable re-hosts) so gallery views show images; skipped if present unless `force`. |
| C4 | Idempotent: re-running yields the same key/URL and no duplicate side effects. |
| C5 | Clear errors: game not found (404-style), upstream failure (5xx-style). |
| C6 | Backfill CLI invokes the Lambda for every game without cover art. |
| C7 | All AWS resources defined in Terraform; no secrets in code, state or logs. |

## Success metrics

- 100% of games in the base have a working cover URL after one backfill run.
- `uv run pytest` passes offline; `ruff`, `terraform fmt -check` and `terraform validate` pass.
- Monthly AWS cost stays at or near $0 (free tier).
- Airtable Free-plan limits are never exceeded in normal use (1,000 records per base, 100 automation runs per month, 1 GB attachments).
