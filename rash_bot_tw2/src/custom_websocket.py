import websockets
import traceback
import json
from time import sleep
import random

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
            self.session.bLogged = await self.tryGetLoginInformations(ws)
            if self.session.bLogged:
                print("Logado")
                await self.tryExecuteCommands(ws)
            else:
                print("Erro ao conectar.")

    async def tryGetLoginInformations(self, ws):
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

                        for en, village in enumerate(self.session.lVillagesPlayer):
                            village['lBarb'] = []
                            await ws.send(self.produceMessage('42["msg",{"type":"Map/getVillageDetails","data":{"village_id":'+str(village['id'])+',"my_village_id":'+str(self.session.lVillagesPlayer[en]['id'])+',"num_reports":5},'))

                    elif objr['type'] == 'Map/villageDetails':
                        for village in self.session.lVillagesPlayer:
                            if objr['data']['village_id'] == village['id']:
                                village['units'] = objr['data']['units']
                                village['qntAtaques'] = len(objr['data']['commands']['own'])
                                village['lAtqs'] = []

                                await ws.send(self.produceMessage('42["msg",{"type":"Overview/getCommands","data":{"count":25,"offset":0,"sorting":"origin_village_name","reverse":0,"groups":[],"directions":["forward","back"],"command_types":["attack"],"villages":['+ str(village['id']) +']},'))
                                if village['qntAtaques'] > 25:
                                    await ws.send(self.produceMessage('42["msg",{"type":"Overview/getCommands","data":{"count":25,"offset":25,"sorting":"origin_village_name","reverse":0,"groups":[],"directions":["forward","back"],"command_types":["attack"],"villages":[' + str(village['id']) + ']},'))
                                
                    elif objr['type'] == 'Overview/commands':
                        if objr['data']['total'] > 0:
                            for village in self.session.lVillagesPlayer:
                                if objr['data']['commands'][0]['origin_village_id'] == village['id']:
                                    for command in objr['data']['commands']:
                                        _Units = {}
                                        if command['spear'] > 0:
                                            _Units['spear'] = command['spear']
                                        if command['axe'] > 0:
                                            _Units['axe'] = command['axe']
                                        if command['sword'] > 0:
                                            _Units['sword'] = command['sword']
                                        if command['archer'] > 0:
                                            _Units['archer'] = command['archer']
                                        if command['light_cavalry'] > 0:
                                            _Units['light_cavalry'] = command['light_cavalry']
                                        if command['heavy_cavalry'] > 0:
                                            _Units['heavy_cavalry'] = command['heavy_cavalry']
                                        if command['mounted_archer'] > 0:
                                            _Units['mounted_archer'] = command['mounted_archer']
                                        if command['ram'] > 0:
                                            _Units['ram'] = command['ram']
                                        if command['catapult'] > 0:
                                            _Units['catapult'] = command['catapult']
                                        if command['knight'] > 0:
                                            _Units['knight'] = command['knight']
                                        if command['snob'] > 0:
                                            _Units['snob'] = command['snob']
                                        if command['trebuchet'] > 0:
                                            _Units['trebuchet'] = command['trebuchet']
                                        if command['doppelsoldner'] > 0:
                                            _Units['doppelsoldner'] = command['doppelsoldner']

                                        village['lAtqs'].append({'units':str(_Units).replace(' ', '').replace("'", '"'),
                                                    'id_vil': command['origin_village_id'],
                                                    'id_barb': command['target_village_id'],
                                                    'time_completed': command['time_completed'],
                                                    'time': (command['time_completed'] - command['time_start'])
                                                })

                                    village['lAtqs'] = sorted(village['lAtqs'], key=lambda k: k['time_completed'])

                        sleep(2)            
                        await ws.send(self.produceMessage('42["msg",{"type":"System/getTime","data":{},'))

                    elif objr['type'] == 'System/time':
                        return True
                    
                    elif objr['type'] == 'System/error':
                        return False
                except:
                    traceback.print_exc()
                    return False
                    
    async def tryExecuteCommands(self, ws):
        #Cria uma lista de vilas bárbaras vazia para cada vila do player
        option = 1 #int(input("Escolha uma ação:\n1. Atacar bárbaros\n2.Recolher recursos do depósito"))

        if option == 1:
            await self.tryAttackBarbarians(ws)
            await self.tryAutoAttackBarbarians(ws)

        elif option == 2:
            if(str(input('Deseja continuar rodando no modo ataque automático?')) == 's'):
                await self.tryAutoAttackBarbarians(ws)

    async def tryAttackBarbarians(self, ws):
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
                        if 'type' in objr:
                            if objr['type'] == 'Map/villageData':
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

        qntAtaques = int(input(f'Quantidade de ataques que deseja realizar:'))

        # Envia as tropas
        for village in self.session.lVillagesPlayer:
            if (qntAtaques + village['qntAtaques']) > 50:
                qntAtaques = 50 - village['qntAtaques']

            village['qntAtaques'] = village['qntAtaques'] + qntAtaques

            for i in range(0, qntAtaques):
                _Units = {}
                bRemoverUnidade = False
                lUnidadesRemover = []
                j = 0

                # Divide as unidades em grupos iguais (O primeiro e ultimo serão diferentes caso a quantidade seja quebrada)
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
                
                if (i + 1) == qntAtaques:
                    for unit, qnt in _Units.items():
                        _Units[unit] = qnt + village['units'][unit] - qnt * qntAtaques

                if _Units:
                    await ws.send(self.produceMessage('42["msg",{"type":"Command/sendCustomArmy","data":{"start_village":' + str(village['id']) + ',"target_village":' + str(village['lBarb'][i]['id']) + ',"type":"attack","units":'+ str(_Units).replace(' ', '').replace("'", '"') +',"icon":0,"officers":{},"catapult_target":"headquarter"},'))
                    
                    # Popula a lista de ataques
                    async for msgServer in ws:
                        if 'type' in msgServer:
                            objr = json.loads(msgServer[msgServer.find('{'):msgServer.rfind('}')+1])
                            _Units = {}
                            j += 1
                            
                            if objr['type'] == 'Command/sent':
                                for unit, qnt in objr['data']['units'].items():
                                    if qnt > 0:
                                        _Units[unit] = qnt

                                village['lAtqs'].append({'units':str(_Units).replace(' ', '').replace("'", '"'),
                                                        'id_vil': objr['data']['origin']['id'],
                                                        'id_barb': objr['data']['target']['id'],
                                                        'time_completed': objr['data']['time_completed'],
                                                        'time': (objr['data']['time_completed'] - objr['data']['time_start'])
                                                        })

                        if (j == 4):
                            break

            village['lAtqs'] = sorted(village['lAtqs'], key=lambda k: k['time_completed'])

        print("Tropas enviadas com sucesso!")

    async def tryAutoAttackBarbarians(self, ws):
        while True:
            await ws.send(self.produceMessage('42["msg",{"type":"System/getTime","data":{},'))
            async for msgServer in ws:
                if 'type' in msgServer:
                    objr = json.loads(msgServer[msgServer.find('{'):msgServer.rfind('}')+1])
                    if objr['type'] == 'System/time':
                        iTime = objr["data"]["time"]
                        break

            for village in self.session.lVillagesPlayer:
                for atq in village['lAtqs']:
                    print(f"Proximo envio de tropa em :{atq['time_completed'] - iTime}")
                    if atq['time_completed'] < iTime:
                        await ws.send(self.produceMessage('42["msg",{"type":"Command/sendCustomArmy","data":{"start_village":' + str(atq['id_vil']) + ',"target_village":' + str(atq['id_barb']) + ',"type":"attack","units":'+ str(atq['units']) +',"icon":0,"officers":{},"catapult_target":"headquarter"},'))
                        atq['time_completed'] = iTime + atq['time']
                        village['lAtqs'] = sorted(village['lAtqs'], key=lambda k: k['time_completed'])
                        break
                    else:
                        await ws.send('2')
                        break

            sleep(random.randrange(7,12))

    async def tryGetResource(self, ws):
        msg = self.produceMessage('42["msg",{"type":"ResourceDeposit/getInfo",')
        await ws.send(msg)
        async for msgServer in ws:
            if 'type' in msgServer:
                objr = json.loads(msgServer[msgServer.find('{'):msgServer.rfind('}')+1])

                if objr['type'] == 'ResourceDeposit/info':
                    for job in objr['data']['jobs']:
                        msg = self.produceMessage('42["msg",{"type":"ResourceDeposit/startJob","data":{"job_id":'+ str(job['id']) +'},')
