"""The echo server from lesson 01, now wrapped in TLS.

    python tools/make_certs.py      (once)
    python 04-tls/tls_server.py
"""
import ssl
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "shared"))
from lab import cert, serve

context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
# The certificate is public: it is sent to every client.
# The private key is secret: it proves the certificate is really ours.
context.load_cert_chain(cert("localhost.crt"), cert("localhost.key"))


def handle(conn, addr):
    # TCP is connected already. wrap_socket performs the TLS handshake on top of it.
    with context.wrap_socket(conn, server_side=True) as tls:
        print(f"[{addr[1]}] handshake done: {tls.version()} {tls.cipher()[0]}", flush=True)
        while data := tls.recv(1024):
            print(f"[{addr[1]}] decrypted: {data!r}", flush=True)
            tls.sendall(data.upper())


serve(9004, handle)
