import socket
import threading
import time
from Message import Message

host = "127.0.0.1"
port = 55555

time.sleep(1) # delay for testing

# lock to prevent race conditions
lock = threading.Lock()

# currently connected client list
clients = []
clnt_addrs = []

def broadcast(msg: Message, from_ip: str, from_port: int) -> None:
    with lock:
        clnt_copy = list(clients)
        clnt_addrs_copy = list(clnt_addrs)

    for sock, addr in zip(clnt_copy, clnt_addrs_copy):
        if addr[0] == from_ip and addr[1] == from_port:
            if not msg.isDisconnecting(): # allow client recv to stop blocking when trying to disconnect
                continue

        try: 
            msg.send(sock)
        except ConnectionError as e:
            print(f"Connection error broadcasting from {from_ip}:{from_port} to {addr[0]}:{addr[1]}: {e}")
            print(f"Closing socket w/ client {addr[0]}:{addr[1]}")

            with lock:
                if sock in clients:
                    clients.remove(sock)
                if addr in clnt_addrs:
                    clnt_addrs.remove(addr)

            # recursively broadcast disconnects that occur till either everyone is disconnected or there are no connection errors during a broadcast
            msg.set_text("/quit") # msg might not already be "/quit"
            broadcast(msg, addr[0], addr[1])
            print('had to recursively call broadcast due to connection error')

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
    local_ip = client_address[0]
    local_port = client_address[1]

    try: # listen for client message
        msg = Message("")
        while True:
            msg.recv(client_socket)
            time.sleep(0.1) # prevent excessive CPU use
            broadcast(msg, local_ip, local_port)
            print(f"{client_address}: {msg}")
            if msg.isDisconnecting(): # FIXME: Currently continues receiving messages from client that is not yet disconnected
                break

        print(f"{client_address} disconnected")

    except ConnectionError as e:
        print(f"{client_address} disconnected with error: {e}")

        # let other servers know that this client is abruptly disconnecting
        msg.set_text("/quit") 
        broadcast(msg, local_ip, local_port)

    except Exception as e: 
        print(f"Error while handling client: {client_address}: {e}")

    finally: # close socket that communicates with client
        with lock:
            if client_socket in clients:
                clients.remove(client_socket)
            if client_address in clnt_addrs:
                clnt_addrs.remove(client_address)
        
        try:
            client_socket.shutdown(socket.SHUT_RDWR)
        except Exception: # ignore shutdown errors
            pass
        finally:
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
        
    
    except KeyboardInterrupt:
        print(f"Beginning server shutdown due to keyboard interrupt...")

    except Exception as e:
        print(f"Error in server: {e}")

    finally:
        # graceful shutdown
        try:
            serv_sock.shutdown(socket.SHUT_RDWR)
        except Exception:
            # print("Failed serv_sock shutdown")
            pass

        print("Closing server")
        if serv_sock:
            serv_sock.close()

if __name__ == "__main__":
    start_server()