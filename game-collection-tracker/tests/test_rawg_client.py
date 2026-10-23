import pytest
import responses

from game_tracker.rawg_client import GameNotFoundError, RawgClient, UpstreamError

SEARCH = "https://api.rawg.io/api/games"


@responses.activate
def test_picks_exact_title_match_over_first_result():
    responses.get(
        SEARCH,
        json={
            "results": [
                {"name": "Zelda Clone", "background_image": "http://img/a.jpg"},
                {"name": "The Legend of Zelda", "background_image": "http://img/b.jpg"},
            ]
        },
    )
    cover = RawgClient("k").find_cover("the legend of zelda")
    assert cover.image_url == "http://img/b.jpg"


@responses.activate
def test_partial_title_matches_when_all_words_present_and_skips_imageless():
    responses.get(
        SEARCH,
        json={
            "results": [
                {"name": "Witcher 3 Mod", "background_image": None},
                {"name": "The Witcher 3: Wild Hunt", "background_image": "u"},
            ]
        },
    )
    assert RawgClient("k").find_cover("witcher 3").name == "The Witcher 3: Wild Hunt"


@responses.activate
def test_fuzzy_junk_is_rejected():
    responses.get(SEARCH, json={"results": [{"name": "A Sirius Game", "background_image": "u"}]})
    with pytest.raises(GameNotFoundError):
        RawgClient("k").find_cover("zzzqqq not a game")


@responses.activate
def test_not_found():
    responses.get(SEARCH, json={"results": []})
    with pytest.raises(GameNotFoundError):
        RawgClient("k").find_cover("zzz")


@responses.activate
def test_5xx_is_upstream_error():
    responses.get(SEARCH, status=503)
    with pytest.raises(UpstreamError):
        RawgClient("k").find_cover("x")


@responses.activate
def test_download_returns_bytes_and_content_type():
    responses.get("https://media.rawg.io/a.png", body=b"png", content_type="image/png")
    data, ct = RawgClient("k").download("https://media.rawg.io/a.png")
    assert (data, ct) == (b"png", "image/png")


@responses.activate
def test_network_error_does_not_leak_key():
    import requests

    responses.get(SEARCH, body=requests.ConnectionError("https://x?key=SECRET"))
    with pytest.raises(UpstreamError) as e:
        RawgClient("SECRET").find_cover("x")
    assert "SECRET" not in str(e.value)


@pytest.mark.parametrize(
    "url",
    [
        "http://media.rawg.io/a.jpg",  # not https
        "https://evil.example.com/a.jpg",
        "https://media.rawg.io.evil.com/a.jpg",
        "https://169.254.169.254/latest/meta-data",
        "file:///etc/passwd",
    ],
)
@responses.activate
def test_download_refuses_other_hosts(url):
    with pytest.raises(UpstreamError):
        RawgClient("k").download(url)
    assert len(responses.calls) == 0


@responses.activate
def test_download_does_not_follow_redirects():
    responses.get("https://media.rawg.io/a.jpg", status=302, headers={"Location": "http://evil/x"})
    with pytest.raises(UpstreamError):
        RawgClient("k").download("https://media.rawg.io/a.jpg")
