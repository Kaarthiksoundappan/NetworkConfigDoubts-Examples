"""The classic ways a TCP connection fails, and what each one tells you.

    python 01-tcp/connect_errors.py
"""
import socket
import time


def free_port():
    """Find a port that nothing is listening on."""
    with socket.create_server(("127.0.0.1", 0)) as s:
        return s.getsockname()[1]


def attempt(title, host, port, meaning):
    print(f"\n{title}  ->  {host}:{port}")
    start = time.perf_counter()
    try:
        socket.create_connection((host, port), timeout=5).close()
        result = "CONNECTED"
    except socket.gaierror as e:
        result = f"DNS FAILURE ({e})"
    except ConnectionRefusedError:
        result = "REFUSED"
    except TimeoutError:
        result = "TIMED OUT"
    except OSError as e:
        result = f"OTHER ERROR ({e})"
    print(f"  result : {result} after {time.perf_counter() - start:.1f}s")
    print(f"  meaning: {meaning}")


attempt("Nobody listening", "127.0.0.1", free_port(),
        "REFUSED: the machine answered 'no' (RST). Wrong port, or the service is down.")
attempt("Packets vanish", "192.0.2.1", 80,   # an address reserved for documentation
        "TIMED OUT: no answer at all. Firewall dropping packets, or wrong IP / no route.")
attempt("Unknown name", "no-such-host.invalid", 80,
        "DNS FAILURE: the name has no IP, so TCP was never even tried.")

with socket.create_server(("127.0.0.1", 0)) as listener:
    attempt("Something is listening", *listener.getsockname(),
            "CONNECTED: the network path and the port are fine.")
