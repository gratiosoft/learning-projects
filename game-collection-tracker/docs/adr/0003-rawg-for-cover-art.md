# 0003. RAWG as the cover art source

Status: accepted

## Context
We need a free API that searches games by title and returns an image URL.

## Decision
RAWG Video Games Database (`GET /api/games?search=...&key=...`, field `background_image`). Best match: exact normalized-title match first, otherwise the first result (RAWG ranks by relevance). Secrets (`RAWG_API_KEY`, `AIRTABLE_TOKEN`) live in SSM Parameter Store SecureStrings for the Lambda and in a gitignored `.env` locally; `.env.example` documents them.

## Consequences
- Free tier needs attribution and a key; terms apply to display, and we copy images to our own bucket, so keep this for personal use.
- `background_image` is a screenshot-style image, not always a box cover. Acceptable for a gallery; swappable behind `rawg_client.py`.
- The key is sent as a query parameter, so request URLs must never be logged.
- SSM standard SecureString parameters are free; Secrets Manager costs about $0.40 per secret per month, so SSM wins here.
- Terraform creates the parameters with a placeholder value and ignores later changes, so real secrets never enter state.
