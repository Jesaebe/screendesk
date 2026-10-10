"""Schedule matching using each source's local timezone."""

from datetime import datetime
from zoneinfo import ZoneInfo

from .dump import Source


def is_due(source: Source, instant: datetime) -> bool:
    if not source.enabled:
        return False
    local = instant.astimezone(ZoneInfo(source.timezone))
    return local.strftime("%H:%M") in source.schedule
