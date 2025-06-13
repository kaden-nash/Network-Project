import socket

HOST = "127.0.0.1"
PORT = 55555

# new socket, IPv4 address, TCP transmission
client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


# connect to server (initiates 3 way handshake)
try:
    client_sock.connect((HOST, PORT))
    print(f"Connected to {HOST}:{PORT}")
except ConnectionError as e:
    print(f"An error occured while connecting to server: {e}")

# send data (as bytes) to destination
client_sock.sendall("Hello world!".encode('utf-8'))

# receive response
response = client_sock.recv(1024).decode('utf-8')

print(f"Server says: {response}")

# close seockets
try:
    pass
finally:
    print("Closing client")
    client_sock.close()