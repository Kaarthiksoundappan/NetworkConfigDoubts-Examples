"""Find out WHICH LAYER is broken: DNS, TCP, TLS or HTTP.

    python tools/netcheck.py https://example.com
    python tools/netcheck.py http://127.0.0.1:9003
    python tools/netcheck.py https://expired.badssl.com
    python tools/netcheck.py https://localhost:9005 --ca certs/ca.crt
"""
import argparse
import http.client
import socket
import ssl
import sys
import time
from urllib.parse import urlsplit


def ok(layer, started, text):
    print(f"[ OK ] {layer:<5} {(time.perf_counter() - started) * 1000:6.0f} ms  {text}")


def fail(layer, text, hint):
    print(f"[FAIL] {layer:<5}            {text}\n       Hint: {hint}")
    sys.exit(1)


def tls_hint(error):
    text = str(error).lower()
    if isinstance(error, ssl.SSLCertVerificationError):
        if error.verify_code == 10:
            return "The certificate has expired. Renew it (and check this computer's clock)."
        if error.verify_code in (62, 64):
            return "This name is not in the certificate's SAN list. Wrong certificate or wrong SNI?"
        if error.verify_code in (18, 19, 20, 21):
            return "Issuer not trusted: private or self-signed CA, or the server omits an intermediate."
        return "The certificate was not accepted."
    if "wrong_version_number" in text or "wrong version number" in text or "record layer" in text:
        return "The other side does not speak TLS here. Is this a plain HTTP port?"
    if "unrecognized_name" in text or "unrecognized name" in text:
        return "The server does not know this SNI name."
    if "handshake" in text or "protocol" in text:
        return "No TLS version or cipher in common, or the server rejected us."
    return "The connection was dropped in the handshake. Firewall, proxy, or SNI filtering?"


def main():
    parser = argparse.ArgumentParser(description="Check each network layer in order.")
    parser.add_argument("url")
    parser.add_argument("--ca", help="also trust this CA file")
    args = parser.parse_args()
    url = urlsplit(args.url if "://" in args.url else "https://" + args.url)
    if url.scheme not in ("http", "https") or not url.hostname:
        parser.error("use a URL such as https://example.com")
    host = url.hostname
    try:
        port = url.port or (443 if url.scheme == "https" else 80)
    except ValueError as e:
        parser.error(str(e))

    # 1. DNS: name -> IP addresses
    t = time.perf_counter()
    try:
        found = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    except (socket.gaierror, UnicodeError) as e:
        fail("DNS", f"{host}: {e}", "Typo in the name, missing DNS record, or DNS server problem.")
    ok("DNS", t, f"{host} -> {', '.join(dict.fromkeys(info[4][0] for info in found))}")

    # 2. TCP: can we reach that IP and port?
    t = time.perf_counter()
    try:
        sock = socket.create_connection((host, port), timeout=5)
    except ConnectionRefusedError:
        fail("TCP", f"port {port} refused", "Machine reachable, but nothing listens on this port.")
    except TimeoutError:
        fail("TCP", f"port {port} timed out", "Firewall dropping packets, or wrong IP / no route.")
    except OSError as e:
        fail("TCP", str(e), "Network unreachable?")
    ok("TCP", t, f"connected to {sock.getpeername()[0]} port {port}")

    # 3. TLS: encryption and identity
    if url.scheme == "https":
        t = time.perf_counter()
        context = ssl.create_default_context()
        if args.ca:
            try:
                context.load_verify_locations(args.ca)
            except OSError as e:
                parser.error(f"cannot load --ca {args.ca}: {e}")
        try:
            sock = context.wrap_socket(sock, server_hostname=host)
        except OSError as e:
            fail("TLS", getattr(e, "verify_message", None) or str(e), tls_hint(e))
        info = sock.getpeercert()
        days = int((ssl.cert_time_to_seconds(info["notAfter"]) - time.time()) / 86400)
        issuer = dict(pair for rdn in info["issuer"] for pair in rdn)
        ok("TLS", t, f"{sock.version()}, {sock.cipher()[0]}, certificate valid for {days} more days")
        # An antivirus or company name here means your TLS is being intercepted.
        print(f"       Issued by: {issuer.get('organizationName', '')} / {issuer.get('commonName', '')}")

    # 4. HTTP: does the application answer? (http.client, on the socket we already opened)
    t = time.perf_counter()
    http_conn = http.client.HTTPConnection(host, port)
    http_conn.sock = sock
    path = (url.path or "/") + (f"?{url.query}" if url.query else "")
    host_header = url.netloc.rpartition("@")[2]
    try:
        http_conn.request("GET", path, headers={"Host": host_header, "User-Agent": "netcheck"})
        response = http_conn.getresponse()
    except (OSError, http.client.HTTPException) as e:
        fail("HTTP", f"{type(e).__name__}: {e}", "Connected, but no valid HTTP answer. Is this an HTTP(S) port?")
    ok("HTTP", t, f"{response.status} {response.reason}")
    location = response.getheader("Location")
    if location:
        print(f"       Redirects to {location}")
    if response.status in (502, 503, 504):
        print("       Hint: you reached a proxy, but the server BEHIND it has a problem.")
    http_conn.close()


if __name__ == "__main__":
    main()
