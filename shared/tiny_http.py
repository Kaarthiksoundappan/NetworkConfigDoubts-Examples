"""A tiny hand-written HTTP/1.1 server.

It only needs an object with recv() and sendall(). It does not know or care whether
that object is a plain TCP socket (lesson 03) or a TLS socket (lesson 05).
For learning only: real servers handle far more cases.
"""
from lab import show

REASONS = {200: "OK", 302: "Found", 400: "Bad Request", 404: "Not Found",
           405: "Method Not Allowed", 421: "Misdirected Request"}
MAX_SIZE = 65536


class BadRequest(Exception):
    pass


def read_request(conn):
    """Read one request. Returns (method, path, headers, body), or None if the client left."""
    data = b""
    # Headers end at the first blank line. TCP may deliver them in several pieces.
    while b"\r\n\r\n" not in data:
        chunk = conn.recv(4096)
        if not chunk:
            return None
        data += chunk
        if not data[:1].isalpha():
            # Every HTTP request starts with a method such as GET. A TLS ClientHello
            # starts with byte 0x16, so this catches "https:// to an http:// port".
            raise BadRequest(f"this is not HTTP (first bytes: {data[:8].hex(' ')})")
        if len(data) > MAX_SIZE:
            raise BadRequest("headers too large")
    head, body = data.split(b"\r\n\r\n", 1)
    try:
        request_line, *lines = head.decode("iso-8859-1").split("\r\n")
        method, path, _version = request_line.split(" ")
        headers = {}
        for line in lines:
            name, value = line.split(":", 1)
            headers[name.strip().lower()] = value.strip()   # header names ignore case
        length = int(headers.get("content-length", 0))
    except ValueError:
        raise BadRequest("this does not look like HTTP") from None
    if not 0 <= length <= MAX_SIZE:
        raise BadRequest("unsupported body size")
    # The body has no end marker: Content-Length says how many bytes to read.
    while len(body) < length:
        chunk = conn.recv(4096)
        if not chunk:
            return None
        body += chunk
    show("<", head + b"\r\n\r\n" + body)
    return method, path, headers, body[:length]


def send_response(conn, status, body, extra_headers=(), head_only=False):
    body = body.encode()
    lines = [f"HTTP/1.1 {status} {REASONS[status]}",
             "Content-Type: text/plain; charset=utf-8",
             f"Content-Length: {len(body)}",
             "Connection: close",          # one request per connection keeps this simple
             *extra_headers]
    head = ("\r\n".join(lines) + "\r\n\r\n").encode()
    conn.sendall(head if head_only else head + body)
    print(f"  > {lines[0]}", flush=True)


def route(method, path, headers, body):
    """Decide the answer. Returns (status, body, extra_headers)."""
    host = headers.get("host")
    if host is None:
        return 400, "HTTP/1.1 requires a Host header\n", ()
    if path == "/":
        # Virtual hosting: one server, one port, different sites chosen by Host.
        site = host.split(":")[0]
        return 200, f"Hello! You asked for the site '{site}'.\n", ()
    if path == "/old":
        return 302, "This page moved to /new\n", ("Location: /new",)
    if path == "/new":
        return 200, "You found the new page.\n", ()
    if path == "/cookie":
        if "visited=yes" in headers.get("cookie", ""):
            return 200, "Welcome back, your cookie told me you were here before.\n", ()
        return 200, "First visit. I am giving you a cookie.\n", ("Set-Cookie: visited=yes",)
    if path == "/echo":
        if method != "POST":
            return 405, "Use POST here\n", ("Allow: POST",)
        return 200, f"You sent {len(body)} bytes: {body.decode('utf-8', 'replace')}\n", ()
    return 404, f"Nothing at {path}\n", ()


def handle_http(conn, addr):
    print(f"[{addr[1]}] connected", flush=True)
    try:
        request = read_request(conn)
    except BadRequest as e:
        print(f"[{addr[1]}] bad request: {e}", flush=True)
        send_response(conn, 400, f"{e}\n")
        return
    if request is None:
        print(f"[{addr[1]}] client left without sending a full request", flush=True)
        return
    method, path, headers, body = request
    status, text, extra = route(method, path, headers, body)
    send_response(conn, status, text, extra, head_only=(method == "HEAD"))
