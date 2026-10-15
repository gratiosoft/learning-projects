import responses

from game_tracker import cli
from game_tracker.schema import META, ensure_games_table, games_table


def test_every_select_option_has_a_distinct_color():
    selects = [f for f in games_table()["fields"] if f["type"] == "singleSelect"]
    assert {f["name"] for f in selects} == {
        "Platform", "Genre", "Completion Status", "Review Status",
    }  # fmt: skip
    for f in selects:
        colors = [c["color"] for c in f["options"]["choices"]]
        assert all(colors) and len(colors) == len(set(colors)), f["name"]


def test_required_fields_present_and_title_is_primary():
    names = [f["name"] for f in games_table()["fields"]]
    assert names[0] == "Title"
    assert {"Platform", "Genre", "Completion Status", "Rating", "Cover Art URL",
            "Review Status"} <= set(names)  # fmt: skip


@responses.activate
def test_creates_table_when_missing():
    responses.get(f"{META}/appX/tables", json={"tables": [{"name": "Table 1"}]})
    responses.post(f"{META}/appX/tables", json={"id": "tbl1", "name": "Games", "fields": []})
    assert ensure_games_table("t", "appX")["id"] == "tbl1"
    assert responses.calls[1].request.method == "POST"


@responses.activate
def test_idempotent_when_table_exists():
    responses.get(f"{META}/appX/tables", json={"tables": [{"id": "tbl1", "name": "Games"}]})
    assert ensure_games_table("t", "appX")["id"] == "tbl1"
    assert len(responses.calls) == 1


def test_cli_prints_ids(monkeypatch, capsys):
    monkeypatch.setenv("AIRTABLE_BASE_ID", "appX")
    monkeypatch.setenv("AIRTABLE_TOKEN", "t")
    table = {
        "id": "tbl1",
        "name": "Games",
        "fields": [{"id": "fld1", "name": "Title", "type": "singleLineText"}],
    }
    assert cli.setup_base([], ensure=lambda token, base: table) == 0
    assert "fld1" in capsys.readouterr().out
