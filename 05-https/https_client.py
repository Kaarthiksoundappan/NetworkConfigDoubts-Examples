"""The raw HTTP client from lesson 03, sent through TLS.

    python 05-https/https_client.py                    -> https_server.py on port 9005
    python 05-https/https_client.py 127.0.0.1 9100     -> through tools/wiretap.py
    python 05-https/https_client.py example.com 443    -> a real website
"""
import socket
import ssl
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "shared"))
from lab import INTERCEPT_HINT, cert

host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
port = int(sys.argv[2]) if len(sys.argv) > 2 else 9005

context = ssl.create_default_context()          # trusts your system's public CAs
if host in ("127.0.0.1", "localhost"):
    context.load_verify_locations(cert("ca.crt"))   # and, for the lab, our own CA

request = (f"GET / HTTP/1.1\r\nHost: {host}\r\nUser-Agent: my-first-client\r\n"
           f"Cookie: secret=12345\r\nConnection: close\r\n\r\n")

response = b""
try:
    with socket.create_connection((host, port), timeout=5) as tcp:       # 1. TCP
        with context.wrap_socket(tcp, server_hostname=host) as tls:      # 2. TLS
            print(f"Encrypted with {tls.version()}, {tls.cipher()[0]}")
            tls.sendall(request.encode("ascii"))                         # 3. HTTP
            while chunk := tls.recv(4096):
                response += chunk
except ssl.SSLError as e:
    sys.exit(f"TLS failed: {e}\n{INTERCEPT_HINT}")
except OSError as e:
    sys.exit(f"Could not connect: {e}\nFor the local lesson, start 05-https/https_server.py first.")

print(response.decode("utf-8", "replace")[:1500].replace("\r\n", "\n"))
