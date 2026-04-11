import socket
import time
import traceback
from datetime import datetime

TCP_IP = "192.168.12.101"
TCP_PORT = 50000  # confirm this port from Orbits config
LOG_FILE = "raw_packets.log"
RECONNECT_DELAY_SECONDS = 2


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
