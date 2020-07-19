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
            if self.session.bLogged:
                print("Logado")
                await self.tryExecuteCommands(ws)
            else:
                print("Erro ao conectar.")

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
                        msg = self.produceMessage('42["msg",{"type":"Character/getInfo","data":{},')
                        await ws.send(msg)

                    elif objr['type'] == 'Character/info':
                        self.session.lVillagesPlayer = objr['data']['villages']

                        for village in self.session.lVillagesPlayer:
                            msg = self.produceMessage('42["msg",{"type":"Map/getVillageDetails","data":{"village_id":'+str(village['id'])+',"my_village_id":'+str(self.session.lVillagesPlayer[0]['id'])+',"num_reports":5},')
                            await ws.send(msg) 

                        sleep(0.3)
                        await ws.send(self.produceMessage('42["msg",{"type":"System/getTime","data":{},'))

                    elif objr['type'] == 'Map/villageDetails':
                        for village in self.session.lVillagesPlayer:
                            if objr['data']['village_id'] == village['id']:
                                village['units'] = objr['data']['units']
                                break

                    elif objr['type'] == 'System/time':
                        return True
                except:
                    traceback.print_exc()
                    return False
                    
    async def tryAttackBarbarians(self, ws):
        for village in self.session.lVillagesPlayer:
            village['lBarb'] = []

        #Absorve todas as informações do mapa
        i = j = 0
        for x in range(self.session.lVillagesPlayer[0]['x']-100, self.session.lVillagesPlayer[0]['x']+100, 25):
            for y in range(self.session.lVillagesPlayer[0]['y']-100, self.session.lVillagesPlayer[0]['y']+100, 25):
                await ws.send(self.produceMessage('42["msg",{"type":"Map/getVillagesByArea","data":{"x":'+str(x)+',"y":'+str(y)+',"width":25,"height":25},'))
                i += 1
                if i == 32:
                    i = j = 0
                    # Popula a lista de vilas bárbaras para cada vila que o usuário 
                    # com a distância da vila para a dos bárbaros
                    async for msgServer in ws:
                        objr = json.loads(msgServer[msgServer.find('{'):msgServer.rfind('}')+1])
                        for bvillage in objr['data']['villages']:
                            if bvillage['name'] == 'Aldeia Bárbara':
                                for village in self.session.lVillagesPlayer:
                                    dist = abs(bvillage['x'] - village['x']) + abs(bvillage['y'] - village['y'])
                                    if dist < 40:
                                        village['lBarb'].append({'id':bvillage['id'], 'dist':dist})
                        j += 1
                        if j == 32:
                            break

        # Organiza para as vilas mais proximas ficarem por primeiro        
        for village in self.session.lVillagesPlayer:
            village['lBarb'] = sorted(village['lBarb'], key=lambda k: k['dist'])

        #Envia quantia de ataques possíveis
        units = {}
        j = k = menor = 50

        for village in self.session.lVillagesPlayer:
            for unit, qnt in village['units'].items():
                if qnt >= 50:
                    units = {unit: int(qnt/50)}
            if units:
                for i in range(0, 50):
                    await ws.send(self.produceMessage('42["msg",{"type":"Command/sendCustomArmy","data":{"start_village":' + str(village['id']) + ',"target_village":' + str(village['lBarb'][i]['id']) + ',"type":"attack","units":'+ str(units).replace(' ', '').replace("'", '"') +',"icon":0,"officers":{},"catapult_target":"headquarter"},'))
                    if i == 32:
                        async for msgServer in ws:
                            j += 1
                            if j == 32:
                                break
            else:
                for unit, qnt in village['units'].items():
                    if qnt > 0:
                        if menor > qnt:
                            menor = qnt
                        units = {unit: 1}
                if menor < 50:
                    for i in range(0, menor):
                        await ws.send(self.produceMessage('42["msg",{"type":"Command/sendCustomArmy","data":{"start_village":' + str(village['id']) + ',"target_village":' + str(village['lBarb'][i]['id']) + ',"type":"attack","units":'+ str(units).replace(' ', '').replace("'", '"') +',"icon":0,"officers":{},"catapult_target":"headquarter"},'))
                        if i == 32:
                            async for msgServer in ws:
                                k += 1
                                if k == 32:
                                    break

            if len(ws.messages) != 0:                    
                async for msgServer in ws:
                    print(msgServer)
                    if len(ws.messages) == 0:
                        break
        print("Tropas enviadas com sucesso!")

    '''async def tryGetResource(self, ws):
        msg = self.produceMessage('42["msg",{"type":"ResourceDeposit/getInfo",')
        await ws.send(msg)
        async for msgServer in ws:
            if 'type' in msgServer:
                objr = json.loads(msgServer[msgServer.find('{'):msgServer.rfind('}')+1])

                if objr['type'] == 'ResourceDeposit/info':
                    for job in objr['data']['jobs']:
                        msg = self.produceMessage('42["msg",{"type":"ResourceDeposit/startJob","data":{"job_id":'+ str(job['id']) +'},'''



    async def tryExecuteCommands(self, ws):
        #Cria uma lista de vilas bárbaras vazia para cada vila do player
        option = 1 #int(input("Escolha uma ação:\n1. Atacar bárbaros\n2.Recolher recursos do depósito"))

        if option == 1:
            await self.tryAttackBarbarians(ws)
        #elif option == 2:
         #   self.tryGetResource(ws)
            