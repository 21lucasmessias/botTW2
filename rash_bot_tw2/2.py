import asyncio
import websockets
from time import sleep
import json
import random

class EchoWebsocket:
    async def __aenter__(self):
        self._conn = websockets.connect('wss://br.tribalwars2.com/socket.io/?platform=desktop&EIO=3&transport=websocket')
        self.websocket = await self._conn.__aenter__()        
        return self

    async def __aexit__(self, *args, **kwargs):
        await self._conn.__aexit__(*args, **kwargs)

    async def send(self, message):
        await self.websocket.send(message)

    async def receive(self):
        return await self.websocket.recv()

class mtest:
    def __init__(self):
        self.wws = EchoWebsocket()
        self.loop = asyncio.get_event_loop()

    def get_ticks(self):
        return self.loop.run_until_complete(self.__async__get_ticks())

    async def __async__get_ticks(self):
        async with self.wws as echo:
            await echo.send('2')
            return await echo.receive()

test = mtest()
print(test.get_ticks())