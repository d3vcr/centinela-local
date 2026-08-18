"""Loopback-only read-only HTTP API."""

from __future__ import annotations

import json
import time
from copy import deepcopy
from datetime import UTC, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Lock
from typing import Any
from urllib.parse import parse_qs, urlsplit

from . import VERSION


def _iso_now() -> str:
    return datetime.now(UTC).isoformat()


class SharedState:
    def __init__(self, poll_interval: float) -> None:
        self.lock = Lock()
        self.started_monotonic = time.monotonic()
        self.poll_interval = poll_interval
        self.state: dict[str, Any] = {
            "overall": "BOOTING",
            "components": {},
            "active_alerts": [],
        }
        self.events: list[dict[str, Any]] = []
        self.last_successful_poll: str | None = None

    def update(
        self,
        state: dict[str, Any],
        events: list[dict[str, Any]],
        last_successful_poll: str | None,
    ) -> None:
        with self.lock:
            self.state = state
            self.events = events
            self.last_successful_poll = last_successful_poll

    def health(self) -> dict[str, Any]:
        with self.lock:
            return {
                "ok": True,
                "service": "nexo-centinela",
                "version": VERSION,
                "generated_at": _iso_now(),
                "state": self.state.get("overall", "BOOTING"),
                "uptime": max(0.0, time.monotonic() - self.started_monotonic),
                "poll_interval": self.poll_interval,
                "last_successful_poll": self.last_successful_poll,
            }

    def state_payload(self) -> dict[str, Any]:
        with self.lock:
            return deepcopy(self.state)

    def event_payload(self, limit: int) -> list[dict[str, Any]]:
        with self.lock:
            return deepcopy(self.events[-limit:])


def make_handler(shared: SharedState) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        server_version = "NexoCentinela/0.2"

        def log_message(self, format: str, *args: object) -> None:
            return

        def _json(self, status: int, value: object) -> None:
            body = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(body)

        def do_HEAD(self) -> None:
            self.do_GET()

        def do_GET(self) -> None:
            parsed = urlsplit(self.path)
            if parsed.path == "/health":
                self._json(200, shared.health())
                return
            if parsed.path == "/state":
                self._json(200, shared.state_payload())
                return
            if parsed.path == "/events":
                raw_limit = parse_qs(parsed.query).get("limit", ["50"])[0]
                try:
                    limit = min(max(int(raw_limit), 1), 100)
                except ValueError:
                    self._json(400, {"ok": False, "error": "invalid_limit"})
                    return
                self._json(200, {"events": shared.event_payload(limit), "limit": limit})
                return
            self._json(404, {"ok": False, "error": "not_found"})

        def do_POST(self) -> None:
            self._json(405, {"ok": False, "error": "method_not_allowed"})

        do_PUT = do_POST
        do_PATCH = do_POST
        do_DELETE = do_POST

    return Handler


def create_server(
    host: str, port: int, shared: SharedState
) -> ThreadingHTTPServer:
    if host not in {"127.0.0.1", "::1", "localhost"}:
        raise ValueError("Centinela HTTP server must remain loopback")
    return ThreadingHTTPServer((host, port), make_handler(shared))
