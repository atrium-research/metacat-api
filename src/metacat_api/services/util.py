from datetime import UTC, datetime


def time_to_str(dt: datetime) -> str:
    return dt.isoformat(timespec="seconds").replace("+00:00", "Z")


def now() -> datetime:
    return datetime.now(UTC)
