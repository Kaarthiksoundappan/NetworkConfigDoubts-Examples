"""Build a DNS question by hand, send it over UDP, and read the answer.

    python 02-udp-and-dns/dns_query.py example.com
    python 02-udp-and-dns/dns_query.py www.github.com 8.8.8.8
    python 02-udp-and-dns/dns_query.py no-such-host.invalid
"""
import secrets
import socket
import struct
import sys

TYPE_NAMES = {1: "A", 5: "CNAME", 28: "AAAA"}
ERRORS = {0: "no error", 2: "SERVFAIL (the DNS server had a problem)",
          3: "NXDOMAIN (this name does not exist)", 5: "REFUSED"}


def build_query(name, query_id):
    # Header: id, flags (0x0100 = please resolve fully), 1 question, 0 answers, 0, 0
    header = struct.pack("!HHHHHH", query_id, 0x0100, 1, 0, 0, 0)
    # "example.com" travels as: 7 example 3 com 0
    qname = b"".join(bytes([len(p)]) + p.encode("ascii") for p in name.split(".")) + b"\0"
    return header + qname + struct.pack("!HH", 1, 1)   # type A (IPv4), class Internet


def read_name(data, pos):
    """Names can be compressed: two top bits set means 'continue at this offset'."""
    labels, end = [], None
    for _ in range(128):                       # limit, so bad data cannot loop forever
        length = data[pos]
        if length & 0xC0 == 0xC0:
            if end is None:
                end = pos + 2
            pos = struct.unpack_from("!H", data, pos)[0] & 0x3FFF
        elif length == 0:
            return ".".join(labels), (pos + 1 if end is None else end)
        else:
            labels.append(data[pos + 1:pos + 1 + length].decode("ascii", "replace"))
            pos += 1 + length
    raise ValueError("bad DNS name")


def main():
    name = sys.argv[1].rstrip(".") if len(sys.argv) > 1 else "example.com"
    server = sys.argv[2] if len(sys.argv) > 2 else "1.1.1.1"
    query_id = secrets.randbelow(65536)
    query = build_query(name, query_id)

    print(f"Question: what is the IPv4 address of {name}?")
    print(f"Sending {len(query)} bytes by UDP to {server}:53\n  {query.hex(' ')}")
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(3)
        # connect() on UDP sends nothing; it only makes us ignore replies from elsewhere.
        sock.connect((server, 53))
        sock.send(query)
        try:
            reply = sock.recv(4096)
        except TimeoutError:
            sys.exit("No reply. Your network may block UDP port 53 to outside DNS servers.")

    reply_id, flags, questions, answers = struct.unpack_from("!HHHH", reply)
    if reply_id != query_id:
        sys.exit("The reply id does not match our question. Ignoring it.")
    code = flags & 0x000F
    print(f"\nReply: {len(reply)} bytes, status: {ERRORS.get(code, code)}, {answers} answer(s)")

    pos = 12                                   # skip the header
    for _ in range(questions):                 # skip our own question, which is echoed back
        _, pos = read_name(reply, pos)
        pos += 4
    for _ in range(answers):
        owner, pos = read_name(reply, pos)
        rtype, _cls, ttl, length = struct.unpack_from("!HHIH", reply, pos)
        pos += 10
        if rtype == 1:
            value = socket.inet_ntoa(reply[pos:pos + 4])
        elif rtype == 5:
            value = read_name(reply, pos)[0] + "   (an alias: look up this name instead)"
        else:
            value = f"{length} bytes"
        print(f"  {owner}  {TYPE_NAMES.get(rtype, rtype)}  {value}   [cache for {ttl}s]")
        pos += length

    print("\nThe same lookup the normal way (hosts file, cache, then your DNS server):")
    try:
        found = socket.getaddrinfo(name, None, type=socket.SOCK_STREAM)
        print(" ", sorted({info[4][0] for info in found}))
    except socket.gaierror as e:
        print("  failed:", e)


if __name__ == "__main__":
    main()
