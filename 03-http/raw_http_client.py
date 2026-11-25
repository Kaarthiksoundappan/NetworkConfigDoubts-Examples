"""HTTP is just text. Type it into a TCP socket yourself, without any HTTP library.

    python 03-http/raw_http_client.py                        -> http_server.py on port 9003
    python 03-http/raw_http_client.py 127.0.0.1 9003 /old
    python 03-http/raw_http_client.py example.com 80 /       -> a real website
"""
import socket
import sys

host = sys.argv[1] if len(sys.argv) > 1 else "127.0.0.1"
port = int(sys.argv[2]) if len(sys.argv) > 2 else 9003
path = sys.argv[3] if len(sys.argv) > 3 else "/"

request = (
    f"GET {path} HTTP/1.1\r\n"     # request line: method, path, version
    f"Host: {host}\r\n"            # which site do I want? (required in HTTP/1.1)
    f"User-Agent: my-first-client\r\n"
    f"Connection: close\r\n"       # please hang up when you are done
    f"\r\n"                        # a blank line: end of headers
)

print("----- request -----")
print(request, end="")
try:
    sock = socket.create_connection((host, port), timeout=5)
except OSError as e:
    sys.exit(f"Could not connect to {host}:{port}: {e}\n"
             "For the local lesson, start 03-http/http_server.py first.")
with sock:
    sock.sendall(request.encode("ascii"))
    response = b""
    while chunk := sock.recv(4096):     # keep reading until the server hangs up
        response += chunk

print("----- response -----")
print(response.decode("utf-8", "replace")[:1500].replace("\r\n", "\n"))
