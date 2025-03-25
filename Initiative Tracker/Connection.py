import socket

connections = {}
sockets = []



def establishUDPLisener():
    global sockets
    # Create UDP socket
    BROADCAST_PORT = 5005
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    # Bind to all network interfaces on the chosen port
    server_socket.bind(('', BROADCAST_PORT))

    print("Server listening for broadcasts...")

    sockets.append(server_socket)
    while True:
        try:
            data, addr = server_socket.recvfrom(1024)  # Receive data
            print(f"Received broadcast from {addr}: {data.decode()}")

            # Send response directly to sender
            response = f"Server IP: {socket.gethostbyname(socket.gethostname())}"
            server_socket.sendto(response.encode(), addr)

            connections[data.decode()] = addr
        except:
            break

def establishUDPSender(name):
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

        message = name
        client_socket.sendto(message.encode(), (BROADCAST_IP, BROADCAST_PORT))
        print("Broadcast message sent.")

        # Listen for response
        client_socket.settimeout(3)  # Wait for a response for up to 3 seconds
        try:
            response, server_addr = client_socket.recvfrom(2048)
            print(f"Received response from {server_addr}: {response.decode()}")
            establishTCPSender(server_addr)
        except socket.timeout:
            print("No response received.")



def establishTCPListener():
    global sockets
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

    sockets.append(server_socket)



def establishTCPSender(addr):
    SERVER_HOST = addr  # Replace with the actual IP address of the server
    SERVER_PORT = 2006

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect((SERVER_HOST, SERVER_PORT))
        print(f"Connected to {SERVER_HOST}:{SERVER_PORT}")

        message = "Hello, server!"
        client_socket.send(message.encode())

        data = client_socket.recv(1024).decode()
        print(f"Received: {data}")

    except socket.error as e:
        print(f"Connection error: {e}")

    finally:
        client_socket.close()


def closeAll():
    global sockets
    for socketObj in sockets:
        sockets.remove(socketObj)
        socketObj.close()
