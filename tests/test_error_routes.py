from api import spotify
from api.exceptions import AuthenticationError


def test_not_configured_card(client):
    r = client.get("/?lang=pt-BR")
    assert r.status_code == 200
    assert r.headers["X-Widget-Error"] == "not_configured"
    assert r.headers["Cache-Control"] == "no-cache"
    assert "Widget não configurado" in r.get_data(as_text=True)


def test_auth_failure_card(client, monkeypatch, use_spotify):
    use_spotify()

    def fail():
        raise AuthenticationError("Spotify", code="token_expired")

    monkeypatch.setattr(spotify, "get_now_playing", fail)
    r = client.get("/api/spotify/?compact=true")
    assert r.status_code == 200
    assert r.headers["X-Widget-Error"] == "token_expired"
    assert 'width="400"' in r.get_data(as_text=True)


def test_unexpected_exception_card(client, monkeypatch, use_spotify):
    use_spotify()

    def fail():
        raise RuntimeError("boom")

    monkeypatch.setattr(spotify, "get_now_playing", fail)
    r = client.get("/")
    assert r.status_code == 200
    assert r.headers["X-Widget-Error"] == "unknown"


def test_preview_error_route(client):
    r = client.get("/api/spotify/preview/error?code=token_expired&lang=en&background_color=112233")
    assert r.status_code == 200
    assert r.headers["X-Widget-Error"] == "token_expired"
    assert "#112233" in r.get_data(as_text=True)


def test_preview_error_bad_input(client):
    r = client.get("/preview/error?code=nope&background_color=zzz")
    assert r.headers["X-Widget-Error"] == "unknown"
    assert "#181414" in r.get_data(as_text=True)
