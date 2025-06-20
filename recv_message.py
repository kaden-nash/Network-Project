import struct
import socket

def recv_message(sock: socket.socket) -> bytes | str:
    """
    Receives messages from clients

        sock - client_socket

    @returns encoded message from client, "" otherwise
    """
    # get length of message
    raw_length = b""
    while len(raw_length) < 4: # put this in a loop to ensure retransmissions are captured
        try:
            byte_length = sock.recv(4 - len(raw_length)) # source of OSError "socket doesn't exist" when quitting
            if not byte_length:
                return ""
            raw_length += byte_length
        except ConnectionError as e:
            raise ConnectionError(f"Error recving from socket in recv_message: {e}")
        except OSError as e:
            e.add_note("User closed connection")
            return ""
    
    rest_len = struct.unpack("!I", byte_length)[0]
    
    # get rest of message
    data = b""
    while len(data) < rest_len: # put this in a loop to ensure retransmissions are captured
        try:
            message = sock.recv(rest_len - len(data))
            if not message:
                return None
            data += message
        except Exception as e:
            raise ConnectionError(f"Error recving from socket in recv_message: {e}") from e

    return data.decode("utf-8")