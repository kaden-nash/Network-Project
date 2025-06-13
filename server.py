import socket
import threading

host = "127.0.0.1"
port = 55555

# create a server
# socket.create_server(host, port)

# create a socket that listens over the internet and sends data via TCP
serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# tells OS to open up this socket once run is complete
serv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# let OS know that this is the application listening for comms to host:port (a further specification than port)
serv_sock.bind((host, port))

# start listening (argument is backlog: any devices more than num trying to connect will be refused)
serv_sock.listen(1)
print(f"Server listening on {host}:{port}")

# accept a connection
client_socket, client_address_and_port = serv_sock.accept()
print(f"Accepted connection from {client_address_and_port[0]}")

# listen for client message
response = client_socket.recv(1024).decode('utf-8')
print(f"Client says: {response}")

# send message to client
client_socket.sendall("We did it!".encode('utf-8'))

# close seockets
try:
    pass
finally:
    print("Closing server")
    client_socket.close()
    serv_sock.close()