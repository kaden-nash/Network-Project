from MessageA import AsyncMessage
from prompt_toolkit import PromptSession
import asyncio

async def send(writer: asyncio.StreamWriter, session: PromptSession) -> None:
    print("Begin chat")
    print("**************************************************")

    while not stop_event.is_set():
        try:
            raw_text = await session.prompt_async("me: ")
            msg = AsyncMessage(raw_text)
            await msg.send(writer)

        except asyncio.CancelledError:
            if session.app and session.app.loop:
                session.app.exit()
            raise asyncio.CancelledError

        except ConnectionError as e:
            print(f"{e}")
            stop_event.set()
            break
        
        if msg.isDisconnecting():
            stop_event.set()
            break
    

async def listen(reader: asyncio.StreamReader) -> None:
    msg = AsyncMessage("")

    while not stop_event.is_set():
        try:
            await msg.recv(reader)

        except asyncio.CancelledError:
            stop_event.set()
            if session.app and session.app.loop:
                session.app.exit()
            raise asyncio.CancelledError

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
            stop_event.set()
            break
        
        print(f"A client says: {msg}")
    
    listen_fin.set()

    print("**************************************************")
    print("End chat")
        

async def start_client() -> None:    
    await asyncio.sleep(1) # delay for testing
    writer, reader = None, None
    try:
        reader, writer = await asyncio.open_connection(HOST, PORT)
        print(f"Connected to {HOST}:{PORT}\n")

        send_handler = asyncio.create_task(send(writer, session))

        await listen_fin.wait()

        send_handler.cancel()
        try:
            await send_handler
        except asyncio.CancelledError:
            pass # expected

    except ConnectionError as e:
        print(f"A connection error occured: {e}")
    
    except Exception as e:
        print(f"An error occured: {e}")

    finally:
        if session.app and session.app.loop:
            session.app.exit()
        
        # closes writer and reader apparently
        if writer:
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:
                pass # ignore failures to close properly

        print("\n\nClosing connection")

if __name__ == "__main__":
    
    HOST = "127.0.0.1"
    PORT = 55555

    stop_event = asyncio.Event()
    listen_fin = asyncio.Event()

    session = PromptSession()

    asyncio.run(start_client())