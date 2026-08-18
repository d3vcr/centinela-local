"""Configuration for the read-only Centinela process."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

PROTECTED_SERVICES = (
    "mosquitto.service",
    "ecu-remote-relay.service",
    "nexo-ingest.service",
    "nexo-normalizer.timer",
    "nexo-api.service",
    "nexo-cockpit.service",
    "nexo-orbital-guardian-temp.service",
    "tailscaled.service",
)

LEGACY_SERVICES = (
    "motoguarana-funnel.timer",
    "motoguarana-funnel.service",
    "motoguarana-portal-publico.service",
    "motoguarana-startup.service",
)


@dataclass(frozen=True)
class CentinelaConfig:
    api_base: str = "http://127.0.0.1:8080"
    bind_host: str = "127.0.0.1"
    bind_port: int = 8090
    poll_interval: float = 3.0
    request_timeout: float = 2.0
    state_dir: Path = Path("/var/lib/nexo/centinela")
    event_limit: int = 500
    odometer_reference_km: float = 10148.2
    tailscale_target: str = "http://127.0.0.1:8181"
    database_path: Path = Path("/var/lib/nexo/db/nexo.sqlite3")
    frontend_base: str = "http://127.0.0.1:8181"
    current_frontend_path: Path = Path("/opt/nexo/current-frontend")

    @classmethod
    def from_env(cls) -> CentinelaConfig:
        return cls(
            api_base=os.getenv("NEXO_CENTINELA_API_BASE", cls.api_base),
            bind_host=os.getenv("NEXO_CENTINELA_HOST", cls.bind_host),
            bind_port=int(os.getenv("NEXO_CENTINELA_PORT", str(cls.bind_port))),
            poll_interval=float(
                os.getenv("NEXO_CENTINELA_POLL_INTERVAL", str(cls.poll_interval))
            ),
            request_timeout=float(
                os.getenv("NEXO_CENTINELA_REQUEST_TIMEOUT", str(cls.request_timeout))
            ),
            state_dir=Path(os.getenv("NEXO_CENTINELA_STATE_DIR", str(cls.state_dir))),
            event_limit=int(os.getenv("NEXO_CENTINELA_EVENT_LIMIT", str(cls.event_limit))),
            odometer_reference_km=float(
                os.getenv(
                    "NEXO_CENTINELA_ODOMETER_REFERENCE_KM",
                    str(cls.odometer_reference_km),
                )
            ),
            tailscale_target=os.getenv(
                "NEXO_CENTINELA_TAILSCALE_TARGET", cls.tailscale_target
            ),
            database_path=Path(
                os.getenv("NEXO_CENTINELA_DATABASE_PATH", str(cls.database_path))
            ),
            frontend_base=os.getenv(
                "NEXO_CENTINELA_FRONTEND_BASE", cls.frontend_base
            ),
            current_frontend_path=Path(
                os.getenv(
                    "NEXO_CENTINELA_CURRENT_FRONTEND",
                    str(cls.current_frontend_path),
                )
            ),
        )

    def validate(self) -> None:
        if self.bind_host not in {"127.0.0.1", "::1", "localhost"}:
            raise ValueError("Centinela must bind to loopback")
        if not self.api_base.startswith(("http://127.0.0.1:", "http://localhost:")):
            raise ValueError("Centinela API base must be loopback HTTP")
        if not 2.0 <= self.poll_interval <= 30.0:
            raise ValueError("Poll interval must be between 2 and 30 seconds")
        if not 1 <= self.event_limit <= 5000:
            raise ValueError("Event limit is outside the safe range")
        if not self.frontend_base.startswith(
            ("http://127.0.0.1:", "http://localhost:")
        ):
            raise ValueError("Centinela frontend base must be loopback HTTP")
