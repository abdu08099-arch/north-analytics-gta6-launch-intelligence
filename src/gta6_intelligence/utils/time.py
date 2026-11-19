"""Time helpers. All timestamps in this project are timezone-aware UTC (PRD §7)."""

from datetime import UTC, datetime


def utc_now() -> datetime:
    return datetime.now(UTC)


def ensure_utc(value: datetime) -> datetime:
    """Return `value` in UTC. Naive datetimes are rejected rather than guessed."""
    if value.tzinfo is None:
        raise ValueError("naive datetime: timezone is required (store UTC)")
    return value.astimezone(UTC)
