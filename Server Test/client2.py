import socket

BROADCAST_PORT = 5005


# Step 1: Get the local hostname.
local_hostname = socket.gethostname()

# Step 2: Get a list of IP addresses associated with the hostname.
ip_addresses = socket.gethostbyname_ex(local_hostname)[2]

# Step 3: Filter out loopback addresses (IPs starting with "127.").
filtered_ips = [ip for ip in ip_addresses if not ip.startswith("127.")]

for ip in filtered_ips:
    ipSplit = ip.split(".")
    ipSplit[3] = "255"
    BROADCAST_IP = ".".join(ipSplit)  # Broadcast address for local network

    # Create UDP socket
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    message = "Hello, any servers out there?"
    client_socket.sendto(message.encode(), (BROADCAST_IP, BROADCAST_PORT))
    print("Broadcast message sent.")

    # Listen for response
    client_socket.settimeout(3)  # Wait for a response for up to 3 seconds
    try:
        response, server_addr = client_socket.recvfrom(1024)
        print(f"Received response from {server_addr}: {response.decode()}")
    except socket.timeout:
        print("No response received.")
