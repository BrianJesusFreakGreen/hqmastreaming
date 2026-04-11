import json
import socket
import time
import traceback
from datetime import datetime

TCP_IP = "192.168.12.101"
TCP_PORT = 50000  # confirm this port from Orbits config
LOG_FILE = "raw_packets.log"
RECONNECT_DELAY_SECONDS = 2



def _safe_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _split_rows(data):
    leaders = data.get("leaders")
    rest = data.get("rest")

    if isinstance(leaders, list) and isinstance(rest, list):
        return leaders, rest

    rows = data.get("rows") or data.get("entries") or []
    if not isinstance(rows, list):
        return [], []

    leaders = rows[:5]
    rest = rows[5:10]
    return leaders, rest


def parse_packet(decoded):
    """Best-effort parser for listener packets.

    Supports JSON payloads and simple key/value lines:
      event_name=HQMA Feature Race
      session_name=Senior Honda
      laps_remaining=12
    """
    payload = decoded.strip()
    if not payload:
        return None

    parsed = None

    # Preferred format: JSON payload
    try:
        candidate = json.loads(payload)
        if isinstance(candidate, dict):
            parsed = candidate
    except json.JSONDecodeError:
        parsed = None

    # Fallback format: line-delimited key/value
    if parsed is None:
        parsed = {}
        for line in payload.splitlines():
            line = line.strip()
            if not line:
                continue
            for sep in ("=", ":"):
                if sep in line:
                    key, value = line.split(sep, 1)
                    parsed[key.strip()] = value.strip()
                    break

        if not parsed:
            return None

    leaders, rest = _split_rows(parsed)

    out = {
        "event_name": parsed.get("event_name") or parsed.get("event") or "",
        "session_name": parsed.get("session_name") or parsed.get("session") or "",
        "track_status": parsed.get("track_status") or parsed.get("status") or "",
        "laps_remaining": _safe_int(parsed.get("laps_remaining") or parsed.get("laps_to_go")),
        "leaders": leaders,
        "rest": rest,
    }

    return out


def start_listener(shared_state):
    print("STARTING LISTENER")
    while True:
        sock = None
        try:
            shared_state["listener_status"] = "connecting"
            shared_state["listener_error"] = None

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((TCP_IP, TCP_PORT))

            # Switch to blocking mode for sustained stream reads.
            sock.settimeout(None)
            sock.sendall(b"\n")
            shared_state["listener_status"] = "connected"

            with open(LOG_FILE, "a", encoding="utf-8") as log:
                while True:
                    data = sock.recv(4096)
                    if not data:
                        shared_state["listener_status"] = "disconnected"
                        break

                    ts = datetime.now().isoformat(timespec="seconds")
                    decoded = data.decode("utf-8", errors="replace")

                    shared_state["last_packet"] = {
                        "timestamp": ts,
                        "from": f"{TCP_IP}:{TCP_PORT}",
                        "byte_length": len(data),
                        "raw_utf8": decoded,
                        "raw_hex": data.hex(),
                    }

                    line = (
                        f"\n[{ts}] from={TCP_IP}:{TCP_PORT} bytes={len(data)}"
                        f"\nutf8:\n{decoded}\nhex:\n{data.hex()}\n"
                    )
                    log.write(line)
                    log.flush()
        except Exception as e:
            shared_state["listener_status"] = "error"
            shared_state["listener_error"] = str(e)
            print("LISTENER CRASHED:", e)
            traceback.print_exc()
        finally:
            if sock:
                try:
                    sock.close()
                except Exception:
                    pass

            time.sleep(RECONNECT_DELAY_SECONDS)
