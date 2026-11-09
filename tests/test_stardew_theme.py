"""Stardew theme: per-request ?theme= selection and embedded assets."""

from __future__ import annotations

import pytest

from api import orchestrator
from api.config import compact_svg_config, svg_config


TRACK = {
    "is_playing": True,
    "track_name": "Song",
    "artist_name": "Artist",
    "track_url": "https://example.com/t",
    "artist_url": "https://example.com/a",
    "album_art_url": "",
    "audio_features": None,
}


class FakeService:
    @staticmethod
    def get_now_playing():
        return dict(TRACK)


@pytest.fixture
def widget(monkeypatch, client):
    """Serve the widget from a fake service, with no network for the album art."""
    monkeypatch.setattr(orchestrator, "get_active_service", lambda: ("spotify", FakeService))
    monkeypatch.setattr(
        orchestrator,
        "load_image_with_fallback",
        lambda url: (
            compact_svg_config.placeholder_image,
            svg_config.default_bar_palette,
            svg_config.default_song_palette,
        ),
    )

    def get(query: str = "") -> str:
        r = client.get("/" + query)
        assert r.status_code == 200 and r.mimetype == "image/svg+xml"
        return r.get_data(as_text=True)

    return get


def test_stardew_theme_embeds_font_and_border(widget):
    svg = widget("?theme=stardew")
    assert "@font-face" in svg
    assert "data:font/woff2;base64," in svg
    assert "data:image/png;base64," in svg and "border-image" in svg
    assert "StardewValley" in svg


def test_default_theme_has_no_stardew_assets(widget):
    svg = widget()
    assert "StardewValley" not in svg
    assert "data:font/woff2" not in svg


def test_unknown_theme_falls_back_to_default(widget):
    svg = widget("?theme=nope")
    assert "StardewValley" not in svg
    assert "<svg" in svg


def test_theme_param_is_case_insensitive(widget):
    assert "StardewValley" in widget("?theme=Stardew")


def test_stardew_ignores_blur_background(widget):
    blur_class = 'class="container blur-bg'
    assert blur_class in widget("?background_type=blur_dark")
    assert blur_class not in widget("?theme=stardew&background_type=blur_dark")


@pytest.mark.parametrize("query", ["?theme=stardew", "?theme=stardew&compact=true"])
def test_stardew_status_toggle(widget, query):
    assert "Vibing to:" in widget(query + "&show_status=true")
    assert "Vibing to:" not in widget(query)


def test_stardew_svg_stays_small(widget):
    # Assets are embedded per response; keep the payload light for GitHub's proxy.
    # The placeholder cover is the same for every theme, so measure the overhead.
    overhead = len(widget("?theme=stardew")) - len(widget())
    assert overhead < 20_000


@pytest.mark.parametrize("compact", [False, True])
def test_stardew_layout_fills_height(compact):
    # Bars are placed in Python from these numbers; the art must fill the box.
    from api.config import layout_config

    cfg = layout_config("stardew", compact)
    vertical = cfg.widget_padding_top + cfg.widget_padding_bottom + 2 * cfg.widget_border_width
    assert cfg.album_art_size + vertical == cfg.height
