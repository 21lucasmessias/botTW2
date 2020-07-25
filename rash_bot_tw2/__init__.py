import asyncio

from rash_bot_tw2.src.session import Session
from rash_bot_tw2.src.custom_websocket import CustomWebsocket

if __name__ == "__main__":
    session = Session()
    customWebsocket = CustomWebsocket(session)
    asLoop = asyncio.get_event_loop()

    asLoop.run_until_complete(customWebsocket.tryLogin())      
    asLoop.close()