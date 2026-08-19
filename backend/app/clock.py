"""Indirection around "today" so tests can freeze time deterministically."""

from datetime import date, datetime, timezone

_override: date | None = None


def today() -> date:
    if _override is not None:
        return _override
    return datetime.now(timezone.utc).date()


def set_override(value: date | None) -> None:
    global _override
    _override = value
