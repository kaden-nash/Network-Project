import struct

def recv_message(sock):
    """
    Receives messages from clients and acknowledges

        sock - client_socket

    @returns decoded message from client, None otherwise
    """
    # get length of message
    raw_length = b""
    while len(raw_length) < 4: # put this in a loop to ensure retransmissions are captured
        byte_length = sock.recv(4 - len(raw_length))
        if not byte_length:
            return None
        raw_length += byte_length
    
    rest_len = struct.unpack("!I", byte_length)[0]
    
    # get rest of message
    data = b""
    while len(data) < rest_len: # put this in a loop to ensure retransmissions are captured
        message = sock.recv(rest_len - len(data))
        if not message:
            return None
        data += message

    return data.decode('utf-8')