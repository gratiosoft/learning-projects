# Game Collection Tracker: Project Instructions

Follows the repo-level [CLAUDE.md](../CLAUDE.md); nothing here overrides it.

## Stack
Python 3.12 + uv, ruff, pytest, `responses` (HTTP mocks), `moto` (AWS mocks). Terraform (AWS provider 5.x) in `infra/`. Airtable Free plan. RAWG API for cover art.

## Commands
- Setup: `make setup`
- Test: `make test` (offline) · Lint: `make lint` · Everything: `make check`
- Package Lambda: `make package` → `build/lambda.zip`
- Deploy: `make plan`, then `make deploy`. **Never run `terraform apply` or create AWS resources without the owner's explicit OK.**
- CLIs: `uv run setup-base` (creates the Games table), `list-games`, `add-game`, `backfill-covers`

## Conventions
- Commits: `type(game-collection-tracker): subject`.
- One external dependency per module (`airtable_client`, `rawg_client`, `s3_uploader`); the handler composes them via a `Deps` object so tests inject fakes.
- Update PRD, architecture and ADRs in the same commit as behavior changes.
- Tests never hit the network or real AWS (`tests/conftest.py` sets fake credentials).

## Env vars
`AIRTABLE_TOKEN`, `RAWG_API_KEY` (secrets: `.env` locally, SSM `/game-tracker/*` in Lambda), `AIRTABLE_BASE_ID`, `AIRTABLE_TABLE`, `COVERS_BUCKET`, `COVER_BASE_URL`, `LAMBDA_FUNCTION_NAME`, `SSM_PREFIX`; `MAX_PER_RUN` (scheduled function only, set by Terraform). See `.env.example`.

## Gotchas
- Airtable select options cannot be recolored via API: always create them with distinct colors.
- Airtable: 5 req/s, max 10 records per create/update, 100 automation runs/month on Free.
- RAWG takes its key in the query string: never log request URLs.
- Terraform creates SSM parameters with a `CHANGE_ME` placeholder and ignores value changes; real secrets are set with the AWS CLI and must never enter state.
- The Lambda role needs `s3:ListBucket`, otherwise `HeadObject` on a missing key returns 403, not 404.
- Never commit `.env`, `*.tfstate`, `.terraform/` (the lock file `.terraform.lock.hcl` is committed).
- Never generate `infra/terraform.tfvars` from a `.env` line that has an inline `# comment`: the comment ends up in the value (this once deployed a malformed `AIRTABLE_BASE_ID`). Keep comments on their own lines; `variables.tf` validates the ID at plan time.
- RAWG outages return Cloudflare 5xx (e.g. 522). The handler maps them to `502 upstream_error` and writes nothing; just re-run.
- CloudFront returns 403, not 404, for a cover that does not exist.
- Deleting a record does not delete its S3 object or CloudFront cache entry: remove `covers/<record_id>.jpg` yourself.
- A second Lambda, `scheduled_backfill`, runs daily from EventBridge (ADR 0008) using the same zip and role. The form must not include `Cover art URL` or `Cover art attachment`, or records look already covered. `backfill_enabled = false` switches it off.
- The S3 bucket has no `force_destroy`: empty it before `terraform destroy`.
