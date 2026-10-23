# 0006. Airtable schema and select colors

Status: accepted (attachment clause superseded by [0007](0007-attachment-display-copy.md))

## Context
The Airtable API cannot recolor select options after creation, so colors must be right at creation time. Free plan: 1,000 records per base, 100 automation runs per month.

## Decision
Single table `Games`. Single-select fields (`Platform`, `Genre`, `Completion Status`, `Review Status`) are created with a distinct color per option. `Rating` is a rating field (1-5 stars). `Cover Art URL` is a URL field (written by the Lambda); `Cover Art Attachment` is an attachment field for gallery display (written by the Lambda as a display copy, see 0007; originally planned as unwritten). The "Unreviewed" auto-tag is a `Review Status` option set by an automation (also usable as a default via the form).

## Consequences
- Adding a new Platform or Genre later means adding an option; it needs a color picked manually in the UI.
- Schema IDs are recorded in the project README so scripts can use IDs or names.
