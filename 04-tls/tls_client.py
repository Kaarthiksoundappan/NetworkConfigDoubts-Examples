"""A TLS client. Start tls_server.py first.

    python 04-tls/tls_client.py
    python 04-tls/tls_client.py 9100     (through tools/wiretap.py)
"""
import socket
import ssl
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "shared"))
from lab import INTERCEPT_HINT, cert

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 9004

# cafile = "I trust certificates signed by this CA". Your OS has a list of public CAs;
# our lab CA is not on it, so we must name it ourselves.
context = ssl.create_default_context(cafile=cert("ca.crt"))

try:
    tcp = socket.create_connection(("127.0.0.1", PORT), timeout=5)      # step 1: TCP
except OSError as e:
    sys.exit(f"Could not connect: {e}\nStart 04-tls/tls_server.py first.")

try:
    with tcp, context.wrap_socket(tcp, server_hostname="localhost") as tls:  # step 2: TLS
        info = tls.getpeercert()
        print("TLS version :", tls.version())
        print("Cipher      :", tls.cipher()[0])
        print("Valid names :", [value for _kind, value in info["subjectAltName"]])
        print("Issued by   :", dict(pair for rdn in info["issuer"] for pair in rdn))
        print("Expires     :", info["notAfter"])

        tls.sendall(b"my secret password")                                  # step 3: data
        print("Reply       :", tls.recv(1024))
except ssl.SSLCertVerificationError as e:
    sys.exit(f"TLS FAILED: {e.verify_message}\n{INTERCEPT_HINT}")
