"""Small helpers shared by the lessons. You do not need to study this file."""
import socket
import sys
import threading
from pathlib import Path

INTERCEPT_HINT = ("If something fails unexpectedly, antivirus or a company proxy may be replacing\n"
                  "certificates. Check with:  python tools/check_setup.py")
CERTS = Path(__file__).resolve().parent.parent / "certs"


def cert(name):
    """Path of a file in certs/, with a friendly error if it is missing."""
    path = CERTS / name
    if not path.exists():
        sys.exit(f"Missing {path}\nCreate the lab certificates first:  python tools/make_certs.py")
    return str(path)


def serve(port, handle):
    """Listen on 127.0.0.1:port and run handle(conn, addr) in a thread per connection.

    127.0.0.1 (not 0.0.0.0) means only this computer can connect.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        if sys.platform == "win32":
            # Without this, Windows may let another program share our port.
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        else:
            # Lets you restart the server without waiting for TIME_WAIT to finish.
            listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            listener.bind(("127.0.0.1", port))
        except OSError as e:
            sys.exit(f"Cannot use port {port} ({e}). Is another copy already running?")
        listener.listen()
        # On Windows, Ctrl+C cannot interrupt a blocked accept(), so wake up regularly.
        listener.settimeout(0.5)
        print(f"Listening on 127.0.0.1:{port}  (Ctrl+C to stop)", flush=True)
        try:
            while True:
                try:
                    conn, addr = listener.accept()
                except TimeoutError:
                    continue
                threading.Thread(target=_run, args=(handle, conn, addr), daemon=True).start()
        except KeyboardInterrupt:
            print("\nServer stopped.")


def _run(handle, conn, addr):
    with conn:
        try:
            handle(conn, addr)
        except OSError as e:  # includes TLS errors and dropped connections
            print(f"[{addr[1]}] connection error: {e}", flush=True)


def show(prefix, data):
    """Print bytes line by line, making the invisible \\r\\n visible."""
    for line in data.splitlines(keepends=True):
        text = line.decode("ascii", "backslashreplace").replace("\r", "\\r").replace("\n", "\\n")
        print(f"  {prefix} {text}", flush=True)
