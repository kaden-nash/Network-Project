import socket
import time
from Message import Message

HOST = "127.0.0.1"
PORT = 55555


time.sleep(2)

def start_client() -> None:
    client_sock = None

    try:
        # new socket, IPv4 address, TCP transmission
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # could be declared with "with" to eliminate need for finally block

        # connect to server (initiates 3 way handshake)
        client_sock.connect((HOST, PORT))
        print(f"Connected to {HOST}:{PORT}")

        # prepare message
        message_str = "The quick brown fox jumped over the lazy dog"
        msg = Message("")
        message_list_strs = message_str.split(sep=" ")
        message_list_strs.reverse()

        # send message
        while len(message_list_strs) > 0:
            time.sleep(0.25)
            word = message_list_strs.pop()
            msg.send(client_sock, word)

            # receive acknowledgement
            msg.recv(client_sock)
            if msg.isEmpty():
                print(f"Problem sending message: {word}")
            else:
                print(f"Server ack: {msg}")
        
        # graceful disconnect
        msg.send(client_sock, "")

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