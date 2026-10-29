import importlib.util
from datetime import date
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "get_token.py"


def _load():
    spec = importlib.util.spec_from_file_location("get_token", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


get_token = _load()


@pytest.mark.parametrize(
    "text",
    [
        "https://example.com/callback?code=ABC123&state=x",
        '  "https://example.com/callback?code=ABC123"  ',
        "'https://example.com/callback?code=ABC123'",
        "ABC123",
    ],
)
def test_parse_callback_accepts(text):
    assert get_token.parse_callback(text) == "ABC123"


@pytest.mark.parametrize(
    "text, key",
    [
        ("https://example.com/callback?error=access_denied", "denied"),
        ("", "empty"),
        ('  ""  ', "empty"),
        ("AQ" + "x" * 200, "looks_like_refresh_token"),
        ("https://example.com/callback?state=x", "no_code"),
    ],
)
def test_parse_callback_rejects(text, key):
    with pytest.raises(get_token.CallbackError) as exc:
        get_token.parse_callback(text)
    assert exc.value.message_key == key


def test_build_authorize_url():
    url = get_token.build_authorize_url("cid")
    assert "client_id=cid" in url
    assert "response_type=code" in url
    assert "redirect_uri=https%3A%2F%2Fexample.com%2Fcallback" in url
    assert "user-read-currently-playing" in url and "user-read-recently-played" in url


def test_add_six_months():
    assert get_token.add_six_months(date(2026, 8, 31)) == date(2027, 2, 28)
    assert get_token.add_six_months(date(2026, 10, 29)) == date(2027, 4, 29)


def test_every_text_in_both_langs():
    assert set(get_token.TEXTS["en"]) == set(get_token.TEXTS["pt-BR"])


def test_script_is_standalone():
    source = SCRIPT.read_text(encoding="utf-8")
    assert "from api" not in source and "import api" not in source


def test_hint_matches_error():
    assert get_token.hint_key_for("invalid_client") == "client_hint"
    assert get_token.hint_key_for("invalid_grant") == "code_hint"
    assert get_token.hint_key_for("network_error") == "network_hint"
