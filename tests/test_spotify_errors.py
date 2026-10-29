from pathlib import Path

import pytest
import requests

from api import spotify
from api.exceptions import APIError, AuthenticationError
from api.spotify import classify_token_error
from tests.conftest import FakeResponse


@pytest.mark.parametrize("description", ["Refresh token revoked", "Invalid refresh token"])
def test_classify_invalid_grant(description):
    body = f'{{"error":"invalid_grant","error_description":"{description}"}}'
    assert classify_token_error(400, body) == "token_expired"


def test_classify_invalid_client():
    assert classify_token_error(401, '{"error":"invalid_client"}') == "invalid_client"


def test_classify_other_4xx():
    assert classify_token_error(400, '{"error":"unsupported_grant_type"}') == "auth_failed"


def test_classify_non_json():
    assert classify_token_error(400, "<html>") == "auth_failed"


def test_classify_5xx():
    assert classify_token_error(503, "") == "service_unavailable"


def test_refresh_raises_with_code(monkeypatch, use_spotify):
    use_spotify()
    monkeypatch.setattr(
        spotify.requests, "post",
        lambda *a, **k: FakeResponse(400, {"error": "invalid_grant", "error_description": "Refresh token revoked"}),
    )
    with pytest.raises(AuthenticationError) as exc:
        spotify._token_manager.get_token(force_refresh=True)
    assert exc.value.code == "token_expired"


def test_refresh_network_error(monkeypatch, use_spotify):
    use_spotify()

    def boom(*a, **k):
        raise requests.ConnectionError("down")

    monkeypatch.setattr(spotify.requests, "post", boom)
    with pytest.raises(AuthenticationError) as exc:
        spotify._token_manager.get_token(force_refresh=True)
    assert exc.value.code == "service_unavailable"


def test_api_get_403(monkeypatch, use_spotify):
    use_spotify()
    monkeypatch.setattr(spotify.requests, "post", lambda *a, **k: FakeResponse(200, {"access_token": "a"}))
    monkeypatch.setattr(spotify.requests, "get", lambda *a, **k: FakeResponse(403, text="Premium required"))
    with pytest.raises(APIError) as exc:
        spotify._api_get("https://api.spotify.com/v1/me/player/currently-playing")
    assert exc.value.code == "premium_required"


def test_api_get_5xx(monkeypatch, use_spotify):
    use_spotify()
    monkeypatch.setattr(spotify.requests, "post", lambda *a, **k: FakeResponse(200, {"access_token": "a"}))
    monkeypatch.setattr(spotify.requests, "get", lambda *a, **k: FakeResponse(502, text="bad gateway"))
    with pytest.raises(APIError) as exc:
        spotify._api_get("https://api.spotify.com/v1/me/player/currently-playing")
    assert exc.value.code == "service_unavailable"


def test_no_tls_bypass():
    api_dir = Path(__file__).resolve().parent.parent / "api"
    for path in api_dir.glob("*.py"):
        source = path.read_text(encoding="utf-8")
        assert "verify=False" not in source, path.name
        assert "disable_warnings" not in source, path.name
