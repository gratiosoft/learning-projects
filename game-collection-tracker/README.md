# Game Collection Tracker

Track a video game collection in Airtable (Free plan) and attach cover art stored in S3 and served by CloudFront. Learning project for Airtable, AWS Lambda/S3 and Terraform.

Docs: [PRD](docs/prd.md) · [Architecture](docs/architecture.md) · [ADRs](docs/adr/) · [Manual steps](docs/manual-steps.md)

## Status

| Part | State |
|------|-------|
| Python client, CLI, Lambda handler, tests | done, tests pass offline |
| Terraform (`infra/`) | written, `fmt` and `validate` pass, **not applied** |
| Airtable base and form | table and form exist (built by hand), verified live |
| Airtable automations, interface | manual, see [manual-steps.md](docs/manual-steps.md) |

## Setup

```bash
make setup                 # uv sync
cp .env.example .env       # fill in values; .env is gitignored
```

## Run

```bash
uv run setup-base                      # once: creates the Games table (needs schema.bases:write)
uv run list-games
uv run add-game --title "Hades" --platform Steam --genre Action --status "Not played" --rating 5
uv run backfill-covers --dry-run     # then without --dry-run once deployed
```

## Test and lint

```bash
make check     # ruff, pytest (offline, all external services mocked), terraform fmt + validate
```

## Deploy (AWS)

Prerequisites: AWS credentials (profile or env), Terraform >= 1.6, a RAWG API key, an Airtable token.

1. `cp infra/terraform.tfvars.example infra/terraform.tfvars` and set `airtable_base_id` (and `aws_profile`, `region`).
2. `make plan` builds the zip and shows the plan. Review it.
3. `make deploy` runs `terraform apply` (asks for confirmation). First apply takes a few minutes because of CloudFront.
4. Store the real secrets (Terraform only creates placeholders):
   ```bash
   aws ssm put-parameter --name /game-tracker/RAWG_API_KEY --type SecureString --overwrite --value "..."
   aws ssm put-parameter --name /game-tracker/AIRTABLE_TOKEN --type SecureString --overwrite --value "..."
   ```
5. Smoke test: `aws lambda invoke --function-name game-tracker-cover-art --payload '{"title":"Hades"}' --cli-binary-format raw-in-base64-out out.json`
6. Backfill: `uv run backfill-covers`.

Cost is near zero within the free tiers. `terraform destroy` removes everything (empty the bucket first).

## Airtable

Base **Game Collection Tracker**: `app1kBugyp3q8ftks` · table `Games`: `tblVWPMLcgbX3ZqNO` · form view "Add game". IDs are not secrets; the token never goes in the repo.

| Field | ID | Type |
|-------|----|------|
| Title | `fldx6qjcGB9yb51lG` | single line text (primary) |
| Platform | `fldi86d4pcPzQt6pr` | multiple select |
| Genre | `fldpeNOzgyXRUYTkD` | multiple select |
| Completion status | `fldXQkNMHD8EQ7wpy` | single select |
| Rating | `fldliwWWQAzlzbogn` | rating (5 stars) |
| Cover art URL | `fldXUvUiDQQbUK7Lx` | URL (written by the Lambda) |
| Cover art attachment | `fldqlpeWhIprfvIFi` | attachments (display copy, below) |
| Review status | `fldHPlgTKZK11LnhS` | single select (Unreviewed / Reviewed) |

Field names are case-sensitive in the API (`Completion status`, not `Completion Status`). The table was built by hand; `uv run setup-base` mirrors it for a fresh base and does nothing if `Games` exists. Select options are never auto-created (no `typecast`), so a typo in `--platform` fails instead of adding an uncolored option.

Cover art: S3 + CloudFront is the source of truth (`Cover art URL`). The Lambda also writes `Cover art attachment` so gallery views show images; **Airtable downloads and keeps its own copy** of that file (counts toward the 1 GB Free attachment quota). See [ADR 0007](docs/adr/0007-attachment-display-copy.md).

## Layout

```
src/game_tracker/   airtable_client, rawg_client, s3_uploader, handler, config, cli
tests/              pytest, mocks via responses and moto
infra/              Terraform
scripts/package.sh  builds build/lambda.zip
```
