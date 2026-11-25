"""Connect to the mTLS server with and without a client certificate.

    python 07-mtls/mtls_client.py
"""
import socket
import ssl
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "shared"))
from lab import INTERCEPT_HINT, cert


def attempt(title, send_certificate):
    print(f"\n{title}")
    context = ssl.create_default_context(cafile=cert("ca.crt"))
    if send_certificate:
        context.load_cert_chain(cert("client.crt"), cert("client.key"))
    try:
        with socket.create_connection(("127.0.0.1", 9007), timeout=5) as tcp:
            with context.wrap_socket(tcp, server_hostname="localhost") as tls:
                # In TLS 1.3 the client finishes first, so a refusal only shows up on read.
                print("  handshake looks finished from the client side")
                print("  server said:", tls.recv(1024).decode())
    except ConnectionRefusedError:
        sys.exit("Start 07-mtls/mtls_server.py first.")
    except OSError as e:
        print("  REJECTED:", e)


print("Case 1 is meant to fail.", INTERCEPT_HINT)
attempt("1) Without a client certificate", send_certificate=False)
attempt("2) With a client certificate", send_certificate=True)
