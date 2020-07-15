import asyncio
import websockets
import time
import json
import traceback
class Login:
   def __init__(self, sUsername, sPassword, sToken, sId, sWorldId):
      self.sUsername = sUsername
      self.sPassword = sPassword
      self.sToken    = sToken
      self.sId       = sId
      self.sWorldId  = sWorldId

class Conection:
   def __init__(self, iHeaderId, bLogged, bAuth, bLogOff):
      self.iHeaderId = iHeaderId
      self.bLogged   = bLogged
      self.bLogOff   = bLogOff

   def getHeaders(self, iHeaderId):
      self.iHeaderId = self.iHeaderId + 1
      return ',"id":' + str(self.iHeaderId) + ',"headers":{"traveltimes":[["browser_send"]]}}]'

async def tryLogin():
   async with websockets.connect(url) as ws:
      msgLogin = '42["msg",{"type":"Authentication/login","data":{"name":"' + cLogin.sUsername + '","pass":"' + cLogin.sPassword + '"},"id":2,"headers":{"traveltimes":[["browser_send"]]}}]'
      await ws.send(msgLogin)
      async for msgServer in ws:
         if 'type' in msgServer:
            try:
               objr = json.loads(msgServer[msgServer.find('{'):msgServer.rfind('}')+1])

               if objr['type'] == 'Login/success':
                  cLogin.sToken   = objr['data']['token']
                  cLogin.sId      = str(objr['data']['player_id'])
                  cLogin.sWorldId = 'br49'

                  while cLogin.sWorldId not in ['br43','br44','br46','br47','br48','br49']: #Select World
                     cLogin.sWorldId = input('Logado com sucesso\nEm qual mundo deseja entrar?\n1.Queen\'s Sconce\n2.Rupea\n3.Tzschocha\n4.Uhrovec\n5.Visegrád\n6.Warkworth Castle\n>')
                     if cLogin.sWorldId == '1':
                        cLogin.sWorldId = 'br43'
                     elif cLogin.sWorldId == '2':
                        cLogin.sWorldId = 'br44'
                     elif cLogin.sWorldId == '3':
                        cLogin.sWorldId = 'br46'
                     elif cLogin.sWorldId == '4':
                        cLogin.sWorldId = 'br47'
                     elif cLogin.sWorldId == '5':
                        cLogin.sWorldId = 'br48'
                     elif cLogin.sWorldId == '6':
                        cLogin.sWorldId = 'br49'

                  cSession.bLogged = True
                  break
               elif objr['type'] == 'System/error':
                  break
            except:
               traceback.print_exc()

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
   bExit = False

   while not bExit:
      asLoop   = asyncio.get_event_loop()
      url      = "wss://br.tribalwars2.com/socket.io/?platform=desktop&EIO=3&transport=websocket"
      cSession = Conection(0, False, False, False)

      while not cSession.bLogged:
         cLogin   = Login(input('Login: '), input('Senha: '), '', '', '')
         asLoop.run_until_complete(tryLogin())

         if not cSession.bLogged:
            print("Falha ao entrar no jogo.")

      while not cSession.bLogOff:
         cSession.bLogOff = asLoop.run_until_complete(tryAuth())

      bExit = str(input('Deseja reconectar?\n1.Sim\n2.Não\n>')) == '2'

   asLoop.close()   