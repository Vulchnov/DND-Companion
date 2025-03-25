import socket

SERVER_HOST = "192.168.1.14"  # Replace with the actual IP address of the server
SERVER_PORT = 5006


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