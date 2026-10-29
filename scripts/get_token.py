#!/usr/bin/env python3
"""
Get a new Spotify refresh token for the widget.

Usage:
    python scripts/get_token.py              # English
    python scripts/get_token.py --lang pt-BR # Português

Standard library only, so it runs without installing the project.
Spotify refresh tokens expire 6 months after authorization; run this again
before that and update SPOTIFY_REFRESH_TOKEN and SPOTIFY_REFRESH_TOKEN_DATE.
"""

from __future__ import annotations

import argparse
import base64
import calendar
import getpass
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import webbrowser
from datetime import date
from typing import Optional

AUTHORIZE_URL = "https://accounts.spotify.com/authorize"
TOKEN_URL = "https://accounts.spotify.com/api/token"
REDIRECT_URI = "https://example.com/callback"
SCOPES = "user-read-currently-playing user-read-recently-played"

TEXTS: dict[str, dict[str, str]] = {
    "en": {
        "client_id": "Client ID: ",
        "client_secret": "Client Secret (hidden): ",
        "redirect_note": f"Your app's Redirect URI in the Spotify dashboard must be exactly {REDIRECT_URI}",
        "opening": "Opening the authorization page. If it doesn't open, visit:",
        "paste": "After approving, paste the FULL URL of the page you were sent to:\n> ",
        "empty": "Nothing was pasted. Copy the whole address bar after approving access.",
        "denied": "Access was denied on the Spotify page. Run the script again and click Agree.",
        "no_code": "That URL has no 'code' parameter. Paste the address you land on after clicking Agree.",
        "exchange_failed": "Spotify rejected the code: {error} ({description})",
        "code_hint": (
            "Codes are single-use and expire in minutes; run the script again for a fresh one. "
            "Make sure you pasted the callback URL or its code, not a refresh token."
        ),
        "client_hint": "Check the Client ID and Client Secret in the Spotify dashboard.",
        "network_hint": "Could not reach Spotify; check your connection (or your network proxy).",
        "done": "Done! Set these environment variables on Vercel (Settings > Environment Variables):",
        "expires": "This token expires around {date}. Renew it before then.",
        "redeploy": "Then redeploy the project so the new values take effect.",
    },
    "pt-BR": {
        "client_id": "Client ID: ",
        "client_secret": "Client Secret (oculto): ",
        "redirect_note": f"A Redirect URI do seu app no dashboard do Spotify precisa ser exatamente {REDIRECT_URI}",
        "opening": "Abrindo a página de autorização. Se ela não abrir, acesse:",
        "paste": "Depois de aprovar, cole a URL COMPLETA da página para onde você foi enviado:\n> ",
        "empty": "Nada foi colado. Copie a barra de endereço inteira depois de aprovar o acesso.",
        "denied": "O acesso foi negado na página do Spotify. Rode o script de novo e clique em Concordo.",
        "no_code": "Essa URL não tem o parâmetro 'code'. Cole o endereço que aparece depois de clicar em Concordo.",
        "exchange_failed": "O Spotify recusou o código: {error} ({description})",
        "code_hint": (
            "O código só pode ser usado uma vez e expira em minutos; rode o script de novo para gerar outro. "
            "Confira se você colou a URL do callback ou o código dela, e não um refresh token."
        ),
        "client_hint": "Confira o Client ID e o Client Secret no dashboard do Spotify.",
        "network_hint": "Não foi possível falar com o Spotify; confira a conexão (ou o proxy da rede).",
        "done": "Pronto! Configure estas variáveis de ambiente na Vercel (Settings > Environment Variables):",
        "expires": "Este token expira por volta de {date}. Renove antes disso.",
        "redeploy": "Depois faça o redeploy do projeto para os novos valores valerem.",
    },
}


class CallbackError(Exception):
    """The pasted text is not a usable authorization code."""

    def __init__(self, message_key: str):
        self.message_key = message_key
        super().__init__(message_key)


class TokenError(Exception):
    """The token endpoint rejected the exchange."""

    def __init__(self, error: str, description: str = ""):
        self.error = error
        self.description = description
        super().__init__(f"{error}: {description}")


def normalize_lang(raw: Optional[str]) -> str:
    """Map --lang to "en" or "pt-BR"."""
    value = (raw or "").strip().lower().replace("_", "-")
    return "pt-BR" if value in ("pt", "pt-br") else "en"


def parse_callback(text: str) -> str:
    """
    Extract the authorization code from the pasted callback URL or bare code.

    Raises:
        CallbackError: With a message_key from TEXTS
    """
    text = text.strip().strip("\"'").strip()
    if not text:
        raise CallbackError("empty")

    if "?" in text or "://" in text:
        query = urllib.parse.parse_qs(urllib.parse.urlparse(text).query)
        if "error" in query:
            raise CallbackError("denied")
        codes = query.get("code")
        if not codes or not codes[0]:
            raise CallbackError("no_code")
        return codes[0]

    # A bare code can't be told apart from a refresh token (both start with
    # "AQ"); a refresh token pasted here fails the exchange with invalid_grant,
    # and that error's hint explains the difference.
    return text


def build_authorize_url(client_id: str) -> str:
    """Authorization page URL for the widget's scopes."""
    params = {
        "client_id": client_id,
        "response_type": "code",
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES,
    }
    return f"{AUTHORIZE_URL}?{urllib.parse.urlencode(params)}"


def exchange_code(client_id: str, client_secret: str, code: str) -> dict:
    """
    Exchange an authorization code for tokens.

    Raises:
        TokenError: With Spotify's error and error_description
    """
    credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode("ascii")
    data = urllib.parse.urlencode({
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
    }).encode()
    request = urllib.request.Request(
        TOKEN_URL,
        data=data,
        headers={
            "Authorization": f"Basic {credentials}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read().decode())
        except ValueError:
            body = {}
        raise TokenError(body.get("error", f"HTTP {e.code}"), body.get("error_description", "")) from e
    except urllib.error.URLError as e:
        raise TokenError("network_error", str(e.reason)) from e


def hint_key_for(error: str) -> str:
    """Pick the follow-up hint for a token endpoint error."""
    if error == "invalid_client":
        return "client_hint"
    if error == "network_error":
        return "network_hint"
    return "code_hint"


def add_six_months(d: date) -> date:
    """Add 6 calendar months, clamping to the last day of the month."""
    month_index = d.month - 1 + 6
    year = d.year + month_index // 12
    month = month_index % 12 + 1
    return date(year, month, min(d.day, calendar.monthrange(year, month)[1]))


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Get a Spotify refresh token for the widget.")
    parser.add_argument("--lang", default="en", help="en (default) or pt-BR")
    args = parser.parse_args(argv)
    t = TEXTS[normalize_lang(args.lang)]

    client_id = os.getenv("SPOTIFY_CLIENT_ID") or input(t["client_id"]).strip()
    client_secret = os.getenv("SPOTIFY_SECRET_ID") or getpass.getpass(t["client_secret"]).strip()

    print()
    print(t["redirect_note"])
    url = build_authorize_url(client_id)
    print(t["opening"])
    print(url)
    webbrowser.open(url)
    print()

    try:
        code = parse_callback(input(t["paste"]))
    except CallbackError as e:
        print(t[e.message_key], file=sys.stderr)
        return 1

    try:
        tokens = exchange_code(client_id, client_secret, code)
    except TokenError as e:
        print(t["exchange_failed"].format(error=e.error, description=e.description or "-"), file=sys.stderr)
        print(t[hint_key_for(e.error)], file=sys.stderr)
        return 1

    today = date.today()
    print()
    print(t["done"])
    print()
    print(f"SPOTIFY_REFRESH_TOKEN={tokens['refresh_token']}")
    print(f"SPOTIFY_REFRESH_TOKEN_DATE={today.isoformat()}")
    print()
    print(t["expires"].format(date=add_six_months(today).isoformat()))
    print(t["redeploy"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
