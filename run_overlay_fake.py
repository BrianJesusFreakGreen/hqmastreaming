"""Run the HQMA overlay by replaying a captured log on a loop."""

from __future__ import annotations

import argparse
import threading
import time
from pathlib import Path

from app import CURRENT_STATE, app
from listener import _handle_line, _new_session_state, _parse_csv_line

FRAME_DURATION_SECONDS = 1
SAMPLE_LOG = Path(__file__).with_name("sample_orbits.log")


def _disable_live_listener() -> None:
    """Remove app.before_request hook that auto-starts the live listener thread."""
    funcs = app.before_request_funcs.get(None, [])
    app.before_request_funcs[None] = [
        fn for fn in funcs if getattr(fn, "__name__", "") != "ensure_listener_running"
    ]


def _load_log_lines(path: Path) -> list[str]:
    return [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _publisher_loop() -> None:
    log_lines = _load_log_lines(SAMPLE_LOG)
    CURRENT_STATE.clear()
    CURRENT_STATE.update(
        {
            "listener_status": "replaying",
            "listener_error": None,
            "replay_source": str(SAMPLE_LOG.name),
        }
    )

    while True:
        session = _new_session_state()

        for raw_line in log_lines:
            line_type, fields = _parse_csv_line(raw_line)
            if not line_type:
                continue

            _handle_line(session, line_type, fields, CURRENT_STATE)
            CURRENT_STATE["listener_status"] = "replaying"
            CURRENT_STATE["listener_error"] = None
            CURRENT_STATE["last_packet"] = {
                "timestamp": time.time(),
                "from": SAMPLE_LOG.name,
                "raw_utf8": raw_line,
            }

            if line_type == "$F":
                time.sleep(FRAME_DURATION_SECONDS)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run HQMA overlay with replayed log data")
    parser.add_argument("--host", default="127.0.0.1", help="Flask bind host (default: 127.0.0.1)")
    parser.add_argument("--port", default=5000, type=int, help="Flask bind port (default: 5000)")
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable Flask debug mode (off by default to avoid reloader confusion)",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    _disable_live_listener()

    thread = threading.Thread(target=_publisher_loop, daemon=True)
    thread.start()

    print(f"[fake-overlay] Replaying {SAMPLE_LOG.name} on a loop.")
    print(f"[fake-overlay] Overlay URL: http://{args.host}:{args.port}/overlay")
    print(f"[fake-overlay] API URL:     http://{args.host}:{args.port}/api/state")

    app.run(host=args.host, port=args.port, debug=args.debug, use_reloader=False)


if __name__ == "__main__":
    main()
