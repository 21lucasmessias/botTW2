import asyncio
import websockets
import time
import json
import traceback
from classes.session import Session
from classes.custom_websocket import CustomWebsocket

if __name__ == "__main__":
	session         = Session()
	customWebsocket = CustomWebsocket(session)
	asLoop          = asyncio.get_event_loop()
	
	asLoop.run_until_complete(customWebsocket.tryLogin())
	if session.bLogged:
		asLoop.run_until_complete(customWebsocket.tryExecuteCommands())
	else:
		print("Erro ao conectar, verifique suas credenciais ou contate o desenvolvedor.")

	asLoop.close()