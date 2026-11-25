"""The certificate errors you will meet in real life, produced on purpose.

    python 04-tls/cert_failures.py          (runs on its own, no server needed)
"""
import socket
import ssl
import sys
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "shared"))
from lab import INTERCEPT_HINT, cert


def serve_once(listener, cert_name):
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(cert(f"{cert_name}.crt"), cert(f"{cert_name}.key"))
    conn, _ = listener.accept()
    with conn:
        try:
            with context.wrap_socket(conn, server_side=True) as tls:
                tls.recv(1)
        except OSError:
            pass     # the client rejected our certificate, as planned


def attempt(title, server_cert, connect_as, trust_lab_ca, fix):
    print(f"\n{title}")
    print(f"  server certificate: {server_cert}.crt    client wants: {connect_as}")
    context = ssl.create_default_context(cafile=cert("ca.crt") if trust_lab_ca else None)
    with socket.create_server(("127.0.0.1", 0)) as listener:
        server = threading.Thread(target=serve_once, args=(listener, server_cert))
        server.start()
        try:
            with socket.create_connection(listener.getsockname(), timeout=5) as tcp:
                with context.wrap_socket(tcp, server_hostname=connect_as) as tls:
                    print(f"  OK     : {tls.version()}")
        except ssl.SSLCertVerificationError as e:
            print(f"  FAILED : {e.verify_message}")
        server.join()
    print(f"  lesson : {fix}")


print("Cases 2, 3 and 4 are meant to fail.", INTERCEPT_HINT)
attempt("1) Everything correct", "localhost", "localhost", True,
        "trusted CA + matching name + valid dates = success.")
attempt("2) Unknown CA", "localhost", "localhost", False,
        "the client does not trust the issuer. Trust the CA, or send the full chain.")
attempt("3) Wrong name", "alpha.test", "beta.test", True,
        "the name you connect to must appear in the certificate's SAN list.")
attempt("4) Expired", "expired", "localhost", True,
        "renew the certificate (and check the client's clock).")
