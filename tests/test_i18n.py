from api.exceptions import APIError, AuthenticationError, NoTracksError, ServiceNotConfiguredError
from api.i18n import (
    ERROR_CODES,
    HINT_MAX_CHARS,
    MESSAGES,
    TITLE_MAX_CHARS,
    get_message,
    normalize_lang,
)


def test_every_code_has_both_langs():
    for code in ERROR_CODES:
        assert set(MESSAGES[code]) == {"en", "pt-BR"}
        for title, hint in MESSAGES[code].values():
            assert title and hint


def test_messages_fit_normal_card():
    for code in ERROR_CODES:
        for title, hint in MESSAGES[code].values():
            assert len(title) <= TITLE_MAX_CHARS, title
            assert len(hint) <= HINT_MAX_CHARS, hint


def test_normalize_lang():
    for raw in ("pt", "pt-br", "PT-BR", "pt_BR", " PT-br "):
        assert normalize_lang(raw) == "pt-BR"
    for raw in ("", None, "es", "en-US", "xx"):
        assert normalize_lang(raw) == "en"


def test_unknown_code_falls_back():
    assert get_message("nope", "pt-BR") == MESSAGES["unknown"]["pt-BR"]


def test_exception_codes():
    codes = [
        ServiceNotConfiguredError().code,
        NoTracksError("Spotify").code,
        AuthenticationError("Spotify", code="token_expired").code,
        APIError("Spotify", 500).code,
    ]
    assert codes == ["not_configured", "no_tracks", "token_expired", "api_error"]
    assert all(code in ERROR_CODES for code in codes)
