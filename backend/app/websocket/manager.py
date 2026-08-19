from dataclasses import dataclass, field

from app.config import get_settings

settings = get_settings()


@dataclass
class ConnectionState:
    """Mutable per-connection state, updated live by client->server messages
    and read by the connection's background notification loop."""

    interval_seconds: int = settings.ws_check_interval_default
    enabled_types: set[str] = field(default_factory=lambda: {"overdue", "due_soon"})
    acked: set[str] = field(default_factory=set)

    def apply_subscribe(self, interval_seconds: int | None, enabled_types: list[str] | None) -> None:
        if interval_seconds is not None:
            self.interval_seconds = max(
                settings.ws_check_interval_min, min(settings.ws_check_interval_max, interval_seconds)
            )
        if enabled_types is not None:
            self.enabled_types = set(enabled_types)

    def apply_ack(self, notification_id: str) -> None:
        self.acked.add(notification_id)
