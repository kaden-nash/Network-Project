import socket
import threading
import time
from Message import Message

host = "127.0.0.1"
port = 55555

time.sleep(2)

# lock to prevent race conditions
lock = threading.Lock()

# currently connected client list
clients = []
clnt_addrs = []

def broadcast(msg: Message, from_: socket.socket) -> None:
    local_addr = from_.getsockname()

    with lock:
        clnt_copy = list(clients)
        clnt_addrs_copy = list(clnt_addrs)

        for sock, addr in zip(clnt_copy, clnt_addrs_copy):
            if sock == from_:
                continue

            try: 
                msg.send(sock)
            except ConnectionError as e:
                print(f"Connection error broadcasting from {local_addr[0]}:{local_addr[1]} to {addr[0]}:{addr[1]}: {e}")

                if sock in clients:
                    clients.remove(sock)
                if addr in clnt_addrs:
                    clnt_addrs.remove(addr)

                try:
                    sock.shutdown(socket.SHUT_RDWR)
                except Exception:
                    pass
                finally:
                    sock.close()
            

def handle_client(client_socket: socket.socket, client_address) -> None:
    """
    Handles session maintenance and shutdown with clients
        client_socket - socket on server for communication with a client
        client_address - Client's IPv4:PORT
    """
    try: # listen for client message
        msg = Message("")
        while True:
            msg.recv(client_socket)
            time.sleep(0.5)

            if msg.isEmpty():
                print(f"{client_address} disconnected.")
                break
            else:
                broadcast(msg, client_socket)

            print(f"{client_address}: {msg}")

    except ConnectionError as e:
        print(f"{client_address} disconnected.")
        pass

    except Exception as e: # handle errors
        print(f"Error while handling client: {client_address}: {e}")

    finally: # close socket that communicates with client
        with lock:
            if client_socket in clients:
                clients.remove(client_socket)
        
        client_socket.close()

def start_server() -> None:
    """
    Initalizes server and accepts incoming connections, creating a new thread for each connection established
    """
    # create a socket that listens over the internet and sends data via TCP
    serv_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # for UDP, socket.SOCK_DGRAM

    # tells OS to open up this socket once run is complete
    serv_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        # let OS know that this is the application listening for comms to host:port (a further specification than port)
        serv_sock.bind((host, port))

        # start listening (argument is backlog: any devices more than num trying to connect will be refused)
        serv_sock.listen(2)
        print(f"Server listening on {host}:{port}")

        # initial join time
        serv_sock.settimeout(10.0)

        serv_running = True
        while serv_running:
            try:
                # accept a connection
                client_socket, client_address = serv_sock.accept()
                print(f"Accepted connection from {client_address}")

                # stop blocking after 1 second if initial connection is made
                serv_sock.settimeout(1.0)

                # start new thread for each client connecting
                handler = threading.Thread(target=handle_client, args=[client_socket, client_address])
                handler.start()

                # append with a lock
                # threads will be removing elements from this list and 
                # we don't want a race condition between the appends
                # and the removes.
                with lock:
                    clients.append(client_socket)
                    clnt_addrs.append(client_address)

            except socket.timeout:
                if len(clients) == 0:
                    break
        
        # graceful shutdown
        try:
            serv_sock.shutdown(socket.SHUT_RDWR)
        except Exception:
            print("Failed serv_sock shutdown")
    
    except KeyboardInterrupt:
        print(f"Beginning server shutdown due to keyboard interrupt...")

    except Exception as e:
        print(f"Error in server: {e}")

    finally:
        print("Closing server")
        if serv_sock:
            serv_sock.close()

if __name__ == "__main__":
    start_server()