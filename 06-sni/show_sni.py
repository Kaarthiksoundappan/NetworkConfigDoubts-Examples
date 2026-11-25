"""Read the SNI out of a TLS ClientHello WITHOUT any key or certificate.

This proves that SNI travels unencrypted, before any secret has been agreed.

    Terminal 1:  python 06-sni/show_sni.py
    Terminal 2:  curl --connect-to ::127.0.0.1:9016 https://any-name-you-like.test/

curl will report an error: we hang up after reading its first message. That is expected.
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "shared"))
from lab import serve


def read_exactly(conn, count):
    data = b""
    while len(data) < count:
        chunk = conn.recv(count - len(data))
        if not chunk:
            raise ConnectionError("client left too early")
        data += chunk
    return data


def read_client_hello(conn):
    """The ClientHello is the first TLS message. It can span more than one record."""
    hello = b""
    while len(hello) < 4 or len(hello) < 4 + int.from_bytes(hello[1:4], "big"):
        # TLS record header: 1 byte type, 2 bytes version, 2 bytes length
        kind, _version, length = struct.unpack("!BHH", read_exactly(conn, 5))
        if kind != 22:                                  # 22 = handshake
            raise ValueError(f"not a TLS handshake (first byte is {kind}). Plain HTTP?")
        hello += read_exactly(conn, length)
    if hello[0] != 1:                                   # 1 = ClientHello
        raise ValueError("not a ClientHello")
    return hello[4:]


def find_extensions(hello):
    """Return {extension number: raw bytes}."""
    pos = 2 + 32                                             # version, random
    pos += 1 + hello[pos]                                    # session id
    pos += 2 + struct.unpack_from("!H", hello, pos)[0]       # cipher suites
    pos += 1 + hello[pos]                                    # compression methods
    if pos >= len(hello):
        return {}
    end = pos + 2 + struct.unpack_from("!H", hello, pos)[0]
    pos += 2
    found = {}
    while pos < end:
        number, length = struct.unpack_from("!HH", hello, pos)
        found[number] = hello[pos + 4:pos + 4 + length]
        pos += 4 + length
    return found


def handle(conn, addr):
    conn.settimeout(5)
    try:
        extensions = find_extensions(read_client_hello(conn))
    except (ValueError, IndexError, struct.error) as e:
        print(f"[{addr[1]}] {e}", flush=True)
        return
    print(f"\n[{addr[1]}] ClientHello received")
    if 0 in extensions:                                      # 0 = server_name (SNI)
        # list length (2), name type (1), name length (2), then the name itself
        raw = extensions[0]
        name_length = struct.unpack_from("!H", raw, 3)[0]
        print("  SNI :", raw[5:5 + name_length].decode("ascii", "replace"))
    else:
        print("  SNI : (none sent)")
    if 16 in extensions:                                     # 16 = ALPN
        raw, pos, protocols = extensions[16], 2, []
        while pos < len(raw):
            protocols.append(raw[pos + 1:pos + 1 + raw[pos]].decode("ascii", "replace"))
            pos += 1 + raw[pos]
        print("  ALPN:", protocols)
    sys.stdout.flush()


if __name__ == "__main__":
    serve(9016, handle)
