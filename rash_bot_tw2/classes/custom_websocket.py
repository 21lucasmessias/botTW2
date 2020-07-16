import websockets
import traceback
import json
from time import sleep

class CustomWebsocket:
    def __init__(self, session):
        self._url = "wss://br.tribalwars2.com/socket.io/?platform=desktop&EIO=3&transport=websocket"
        self._ws = websockets.connect(self._url)
        self.session = session

    def produceMessage(self, sMsg):
        self.session.iHeaderId += 1
        return sMsg + '"id":' + str(self.session.iHeaderId) + ',"headers":{"traveltimes":[["browser_send"]]}}]'

    async def tryLogin(self):
        async with self._ws as ws:
            sMsg = self.produceMessage('42["msg",{"type":"Authentication/login","data":{"name":"' + self.session.sUsername + '","pass":"' + self.session.sPassword + '"},')
            await ws.send(sMsg)            
            self.session.bLogged = await self.listenLoginReturn(ws)

    async def listenLoginReturn(self, ws):
        async for msgServer in ws:
            if 'type' in msgServer:
                try:
                    objr = json.loads(msgServer[msgServer.find('{'):msgServer.rfind('}')+1])
                    if objr['type'] == 'Login/success':
                        self.session.sId = str(objr['data']['player_id'])
                        
                        if len(objr['data']['characters']) == 1:
                            self.session.sWorldId = objr['data']['characters'][0]['world_id']
                        else:
                            print('Escolha um dos mundos:')
                            for e, character in enumerate(objr['data']['characters']):
                                print(f'{e}-{character[e]["world_id"]}')
                            self.session.sWorldId = self.session.idToWorld[str(input('>').strip())]

                        #while self.session.sWorldId not in ['br43','br44','br46','br47','br48','br49']: #Select World
                        #    userWorldId = input('Logado com sucesso\nEm qual mundo deseja entrar?\n1.Queen\'s Sconce\n2.Rupea\n3.Tzschocha\n4.Uhrovec\n5.Visegrád\n6.Warkworth Castle\n>')
                        #    self.session.sWorldId = self.session.idToWorld[userWorldId]
                    
                        sMsg = self.produceMessage('42["msg",{"type":"Authentication/selectCharacter","data":{"id":' + self.session.sId + ',"world_id":"' + self.session.sWorldId + '"},')
                        await ws.send(sMsg)

                    elif objr['type'] == 'System/error':
                        return False

                    elif objr['type'] == 'Authentication/characterSelected':
                        return True
                except:
                    traceback.print_exc()
                    return False
                    
    
   # async def tryExecuteCommands(self):
