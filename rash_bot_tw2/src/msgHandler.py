from rash_bot_tw2.src.utils import produceMessage, lUnits, getJsonFromMsg
from time import sleep
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
            'Map/villageData': self.Map_villageData,
            'Command/returned': self.Command_returned,
        }

    # Bypass
    async def System_welcome(self):
        await self.ws.send(produceMessage(self, 'Authentication/login', {'name': self.session.sUsername, "pass": self.session.sPassword}))

    # Bypass
    async def Login_success(self):
        self.session.sId = str(self.oRcv['data']['player_id'])
        self.session.sWorldId = self.oRcv['data']['characters'][0]['world_id']
        await self.ws.send(produceMessage(self, 'Authentication/selectCharacter', {"id": self.session.sId, 'world_id':self.session.sWorldId}))

    # Bypass
    async def Authentication_characterSelected(self):
        await self.ws.send(produceMessage(self, "Premium/listItems"))

    # Popula o inventário
    async def Premium_items(self):
        self.session.lInventory = self.oRcv['data']['inventory']
        await self.ws.send(produceMessage(self, 'Character/getInfo', sMore=',"data":{}'))

    # Popula a lista de vilas
    async def Character_info(self):
        self.session.lVillagesPlayer = self.oRcv['data']['villages']
        

        for village in self.session.lVillagesPlayer:
            village['lBarb'] = []
            village['lUnits'] = {}
            await self.ws.send(produceMessage(self, 'Map/getVillageDetails', {'village_id': str(village['id']), 'my_village_id': str(village['id']),'num_reports':5}))
        
    # Popula as unidades de combate e armazena a quantia de ataques atuais
    async def Map_villageDetails(self):
        for village in self.session.lVillagesPlayer:
            if self.oRcv['data']['village_id'] == village['id']:
                village['qntAtaques'] = len(self.oRcv['data']['commands']['own'])

                for (key, value) in sorted(self.oRcv['data']['units'].items(), key=lambda k: k[1]):
                    if value != 0:
                        village['lUnits'][key] = value

        self.session.aux += 1
        if self.session.aux == len(self.session.lVillagesPlayer):
            await self.ws.send('2')

    # Popula a lista de vilas bárbaras para cada vila que o usuário com a distância da vila para a dos bárbaros
    async def Map_villageData(self):
        for bvillage in self.oRcv['data']['villages']:
            if bvillage['name'] == 'Aldeia Bárbara':
                for pVillage in self.session.lVillagesPlayer:
                    pVillage['lBarb'].append({'id':bvillage['id'], 'dist':abs(bvillage['x'] - pVillage['x']) + abs(bvillage['y'] - pVillage['y'])})

        await self.ws.send('2')

    async def Command_returned(self):
        if self.session.bAutomatic:
            await self.ws.send(produceMessage(self, 'Command/sendCustomArmy', {"start_village":self.oRcv['data']['origin']['id'],"target_village":self.oRcv['data']['target']['id'],"type":"attack","units":self.oRcv['data']['units'],"icon":0,"officers":{},"catapult_target":"headquarter"}))
            await self.ws.send('2')

    async def RequestHandler(self):      
        async for msgServer in self.ws:
            try:
                if 'type' in msgServer:
                    self.oRcv = getJsonFromMsg(msgServer)
                    await self.MsgsCall[self.oRcv['type']]()
                elif msgServer == '3':
                    break
            except Exception:
                pass
