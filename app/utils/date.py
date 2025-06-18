from datetime import datetime
from zoneinfo import ZoneInfo


def to_utc(dt: datetime, local_tz: str) -> datetime:
    """Convert a naive or local-aware datetime to UTC."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo(local_tz))
    return dt.astimezone(ZoneInfo("UTC"))
