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


def test_stardew_embeds_tab_frame(widget):
    from api.theme_assets import asset_base64

    assert asset_base64("stardew/tab_border_side.png") in widget("?theme=stardew")


@pytest.mark.parametrize("compact", [False, True])
def test_stardew_tab_fits_height(compact):
    from api.config import layout_config, theme_style

    cfg = layout_config("stardew", compact)
    tab = theme_style("stardew", compact)["tab_frame"]
    pad = theme_style("stardew", compact)["tab_padding"]
    assert cfg.album_art_size + tab["top"] + tab["bottom"] + 2 * pad <= cfg.height


@pytest.mark.parametrize("query", ["?theme=stardew", "?theme=stardew&compact=true"])
def test_stardew_bars_inside_content_box(widget, query):
    # Bars are placed in Python; they must land inside the framed content box,
    # to the right of the cover tab.
    import re

    from api.config import layout_config, theme_style

    compact = "compact" in query
    cfg = layout_config("stardew", compact)
    style = theme_style("stardew", compact)
    tab, box = style["tab_frame"], style["box_frame"]

    tab_width = cfg.album_art_size + tab["left"] + tab["right"] + 2 * style["tab_padding"]
    inner_left = tab_width + box["left"]
    inner_right = cfg.width - box["right"]
    inner_bottom = cfg.height - box["bottom"]

    svg = widget(query)
    starts = [(float(x), float(y)) for x, y in re.findall(r'class="bar" d="M ([\d.]+),([\d.]+)', svg)]
    assert len(starts) == cfg.eq_bar_count
    assert min(x for x, _ in starts) >= inner_left
    right_edges = [float(x) for x in re.findall(r'L ([\d.]+),[\d.]+ Z', svg)]
    assert max(right_edges) <= inner_right + 0.01
    assert max(y for _, y in starts) <= inner_bottom


def test_stardew_bars_have_square_corners(widget):
    import re

    def bar_paths(svg):
        return re.findall(r'<path class="bar" d="([^"]+)"', svg)

    # Default theme keeps the rounded tops (quadratic curves)...
    assert all(" Q " in d for d in bar_paths(widget()))
    # ...stardew bars are plain rectangles, for a pixel look
    stardew = bar_paths(widget("?theme=stardew"))
    assert stardew and all(" Q " not in d for d in stardew)
