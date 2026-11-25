"""UDP: no connection, no handshake, but message boundaries are kept.

    python 02-udp-and-dns/udp_demo.py
"""
import socket

# SOCK_DGRAM = UDP
with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as receiver, \
     socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sender:

    receiver.bind(("127.0.0.1", 0))
    receiver.settimeout(1)
    address = receiver.getsockname()

    print("1) Send three messages. No connect(), no accept():")
    for part in (b"ONE", b"TWO", b"THREE"):
        sender.sendto(part, address)
    for _ in range(3):
        data, _sender = receiver.recvfrom(1024)
        print("   received", data)
    print("   Compare with 01-tcp/stream_demo.py, where they were glued together.")

    print("2) Send to a port where nobody is listening:")
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as unused:
        unused.bind(("127.0.0.1", 0))
        nobody = unused.getsockname()
    sender.sendto(b"is anyone there?", nobody)
    print("   sendto() succeeded anyway. UDP does not tell you if the data arrived.")
