# Game Collection Tracker

Track a video game collection in Airtable (Free plan) and attach cover art stored in S3 and served by CloudFront. Learning project for Airtable, AWS Lambda/S3 and Terraform.

Docs: [PRD](docs/prd.md) · [Architecture](docs/architecture.md) · [ADRs](docs/adr/) · [Manual steps](docs/manual-steps.md)

## Status

| Part | State |
|------|-------|
| Python client, CLI, Lambda handler, tests | done, tests pass offline |
| Terraform (`infra/`) | written, `fmt` and `validate` pass, **not applied** |
| Airtable base, form, automations, interface | **pending**: `uv run setup-base` creates the table; the rest is manual, see [manual-steps.md](docs/manual-steps.md) |

## Setup

```bash
make setup                 # uv sync
cp .env.example .env       # fill in values; .env is gitignored
```

## Run

```bash
uv run setup-base                      # once: creates the Games table (needs schema.bases:write)
uv run list-games
uv run add-game --title "Hades" --platform PC --status Backlog --rating 5
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

Base: **not created yet.** Once created, its base ID and table/field IDs are recorded here (IDs are not secrets; the token never goes in the repo).

Cover art: S3 + CloudFront is the source of truth (`Cover Art URL`). The Lambda also writes `Cover Art Attachment` so gallery views show images; **Airtable downloads and keeps its own copy** of that file (counts toward the 1 GB Free attachment quota). See [ADR 0007](docs/adr/0007-attachment-display-copy.md).

## Layout

```
src/game_tracker/   airtable_client, rawg_client, s3_uploader, handler, config, cli
tests/              pytest, mocks via responses and moto
infra/              Terraform
scripts/package.sh  builds build/lambda.zip
```
