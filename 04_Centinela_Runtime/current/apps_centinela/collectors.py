"""Read-only API and host collectors."""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import subprocess
import time
from collections import deque
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .config import LEGACY_SERVICES, PROTECTED_SERVICES, CentinelaConfig
from .models import CollectorSnapshot


def _iso_now() -> str:
    return datetime.now(UTC).isoformat()


def _property_map(output: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in output.splitlines():
        key, separator, value = line.partition("=")
        if separator:
            values[key] = value
    return values


def asset_identity(local_asset: bytes, served_asset: bytes) -> dict[str, object]:
    expected_sha = hashlib.sha256(local_asset).hexdigest()
    actual_sha = hashlib.sha256(served_asset).hexdigest()
    return {
        "expected_sha256": expected_sha,
        "actual_sha256": actual_sha,
        "matched": expected_sha == actual_sha,
    }


class SnapshotCollector:
    def __init__(self, config: CentinelaConfig) -> None:
        self.config = config
        self.previous_cursor_updated_at: str | None = None
        self.previous_cursor_observed_at: float | None = None
        self.source_gaps = 0
        self.normalizer_lag_events = 0
        self.partial_payloads = 0
        self.sample_advances = 0
        self.sample_regressions = 0
        self.previous_sample: tuple[object, object, object] | None = None
        self.previous_status: str | None = None
        self.status_transitions = 0
        self.retained_sample_cycles = 0
        self.frontend_cache: dict[str, Any] | None = None
        self.frontend_checked_monotonic = 0.0
        self.seen_gap_ids: set[int] = set()
        self.gap_events: deque[float] = deque()

    def _get_json(self, path: str) -> dict[str, Any]:
        request = Request(
            f"{self.config.api_base.rstrip('/')}{path}",
            method="GET",
            headers={"Accept": "application/json", "User-Agent": "NexoCentinela/0.2"},
        )
        with urlopen(request, timeout=self.config.request_timeout) as response:
            if response.status != 200:
                raise ValueError(f"unexpected HTTP status: {response.status}")
            content_type = response.headers.get("Content-Type", "")
            if "application/json" not in content_type.lower():
                raise ValueError("response is not JSON")
            value = json.loads(response.read(2_000_000))
            if not isinstance(value, dict):
                raise ValueError("JSON root is not an object")
            return value

    def _command(self, *arguments: str) -> tuple[str, str | None]:
        try:
            result = subprocess.run(
                arguments,
                check=False,
                capture_output=True,
                text=True,
                timeout=self.config.request_timeout,
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            return "", type(error).__name__
        if result.returncode != 0:
            return result.stdout, (result.stderr.strip() or f"exit_{result.returncode}")
        return result.stdout, None

    @staticmethod
    def _timestamp(value: object) -> float | None:
        if not isinstance(value, str):
            return None
        normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
        try:
            parsed = datetime.fromisoformat(normalized)
        except ValueError:
            return None
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=UTC)
        return parsed.timestamp()

    def _frontend_build(self) -> dict[str, Any]:
        now = time.monotonic()
        if (
            self.frontend_cache is not None
            and now - self.frontend_checked_monotonic < 60
        ):
            return dict(self.frontend_cache)
        try:
            active_root = self.config.current_frontend_path.resolve(strict=True)
            expected = active_root.name
            index_request = Request(
                f"{self.config.frontend_base.rstrip('/')}/",
                headers={"Cache-Control": "no-cache"},
            )
            with urlopen(index_request, timeout=self.config.request_timeout) as response:
                index = response.read(100_000).decode("utf-8", "replace")
            match = re.search(r'src="(/assets/index-[^"]+\.js)"', index)
            if match is None:
                raise ValueError("frontend entry asset not found")
            asset_request = Request(
                f"{self.config.frontend_base.rstrip('/')}{match.group(1)}",
                headers={"Cache-Control": "no-cache"},
            )
            with urlopen(asset_request, timeout=self.config.request_timeout) as response:
                served_asset = response.read(5_000_000)
            local_asset_path = (active_root / match.group(1).lstrip("/")).resolve(
                strict=True
            )
            if active_root not in local_asset_path.parents:
                raise ValueError("frontend asset escaped active release")
            identity = asset_identity(local_asset_path.read_bytes(), served_asset)
            result = {
                "expected": expected,
                "actual": expected if identity["matched"] else "different-content",
                **identity,
                "asset": match.group(1),
                "error": None,
            }
        except (HTTPError, OSError, URLError, TimeoutError, ValueError) as error:
            result = {
                "expected": (
                    self.config.current_frontend_path.resolve(strict=False).name
                ),
                "actual": None,
                "matched": False,
                "asset": None,
                "error": type(error).__name__,
            }
        self.frontend_cache = result
        self.frontend_checked_monotonic = now
        return dict(result)

    def _telemetry_metrics(
        self, live: dict[str, Any] | None, api_latency_ms: float | None
    ) -> dict[str, Any]:
        metrics: dict[str, Any] = {
            "api_latency_ms": api_latency_ms,
            "frontend": self._frontend_build(),
        }
        uri = Path(self.config.database_path).resolve().as_uri() + "?mode=ro"
        try:
            with sqlite3.connect(uri, uri=True, timeout=0) as connection:
                connection.row_factory = sqlite3.Row
                connection.execute("PRAGMA query_only=ON")
                raw_rows = connection.execute(
                    """
                    SELECT id, received_ts, payload
                    FROM raw_mqtt
                    WHERE topic LIKE '%/data' OR topic LIKE '%/telemetry'
                    ORDER BY id DESC LIMIT 10
                    """
                ).fetchall()
                normalized_rows = connection.execute(
                    """
                    SELECT id, received_ts, boot_id, publish_counter
                    FROM ecu_samples
                    WHERE boot_id IS NOT NULL AND publish_counter IS NOT NULL
                    ORDER BY id DESC LIMIT 2
                    """
                ).fetchall()
                cursor = connection.execute(
                    """
                    SELECT value, updated_ts FROM system_state
                    WHERE key = 'normalizer_last_raw_id'
                    """
                ).fetchone()
        except (OSError, sqlite3.Error) as error:
            return {
                **metrics,
                "storage_error": type(error).__name__,
            }

        raw = raw_rows[0] if raw_rows else None
        normalized = normalized_rows[0] if normalized_rows else None
        raw_times = [
            value
            for value in (self._timestamp(row["received_ts"]) for row in raw_rows)
            if value is not None
        ]
        raw_intervals = [
            (newer - older) * 1000
            for newer, older in zip(raw_times, raw_times[1:], strict=False)
        ]
        recent_gap_count = sum(interval > 2500 for interval in raw_intervals)
        new_gap_ids = {
            int(raw_rows[index]["id"])
            for index, interval in enumerate(raw_intervals)
            if interval > 2500
        } - self.seen_gap_ids
        self.seen_gap_ids.update(new_gap_ids)
        if len(self.seen_gap_ids) > 500:
            self.seen_gap_ids = {
                int(row["id"]) for row in raw_rows if row["id"] is not None
            }
        self.source_gaps += len(new_gap_ids)
        now_monotonic = time.monotonic()
        self.gap_events.extend(now_monotonic for _ in new_gap_ids)
        while self.gap_events and now_monotonic - self.gap_events[0] > 60:
            self.gap_events.popleft()

        normalized_times = [
            value
            for value in (
                self._timestamp(row["received_ts"]) for row in normalized_rows
            )
            if value is not None
        ]
        normalized_interval_ms = (
            (normalized_times[0] - normalized_times[1]) * 1000
            if len(normalized_times) == 2
            else None
        )
        normalizer_commit_interval_ms: float | None = None
        cursor_updated_at = str(cursor["updated_ts"]) if cursor is not None else None
        if (
            cursor_updated_at is not None
            and self.previous_cursor_updated_at is not None
            and cursor_updated_at != self.previous_cursor_updated_at
            and self.previous_cursor_observed_at is not None
        ):
            normalizer_commit_interval_ms = (
                now_monotonic - self.previous_cursor_observed_at
            ) * 1000
        if cursor_updated_at != self.previous_cursor_updated_at:
            self.previous_cursor_updated_at = cursor_updated_at
            self.previous_cursor_observed_at = now_monotonic

        raw_ts = self._timestamp(raw["received_ts"]) if raw is not None else None
        normalized_ts = (
            self._timestamp(normalized["received_ts"])
            if normalized is not None
            else None
        )
        raw_to_normalized = (
            max((raw_ts - normalized_ts) * 1000, 0)
            if raw_ts is not None and normalized_ts is not None
            else None
        )
        if raw_to_normalized is not None and raw_to_normalized > 2500:
            self.normalizer_lag_events += 1

        live_map = live if isinstance(live, dict) else {}
        ecu = live_map.get("ecu")
        ecu_map = ecu if isinstance(ecu, dict) else {}
        status = ecu_map.get("status")
        status_map = status if isinstance(status, dict) else {}
        sample = ecu_map.get("sample")
        sample_map = sample if isinstance(sample, dict) else {}
        required = (
            "id",
            "received_ts",
            "boot_id",
            "publish_counter",
            "rpm_real_value",
            "ignition_state",
            "brake_global",
            "lights_state",
            "turn_left",
            "turn_right",
        )
        missing = [field for field in required if sample_map.get(field) is None]
        if missing:
            self.partial_payloads += 1

        identity = (
            sample_map.get("boot_id"),
            sample_map.get("publish_counter"),
            sample_map.get("id"),
        )
        if self.previous_sample is not None and identity == self.previous_sample:
            self.retained_sample_cycles += 1
        if self.previous_sample is not None and identity != self.previous_sample:
            previous_boot, previous_counter, previous_id = self.previous_sample
            current_boot, current_counter, current_id = identity
            if (
                current_boot == previous_boot
                and isinstance(current_counter, int)
                and isinstance(previous_counter, int)
                and current_counter < previous_counter
            ) or (
                current_boot == previous_boot
                and isinstance(current_id, int)
                and isinstance(previous_id, int)
                and current_id < previous_id
            ):
                self.sample_regressions += 1
            else:
                self.sample_advances += 1
        if any(value is not None for value in identity):
            self.previous_sample = identity

        current_status = str(status_map.get("state", "unknown"))
        if self.previous_status is not None and current_status != self.previous_status:
            self.status_transitions += 1
        self.previous_status = current_status
        api_sample_ts = self._timestamp(sample_map.get("received_ts"))
        normalized_to_api = (
            abs(api_sample_ts - normalized_ts) * 1000
            if api_sample_ts is not None and normalized_ts is not None
            else None
        )
        return {
            **metrics,
            "source_publish_interval_ms": raw_intervals[0] if raw_intervals else None,
            "raw_arrival_interval_ms": raw_intervals[0] if raw_intervals else None,
            "normalized_interval_ms": normalized_interval_ms,
            "normalizer_commit_interval_ms": normalizer_commit_interval_ms,
            "raw_to_normalized_lag_ms": raw_to_normalized,
            "normalized_to_api_lag_ms": normalized_to_api,
            "api_sample_age_ms": status_map.get("age_ms"),
            "sample_id": sample_map.get("id"),
            "publish_counter": sample_map.get("publish_counter"),
            "boot_id": sample_map.get("boot_id"),
            "sample_advances": self.sample_advances,
            "sample_regressions": self.sample_regressions,
            "source_gaps": self.source_gaps,
            "recent_source_gap_count": recent_gap_count,
            "new_source_gap_count": len(new_gap_ids),
            "source_gap_events_60s": len(self.gap_events),
            "normalizer_lag_events": self.normalizer_lag_events,
            "partial_payloads": self.partial_payloads,
            "partial_fields": missing,
            "retained_sample_cycles": self.retained_sample_cycles,
            "status_transitions": self.status_transitions,
            "raw_id": raw["id"] if raw is not None else None,
            "normalizer_cursor": int(cursor["value"]) if cursor is not None else None,
            "normalized_id": normalized["id"] if normalized is not None else None,
            "storage_error": None,
        }

    def _unit(self, name: str) -> dict[str, Any]:
        output, error = self._command(
            "systemctl",
            "show",
            name,
            "--property=LoadState,ActiveState,SubState,UnitFileState,NRestarts,Result,ExecMainStatus",
        )
        values = _property_map(output)
        return {
            "load_state": values.get("LoadState", "unknown"),
            "active_state": values.get("ActiveState", "unknown"),
            "sub_state": values.get("SubState", "unknown"),
            "unit_file_state": values.get("UnitFileState", "unknown"),
            "n_restarts": int(values.get("NRestarts") or 0),
            "result": values.get("Result", "unknown"),
            "exec_main_status": int(values.get("ExecMainStatus") or 0),
            "error": error,
        }

    def collect(self) -> CollectorSnapshot:
        payloads: dict[str, dict[str, Any] | None] = {
            "health": None,
            "live": None,
            "odometer": None,
        }
        api_errors: dict[str, str] = {}
        api_latency_ms: float | None = None
        for name, path in (
            ("health", "/health"),
            ("live", "/live"),
            ("odometer", "/odometer"),
        ):
            try:
                started = time.monotonic()
                payloads[name] = self._get_json(path)
                if name == "live":
                    api_latency_ms = (time.monotonic() - started) * 1000
            except (HTTPError, URLError, TimeoutError, ValueError, json.JSONDecodeError) as error:
                api_errors[name] = type(error).__name__

        services = {name: self._unit(name) for name in PROTECTED_SERVICES}
        legacy = {name: self._unit(name) for name in LEGACY_SERVICES}
        boot_check = self._unit("nexo-startup-verify.service")

        tailscale_status, tailscale_error = self._command("tailscale", "serve", "status")
        listeners_output, _ = self._command("ss", "-ltn")
        listeners = tuple(
            sorted(
                {
                    int(match)
                    for match in re.findall(r":(\d+)\s", listeners_output)
                    if 0 < int(match) <= 65535
                }
            )
        )
        return CollectorSnapshot(
            observed_at=_iso_now(),
            monotonic_time=time.monotonic(),
            health=payloads["health"],
            live=payloads["live"],
            odometer=payloads["odometer"],
            api_errors=api_errors,
            services=services,
            legacy=legacy,
            boot_check=boot_check,
            tailscale_status=tailscale_status,
            tailscale_error=tailscale_error,
            listeners=listeners,
            telemetry_metrics=self._telemetry_metrics(payloads["live"], api_latency_ms),
        )
