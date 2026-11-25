"""One IP, one port, two HTTPS sites. SNI decides which certificate is sent.

    python 06-sni/sni_server.py
"""
import ssl
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "shared"))
from lab import cert, serve
from tiny_http import BadRequest, read_request, route, send_response


def make_context(name):
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(cert(f"{name}.crt"), cert(f"{name}.key"))
    return context


SITES = {name: make_context(name) for name in ("alpha.test", "beta.test")}
DEFAULT = make_context("localhost")      # used when SNI is missing or unknown


def choose_certificate(tls, server_name, _default_context):
    """Called in the middle of the handshake, BEFORE any HTTP has been sent."""
    tls.requested_name = server_name
    chosen = SITES.get(server_name)
    if chosen:
        tls.context = chosen
    print(f"  SNI = {server_name!r} -> sending the certificate for "
          f"{server_name if chosen else 'localhost (default)'}", flush=True)


DEFAULT.sni_callback = choose_certificate


def handle(conn, addr):
    print(f"\n[{addr[1]}] connected", flush=True)
    with DEFAULT.wrap_socket(conn, server_side=True) as tls:
        try:
            request = read_request(tls)
        except BadRequest as e:
            send_response(tls, 400, f"{e}\n")
            return
        if request is None:
            return
        # SNI (from TLS) and Host (from HTTP) are two separate values. They normally
        # match, but nothing forces the client to make them match.
        sni = tls.requested_name
        host = request[2].get("host", "").split(":")[0].lower()
        if sni in SITES and host != sni:
            send_response(tls, 421, f"SNI was {sni} but Host was {host}\n")
            return
        status, text, extra = route(*request)
        send_response(tls, status, text, extra, head_only=(request[0] == "HEAD"))


serve(9006, handle)
