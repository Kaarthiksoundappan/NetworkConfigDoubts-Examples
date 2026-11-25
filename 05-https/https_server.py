"""HTTPS = the HTTP server from lesson 03 + the TLS wrapper from lesson 04.

Compare with 03-http/http_server.py: handle_http is exactly the same function.

    python 05-https/https_server.py
"""
import ssl
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "shared"))
from lab import cert, serve
from tiny_http import handle_http

context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
context.load_cert_chain(cert("localhost.crt"), cert("localhost.key"))
context.set_alpn_protocols(["http/1.1"])    # ALPN: tell clients which HTTP version we speak


def handle(conn, addr):
    with context.wrap_socket(conn, server_side=True) as tls:
        handle_http(tls, addr)


serve(9005, handle)
