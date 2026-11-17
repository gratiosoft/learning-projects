"""Shared backfill loop used by the scheduled Lambda and the `backfill-covers` CLI.

Each record is enriched by a caller-supplied function that returns the same response dict
as `handler.lambda_handler`. Expected failures (not found, upstream) are counted, never raised.
After MAX_CONSECUTIVE_ERRORS upstream errors in a row the run stops (an outage: retrying
the rest only wastes time and quota); the unprocessed records stay in `remaining`.
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Iterable
from dataclasses import asdict, dataclass

log = logging.getLogger(__name__)

MAX_CONSECUTIVE_ERRORS = 3


@dataclass
class BackfillResult:
    updated: int = 0
    skipped: int = 0
    not_found: int = 0
    errors: int = 0
    remaining: int = 0
    stopped_early: bool = False

    def as_dict(self) -> dict:
        return asdict(self)


def run_backfill(
    records: Iterable[dict],
    enrich: Callable[[dict], dict],
    limit: int | None = None,
    max_consecutive_errors: int = MAX_CONSECUTIVE_ERRORS,
    on_result: Callable[[dict, dict], None] | None = None,
) -> BackfillResult:
    todo = list(records)
    out = BackfillResult()
    processed = 0
    streak = 0
    for rec in todo:
        if limit is not None and processed >= limit:
            break
        if streak >= max_consecutive_errors:
            out.stopped_early = True
            break
        result = enrich(rec)
        processed += 1
        status = result.get("statusCode")
        if status == 200 and result.get("cached"):
            out.skipped += 1
            streak = 0
        elif status == 200:
            out.updated += 1
            streak = 0
        elif status == 404:
            out.not_found += 1
            streak = 0  # a missing title is not an outage
        else:  # 502, 400 or anything unexpected
            out.errors += 1
            streak += 1
        if on_result:
            on_result(rec, result)
    out.remaining = len(todo) - processed
    log.info("backfill finished: %s", out.as_dict())
    return out
