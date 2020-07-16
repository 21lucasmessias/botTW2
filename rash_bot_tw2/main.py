import asyncio
import websockets
import time
import json
import traceback
from classes.login import Login
from classes.connection import Connection
from classes.custom_websocket import CustomWebsocket

async def tryAuth():
   async with websockets.connect(url) as ws:
      try:
         async for msgServer in ws:
            print(msgServer)
            if 'type' in msgServer:
               try:
                  objr = json.loads(msgServer[msgServer.find('{'):msgServer.rfind('}')+1])
                  #print(objr["type"])
                  #print(json.dumps(objr, indent=1))
                  if objr['type'] == 'System/welcome':
                     msgAuth = '42["msg",{"type":"Authentication/login","data":{"name":"' + cLogin.sUsername + '","token":"'+ cLogin.sToken +'"}' + cSession.getHeaders(cSession.iHeaderId)
                     await ws.send(msgAuth)
                  elif objr['type'] == 'Login/success':
                     msgAuth = '42["msg",{"type":"Authentication/selectCharacter","data":{"id":' + cLogin.sId + ',"world_id":"' + cLogin.sWorldId + '"}' + cSession.getHeaders(cSession.iHeaderId)
                     await ws.send(msgAuth)
                  elif objr['type'] == 'Authentication/logout':
                     return True      
               except:
                  traceback.print_exc()
      except websockets.exceptions.ConnectionClosedError:
         print('Reconectando...')

      return False
      

if __name__ == "__main__":
   # cLogin   = Login(input('Login: '), input('Senha: '), '', '', '')
   cLogin   = Login('fslucasfs', '123456abc', '', '', '')
   cSession = Connection(0, False, False, False)
   customWebsocket = CustomWebsocket(cLogin, cSession)

   asLoop   = asyncio.get_event_loop()

   while not cSession.bLogged:
      asLoop.run_until_complete(customWebsocket.tryLogin())

      if not cSession.bLogged:
         print("Falha ao entrar no jogo.")

   while not cSession.bLogOff:
      cSession.bLogOff = asLoop.run_until_complete(tryAuth())

   asLoop.close()   