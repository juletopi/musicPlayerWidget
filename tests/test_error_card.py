from api import i18n
from api.error_card import pick_text_color, render_error_svg, truncate_text


def _render(code="token_expired", lang="en", bg="181414", border="181414", bg_type="color", compact=False):
    return render_error_svg(code, lang, bg, border, bg_type, compact)


def test_dimensions():
    normal = _render()
    assert 'width="540"' in normal and 'height="135"' in normal
    compact = _render(compact=True)
    assert 'width="400"' in compact and 'height="80"' in compact


def test_uses_given_colors():
    svg = _render(bg="112233", border="445566")
    assert "#112233" in svg and "#445566" in svg


def test_blur_falls_back_to_solid():
    assert "#efefef" in _render(bg="112233", bg_type="blur_light")
    assert "#181414" in _render(bg="112233", bg_type="blur_dark")


def test_text_color_by_luminance():
    assert pick_text_color("ffffff") == "#1a1a1a"
    assert pick_text_color("181414") == "#f0f0f0"


def test_lang():
    assert "Token do Spotify expirou" in _render(lang="pt-BR")
    assert "Spotify token expired" in _render(lang="en")


def test_escapes_xml(monkeypatch):
    monkeypatch.setitem(i18n.MESSAGES, "unknown", {"en": ("a<b&c", "x")})
    assert "a&lt;b&amp;c" in _render(code="unknown")


def test_truncates():
    text = truncate_text("x" * 100, 18, 200)
    assert text.endswith("…")
    assert len(text) * 18 * 0.6 <= 200


def test_short_text_untouched():
    assert truncate_text("Spotify token expired", 18, 395) == "Spotify token expired"


def test_longest_allowed_texts_fit_normal_card(monkeypatch):
    title = "x" * i18n.TITLE_MAX_CHARS
    hint = "y" * i18n.HINT_MAX_CHARS
    monkeypatch.setitem(i18n.MESSAGES, "unknown", {"en": (title, hint)})
    svg = _render(code="unknown")
    assert title in svg and hint in svg


def test_no_tracks_is_neutral():
    svg = _render(code="no_tracks")
    assert "#e5534b" not in svg
    assert "♪" in svg
