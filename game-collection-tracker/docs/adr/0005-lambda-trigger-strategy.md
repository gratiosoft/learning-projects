# 0005. How the Lambda is triggered

Status: accepted

## Context
Options: manual invoke, a Function URL called by an Airtable automation script, or a backfill CLI that invokes the Lambda for every game lacking cover art.

## Decision
Implement a **backfill CLI** (`backfill`) that lists games with an empty `Cover art URL` and calls `lambda:Invoke` through boto3 with the owner's own AWS credentials. Manual invoke (`aws lambda invoke`) works with the same payload. **No Function URL or API Gateway** for now.

## Consequences
- No public endpoint, so no auth scheme to design or get wrong, and nothing extra to pay for or secure.
- Covers are not fetched automatically when a friend submits a game; the owner runs backfill. Fine for a personal collection.
- Later option (not built): a Function URL with `AWS_IAM` auth or a secret header, called from an Airtable automation script. Airtable Free limits (100 automation runs per month) also argue for waiting.

## Idempotency limits
If a record already links to our bucket and the object exists, the handler returns the cached URL without re-checking the title. After correcting a Title, invoke with `{"record_id": "...", "force": true}` to re-fetch. The image host is restricted to RAWG's CDN (`media.rawg.io`, https, no redirects) before any download.
