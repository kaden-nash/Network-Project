from typing import Optional
import asyncio

class AsyncMessage:
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

        return len(self._text).to_bytes(4, 'big')


    async def send(self, writer: asyncio.StreamWriter, otrtext: Optional[str] = None) -> None:
        """
        Sends text to dest socket. If otrtext is specified, it will set this str to the new text and send it
            dest - destination socket
            otrtext - text to send that will also be saved to this Message instance
        """

        if otrtext is not None:
            self.set_text(otrtext)
            
        writer.write(self.get_size_packed() + self.get_encoded_text())
        await writer.drain()
    

    async def recv(self, reader: asyncio.StreamReader) -> None:
        """
        Retreives data from src socket and stores it as text of Message instance
            src - socket to retrieve data from
        """

        # get length of message
        try:
            raw_length = await reader.readexactly(4) # size of msg is packed into 4 bytes
            if not raw_length:
                self._text = ""
                return
            
            msg_len = int.from_bytes(raw_length, 'big') # turns bytes to int
            full_msg_bytes = await reader.readexactly(msg_len)
            self._text = full_msg_bytes.decode('utf-8')

        except asyncio.IncompleteReadError as e:
            self._text = "" # signal a close of connection
        except ConnectionError as e:
            e.add_note("User closed connection")
            return ""

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
