from datetime import date

from api.token_expiry import compute_expiry, expiry_fields

TODAY = date(2026, 10, 29)


def test_six_months_from_today():
    result = compute_expiry(date(2026, 10, 29), TODAY)
    assert result == {"token_date": "2026-10-29", "expires_on": "2027-04-29", "days_remaining": 182}


def test_month_end_clamp():
    assert compute_expiry(date(2026, 8, 31), TODAY)["expires_on"] == "2027-02-28"
    assert compute_expiry(date(2027, 8, 31), TODAY)["expires_on"] == "2028-02-29"


def test_year_rollover():
    assert compute_expiry(date(2026, 12, 15), TODAY)["expires_on"] == "2027-06-15"


def test_negative_days():
    assert compute_expiry(date(2026, 1, 1), date(2026, 7, 4))["days_remaining"] == -3


def test_missing_date():
    assert expiry_fields("", TODAY) == {"token_date": None, "expires_on": None, "days_remaining": None}


def test_invalid_date():
    assert expiry_fields("29/10/2026", TODAY) == {
        "token_date": None,
        "expires_on": None,
        "days_remaining": None,
        "warning": "invalid_token_date",
    }
