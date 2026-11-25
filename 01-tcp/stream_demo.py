"""TCP is a stream of bytes, not a list of messages. Runs on its own.

    python 01-tcp/stream_demo.py
"""
import socket
import time

with socket.create_server(("127.0.0.1", 0)) as listener:    # port 0 = any free port
    sender = socket.create_connection(listener.getsockname())
    receiver, _ = listener.accept()

    with sender, receiver:
        print("1) Three separate sends...")
        for part in (b"ONE", b"TWO", b"THREE"):
            sender.sendall(part)
        time.sleep(0.2)
        print("   ...usually arrive as one blob:", receiver.recv(1024))

        print("2) One send, read with a small buffer, arrives in pieces:")
        sender.sendall(b"HELLO WORLD")
        pieces = []
        while sum(map(len, pieces)) < len(b"HELLO WORLD"):
            pieces.append(receiver.recv(4))
        print("  ", pieces)

        print("3) The fix: agree where a message ends. Here, every message ends in \\n:")
        sender.sendall(b"ONE\nTWO\nTHREE\n")
        sender.shutdown(socket.SHUT_WR)     # send FIN: "I have nothing more to send"
        with receiver.makefile("rb") as lines:
            for line in lines:
                print("  ", line)
