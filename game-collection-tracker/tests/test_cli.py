import io
import json

from game_tracker import cli


class FakeAirtable:
    def __init__(self, records=()):
        self.records = list(records)
        self.created = []

    def list_records(self, formula=None, fields=None):
        self.formula = formula
        return iter(self.records)

    def create_records(self, rows, typecast=False):
        self.created += rows
        return [{"id": "recNEW"}]


class FakeLambda:
    def __init__(self, results):
        self.results, self.calls = results, []

    def invoke(self, FunctionName, Payload):
        self.calls.append(json.loads(Payload))
        return {"Payload": io.BytesIO(json.dumps(self.results.pop(0)).encode())}


def test_list_games(capsys):
    c = FakeAirtable([{"id": "rec1", "fields": {"Title": "Hades", "Platform": ["Steam"]}}])
    assert cli.list_games([], client=c) == 0
    assert "Hades" in capsys.readouterr().out


def test_add_game_drops_empty_fields():
    c = FakeAirtable()
    cli.add_game(["--title", "Hades", "--rating", "5"], client=c)
    assert c.created == [{"Title": "Hades", "Rating": 5}]


def test_backfill_invokes_lambda_and_reports_failures(monkeypatch, capsys):
    monkeypatch.setenv("AIRTABLE_BASE_ID", "appABCDEFGHIJKLMN")
    c = FakeAirtable(
        [{"id": "rec1", "fields": {"Title": "A"}}, {"id": "rec2", "fields": {"Title": "B"}}]
    )
    lam = FakeLambda(
        [{"statusCode": 200, "url": "u"}, {"statusCode": 404, "error": "game_not_found"}]
    )
    assert cli.backfill([], client=c, lambda_client=lam) == 1
    assert [p["record_id"] for p in lam.calls] == ["rec1", "rec2"]
    assert "Cover art URL" in c.formula
    assert "game_not_found" in capsys.readouterr().err


def test_backfill_dry_run(monkeypatch):
    monkeypatch.setenv("AIRTABLE_BASE_ID", "appABCDEFGHIJKLMN")
    lam = FakeLambda([])
    c = FakeAirtable([{"id": "rec1", "fields": {}}])
    assert cli.backfill(["--dry-run"], client=c, lambda_client=lam) == 0
    assert lam.calls == []


class FakeRawg:
    def find_cover(self, title):
        from game_tracker.rawg_client import Cover, GameNotFoundError

        if title == "Nope":
            raise GameNotFoundError("no cover found")
        return Cover(name=title + " (RAWG)", image_url="https://media.rawg.io/x.jpg")


def test_backfill_preview_only_looks_up_rawg(monkeypatch, capsys):
    monkeypatch.setenv("AIRTABLE_BASE_ID", "appABCDEFGHIJKLMN")
    lam = FakeLambda([])
    c = FakeAirtable(
        [{"id": "rec1", "fields": {"Title": "Hades"}}, {"id": "rec2", "fields": {"Title": "Nope"}}]
    )
    assert cli.backfill(["--preview"], client=c, lambda_client=lam, rawg=FakeRawg()) == 0
    out = capsys.readouterr().out
    assert "Hades (RAWG)" in out and "media.rawg.io" in out and "no cover found" in out
    assert lam.calls == []
    assert "!= ''" in c.formula  # blank rows are skipped
