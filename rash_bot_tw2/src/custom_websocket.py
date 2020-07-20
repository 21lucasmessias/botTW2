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
                        self.session.sWorldId = objr['data']['characters'][0]['world_id']

                        sMsg = self.produceMessage('42["msg",{"type":"Authentication/selectCharacter","data":{"id":' + self.session.sId + ',"world_id":"' + self.session.sWorldId + '"},')
                        await ws.send(sMsg)

                    elif objr['type'] == 'Authentication/characterSelected':
                        msg = self.produceMessage('42["msg",{"type":"Premium/listItems",')
                        await ws.send(msg)

                    elif objr['type'] == 'Premium/items':
                        self.session.lInventory = objr['data']['inventory']

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
                    
                    elif objr['type'] == 'System/error':
                        return False
                except:
                    traceback.print_exc()
                    return False
                    
    async def tryAttackBarbarians(self, ws):
        for village in self.session.lVillagesPlayer:
            village['lBarb'] = []

        #Absorve as informações de bárbaros da região proxima ao jogador
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

            _Units = {}
            for (key, value) in sorted(village['units'].items(), key=lambda k: k[1]):
                if value != 0:
                    _Units[key] = value

            village['units'] = _Units

        qntAtaques = int(input('Quantidade de ataques que deseja realizar:'))

        for village in self.session.lVillagesPlayer:
            for i in range(0, qntAtaques):
                _Units = {}
                bRemoverUnidade = False
                lUnidadesRemover = []

                for unit, qnt in village['units'].items():
                    if int(qnt/qntAtaques) > 0:
                        _Units[unit] = int(qnt/qntAtaques)
                    else:
                         _Units[unit] = qnt
                         bRemoverUnidade = True
                         lUnidadesRemover.append(unit)
                
                if bRemoverUnidade:
                    for unit in lUnidadesRemover:
                        village['units'].pop(unit)
                
                if i+1 == qntAtaques:
                    for unit, qnt in _Units.items():
                        _Units[unit] = qnt + village['units'][unit] - qnt * qntAtaques
                await ws.send(self.produceMessage('42["msg",{"type":"Command/sendCustomArmy","data":{"start_village":' + str(village['id']) + ',"target_village":' + str(village['lBarb'][i]['id']) + ',"type":"attack","units":'+ str(_Units).replace(' ', '').replace("'", '"') +',"icon":0,"officers":{},"catapult_target":"headquarter"},'))


        print("Tropas enviadas com sucesso!")


    async def tryGetResource(self, ws):
        msg = self.produceMessage('42["msg",{"type":"ResourceDeposit/getInfo",')
        await ws.send(msg)
        async for msgServer in ws:
            if 'type' in msgServer:
                objr = json.loads(msgServer[msgServer.find('{'):msgServer.rfind('}')+1])

                if objr['type'] == 'ResourceDeposit/info':
                    for job in objr['data']['jobs']:
                        msg = self.produceMessage('42["msg",{"type":"ResourceDeposit/startJob","data":{"job_id":'+ str(job['id']) +'},')

    async def tryExecuteCommands(self, ws):
        #Cria uma lista de vilas bárbaras vazia para cada vila do player
        option = 1 #int(input("Escolha uma ação:\n1. Atacar bárbaros\n2.Recolher recursos do depósito"))

        if option == 1:
            await self.tryAttackBarbarians(ws)
        #elif option == 2:
         #   self.tryGetResource(ws)
