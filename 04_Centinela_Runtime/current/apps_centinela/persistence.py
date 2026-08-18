"""Atomic bounded persistence outside the official SQLite database."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Any


class CentinelaPersistence:
    def __init__(self, state_dir: Path, event_limit: int = 500) -> None:
        self.state_dir = state_dir
        self.state_path = state_dir / "state.json"
        self.events_path = state_dir / "events.jsonl"
        self.event_limit = event_limit

    def prepare(self) -> None:
        self.state_dir.mkdir(parents=True, exist_ok=True, mode=0o750)

    def load_state(self) -> dict[str, Any] | None:
        try:
            value = json.loads(self.state_path.read_text(encoding="utf-8"))
            return value if isinstance(value, dict) else None
        except (FileNotFoundError, json.JSONDecodeError, OSError, UnicodeError):
            return None

    def load_events(self, limit: int | None = None) -> list[dict[str, Any]]:
        safe_limit = min(max(limit or self.event_limit, 1), self.event_limit)
        try:
            lines = self.events_path.read_text(encoding="utf-8").splitlines()
        except (FileNotFoundError, OSError, UnicodeError):
            return []
        events: list[dict[str, Any]] = []
        for line in lines[-safe_limit:]:
            try:
                value = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(value, dict):
                events.append(value)
        return events

    def save_state(self, value: dict[str, Any]) -> None:
        self.prepare()
        self._atomic_text(
            self.state_path,
            json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            + "\n",
        )

    def append_events(self, new_events: list[dict[str, Any]]) -> None:
        if not new_events:
            return
        self.prepare()
        events = [*self.load_events(self.event_limit), *new_events][-self.event_limit :]
        body = "".join(
            json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
            + "\n"
            for item in events
        )
        self._atomic_text(self.events_path, body)

    def _atomic_text(self, target: Path, body: str) -> None:
        descriptor, temporary_name = tempfile.mkstemp(
            dir=self.state_dir, prefix=f".{target.name}.", text=True
        )
        temporary = Path(temporary_name)
        try:
            with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(body)
                handle.flush()
                os.fsync(handle.fileno())
            os.chmod(temporary, 0o600)
            os.replace(temporary, target)
        finally:
            temporary.unlink(missing_ok=True)
