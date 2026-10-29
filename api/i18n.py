"""
Translations for user-facing error cards.

Language comes from the ?lang= query parameter, because GitHub's image
proxy (camo) strips Accept-Language.
"""

from __future__ import annotations

from typing import Optional


ERROR_CODES: tuple[str, ...] = (
    "not_configured",
    "token_expired",
    "invalid_client",
    "auth_failed",
    "premium_required",
    "service_unavailable",
    "api_error",
    "no_tracks",
    "unknown",
)

# What fits on the normal-size card without truncation (see error_card.py)
TITLE_MAX_CHARS = 36
HINT_MAX_CHARS = 47

# code -> lang -> (title, hint)
MESSAGES: dict[str, dict[str, tuple[str, str]]] = {
    "not_configured": {
        "en": ("Widget not configured", "Set SPOTIFY_* or LAST_FM_* env variables"),
        "pt-BR": ("Widget não configurado", "Defina as variáveis SPOTIFY_* ou LAST_FM_*"),
    },
    "token_expired": {
        "en": ("Spotify token expired", "Renew it with scripts/get_token.py"),
        "pt-BR": ("Token do Spotify expirou", "Renove com scripts/get_token.py"),
    },
    "invalid_client": {
        "en": ("Invalid Spotify credentials", "Check SPOTIFY_CLIENT_ID and SPOTIFY_SECRET_ID"),
        "pt-BR": ("Credenciais do Spotify inválidas", "Confira SPOTIFY_CLIENT_ID e SPOTIFY_SECRET_ID"),
    },
    "auth_failed": {
        "en": ("Spotify authentication failed", "Check the deploy logs for details"),
        "pt-BR": ("Falha na autenticação do Spotify", "Veja os detalhes nos logs do deploy"),
    },
    "premium_required": {
        "en": ("Spotify access denied", "App owner needs Spotify Premium"),
        "pt-BR": ("Acesso negado pelo Spotify", "O dono do app precisa de Spotify Premium"),
    },
    "service_unavailable": {
        "en": ("Music service unavailable", "Spotify or Last.fm is down, try again later"),
        "pt-BR": ("Serviço de música indisponível", "Spotify ou Last.fm fora do ar, tente depois"),
    },
    "api_error": {
        "en": ("Music service error", "Check the deploy logs for details"),
        "pt-BR": ("Erro no serviço de música", "Veja os detalhes nos logs do deploy"),
    },
    "no_tracks": {
        "en": ("No song to show right now", "Podcasts and other content aren't shown"),
        "pt-BR": ("Nenhuma música para mostrar agora", "Podcasts e outros conteúdos não aparecem aqui"),
    },
    "unknown": {
        "en": ("Something went wrong", "Check the deploy logs for details"),
        "pt-BR": ("Algo deu errado", "Veja os detalhes nos logs do deploy"),
    },
}


def normalize_lang(raw: Optional[str]) -> str:
    """Map the ?lang= value to a supported language ("en" or "pt-BR")."""
    value = (raw or "").strip().lower().replace("_", "-")
    if value in ("pt", "pt-br"):
        return "pt-BR"
    return "en"


def get_message(code: str, lang: str) -> tuple[str, str]:
    """Return (title, hint) for an error code, falling back to "unknown"."""
    messages = MESSAGES.get(code, MESSAGES["unknown"])
    return messages.get(lang, messages["en"])
