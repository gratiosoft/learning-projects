import boto3
import pytest
import responses
from moto import mock_aws

from game_tracker.airtable_client import AirtableClient
from game_tracker.backfill import run_backfill
from game_tracker.handler import Deps, scheduled_backfill
from game_tracker.rawg_client import RawgClient
from game_tracker.s3_uploader import CoverUploader

AT = "https://api.airtable.com/v0/appX/Games"
RAWG = "https://api.rawg.io/api/games"
IMG = "https://media.rawg.io/a.jpg"
CDN = "https://cdn.example.net"


@pytest.fixture
def d():
    with mock_aws():
        s3 = boto3.client("s3")
        s3.create_bucket(Bucket="covers-test")
        yield Deps(
            airtable=AirtableClient("t", "appX", sleep=lambda _: None),
            rawg=RawgClient("k"),
            uploader=CoverUploader("covers-test", CDN, s3),
        )


def _listing(*titles):
    recs = [{"id": f"rec{i}", "fields": {"Title": t}} for i, t in enumerate(titles)]
    responses.get(AT, json={"records": recs})
    for r in recs:
        responses.get(f"{AT}/{r['id']}", json=r)
    return recs


def _rawg_ok():
    responses.get(
        RAWG,
        json={"results": [{"name": "Hades", "background_image": IMG}]},
    )
    responses.get(IMG, body=b"jpg", content_type="image/jpeg")
    responses.patch(AT, json={"records": [{"id": "x"}]})


@responses.activate
def test_only_uncovered_records_are_requested(d):
    _listing()
    out = scheduled_backfill({}, deps=d)
    assert out["statusCode"] == 200
    listing = responses.calls[0].request.url
    assert "filterByFormula" in listing and "Cover+art+URL" in listing.replace("%20", "+")


@responses.activate
def test_noop_when_nothing_missing(d):
    _listing()
    out = scheduled_backfill({}, deps=d)
    assert out == {
        "statusCode": 200,
        "updated": 0,
        "skipped": 0,
        "not_found": 0,
        "errors": 0,
        "remaining": 0,
        "stopped_early": False,
    }
    assert len(responses.calls) == 1  # no RAWG, no S3, no PATCH


@responses.activate
def test_respects_max_per_run_and_reports_counts(d, monkeypatch):
    monkeypatch.setenv("MAX_PER_RUN", "2")
    _listing("Hades", "Hades", "Hades")
    _rawg_ok()
    out = scheduled_backfill({}, deps=d)
    assert out["updated"] == 2 and out["remaining"] == 1 and out["errors"] == 0


@responses.activate
def test_not_found_is_non_fatal_and_does_not_stop_run(d):
    _listing("zzzqqq", "Hades", "zzzqqq", "zzzqqq")
    responses.get(
        RAWG,
        json={"results": []},
    )
    out = scheduled_backfill({}, deps=d)
    assert out["not_found"] == 4 and out["errors"] == 0 and out["remaining"] == 0


@responses.activate
def test_stops_after_three_consecutive_upstream_errors(d):
    _listing("A", "B", "C", "D", "E")
    responses.get(RAWG, status=500)
    out = scheduled_backfill({}, deps=d)
    assert out["errors"] == 3 and out["remaining"] == 2 and out["stopped_early"] is True


@responses.activate
def test_listing_failure_returns_error_instead_of_raising(d):
    responses.get(AT, status=500)
    out = scheduled_backfill({}, deps=d)
    assert out["statusCode"] == 502


def test_streak_resets_on_success():
    seq = iter([502, 502, 200, 502, 502, 200])
    res = run_backfill(range(6), lambda _: {"statusCode": next(seq)})
    assert res.errors == 4 and res.updated == 2 and not res.stopped_early
