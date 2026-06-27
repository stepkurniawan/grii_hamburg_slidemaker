import datetime

from grii_slide_maker.dates import sunday_date


def test_sunday_date_returns_same_day_when_today_is_sunday():
    today = datetime.date(2026, 6, 28)

    assert sunday_date("date", today=today) == today


def test_sunday_date_formats_next_sunday():
    today = datetime.date(2026, 6, 26)

    assert sunday_date("filename", today=today) == "20260628"
    assert sunday_date("slide", today=today) == "28 June 2026"
    assert sunday_date("unknown", today=today) == datetime.date(2026, 6, 28)
