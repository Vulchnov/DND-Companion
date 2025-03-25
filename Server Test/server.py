import socket

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

client_socket.close()
server_socket.close()