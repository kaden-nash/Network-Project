from MessageA import AsyncMessage
import asyncio

async def send(writer: asyncio.StreamWriter) -> None:
    while not stop_event.is_set():
        msg = AsyncMessage("")
        try:
            pass
            # send message

        except asyncio.CancelledError:
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
            pass
            # get message in socket
        except asyncio.CancelledError:
            stop_event.set()
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
            stop_event.set()
            break
        
        # display message

    listen_fin.set()


async def start_client() -> None:    
    await asyncio.sleep(1) # delay for testing
    writer, reader = None, None
    try:
        reader, writer = await asyncio.open_connection(HOST, PORT)
        print(f"Connected to {HOST}:{PORT}\n")

        send_handler = asyncio.create_task(send(writer))
        listen_handler = asyncio.create_task(listen(reader))

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

    asyncio.run(start_client())