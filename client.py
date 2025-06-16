import socket
import time
from Message import Message
import threading

HOST = "127.0.0.1"
PORT = 55555

exit_keywords = {"/quit", "/exit"}

chat_ongoing = True

stop_event = threading.Event()

time.sleep(2)

def send(sock: socket.socket) -> None:
    print("Begin chat")
    print("**************************************************")

    global chat_ongoing
    while not stop_event.is_set():
        raw_text = input("(me): ")
        msg = Message(raw_text)
        msg.send(sock)
    
        if msg.get_text() in exit_keywords or msg.isEmpty():
            stop_event.set()


def listen(sock: socket.socket) -> None:
    global chat_ongoing
    msg = Message("")

    while not stop_event.is_set():
        msg.recv(sock)
        if msg.get_text() in exit_keywords or msg.isEmpty():
            print("<A client disconnected>")
            stop_event.set()
        else:
            print(f"A client says: {msg}")

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

        send_handler = threading.Thread(target=send, args=[client_sock])
        listen_handler = threading.Thread(target=listen, args=[client_sock])
        
        send_handler.start()
        listen_handler.start()

        while send_handler.is_alive() or listen_handler.is_alive():
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("**************************************************")
        print("End chat\n")

    except ConnectionError as e:
        print(f"A connection error occured: {e}")
    
    except Exception as e:
        print(f"An error occured: {e}")

    finally:
        # graceful disconnect
        try:
            client_sock.shutdown(socket.SHUT_RDWR)
        except Exception:
            # print("Failed to properly shutdown"
            pass

        print("Closing connection")
        if client_sock:
            client_sock.close()

if __name__ == "__main__":
    start_client()