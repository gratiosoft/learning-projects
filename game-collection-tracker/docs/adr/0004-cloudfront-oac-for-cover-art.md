# 0004. Serve cover art through CloudFront with Origin Access Control

Status: accepted

## Context
Airtable's `Cover Art URL` needs a link that keeps working. Options:

| Option | Stable link | Bucket stays private | Complexity |
|--------|-------------|----------------------|------------|
| Presigned GET URLs | No: max 7 days, shorter with role credentials | Yes | Low, but links rot |
| Public-read bucket | Yes | No: needs public access block off | Lowest, but weakens security |
| CloudFront + OAC | Yes | Yes | Moderate: about 30 lines of Terraform |

## Decision
CloudFront with Origin Access Control. The bucket keeps Block Public Access on; its policy allows `s3:GetObject` only to this distribution. The Lambda role alone can write, and only under `covers/`. We use the default `*.cloudfront.net` domain.

## Consequences
- Permanent URL: `https://<id>.cloudfront.net/covers/<record_id>.jpg`.
- Bucket is never world-readable or world-writable.
- CloudFront free tier (1 TB/month) covers this; distribution creation takes a few minutes on first apply.
- Overwriting an object can serve a stale cached copy until the TTL expires. Acceptable: covers rarely change; we set a modest default TTL.
