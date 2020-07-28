import websockets
from time import sleep
import random
from rash_bot_tw2.src.utils import produceMessage, lUnits, getJsonFromMsg
from rash_bot_tw2.src.msgHandler import MessageHandler

class CustomWebsocket:
    def __init__(self, session):
        self._url = "wss://br.tribalwars2.com/socket.io/?platform=desktop&EIO=3&transport=websocket"
        self._ws = websockets.connect(self._url)
        self.session = session
        self.msgHandler = None

    async def tryLogin(self):
        async with self._ws as ws:
            self.msgHandler = MessageHandler(ws, self.session)
            await self.msgHandler.RequestHandler()

            if self.session.bLogged:
                print("Logado")
                await self.tryReadMap(ws)
                await self.userMenu(ws)
            else:
                print("Erro ao conectar.")

    async def userMenu(self, ws):
        option = 1 #int(input("Escolha uma ação:\n1. Atacar bárbaros\n2.Recolher recursos do depósito"))

        if option == 1:
            commands = int(input(f'Quantidade de ataques que deseja realizar:'))
            await self.tryAttackBarbarians(ws, commands)
            self.session.bAutomatic = True
            await self.tryAutoAttackBarbarians(ws)

        elif option == 2:
            if(str(input('Deseja continuar rodando no modo ataque automático?')) == 's'):
                self.session.bAutomatic = True
                await self.tryAutoAttackBarbarians(ws)
    
    # Le o mapa e absorve informações
    async def tryReadMap(self, ws):
        for x in range(self.session.lVillagesPlayer[0]['x']-25, self.session.lVillagesPlayer[0]['x']+25, 25):
            for y in range(self.session.lVillagesPlayer[0]['y']-25, self.session.lVillagesPlayer[0]['y']+25, 25):
                await ws.send(produceMessage(self, 'Map/getVillagesByArea', {"x":str(x),"y":str(y),"width":25,"height":25}))
                await self.msgHandler.RequestHandler()

        self.sortBarbarians()

    # Organiza para as vilas mais proximas ficarem por primeiro   
    def sortBarbarians(self):
        for village in self.session.lVillagesPlayer:
            village['lBarb'] = sorted(village['lBarb'], key=lambda k: k['dist'])

    # Envia as tropas
    async def tryAttackBarbarians(self, ws, commands):
        for village in self.session.lVillagesPlayer:
            if (commands + village['qntAtaques']) > 50:
                commands = 50 - village['qntAtaques']

            if commands == 0:
                break

            village['qntAtaques'] = village['qntAtaques'] + commands

            # Divide as unidades de ataque
            lVillageUnits = village['lUnits'].copy()
            firstAttackUnits = {}
            for unit, qnt in lVillageUnits.items():
                if qnt >= commands:
                    firstAttackUnits[unit] = int(qnt/commands) + (qnt % commands)
                else:
                    firstAttackUnits[unit] = qnt
                    village['lUnits'].pop(unit)
            
            defaultAttackUnits = {}
            for unit, qnt in village['lUnits'].items():
                defaultAttackUnits[unit] = int(qnt/commands)
                        
            for i in range(0, commands):
                if i == 0 and firstAttackUnits:
                    await ws.send(produceMessage(self, 'Command/sendCustomArmy', {"start_village":village['id'],"target_village":village['lBarb'][i]['id'],"type":"attack","units":firstAttackUnits,"icon":0,"officers":{},"catapult_target":"headquarter"}))
                    await ws.send('2')
                    await self.msgHandler.RequestHandler()
                elif defaultAttackUnits:
                    await ws.send(produceMessage(self, 'Command/sendCustomArmy', {"start_village":village['id'],"target_village":village['lBarb'][i]['id'],"type":"attack","units":defaultAttackUnits,"icon":0,"officers":{},"catapult_target":"headquarter"}))
                    await ws.send('2')
                    await self.msgHandler.RequestHandler()

        print("Tropas enviadas com sucesso!")

    async def tryAutoAttackBarbarians(self, ws):
        while True:
            await ws.send('2')
            await self.msgHandler.RequestHandler()
            sleep(random.randrange(7,12))
