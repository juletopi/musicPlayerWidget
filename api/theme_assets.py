"""
Static theme assets (fonts, images) embedded into the SVG as base64.

The widget is served through <img> (and GitHub's camo proxy), so it cannot
load external files: every asset a theme uses must travel inside the SVG.
Files are read once per instance and cached.
"""

from __future__ import annotations

import os
from base64 import b64encode
from functools import lru_cache

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


@lru_cache(maxsize=None)
def asset_base64(relative_path: str) -> str:
    """Return the base64 content of a file under api/assets/."""
    with open(os.path.join(ASSETS_DIR, relative_path), "rb") as f:
        return b64encode(f.read()).decode("ascii")


def stardew_assets() -> dict[str, str]:
    """Base64 assets used by the stardew theme template."""
    return {
        "font_regular": asset_base64("stardew/StardewValley.woff2"),
        "font_bold": asset_base64("stardew/StardewValleyBold.woff2"),
        "border": asset_base64("stardew/tooltip_border.png"),
        "tab": asset_base64("stardew/tab_border_side.png"),
    }


# Assets each theme needs, keyed by theme name from templates.json
THEME_ASSETS = {
    "stardew": stardew_assets,
}
