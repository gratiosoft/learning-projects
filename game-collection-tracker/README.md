# Game Collection Tracker

Track a video game collection in Airtable (Free plan) and attach cover art stored in S3 and served by CloudFront. Learning project for Airtable, AWS Lambda/S3 and Terraform.

Docs: [PRD](docs/prd.md) · [Architecture](docs/architecture.md) · [ADRs](docs/adr/) · [Manual steps](docs/manual-steps.md)

## Status

| Part | State |
|------|-------|
| Python client, CLI, Lambda handler, tests | done; 52 tests pass offline |
| Terraform (`infra/`) | **applied** to AWS (profile `giancarlo`, `us-east-1`); 14 resources |
| Cover-art Lambda | deployed and verified end to end (see [Verification](#verification-results)) |
| Airtable base and form | table and form exist (built by hand), verified live |
| Airtable automations, interface, sharing | manual, see [manual-steps.md](docs/manual-steps.md) |

Deployed: function `game-tracker-cover-art`, bucket `game-tracker-covers-546135990880` (private), CloudFront `https://d7yqaa992ies3.cloudfront.net`.

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
uv run backfill-covers --preview     # RAWG lookup only; no S3, Lambda or Airtable writes
uv run backfill-covers --dry-run     # list games that need a cover
uv run backfill-covers               # invoke the Lambda for each (needs AWS credentials)
```

## Test and lint

```bash
make check     # ruff, pytest (offline, all external services mocked), terraform fmt + validate
```

## Deploy (AWS)

Prerequisites: AWS credentials (profile or env), Terraform >= 1.6, a RAWG API key, an Airtable token.

1. `cp infra/terraform.tfvars.example infra/terraform.tfvars` and set `airtable_base_id` (and `aws_profile`, `region`). `variables.tf` rejects a malformed base ID at plan time.
2. `make plan` builds the zip and shows the plan. Review it.
3. `make deploy` runs `terraform apply` (asks for confirmation). The first apply takes a few minutes because of CloudFront.
4. Store the real secrets. Terraform only creates `CHANGE_ME` placeholders, so real values never enter state. Read them from `.env` into the shell instead of typing them, so they stay out of shell history:
   ```bash
   set -a; . ./.env; set +a
   aws ssm put-parameter --name /game-tracker/RAWG_API_KEY --type SecureString --overwrite --value "$RAWG_API_KEY"
   aws ssm put-parameter --name /game-tracker/AIRTABLE_TOKEN --type SecureString --overwrite --value "$AIRTABLE_TOKEN"
   unset RAWG_API_KEY AIRTABLE_TOKEN
   ```
5. Smoke test: `aws lambda invoke --function-name game-tracker-cover-art --payload '{"record_id":"rec..."}' --cli-binary-format raw-in-base64-out out.json`
6. Backfill: `uv run backfill-covers`.

If RAWG is down the Lambda returns `502 upstream_error`; nothing is written. Re-run later.

### Verification results

Run against the deployed stack (profile `giancarlo`, `us-east-1`):

| Check | Result |
|-------|--------|
| Lambda reads SecureString with the default `aws/ssm` key | works, no IAM change needed |
| Invoke for one record | 200, `cached: false`, object at `covers/<record_id>.jpg` |
| S3 object | `image/jpeg`, AES256 encrypted |
| CloudFront URL | 200 `image/jpeg`, full size; `http://` gets a 301 to https |
| Bucket URL directly | 403 (bucket is private) |
| Airtable | `Cover art URL` and `Cover art attachment` both populated; Airtable fetched the file from our CloudFront URL |
| Re-invoke | `cached: true`, S3 object untouched |
| Invoke with `force` | re-fetched and overwritten, attachment rewritten |
| CloudWatch logs | no errors, no RAWG key or Airtable token present |
| Backfill, 6 games with a Title and no cover | 5 updated; 1 `game_not_found` (a deliberately bad title); a second run listed only the unmatched one |

Not verified: gallery rendering in an Airtable interface (interfaces are built by hand), and `terraform destroy`.

## Costs and teardown

Everything fits the free tiers for a personal collection: Lambda, S3, CloudFront (1 TB/month), SSM standard parameters and 14-day log retention. Airtable Free limits apply separately.

To remove everything:

```bash
aws s3 rm s3://game-tracker-covers-<account-id>/ --recursive   # the bucket must be empty first
terraform -chdir=infra destroy
```

The bucket deliberately does **not** set `force_destroy`, so `destroy` refuses to delete cover art by accident. CloudFront takes a few minutes to disable and delete. Airtable keeps its own copy of each attachment (see below), so deleting S3 objects does not clear it.

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
