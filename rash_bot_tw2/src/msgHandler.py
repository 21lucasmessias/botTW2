from src.utils import produceMessage, lUnits, getJsonFromMsg
import traceback

class MessageHandler:
    def __init__(self, ws, session):
        self.ws = ws
        self.session = session
        self.oRcv = {}
        self.MsgsCall = {
            'System/welcome': self.System_welcome,
            'Login/success': self.Login_success,
            'Authentication/characterSelected': self.Authentication_characterSelected,
            'Premium/items': self.Premium_items,
            'Character/info': self.Character_info,
            'Map/villageDetails': self.Map_villageDetails,
            'Overview/commands': self.Overview_commands,
            'System/time': self.System_time,
            'System/error': self.System_error,
            'Map/villageData': self.Map_villageData,
            'Command/sent': self.Command_sent,
        }

    # Bypass
    async def System_welcome(self, **kwargs):
        await self.ws.send(produceMessage(self, 'Authentication/login', {'name': self.session.sUsername, "pass": self.session.sPassword}))

        return False

    # Bypass
    async def Login_success(self, **kwargs):
        self.session.sId = str(self.oRcv['data']['player_id'])
        self.session.sWorldId = self.oRcv['data']['characters'][0]['world_id']
        await self.ws.send(produceMessage(self, 'Authentication/selectCharacter', {"id": self.session.sId, 'world_id':self.session.sWorldId}))

        return False

    # Bypass
    async def Authentication_characterSelected(self, **kwargs):
        await self.ws.send(produceMessage(self, "Premium/listItems"))

        return False

    # Popula o inventário
    async def Premium_items(self, **kwargs):
        self.session.lInventory = self.oRcv['data']['inventory']
        await self.ws.send(produceMessage(self, 'Character/getInfo', sMore=',"data":{}'))

        return False

    # Popula a lista de vilas
    async def Character_info(self, **kwargs):
        self.session.lVillagesPlayer = self.oRcv['data']['villages']

        for village in self.session.lVillagesPlayer:
            village['lBarb'] = []
            village['lAtqs'] = []
            village['lUnits'] = {}
            await self.ws.send(produceMessage(self, 'Map/getVillageDetails', {'village_id': str(village['id']), 'my_village_id': str(village['id']),'num_reports':5}))
        
        await self.ws.send(produceMessage(self, 'System/getTime', sMore=',"data":{}'))
        return False

    # Popula as unidades de combate
    async def Map_villageDetails(self, **kwargs):
        for village in self.session.lVillagesPlayer:
            if self.oRcv['data']['village_id'] == village['id']:
                for (key, value) in sorted(self.oRcv['data']['units'].items(), key=lambda k: k[1]):
                    if value != 0:
                        village['lUnits'][key] = value
                village['qntAtaques'] = len(self.oRcv['data']['commands']['own'])

                await self.ws.send(produceMessage(self, 'Overview/getCommands', {"count":25,"offset":0,"sorting":"origin_village_name","reverse":0,"groups":[],"directions":["forward","back"],"command_types":["attack"],"villages":[str(village['id'])]}))
                if village['qntAtaques'] > 25:
                    await self.ws.send(produceMessage(self, 'Overview/getCommands', {"count":25,"offset":25,"sorting":"origin_village_name","reverse":0,"groups":[],"directions":["forward","back"],"command_types":["attack"],"villages":[str(village['id'])]}))
        
        return False

    # Popula os ataques atuais de cada vila                
    async def Overview_commands(self, **kwargs):
        if self.oRcv['data']['total'] > 0:
            for village in self.session.lVillagesPlayer:
                if self.oRcv['data']['commands'][0]['origin_village_id'] == village['id']:
                    for command in self.oRcv['data']['commands']:
                        units = {}

                        for unit in lUnits:
                            if command[unit] > 0:
                                units[unit] = command[unit]

                        village['lAtqs'].append({'units':units,
                                                    'id_vil': command['origin_village_id'],
                                                    'id_barb': command['target_village_id'],
                                                    'time_completed': command['time_completed'],
                                                    'time': (command['time_completed'] - command['time_start'])
                                                })

                    village['lAtqs'] = sorted(village['lAtqs'], key=lambda k: k['time_completed'])

        return False

    # Popula a lista de vilas bárbaras para cada vila que o usuário com a distância da vila para a dos bárbaros
    async def Map_villageData(self, **kwargs):
        for bvillage in self.oRcv['data']['villages']:
            if bvillage['name'] == 'Aldeia Bárbara':
                for pVillage in self.session.lVillagesPlayer:
                    pVillage['lBarb'].append({'id':bvillage['id'], 'dist':abs(bvillage['x'] - pVillage['x']) + abs(bvillage['y'] - pVillage['y'])})
        return True

    # Atualiza a lista de comandos
    async def Command_sent(self, **kwargs):
        village = kwargs.get('village')
        units = kwargs.get('units')
        village['lAtqs'].append({
            'units':units,
            'id_vil': self.oRcv['data']['origin']['id'],
            'id_barb': self.oRcv['data']['target']['id'],
            'time_completed': self.oRcv['data']['time_completed'],
            'time': (self.oRcv['data']['time_completed'] - self.oRcv['data']['time_start']),
        })

        return True

    # ByPass
    async def System_time(self, **kwargs):
        self.session.iActualTime = self.oRcv["data"]["time"]

        return True

    # SystemError
    async def System_error(self, **kwargs):
        self.session.bLogged = False
        
        return True

    async def RequestHandler(self, **kwargs):      
        async for msgServer in self.ws:
            try:
                if 'type' in msgServer:
                    self.oRcv = getJsonFromMsg(msgServer)
                    if await self.MsgsCall[self.oRcv['type']](**kwargs):
                        break
            except Exception as e:
                pass
                #print(e)