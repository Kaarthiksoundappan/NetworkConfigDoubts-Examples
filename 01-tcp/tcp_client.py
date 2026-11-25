"""A TCP client. Start tcp_server.py first."""
import socket
import sys

HOST, PORT = "127.0.0.1", 9001

try:
    # The three-way handshake (SYN, SYN-ACK, ACK) happens inside this call.
    sock = socket.create_connection((HOST, PORT), timeout=5)
except ConnectionRefusedError:
    sys.exit(f"Nothing is listening on {HOST}:{PORT}. Start tcp_server.py first.")

with sock:
    print("Connected!")
    print("  my end    :", sock.getsockname(), "<- the OS picked this port for me")
    print("  server end:", sock.getpeername())

    for message in [b"hello", b"how are you?"]:
        sock.sendall(message)
        print(f"Sent {message!r}, got back {sock.recv(1024)!r}")

# Leaving the 'with' block closes the socket, which sends FIN to the server.
print("Closed.")
