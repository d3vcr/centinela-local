"""Deterministic state machine with hysteresis and event transitions."""

from __future__ import annotations

from collections import defaultdict, deque
from copy import deepcopy
from datetime import UTC, datetime
from typing import Any

from .config import CentinelaConfig
from .models import (
    CentinelaEvent,
    CollectorSnapshot,
    Observation,
    OverallState,
    Severity,
    Transition,
)
from .rules import RULES, evaluate_conditions

SEVERITY_RANK = {Severity.INFO: 0, Severity.WARNING: 1, Severity.CRITICAL: 2}


def _iso_now() -> str:
    return datetime.now(UTC).isoformat()


def _family_state(payload: dict[str, Any] | None, family: str) -> str:
    if not isinstance(payload, dict):
        return "unknown"
    value = payload.get(family)
    if not isinstance(value, dict):
        return "unknown"
    status = value.get("status")
    if not isinstance(status, dict):
        return "unknown"
    return str(status.get("state", "unknown")).upper()


def _object(value: object) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


class CentinelaEngine:
    def __init__(self, config: CentinelaConfig) -> None:
        self.config = config
        self.observations: dict[str, Observation] = {}
        self.events: list[CentinelaEvent] = []
        self.previous_sample: dict[str, Any] | None = None
        self.previous_restarts: dict[str, int] = {}
        self.restart_history: dict[str, deque[float]] = defaultdict(deque)
        self.poll_count = 0
        self.last_event: CentinelaEvent | None = None
        self.last_successful_poll: str | None = None
        self.latest_state = self._initial_state()

    def _initial_state(self) -> dict[str, Any]:
        return {
            "overall": OverallState.BOOTING.value,
            "components": {
                "system_state": OverallState.BOOTING.value,
                "ecu_state": "UNKNOWN",
                "gps_state": "UNKNOWN",
                "api_state": "UNKNOWN",
                "services_state": "UNKNOWN",
                "tailscale_state": "UNKNOWN",
                "security_state": "UNKNOWN",
                "storage_state": "UNKNOWN",
            },
            "active_alerts": [],
            "last_event": None,
            "source_freshness": {},
            "security": {},
            "services": {},
            "tailscale": {},
            "legacy": {},
            "odometer": {},
            "metadata": {"poll_count": 0},
        }

    def restore(self, payload: dict[str, Any] | None) -> None:
        if not payload:
            return
        try:
            observations = payload.get("observations") or []
            self.observations = {
                item["code"]: Observation.from_dict(item)
                for item in observations
                if isinstance(item, dict)
            }
            metadata = payload.get("engine_metadata") or {}
            self.previous_sample = metadata.get("previous_sample")
            self.previous_restarts = {
                str(key): int(value)
                for key, value in (metadata.get("previous_restarts") or {}).items()
            }
            self.poll_count = int(metadata.get("poll_count", 0))
            self.last_successful_poll = metadata.get("last_successful_poll")
        except (KeyError, TypeError, ValueError):
            self.observations = {}
            self.previous_sample = None
            self.previous_restarts = {}
            self.poll_count = 0

    def evaluate(self, snapshot: CollectorSnapshot) -> tuple[dict[str, Any], list[CentinelaEvent]]:
        self.poll_count += 1
        if snapshot.health is not None:
            self.last_successful_poll = snapshot.observed_at
        restart_total = self._update_restart_history(snapshot)
        conditions = evaluate_conditions(
            snapshot,
            previous_sample=self.previous_sample,
            restart_count_in_window=restart_total,
            odometer_reference_km=self.config.odometer_reference_km,
            tailscale_target=self.config.tailscale_target,
        )

        cycle_events: list[CentinelaEvent] = []
        for spec in RULES:
            finding = conditions[spec.code]
            record = self.observations.get(spec.code)
            if record is None:
                record = Observation(
                    code=spec.code,
                    component=spec.component,
                    severity=spec.severity,
                    active=False,
                    message="",
                    first_seen=snapshot.observed_at,
                    last_seen=snapshot.observed_at,
                    occurrences=0,
                    evidence={},
                    recoverable=spec.recoverable,
                    source=spec.source,
                )
                self.observations[spec.code] = record

            if finding is not None:
                record.failure_streak += 1
                record.recovery_streak = 0
                was_active = record.active
                changed = (
                    record.message != finding.message
                    or record.evidence != finding.evidence
                    or record.severity != (finding.severity or spec.severity)
                )
                record.last_seen = snapshot.observed_at
                record.occurrences += 1
                record.message = finding.message
                record.evidence = deepcopy(finding.evidence)
                record.severity = finding.severity or spec.severity
                if not was_active and record.failure_streak >= spec.activation_count:
                    record.active = True
                    record.first_seen = snapshot.observed_at
                    cycle_events.append(
                        self._event(record, Transition.ACTIVATED, snapshot.observed_at)
                    )
                elif was_active and changed:
                    cycle_events.append(
                        self._event(record, Transition.UPDATED, snapshot.observed_at)
                    )
            else:
                record.failure_streak = 0
                if record.active:
                    record.recovery_streak += 1
                    if record.recovery_streak >= spec.recovery_count:
                        record.active = False
                        record.last_seen = snapshot.observed_at
                        cycle_events.append(
                            self._event(record, Transition.RECOVERED, snapshot.observed_at)
                        )
                else:
                    record.recovery_streak = 0

        self._update_previous_sample(snapshot, conditions["CENTINELA_SAMPLE_REGRESSION"])
        self.events.extend(cycle_events)
        if cycle_events:
            self.last_event = cycle_events[-1]
        self.latest_state = self._build_state(snapshot)
        return deepcopy(self.latest_state), cycle_events

    def _event(
        self, observation: Observation, transition: Transition, timestamp: str
    ) -> CentinelaEvent:
        return CentinelaEvent(
            timestamp=timestamp,
            transition=transition,
            code=observation.code,
            component=observation.component,
            severity=observation.severity,
            message=observation.message,
            occurrences=observation.occurrences,
            evidence=deepcopy(observation.evidence),
        )

    def _update_restart_history(self, snapshot: CollectorSnapshot) -> int:
        now = snapshot.monotonic_time
        for unit, state in snapshot.services.items():
            current = int(state.get("n_restarts") or 0)
            previous = self.previous_restarts.get(unit, current)
            if current > previous:
                for _ in range(current - previous):
                    self.restart_history[unit].append(now)
            self.previous_restarts[unit] = current
        total = 0
        for history in self.restart_history.values():
            while history and now - history[0] > 600:
                history.popleft()
            total += len(history)
        return total

    def _update_previous_sample(
        self, snapshot: CollectorSnapshot, regression: object | None
    ) -> None:
        live = snapshot.live or {}
        ecu = live.get("ecu")
        sample = ecu.get("sample") if isinstance(ecu, dict) else None
        if not isinstance(sample, dict):
            return
        if self.previous_sample is None:
            self.previous_sample = deepcopy(sample)
            return
        boot_changed = sample.get("boot_id") != self.previous_sample.get("boot_id")
        if boot_changed or regression is None:
            self.previous_sample = deepcopy(sample)

    def _build_state(self, snapshot: CollectorSnapshot) -> dict[str, Any]:
        active = [item for item in self.observations.values() if item.active]
        active.sort(key=lambda item: SEVERITY_RANK[item.severity], reverse=True)
        active_codes = {item.code for item in active}
        if "CENTINELA_API_UNREACHABLE" in active_codes:
            overall = OverallState.OFFLINE
        elif any(item.severity is Severity.CRITICAL for item in active):
            overall = OverallState.ALERT
        elif any(item.severity is Severity.WARNING for item in active):
            overall = OverallState.DEGRADED
        else:
            overall = OverallState.HEALTHY

        health = snapshot.health or {}
        live = snapshot.live or {}
        database = _object(health.get("database"))
        safety = _object(health.get("safety"))
        odometer = snapshot.odometer or {}
        ecu = _object(live.get("ecu"))
        ecu_sample = _object(ecu.get("sample"))

        components = {
            "system_state": overall.value,
            "ecu_state": _family_state(snapshot.live, "ecu"),
            "gps_state": _family_state(snapshot.live, "gps"),
            "api_state": (
                "OFFLINE"
                if "CENTINELA_API_UNREACHABLE" in active_codes
                else "DEGRADED"
                if "CENTINELA_API_DEGRADED" in active_codes
                else "HEALTHY"
            ),
            "services_state": (
                "ALERT"
                if "CENTINELA_NEXO_SERVICE_DOWN" in active_codes
                else "DEGRADED"
                if {
                    "CENTINELA_SERVICE_RESTARTING",
                    "CENTINELA_LEGACY_REACTIVATED",
                    "CENTINELA_BOOT_CHECK_FAILED",
                }
                & active_codes
                else "HEALTHY"
            ),
            "tailscale_state": (
                "ALERT"
                if "CENTINELA_TAILSCALE_TARGET_MISMATCH" in active_codes
                else "HEALTHY"
            ),
            "security_state": (
                "ALERT"
                if "CENTINELA_SECURITY_INVARIANT_BROKEN" in active_codes
                else "HEALTHY"
            ),
            "storage_state": (
                "DEGRADED"
                if "CENTINELA_ODOMETER_REFERENCE_CHANGED" in active_codes
                else "HEALTHY"
            ),
        }
        ecu_status = (
            live.get("ecu", {}).get("status", {})
            if isinstance(live.get("ecu"), dict)
            else {}
        )
        gps_status = (
            live.get("gps", {}).get("status", {})
            if isinstance(live.get("gps"), dict)
            else {}
        )
        return {
            "overall": overall.value,
            "components": components,
            "active_alerts": [item.to_dict() for item in active],
            "last_event": self.last_event.to_dict() if self.last_event else None,
            "source_freshness": {
                "api_last_success": self.last_successful_poll,
                "ecu": ecu_status,
                "gps": gps_status,
                "observed_at": snapshot.observed_at,
            },
            "security": {
                **safety,
                "relay_outputs_enabled": ecu_sample.get("relay_outputs_enabled"),
                "database_readonly": database.get("readonly"),
                "database_query_only": database.get("query_only"),
            },
            "services": deepcopy(snapshot.services),
            "tailscale": {
                "target": self.config.tailscale_target,
                "matched": "CENTINELA_TAILSCALE_TARGET_MISMATCH" not in active_codes,
                "error": snapshot.tailscale_error,
            },
            "legacy": deepcopy(snapshot.legacy),
            "odometer": deepcopy(odometer.get("odometer") or {}),
            "metadata": {
                "poll_count": self.poll_count,
                "observed_at": snapshot.observed_at,
                "api_errors": deepcopy(snapshot.api_errors),
                "listeners": list(snapshot.listeners),
            },
            "telemetry_metrics": deepcopy(snapshot.telemetry_metrics),
        }

    def persistence_payload(self) -> dict[str, Any]:
        return {
            "state": deepcopy(self.latest_state),
            "observations": [item.to_dict() for item in self.observations.values()],
            "engine_metadata": {
                "previous_sample": deepcopy(self.previous_sample),
                "previous_restarts": deepcopy(self.previous_restarts),
                "poll_count": self.poll_count,
                "last_successful_poll": self.last_successful_poll,
            },
            "saved_at": _iso_now(),
        }
