"""Shared fixtures: no test touches the network or real credentials."""

from __future__ import annotations

import json
from typing import Any, Optional

import pytest

from api import lastfm, orchestrator, spotify
from api.config import LastFmConfig, SpotifyConfig


class FakeResponse:
    """Minimal stand-in for requests.Response."""

    def __init__(self, status_code: int, json_body: Optional[dict[str, Any]] = None, text: str = ""):
        self.status_code = status_code
        self._json = json_body
        self.text = json.dumps(json_body) if json_body is not None else text

    @property
    def ok(self) -> bool:
        return 200 <= self.status_code < 400

    def json(self) -> Any:
        if self._json is None:
            raise ValueError("No JSON body")
        return self._json


@pytest.fixture(autouse=True)
def _isolate_services(monkeypatch):
    """Start every test with no service configured and no cached state."""
    monkeypatch.setattr(spotify, "spotify_config", SpotifyConfig(client_id="", client_secret="", refresh_token=""))
    monkeypatch.setattr(lastfm, "lastfm_config", LastFmConfig(api_key="", username=""))
    spotify._token_manager.invalidate()
    monkeypatch.setattr(orchestrator, "_auth_cache", None, raising=False)
    yield
    spotify._token_manager.invalidate()


@pytest.fixture
def client():
    return orchestrator.app.test_client()


@pytest.fixture
def use_spotify(monkeypatch):
    def configure() -> None:
        monkeypatch.setattr(
            spotify,
            "spotify_config",
            SpotifyConfig(client_id="id", client_secret="secret", refresh_token="tok"),
        )

    return configure


@pytest.fixture
def use_lastfm(monkeypatch):
    monkeypatch.setattr(lastfm, "lastfm_config", LastFmConfig(api_key="key", username="user"))
