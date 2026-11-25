"""Mutual TLS: the server also demands a certificate from the client.

    python 07-mtls/mtls_server.py
"""
import ssl
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "shared"))
from lab import cert, serve

context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(cert("localhost.crt"), cert("localhost.key"))

# These two lines are the whole difference between TLS and mutual TLS.
context.load_verify_locations(cert("ca.crt"))      # whose client certificates do we accept?
context.verify_mode = ssl.CERT_REQUIRED            # no certificate, no entry


def handle(conn, addr):
    with context.wrap_socket(conn, server_side=True) as tls:
        subject = dict(pair for rdn in tls.getpeercert()["subject"] for pair in rdn)
        print(f"[{addr[1]}] client certificate: {subject}", flush=True)
        tls.sendall(f"Welcome, {subject['commonName']}!".encode())


serve(9007, handle)
