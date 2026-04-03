import socket
from datetime import datetime

UDP_IP = "0.0.0.0"
UDP_PORT = 50000   # replace with actual Orbits feed port Saturday
LOG_FILE = "raw_packets.log"

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    print(f"Listening on UDP {UDP_IP}:{UDP_PORT}")

    with open(LOG_FILE, "a", encoding="utf-8") as log:
        while True:
            data, addr = sock.recvfrom(65535)
            ts = datetime.now().isoformat(timespec="seconds")

            try:
                decoded = data.decode("utf-8")
                preview = decoded[:500]
            except UnicodeDecodeError:
                preview = data[:64].hex()

            line = f"\n[{ts}] from={addr}\n{preview}\n"
            print(line)
            log.write(line)
            log.flush()

if __name__ == "__main__":
    main()