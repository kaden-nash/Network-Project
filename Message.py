import socket
import struct
from recv_message import recv_message
from typing import Optional

class Message:
    EXIT_KEYWORDS = {"/quit", "/exit"}
    
    def __init__(self, text: str):
        self._text = text
    

    def set_text(self, text: str) -> None:
        """
        Sets text to specified text
        """

        self._text = text


    def get_text(self) -> str:
        """
        Returns string of text
        """

        return self._text


    def get_encoded_text(self) -> bytes:
        """
        Returns the bytes of text encoded with utf-8
        """

        return self._text.encode("utf-8")


    def get_size_packed(self) -> bytes:
        """
        Returns the size of text in bytes packed into 4 byte integer
        """

        return struct.pack("!I", len(self._text))


    def send(self, dest: socket.socket, otrtext: Optional[str] = None) -> None:
        """
        Sends text to dest socket. If otrtext is specified, it will set this str to the new text and send it
            dest - destination socket
            otrtext - text to send that will also be saved to this Message instance
        """

        if not isinstance(dest, socket.socket):
            raise TypeError("dest was not a socket")
        
        if otrtext is not None:
            self.set_text(otrtext)
            
        dest.sendall(self.get_size_packed() + self.get_encoded_text())
    

    def recv(self, src: socket.socket) -> None:
        """
        Retreives data from src socket and stores it as text of Message instance
            src - socket to retrieve data from
        """
        if not isinstance(src, socket.socket):
            raise TypeError("src was not a socket")

        self.set_text(recv_message(src))


    def isEmpty(self) -> bool:
        """
        Returns True if text is empty, False otherwise
        """
        return ((not self._text) or (self._text == ""))


    def isDisconnecting(self) -> bool:
        """
        Return True if text is "" or in EXIT_KEYWORDS
        """
        return (self.isEmpty() or self._text in self.EXIT_KEYWORDS)


    def __sizeof__(self):
        return len(self._text)
    
    
    def __str__(self):
        return self._text
