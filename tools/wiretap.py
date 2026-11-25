"""Sit between a client and a server and print every byte that passes.

    python tools/wiretap.py LISTEN_PORT TARGET_PORT [TARGET_HOST]
    python tools/wiretap.py 9100 9003        (spy on the HTTP lesson)
    python tools/wiretap.py 9100 9005        (spy on the HTTPS lesson)

It plays the part of anyone on the network path: a Wi-Fi owner, an ISP, a proxy.
Only use it on your own traffic.
"""
import socket
import sys
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "shared"))
from lab import serve

MAX_ROWS = 14
lock = threading.Lock()     # stops the two directions printing over each other


def dump(title, data):
    with lock:
        print(f"\n{title}: {len(data)} bytes")
        for i in range(0, min(len(data), MAX_ROWS * 16), 16):
            row = data[i:i + 16]
            text = "".join(chr(b) if 32 <= b < 127 else "." for b in row)
            print(f"  {row.hex(' '):<47}  {text}")
        if len(data) > MAX_ROWS * 16:
            print("  ...")
        sys.stdout.flush()


def pump(source, destination, title):
    try:
        while data := source.recv(65536):
            dump(title, data)
            destination.sendall(data)
        destination.shutdown(socket.SHUT_WR)    # pass the "I am finished" signal along
    except OSError:
        # One side vanished (RST), so end the other side too.
        for sock in (source, destination):
            try:
                sock.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass


def handle(client, addr):
    with socket.create_connection((target_host, target_port), timeout=5) as server:
        server.settimeout(None)
        print(f"\n===== new connection from port {addr[1]} =====", flush=True)
        back = threading.Thread(target=pump, args=(server, client, "server -> client"), daemon=True)
        back.start()
        pump(client, server, "client -> server")
        back.join()


if len(sys.argv) < 3:
    sys.exit(__doc__)
target_port = int(sys.argv[2])
target_host = sys.argv[3] if len(sys.argv) > 3 else "127.0.0.1"
serve(int(sys.argv[1]), handle)
