"""
Spotify refresh token expiry.

Since 2026-07-20 Spotify refresh tokens expire 6 months after the original
authorization, and refreshing does not extend that deadline. Spotify does not
expose the authorization date, so it comes from SPOTIFY_REFRESH_TOKEN_DATE.
"""

from __future__ import annotations

import calendar
from datetime import date
from typing import Any, Optional

TOKEN_LIFETIME_MONTHS = 6


def parse_token_date(raw: str) -> Optional[date]:
    """
    Parse a YYYY-MM-DD date.

    Returns None for an empty value; raises ValueError for any other format.
    """
    raw = (raw or "").strip()
    if not raw:
        return None
    return date.fromisoformat(raw)


def _add_months(d: date, months: int) -> date:
    """Add calendar months, clamping to the last day of the target month."""
    month_index = d.month - 1 + months
    year = d.year + month_index // 12
    month = month_index % 12 + 1
    day = min(d.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def compute_expiry(token_date: date, today: date) -> dict[str, Any]:
    """Expiry fields for a token authorized on token_date."""
    expires_on = _add_months(token_date, TOKEN_LIFETIME_MONTHS)
    return {
        "token_date": token_date.isoformat(),
        "expires_on": expires_on.isoformat(),
        "days_remaining": (expires_on - today).days,
    }


def expiry_fields(raw: str, today: date) -> dict[str, Any]:
    """Expiry fields from the raw env value, with nulls when unknown."""
    empty: dict[str, Any] = {"token_date": None, "expires_on": None, "days_remaining": None}
    try:
        token_date = parse_token_date(raw)
    except ValueError:
        return {**empty, "warning": "invalid_token_date"}
    if token_date is None:
        return empty
    return compute_expiry(token_date, today)
