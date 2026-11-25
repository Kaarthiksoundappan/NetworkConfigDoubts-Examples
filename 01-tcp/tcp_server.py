"""A TCP server that shouts back whatever it receives.

Terminal 1:  python 01-tcp/tcp_server.py
Terminal 2:  python 01-tcp/tcp_client.py
"""
import socket

HOST, PORT = "127.0.0.1", 9001

# AF_INET = IPv4, SOCK_STREAM = TCP
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
    listener.bind((HOST, PORT))   # claim this IP + port
    listener.listen()             # ask the operating system to accept connections
    listener.settimeout(0.5)      # wake up regularly so Ctrl+C works on Windows
    print(f"Listening on {HOST}:{PORT}  (Ctrl+C to stop)", flush=True)

    try:
        while True:
            try:
                # accept() returns a NEW socket for this one client.
                # The listener itself keeps waiting for others.
                conn, (client_ip, client_port) = listener.accept()
            except TimeoutError:
                continue

            print(f"\nClient {client_ip}:{client_port} connected", flush=True)
            with conn:
                try:
                    while True:
                        data = conn.recv(1024)    # wait for up to 1024 bytes
                        if data == b"":           # zero bytes = client closed (FIN)
                            print("Client closed the connection", flush=True)
                            break
                        print(f"Received {data!r}", flush=True)
                        conn.sendall(data.upper())
                except ConnectionError as e:      # e.g. the client was killed (RST)
                    print(f"Connection broke: {e}", flush=True)
    except KeyboardInterrupt:
        print("\nServer stopped.")
