from datetime import datetime, timedelta


def get_sunday(date: datetime | None = None) -> datetime:
    """Returns the Sunday that starts the week containing date."""
    if date is None:
        date = datetime.now()
    return date - timedelta(days=(date.weekday() + 1) % 7)
