import socket
from datetime import datetime
import traceback

TCP_IP = "192.168.12.101"
TCP_PORT = 50000  # confirm this port from Orbits config

LOG_FILE = "raw_packets.log"

def start_listener(shared_state):
    print("STARTING LISTENER")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.sendall(b"\n")
        sock.settimeout(5)
        
        sock.connect((TCP_IP, TCP_PORT))

        with open(LOG_FILE, "a", encoding="utf-8") as log:
            while True:
                ##data = sock.recv(65535)
                data = sock.recv(1024)
                if not data:
                    print("Connection closed")
                    break

                ts = datetime.now().isoformat(timespec="seconds")

                try:
                    decoded = data.decode("utf-8")
                    preview = decoded[:200]
                except UnicodeDecodeError:
                    preview = data[:128].hex()

                shared_state["last_packet"] = {
                    "timestamp": ts,
                    "from": f"{TCP_IP}:{TCP_PORT}",
                    "preview": preview
                }

                line = f"\n[{ts}] from={TCP_IP}:{TCP_PORT}\n{preview}\n"
                log.write(line)
                log.flush()
    except Exception as e:
        print("LISTENER CRASHED:",e)
        traceback.print_exc()