# 0008. Scheduled backfill with EventBridge

Status: accepted. Supersedes the trigger part of [0005](0005-lambda-trigger-strategy.md) (the idempotency notes in 0005 still apply).

## Context
Friends submit games through the Airtable form with no cover. Under 0005 nothing fills it in until someone runs `backfill-covers`. The owner is on the Airtable Free plan: automations are limited (100 runs per month), and scripting/webhook calls from Airtable to AWS would need a public endpoint (Function URL or API Gateway) with its own auth.

## Decision
An EventBridge rule (default `rate(1 day)`, validated, switchable with `backfill_enabled = false`) invokes a second Lambda, `game_tracker.handler.scheduled_backfill`, from the same zip, role and environment as `cover_art`.

- It lists records with a `Title` and an empty `Cover art URL`, processes at most `MAX_PER_RUN` (default 10, Terraform `max_per_run`), and calls the existing `lambda_handler` for each record (no duplicated enrichment logic).
- The loop lives in `game_tracker/backfill.py` and is shared with the CLI. It stops after 3 consecutive upstream (502) errors. Not-found is counted and does not stop the run.
- It returns `{updated, skipped, not_found, errors, remaining, stopped_early}` and never raises for expected failures. Logs carry counts and record IDs only.
- Timeout 300 s, its own log group (14-day retention).
- IAM: same role. The only policy change is adding the new log group to the existing `Logs` statement, because a role can only write logs to groups it lists. No new actions, no wildcards.

## Consequences
- Covers appear within a day of a submission. For an immediate run: `aws lambda invoke --function-name game-tracker-scheduled-backfill ...` or `uv run backfill-covers`.
- No public endpoint and no Airtable automation is involved, so no new auth surface and no use of the 100 runs per month.
- A record whose title never matches is retried every day (one RAWG search, no writes) until the Title is fixed. Bounded by `MAX_PER_RUN`; with more than 10 permanently unmatched games the queue would starve newer ones. Fix titles, or raise `max_per_run`.
- The form must not contain `Cover art URL` or `Cover art attachment`: a value typed there makes the record look already covered.
- Two runs could overlap only if a run exceeds a day; the work is idempotent anyway (same S3 key, same URL).
- Cost is negligible: one invocation a day, free-tier Lambda and EventBridge.
