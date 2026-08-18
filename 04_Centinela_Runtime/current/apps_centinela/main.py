"""NEXO Centinela process entry point."""

from __future__ import annotations

import logging
import signal
from threading import Event, Thread
from types import FrameType

from .collectors import SnapshotCollector
from .config import CentinelaConfig
from .engine import CentinelaEngine
from .persistence import CentinelaPersistence
from .server import SharedState, create_server

LOGGER = logging.getLogger("nexo-centinela")


def run() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    config = CentinelaConfig.from_env()
    config.validate()
    persistence = CentinelaPersistence(config.state_dir, config.event_limit)
    persistence.prepare()
    engine = CentinelaEngine(config)
    saved = persistence.load_state()
    engine.restore(saved)

    shared = SharedState(config.poll_interval)
    shared.update(
        engine.latest_state,
        persistence.load_events(config.event_limit),
        engine.last_successful_poll,
    )
    server = create_server(config.bind_host, config.bind_port, shared)
    server_thread = Thread(target=server.serve_forever, name="centinela-http", daemon=True)
    server_thread.start()
    LOGGER.info("HTTP readonly listening on %s:%s", config.bind_host, config.bind_port)

    stop = Event()

    def request_stop(_signum: int, _frame: FrameType | None) -> None:
        stop.set()

    signal.signal(signal.SIGTERM, request_stop)
    signal.signal(signal.SIGINT, request_stop)
    collector = SnapshotCollector(config)
    try:
        while not stop.is_set():
            snapshot = collector.collect()
            state, events = engine.evaluate(snapshot)
            persistence.save_state(engine.persistence_payload())
            event_payloads = [event.to_dict() for event in events]
            persistence.append_events(event_payloads)
            recent_events = persistence.load_events(config.event_limit)
            shared.update(state, recent_events, engine.last_successful_poll)
            for event in events:
                LOGGER.warning(
                    "transition=%s code=%s severity=%s occurrences=%s evidence=%s",
                    event.transition,
                    event.code,
                    event.severity,
                    event.occurrences,
                    event.evidence,
                )
            stop.wait(config.poll_interval)
    finally:
        server.shutdown()
        server.server_close()
        server_thread.join(timeout=5)
        LOGGER.info("Centinela stopped")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
