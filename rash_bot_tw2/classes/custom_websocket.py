import websockets
import traceback
import json

idToWorld = {
    '1': 'br43',
    '2': 'br44',
    '3': 'br46',
    '4': 'br47',
    '5': 'br48',
    '6': 'br49',
}

class CustomWebsocket:
    def __init__(self, cLogin, cSession):
        self.url = "wss://br.tribalwars2.com/socket.io/?platform=desktop&EIO=3&transport=websocket"
        self._ws = websockets.connect(self.url)
        self.cLogin = cLogin
        self.cSession = cSession

    def produceMessage(self):
        return '42["msg",{"type":"Authentication/login","data":{"name":"' + self.cLogin.sUsername + '","pass":"' + self.cLogin.sPassword + '"},"id":2,"headers":{"traveltimes":[["browser_send"]]}}]'

    async def tryLogin(self):
        async with self._ws as ws:
            msgLogin = self.produceMessage()
            await ws.send(msgLogin)
            await self.listenLoginReturn(ws)

    async def listenLoginReturn(self, ws):
        async for msgServer in ws:
            if 'type' in msgServer:
                try:
                    objr = json.loads(msgServer[msgServer.find('{'):msgServer.rfind('}')+1])
                    if objr['type'] == 'Login/success':
                        self.cLogin.sToken = objr['data']['token']
                        self.cLogin.sId = str(objr['data']['player_id'])
                        self.cLogin.sWorldId = 'br49'

                        while self.cLogin.sWorldId not in ['br43','br44','br46','br47','br48','br49']: #Select World
                            userWorldId = input('Logado com sucesso\nEm qual mundo deseja entrar?\n1.Queen\'s Sconce\n2.Rupea\n3.Tzschocha\n4.Uhrovec\n5.Visegrád\n6.Warkworth Castle\n>')
                            self.cLogin.sWorldId = idToWorld[userWorldId]
                            self.cSession.bLogged = True
                            break
                    elif objr['type'] == 'System/error':
                        break
                except:
                    traceback.print_exc()