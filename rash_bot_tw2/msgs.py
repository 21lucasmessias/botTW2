            if objr['type'] == 'Authentication/characterSelected':
               await ws.send('42["msg",{"type":"GameDataBatch/getGameData","id":4,"headers":{"traveltimes":[["browser_send"]]}}]')
               await ws.send('42["msg",{"type":"Group/getGroups","id":5,"headers":{"traveltimes":[["browser_send"]]}}]')

            elif objr['type'] == "Group/groups":
               await ws.send('42["msg",{"type":"Icon/getVillages","id":6,"headers":{"traveltimes":[["browser_send"]]}}]')

            elif objr['type'] == "Icon/villages":
               await ws.send('42["msg",{"type":"Premium/listItems","id":7,"headers":{"traveltimes":[["browser_send"]]}}]')

            elif objr['type'] == "Premium/items":
               await ws.send('42["msg",{"type":"GlobalInformation/getInfo","id":8,"headers":{"traveltimes":[["browser_send"]]}}]')

            elif objr['type'] == "GlobalInformation/info":
               await ws.send('42["msg",{"type":"Effect/getEffects","id":9,"headers":{"traveltimes":[["browser_send"]]}}]')

            elif objr['type'] == "Effect/effects":
               await ws.send('42["msg",{"type":"TribeInvitation/getOwnInvitations","id":10,"headers":{"traveltimes":[["browser_send"]]}}]')

            elif objr['type'] == "TribeInvitation/ownInvitations":
               await ws.send('42["msg",{"type":"WheelEvent/getEvent","id":11,"headers":{"traveltimes":[["browser_send"]]}}]')

            elif objr['type'] == "WheelEvent/event":
               await ws.send('42["msg",{"type":"Character/getColors","id":12,"headers":{"traveltimes":[["browser_send"]]}}]')

            elif objr['type'] == "Character/colors":
               await ws.send('42["msg",{"type":"Character/getInfo","data":{},"id":13,"headers":{"traveltimes":[["browser_send"]]}}]')
               await ws.send('42["msg",{"type":"System/getTime","data":{},"id":14,"headers":{"traveltimes":[["browser_send"]]}}]')

            elif objr['type'] == "System/time" and not bCompleteLogin:
               await ws.send('42["msg",{"type":"Notification/getNotifications","id":15,"headers":{"traveltimes":[["browser_send"]]}}]')
               await ws.send('42["msg",{"type":"DailyLoginBonus/getInfo","data":null,"id":16,"headers":{"traveltimes":[["browser_send"]]}}]')
               await ws.send('42["msg",{"type":"Quest/getQuestLines","id":17,"headers":{"traveltimes":[["browser_send"]]}}]')
               await ws.send('42["msg",{"type":"Map/getVillagesByArea","data":{"x":525,"y":500,"width":25,"height":25},"id":18,"headers":{"traveltimes":[["browser_send"]]}}]')
               await ws.send('42["msg",{"type":"System/startupTime","data":{"startup_time":5177,"platform":"browser","device":"Mozilla/5.0%20(Windows%20NT%2010.0;%20Win64;%20x64)%20AppleWebKit/537.36%20(KHTML,%20like%20Gecko)%20Chrome/83.0.4103.116%20Safari/537.36"},"id":19,"headers":{"traveltimes":[["browser_send"]]}}]')
               await ws.send('42["msg",{"type":"InvitePlayer/getInfo","id":20,"headers":{"traveltimes":[["browser_send"]]}}]')
               await ws.send('42["msg",{"type":"Authentication/completeLogin","data":{},"id":21,"headers":{"traveltimes":[["browser_send"]]}}]')
               bCompleteLogin = True
            
            elif objr['type'] == "Quest/questLines":
               await ws.send('42["msg",{"type":"Crm/getInterstitials","data":{"device_type":"desktop"},"id":22,"headers":{"traveltimes":[["browser_send"]]}}]')
               await ws.send('42["msg",{"type":"VillageBatch/getVillageData","data":{"village_ids":[1072]},"id":23,"headers":{"traveltimes":[["browser_send"]]}}]')
               await ws.send('42["msg",{"type":"Map/getVillagesByArea","data":{"x":525,"y":475,"width":25,"height":25},"id":24,"headers":{"traveltimes":[["browser_send"]]}}]')

            elif objr['type'] == "Crm/interstitials":
               await ws.send('42["msg",{"type":"SecondVillage/getInfo","data":{},"id":25,"headers":{"traveltimes":[["browser_send"]]}}]')
               await ws.send('42["msg",{"type":"ResourceDeposit/getInfo","id":26,"headers":{"traveltimes":[["browser_send"]]}}]')

            elif objr['type'] == "ResourceDeposit/info":
               await ws.send('42["msg",{"type":"System/getTime","data":{},"id":27,"headers":{"traveltimes":[["browser_send"]]}}]')
     
            elif objr['type'] == "System/time":
               await ws.send('2')

            elif objr['type'] == "Authentication/logout":
               return True