import socket

BROADCAST_PORT = 5005
BROADCAST_IP = "255.255.255.255"  # Broadcast address for local network

# Create UDP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

message = "Hello, any servers out there?"
client_socket.sendto(message.encode(), ("<broadcast>", BROADCAST_PORT))
print("Broadcast message sent.")

# Listen for response
client_socket.settimeout(3)  # Wait for a response for up to 3 seconds
try:
    response, server_addr = client_socket.recvfrom(1024)
    print(f"Received response from {server_addr}: {response.decode()}")
except socket.timeout:
    print("No response received.")
