from api import lastfm, spotify
from tests.conftest import FakeResponse


def _token_ok(monkeypatch):
    calls = []

    def post(*a, **k):
        calls.append(1)
        return FakeResponse(200, {"access_token": "a"})

    monkeypatch.setattr(spotify.requests, "post", post)
    return calls


def test_ok(client, monkeypatch, use_spotify):
    use_spotify("2026-10-29")
    _token_ok(monkeypatch)
    r = client.get("/health/auth")
    body = r.get_json()
    assert r.status_code == 200
    assert r.headers["Cache-Control"] == "no-store"
    assert body["service"] == "spotify" and body["status"] == "ok"
    assert body["expires_on"] == "2027-04-29"
    assert isinstance(body["days_remaining"], int)
    assert not {"a", "tok", "secret"} & {str(v) for v in body.values()}


def test_token_expired(client, monkeypatch, use_spotify):
    use_spotify("2026-10-29")
    monkeypatch.setattr(
        spotify.requests, "post",
        lambda *a, **k: FakeResponse(400, {"error": "invalid_grant", "error_description": "Refresh token revoked"}),
    )
    r = client.get("/health/auth")
    body = r.get_json()
    assert r.status_code == 503
    assert body["status"] == "error" and body["error"] == "token_expired"
    assert "Refresh token revoked" not in r.get_data(as_text=True)


def test_not_configured(client):
    r = client.get("/health/auth")
    assert r.status_code == 503
    assert r.get_json()["error"] == "not_configured"


def test_no_token_date(client, monkeypatch, use_spotify):
    use_spotify()
    _token_ok(monkeypatch)
    body = client.get("/health/auth").get_json()
    assert body["token_date"] is None and body["expires_on"] is None and body["days_remaining"] is None


def test_invalid_token_date_warns(client, monkeypatch, use_spotify):
    use_spotify("29/10/2026")
    _token_ok(monkeypatch)
    body = client.get("/health/auth").get_json()
    assert body["warning"] == "invalid_token_date"


def test_cached(client, monkeypatch, use_spotify):
    use_spotify("2026-10-29")
    calls = _token_ok(monkeypatch)
    client.get("/health/auth")
    client.get("/health/auth")
    assert len(calls) == 1


def test_lastfm(client, monkeypatch, use_lastfm):
    monkeypatch.setattr(lastfm, "get_recent_tracks", lambda limit=10: {"recenttracks": {"track": []}})
    r = client.get("/health/auth")
    body = r.get_json()
    assert r.status_code == 200
    assert body["service"] == "lastfm" and body["days_remaining"] is None


def test_via_prefix(client):
    r = client.get("/api/spotify/health/auth")
    assert r.is_json
