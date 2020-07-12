import asyncio
import websockets
from time import sleep
import json

async def login_client():
   url = "wss://br.tribalwars2.com/socket.io/?platform=desktop&EIO=3&transport=websocket"

   async with websockets.connect(url) as ws:
      #login
      username = 'fslucasfs'
      password = '123456abc'
      login = '42["msg",{"type":"Authentication/login","data":{"name":"' + username + '","pass":"' + password + '"},"id":2,"headers":{"traveltimes":[["browser_send"]]}}]'
      
      await ws.send(login)

      async for response in ws:
         print(response)
         try:
            objr = json.loads(response[response.find('{'):response.rfind('}')+1])
         except Exception:
            pass

         if 'Login/success' == response[25:38]:
            player_id = str(objr['data']['player_id'])
            world_id  = 0
            while world_id not in ['1','2','3','4','5','6']:
               world_id = input('Logado com sucesso\nEm qual mundo deseja entrar?\n1.Queen\'s Sconce\n2.Rupea\n3.Tzschocha\n4.Uhrovec\n5.Visegrád\n6.Warkworth Castle\n>')

            if world_id == '1':
               world_id = 'br43'
            elif world_id == '2':
               world_id = 'br44'
            elif world_id == '3':
               world_id = 'br46'
            elif world_id == '4':
               world_id = 'br47'
            elif world_id == '5':
               world_id = 'br48'
            elif world_id == '6':
               world_id = 'br49'

            await ws.send('42["msg",{"type":"Authentication/selectCharacter","data":{"id":'+player_id+',"world_id":"'+ world_id +'"},"id":5,"headers":{"traveltimes":[["browser_send",1594533012021]]}}]')
            loop.close()

if __name__ == "__main__":
   try:
      loop = asyncio.get_event_loop()
      loop.run_until_complete(login_client())
      loop.run_until_complete(auth())


   except Exception as e:
      print(e)
   finally:
      loop.close()