import json

import pytest
import responses

from game_tracker.airtable_client import AirtableClient, AirtableError

URL = "https://api.airtable.com/v0/appX/Games"


@pytest.fixture
def sleeps():
    return []


@pytest.fixture
def client(sleeps):
    return AirtableClient("tok", "appX", sleep=sleeps.append)


@responses.activate
def test_list_records_follows_offset(client):
    responses.get(URL, json={"records": [{"id": "rec1"}], "offset": "next"})
    responses.get(URL, json={"records": [{"id": "rec2"}]})
    assert [r["id"] for r in client.list_records()] == ["rec1", "rec2"]
    assert "offset=next" in responses.calls[1].request.url
    assert responses.calls[0].request.headers["Authorization"] == "Bearer tok"


@responses.activate
def test_retries_on_429_then_succeeds(client, sleeps):
    responses.get(URL, status=429, headers={"Retry-After": "2"})
    responses.get(URL, json={"records": []})
    assert list(client.list_records()) == []
    assert len(responses.calls) == 2
    assert 2.0 in sleeps


@responses.activate
def test_429_exhausts_retries(sleeps):
    c = AirtableClient("t", "appX", max_retries=2, sleep=sleeps.append)
    responses.get(URL, status=429)
    with pytest.raises(AirtableError) as e:
        list(c.list_records())
    assert e.value.status == 429
    assert len(responses.calls) == 3


@responses.activate
def test_create_batches_of_ten(client):
    responses.post(URL, json={"records": [{"id": "r"}] * 10})
    responses.post(URL, json={"records": [{"id": "r"}] * 3})
    out = client.create_records([{"Title": str(i)} for i in range(13)])
    assert len(out) == 13
    sizes = [len(json.loads(c.request.body)["records"]) for c in responses.calls]
    assert sizes == [10, 3]


@responses.activate
def test_update_batches_of_ten(client):
    responses.patch(URL, json={"records": []})
    responses.patch(URL, json={"records": []})
    client.update_records([{"id": f"rec{i}", "fields": {}} for i in range(11)])
    assert len(responses.calls) == 2


@responses.activate
def test_error_raises(client):
    responses.get(URL + "/recX", status=404, body="nope")
    with pytest.raises(AirtableError):
        client.get_record("recX")


@responses.activate
def test_filter_and_fields_params(client):
    responses.get(URL, json={"records": []})
    list(client.list_records(formula="{Cover art URL} = ''", fields=["Title"]))
    assert "filterByFormula" in responses.calls[0].request.url


@responses.activate
def test_delete_batches_of_ten(client):
    responses.delete(URL, json={"records": [{"id": "r", "deleted": True}] * 10})
    responses.delete(URL, json={"records": [{"id": "r", "deleted": True}] * 2})
    assert client.delete_records([f"rec{i}" for i in range(12)]) == 12
    assert len(responses.calls) == 2
