import socket
import struct
from recv_message import recv_message
import time

HOST = "127.0.0.1"
PORT = 55555

time.sleep(5)

def start_client():
    client_sock = None

    try:
        # new socket, IPv4 address, TCP transmission
        client_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # could be declared with "with" to eliminate need for finally block

        # connect to server (initiates 3 way handshake)
        client_sock.connect((HOST, PORT))
        print(f"Connected to {HOST}:{PORT}")

        # prepare message
        message_str = "The quick brown fox jumped over the lazy dog"
        message_list_strs = message_str.split(sep=" ")
        message_list_strs.reverse()
        while len(message_list_strs) > 0:
            # send
            time.sleep(0.5)
            word = message_list_strs.pop()
            word_length = struct.pack("!I", len(word))
            client_sock.sendall(word_length + word.encode("utf-8"))

            # receive acknowledgement
            ack = recv_message(client_sock)
            if not ack:
                print(f"Problem sending message: {word}")
            else:
                print(f"Server ack: {ack}")
    

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