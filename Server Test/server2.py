import socket

BROADCAST_PORT = 5005  # Choose an available port

# Create UDP socket
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