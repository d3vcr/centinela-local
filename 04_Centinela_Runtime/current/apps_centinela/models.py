"""Typed state and event models."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any


class Severity(StrEnum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class OverallState(StrEnum):
    BOOTING = "BOOTING"
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    ALERT = "ALERT"
    OFFLINE = "OFFLINE"


class Transition(StrEnum):
    ACTIVATED = "ACTIVATED"
    UPDATED = "UPDATED"
    RECOVERED = "RECOVERED"


@dataclass(frozen=True)
class Finding:
    message: str
    evidence: dict[str, Any]
    severity: Severity | None = None


@dataclass
class Observation:
    code: str
    component: str
    severity: Severity
    active: bool
    message: str
    first_seen: str
    last_seen: str
    occurrences: int
    evidence: dict[str, Any]
    recoverable: bool
    source: str
    failure_streak: int = 0
    recovery_streak: int = 0

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["severity"] = self.severity.value
        return value

    @classmethod
    def from_dict(cls, value: dict[str, Any]) -> Observation:
        return cls(
            code=str(value["code"]),
            component=str(value["component"]),
            severity=Severity(value["severity"]),
            active=bool(value["active"]),
            message=str(value["message"]),
            first_seen=str(value["first_seen"]),
            last_seen=str(value["last_seen"]),
            occurrences=int(value["occurrences"]),
            evidence=dict(value.get("evidence") or {}),
            recoverable=bool(value.get("recoverable", True)),
            source=str(value["source"]),
            failure_streak=int(value.get("failure_streak", 0)),
            recovery_streak=int(value.get("recovery_streak", 0)),
        )


@dataclass(frozen=True)
class CentinelaEvent:
    timestamp: str
    transition: Transition
    code: str
    component: str
    severity: Severity
    message: str
    occurrences: int
    evidence: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        value = asdict(self)
        value["transition"] = self.transition.value
        value["severity"] = self.severity.value
        return value


@dataclass(frozen=True)
class CollectorSnapshot:
    observed_at: str
    monotonic_time: float
    health: dict[str, Any] | None
    live: dict[str, Any] | None
    odometer: dict[str, Any] | None
    api_errors: dict[str, str] = field(default_factory=dict)
    services: dict[str, dict[str, Any]] = field(default_factory=dict)
    legacy: dict[str, dict[str, Any]] = field(default_factory=dict)
    boot_check: dict[str, Any] = field(default_factory=dict)
    tailscale_status: str = ""
    tailscale_error: str | None = None
    listeners: tuple[int, ...] = ()
    telemetry_metrics: dict[str, Any] = field(default_factory=dict)
