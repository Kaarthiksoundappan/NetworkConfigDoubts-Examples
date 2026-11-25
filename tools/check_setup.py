"""Is this computer ready for the lessons? Run this first.

    python tools/check_setup.py
"""
import socket
import ssl
import sys
import threading
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / ".." / "shared"))
from lab import cert

PORTS = [9001, 9003, 9004, 9005, 9006, 9007, 9016, 9100]


def certificate_received_over_loopback():
    """Serve localhost.crt to ourselves and return the certificate that arrives."""
    server_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    server_context.load_cert_chain(cert("localhost.crt"), cert("localhost.key"))

    def serve_once(listener):
        conn, _ = listener.accept()
        with conn:
            try:
                with server_context.wrap_socket(conn, server_side=True) as tls:
                    tls.recv(1)
            except OSError:
                pass

    # Verification is off ONLY here, because we want to look at whatever arrives.
    client_context = ssl.create_default_context()
    client_context.check_hostname = False
    client_context.verify_mode = ssl.CERT_NONE
    with socket.create_server(("127.0.0.1", 0)) as listener:
        thread = threading.Thread(target=serve_once, args=(listener,), daemon=True)
        thread.start()
        with socket.create_connection(listener.getsockname(), timeout=5) as tcp:
            with client_context.wrap_socket(tcp, server_hostname="localhost") as tls:
                received = tls.getpeercert(binary_form=True)
        thread.join(timeout=5)
    return received


def main():
    print(f"Python  : {sys.version.split()[0]}, {ssl.OPENSSL_VERSION}")
    if sys.version_info < (3, 10):
        sys.exit("PROBLEM : Python 3.10 or newer is needed.")

    busy = []
    for port in PORTS:
        with socket.socket() as s:
            s.settimeout(0.3)
            if s.connect_ex(("127.0.0.1", port)) == 0:
                busy.append(port)
    print(f"Ports   : {'in use: ' + str(busy) if busy else 'all free'}")

    ours = ssl.PEM_cert_to_DER_cert(Path(cert("localhost.crt")).read_text())
    print("Certs   : found")
    try:
        received = certificate_received_over_loopback()
    except OSError as e:
        sys.exit(f"PROBLEM : a TLS connection to ourselves failed: {e}")

    if received == ours:
        print("TLS     : clean, the client received exactly the certificate we served")
        print("\nAll good. Start with 01-tcp.")
        return

    print("TLS     : INTERCEPTED! The client received a DIFFERENT certificate.")
    # Names inside a certificate are readable text, so a rough search finds who made it.
    for word in (b"Norton", b"Avast", b"AVG", b"Kaspersky", b"ESET", b"Bitdefender", b"Zscaler",
                 b"Fortinet", b"Sophos"):
        if word in received:
            print(f"          The replacement certificate mentions: {word.decode()}")
    print("\nSoftware on this computer opens TLS connections to inspect them.\n"
          "Lessons 01 to 03 work. For 04 to 07 use WSL: see 'Setup' in README.md.")
    sys.exit(1)


if __name__ == "__main__":
    main()
