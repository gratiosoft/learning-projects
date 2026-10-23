# 0007. Also write a display copy to `Cover art attachment`

Status: accepted · Supersedes the attachment clause of [0006](0006-airtable-schema-and-colors.md)

## Context
Airtable gallery views render attachment fields, not URL fields. With only `Cover art URL`, the gallery would show no images.

## Decision
After saving `Cover art URL`, the Lambda also writes `Cover art attachment = [{"url": <CloudFront URL>}]`. S3 + CloudFront remains the source of truth; the attachment is a display copy that Airtable downloads from our URL and stores itself.
- The URL is always written first, in its own update. If the attachment write fails, the handler logs a warning and still succeeds.
- Skipped when the record already has an attachment, unless `force` is set. With `force` the attachment URL gets a throwaway `?v=<epoch>` so Airtable does not reuse the old file.
- When the cover already exists (idempotent path) but the attachment is missing, only the attachment is written.

## Consequences
- Airtable keeps its own copy of each image, counted against the Free plan's 1 GB attachment quota (covers are small, roughly 100-300 KB each).
- Deleting an object from S3 does not remove Airtable's copy.
- One extra Airtable request per new cover (still far below 5 req/s).
