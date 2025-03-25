import socket


def listenForNewClient():
    # Create UDP socket
    BROADCAST_PORT = 5005
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Bind to all network interfaces on the chosen port
    server_socket.bind(('', BROADCAST_PORT))

    print("Server listening for broadcasts...")

    while True:
        data, addr = server_socket.recvfrom(1024)  # Receive data
        print(f"Received broadcast from {addr}: {data.decode()}")

        # Send response directly to sender
        response = f"Server IP: {socket.gethostbyname(socket.gethostname())}"
        server_socket.sendto(response.encode(), addr)

def establishTCP():
    SERVER_HOST = '0.0.0.0'  # Listen on all available interfaces
    SERVER_PORT = 5006

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('', SERVER_PORT))
    server_socket.listen(1)

    print(f"Server listening on {SERVER_HOST}:{SERVER_PORT}")

    client_socket, client_address = server_socket.accept()
    print(f"Accepted connection from {client_address[0]}:{client_address[1]}")

    data = client_socket.recv(1024).decode()
    print(f"Received: {data}")

    response = "Hello, client!"
    client_socket.send(response.encode())
