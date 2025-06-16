import socket
import time
from Message import Message

HOST = "127.0.0.1"
PORT = 55555

exit_keywords = set()
exit_keywords.add("/quit")
exit_keywords.add("/exit")

time.sleep(2)

def send(sock: socket.socket) -> None:
    print("Begin chat")
    print("**************************************************")
    count = 0
    while count < 2:
        raw_text = input("(me): ")
        msg = Message(raw_text)
        msg.send(sock)
        count += 1


def listen(sock: socket.socket) -> None:
    msg = Message("")
    while True:
        msg.recv(sock)
        if msg.get_text() in exit_keywords or msg.isEmpty():
            print("<Other client disconnected>")
            break
        else:
            print(f"Other client says: {msg}")

    print("**************************************************")
    print("End chat\n")
        

def start_client() -> None:
    client_sock = None

    try:
        # new socket, IPv4 address, TCP transmission
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # could be declared with "with" to eliminate need for finally block

        # connect to server (initiates 3 way handshake)
        client_sock.connect((HOST, PORT))
        print(f"Connected to {HOST}:{PORT}\n")

        send(client_sock)
        listen(client_sock)
        
        # graceful disconnect
        client_sock.shutdown(socket.SHUT_RDWR)

    except ConnectionError as e:
        print(f"A connection error occured: {e}")
    
    except Exception as e:
        print(f"An error occured: {e}")

    finally:
        print("Closing connection")
        if client_sock:
            client_sock.close()

if __name__ == "__main__":
    start_client()