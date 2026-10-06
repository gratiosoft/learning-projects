import boto3
import pytest
import responses
from moto import mock_aws

from game_tracker.airtable_client import AirtableClient
from game_tracker.handler import Deps, lambda_handler
from game_tracker.rawg_client import RawgClient
from game_tracker.s3_uploader import CoverUploader

BUCKET = "covers-test"
CDN = "https://cdn.example.net"
AT = "https://api.airtable.com/v0/appX/Games"
RAWG = "https://api.rawg.io/api/games"
IMG = "https://media.rawg.io/a.jpg"


@pytest.fixture
def deps():
    with mock_aws():
        s3 = boto3.client("s3")
        s3.create_bucket(Bucket=BUCKET)
        yield (
            Deps(
                airtable=AirtableClient("t", "appX", sleep=lambda _: None),
                rawg=RawgClient("k"),
                uploader=CoverUploader(BUCKET, CDN, s3),
            ),
            s3,
        )


def _mock_happy_path():
    responses.get(f"{AT}/rec1", json={"id": "rec1", "fields": {"Title": "Hades"}})
    responses.get(RAWG, json={"results": [{"name": "Hades", "background_image": IMG}]})
    responses.get(IMG, body=b"jpegdata", content_type="image/jpeg")
    responses.patch(AT, json={"records": [{"id": "rec1"}]})


@responses.activate
def test_success_uploads_and_updates_airtable(deps):
    d, s3 = deps
    _mock_happy_path()
    out = lambda_handler({"record_id": "rec1"}, deps=d)
    assert out == {"statusCode": 200, "url": f"{CDN}/covers/rec1.jpg", "cached": False}
    obj = s3.get_object(Bucket=BUCKET, Key="covers/rec1.jpg")
    assert obj["ContentType"] == "image/jpeg" and obj["Body"].read() == b"jpegdata"
    patch = [c for c in responses.calls if c.request.method == "PATCH"][0]
    assert b"covers/rec1.jpg" in patch.request.body


@responses.activate
def test_game_not_found(deps):
    d, _ = deps
    responses.get(f"{AT}/rec1", json={"id": "rec1", "fields": {"Title": "Nope"}})
    responses.get(RAWG, json={"results": []})
    out = lambda_handler({"record_id": "rec1"}, deps=d)
    assert out["statusCode"] == 404 and out["error"] == "game_not_found"


@responses.activate
def test_upstream_5xx(deps):
    d, _ = deps
    responses.get(f"{AT}/rec1", json={"id": "rec1", "fields": {"Title": "Hades"}})
    responses.get(RAWG, status=500)
    out = lambda_handler({"record_id": "rec1"}, deps=d)
    assert out["statusCode"] == 502 and out["error"] == "upstream_error"


@responses.activate
def test_idempotent_rerun_skips_work(deps):
    d, s3 = deps
    _mock_happy_path()
    first = lambda_handler({"record_id": "rec1"}, deps=d)
    # Second run: the record now carries our URL, so RAWG must not be called again.
    responses.replace(
        responses.GET,
        f"{AT}/rec1",
        json={"id": "rec1", "fields": {"Title": "Hades", "Cover Art URL": first["url"]}},
    )
    n_calls = len(responses.calls)
    second = lambda_handler({"record_id": "rec1"}, deps=d)
    assert second == {"statusCode": 200, "url": first["url"], "cached": True}
    assert len(responses.calls) == n_calls + 1  # only the Airtable GET
    keys = [o["Key"] for o in s3.list_objects_v2(Bucket=BUCKET)["Contents"]]
    assert keys == ["covers/rec1.jpg"]


@responses.activate
def test_title_only_skips_airtable(deps):
    d, s3 = deps
    responses.get(RAWG, json={"results": [{"name": "Hades", "background_image": IMG}]})
    responses.get(IMG, body=b"x", content_type="image/jpeg")
    out = lambda_handler({"title": "Hades"}, deps=d)
    assert out["url"] == f"{CDN}/covers/hades.jpg"
    assert not any("airtable" in c.request.url for c in responses.calls)


def test_bad_request(deps):
    d, _ = deps
    assert lambda_handler({}, deps=d)["statusCode"] == 400
