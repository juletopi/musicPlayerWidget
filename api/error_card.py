"""
Error card rendering.

Draws configuration and service errors as an SVG with the widget's own size,
colors and layout, so a broken setup shows a readable card on the profile
README instead of a broken image.
"""

from __future__ import annotations

from xml.sax.saxutils import escape

from .config import compact_svg_config, svg_config
from .i18n import get_message

ERROR_ACCENT = "#e5534b"
FONT_FAMILY = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"

# No album art to blur, so blur backgrounds fall back to a solid color
BLUR_FALLBACK = {"blur_dark": "181414", "blur_light": "efefef"}

# Same average glyph width estimate used by calculate_marquee
CHAR_WIDTH_EM = 0.6


def truncate_text(text: str, font_size: int, max_width: int) -> str:
    """Cut text with an ellipsis so its estimated width fits max_width."""
    max_chars = int(max_width // (font_size * CHAR_WIDTH_EM))
    if len(text) <= max_chars:
        return text
    return text[: max(max_chars - 1, 0)].rstrip() + "…"


def pick_text_color(background_hex: str) -> str:
    """Dark text on light backgrounds, light text on dark ones."""
    channels = []
    for i in (0, 2, 4):
        c = int(background_hex[i:i + 2], 16) / 255
        channels.append(c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4)
    luminance = 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]
    return "#1a1a1a" if luminance > 0.5 else "#f0f0f0"


def render_error_svg(
    code: str,
    lang: str,
    background_color: str,
    border_color: str,
    background_type: str,
    is_compact: bool,
) -> str:
    """
    Render the error card for an error code.

    Args:
        code: Error code (see i18n.ERROR_CODES)
        lang: Normalized language ("en" or "pt-BR")
        background_color: Validated hex color without #
        border_color: Validated hex color without #
        background_type: "color", "blur_dark" or "blur_light"
        is_compact: Whether to use the compact widget size

    Returns:
        SVG markup
    """
    cfg = compact_svg_config if is_compact else svg_config
    background = BLUR_FALLBACK.get(background_type, background_color)
    text_color = pick_text_color(background)
    title, hint = get_message(code, lang)

    border = cfg.widget_border_width
    art_x = cfg.widget_padding_left + border
    art_y = (cfg.height - cfg.album_art_size) / 2
    art_size = cfg.album_art_size

    text_x = art_x + art_size + cfg.art_content_gap
    text_width = cfg.width - cfg.widget_padding_right - border - text_x
    title_size = cfg.song_font_size - 4
    hint_size = cfg.artist_font_size - 2

    # Two lines centred vertically: title baseline above the middle, hint below
    gap = 6
    block_height = title_size + gap + hint_size
    title_y = (cfg.height - block_height) / 2 + title_size
    hint_y = title_y + gap + hint_size

    title = escape(truncate_text(title, title_size, text_width))
    hint = escape(truncate_text(hint, hint_size, text_width))

    if code == "no_tracks":
        glyph, glyph_color = "♪", text_color
    else:
        glyph, glyph_color = "!", ERROR_ACCENT

    half = border / 2
    return f"""<svg width="{cfg.width}" height="{cfg.height}" viewBox="0 0 {cfg.width} {cfg.height}" xmlns="http://www.w3.org/2000/svg">
    <rect x="{half}" y="{half}" width="{cfg.width - border}" height="{cfg.height - border}" rx="{cfg.border_radius}" fill="#{background}" stroke="#{border_color}" stroke-width="{border}"/>
    <rect x="{art_x}" y="{art_y}" width="{art_size}" height="{art_size}" rx="{cfg.border_radius}" fill="none" stroke="{text_color}" stroke-opacity="0.35" stroke-width="1.5"/>
    <text x="{art_x + art_size / 2}" y="{art_y + art_size / 2}" fill="{glyph_color}" font-family="{FONT_FAMILY}" font-size="{int(art_size * 0.5)}" font-weight="700" text-anchor="middle" dominant-baseline="central">{glyph}</text>
    <text x="{text_x}" y="{title_y}" fill="{text_color}" font-family="{FONT_FAMILY}" font-size="{title_size}" font-weight="700">{title}</text>
    <text x="{text_x}" y="{hint_y}" fill="{text_color}" fill-opacity="0.75" font-family="{FONT_FAMILY}" font-size="{hint_size}">{hint}</text>
</svg>"""
