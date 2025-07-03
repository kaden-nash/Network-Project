import socket
import time
from Message import Message
import threading
# from prompt_toolkit import PromptSession

HOST = "127.0.0.1"
PORT = 55555

exit_keywords = {"/quit", "/exit"}

stop_event = threading.Event()
send_fin = threading.Event()
listen_fin = threading.Event()

time.sleep(1) # delay for testing

def send(sock: socket.socket) -> None:
    print("Begin chat")
    print("**************************************************")

    while not stop_event.is_set():
        raw_text = input()
        msg = Message(raw_text)
        # TODO: Make this stop when listening receives a quit

        try:
            msg.send(sock)
        except ConnectionError as e:
            print(f"{e}")
            stop_event.set()
            break
    
        if msg.isDisconnecting():
            stop_event.set()
            # session.app.exit()
            break
    
    send_fin.set()
    

def listen(sock: socket.socket) -> None:
    msg = Message("")

    while not stop_event.is_set():
        try:
            msg.recv(sock)
        except ConnectionError as e:
            print(f"{e}")
            stop_event.set()
            break

        # handle self disconnect
        if msg.get_text() == "":
            break

        # handle other client disconnect
        if msg.isDisconnecting():
            print("<A client disconnected>")
            #TODO: Need to make this message specific for each account that disconnects and make sure this doesn't print when I myself disconnect
            stop_event.set()
            # if session and session.app and session.app.loop:
            #     session.app.loop.call_soon_threadsafe(session.app.exit)
            break
        
        print(f"A client says: {msg}")
    
    listen_fin.set()

    print("**************************************************")
    print("End chat")
        

def start_client() -> None:    
    client_sock = None

    try:
        # new socket, IPv4 address, TCP transmission
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # could be declared with "with" to eliminate need for finally block

        # connect to server (initiates 3 way handshake)
        client_sock.connect((HOST, PORT))
        print(f"Connected to {HOST}:{PORT}\n")

        # session = PromptSession()

        send_handler = threading.Thread(target=send, args=[client_sock])
        listen_handler = threading.Thread(target=listen, args=[client_sock])
        
        send_handler.start()
        listen_handler.start()
        
        send_fin.wait()
        listen_fin.wait()

    except KeyboardInterrupt: # stop via keyboard interrupt
        pass

    except ConnectionError as e:
        print(f"A connection error occured: {e}")
    
    except Exception as e:
        print(f"An error occured: {e}")

    finally:
        # graceful disconnect
        try:
            client_sock.shutdown(socket.SHUT_RDWR)
        except Exception: # ignore shutdown failure
            pass

        print("\n\nClosing connection")
        if client_sock:
            client_sock.close()

if __name__ == "__main__":
    start_client()