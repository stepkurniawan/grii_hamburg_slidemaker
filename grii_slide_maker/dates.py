"""Date helpers for service slide generation."""

import datetime


def sunday_date(formatted: str, today: datetime.date | None = None):
    """Return the next Sunday in the requested app format."""
    today = today or datetime.date.today()
    days_until_sunday = (6 - today.weekday()) % 7
    next_sunday = today + datetime.timedelta(days=days_until_sunday)

    if formatted == "filename":
        return str(next_sunday).replace("-", "")
    if formatted == "slide":
        return next_sunday.strftime("%d %B %Y")

    return next_sunday
