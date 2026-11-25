"""Connect to the same IP and port with different SNI values. Start sni_server.py first.

    python 06-sni/sni_client.py
"""
import socket
import ssl
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "shared"))
from lab import INTERCEPT_HINT, cert

ADDRESS = ("127.0.0.1", 9006)


def names_in_certificate(tls):
    return [value for _kind, value in tls.getpeercert()["subjectAltName"]]


def attempt(title, sni, host, check_hostname=True):
    print(f"\n{title}\n  SNI={sni}  Host={host}")
    context = ssl.create_default_context(cafile=cert("ca.crt"))
    # Only case 3 turns this off, so that we can look at the certificate we were given.
    context.check_hostname = check_hostname
    try:
        with socket.create_connection(ADDRESS, timeout=5) as tcp:
            with context.wrap_socket(tcp, server_hostname=sni) as tls:
                print("  certificate received for:", names_in_certificate(tls))
                tls.sendall(f"GET / HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n".encode())
                response = b""
                while chunk := tls.recv(4096):
                    response += chunk
                head, body = response.decode().split("\r\n\r\n", 1)
                print("  HTTP answer:", head.splitlines()[0], "|", body.strip())
    except ssl.SSLCertVerificationError as e:
        print("  TLS FAILED:", e.verify_message)
    except ConnectionRefusedError:
        sys.exit("Start 06-sni/sni_server.py first.")


print("Case 4 is meant to fail.", INTERCEPT_HINT)
attempt("1) Ask for alpha", "alpha.test", "alpha.test")
attempt("2) Same IP and port, ask for beta", "beta.test", "beta.test")
attempt("3) Send no SNI: we get the default certificate", None, "alpha.test", check_hostname=False)
attempt("4) SNI for a site this server does not have", "gamma.test", "gamma.test")
attempt("5) SNI and Host disagree", "alpha.test", "beta.test")
