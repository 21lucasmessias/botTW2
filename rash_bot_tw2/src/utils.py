import json

lUnits = ['spear', 'axe', 'sword', 'archer', 'light_cavalry', 'heavy_cavalry', 'mounted_archer', 'ram', 'catapult', 'knight', 'snob', 'trebuchet', 'doppelsoldner']

def produceMessage(self, sType, sData={}, sMore=''):
    self.session.iHeaderId += 1
    return ('42["msg",{"type":"' + sType + '"' + ((',"data":' + str(sData)) if sData else '') + sMore + ',"id":' + str(self.session.iHeaderId) + ',"headers":{"traveltimes":[["browser_send"]]}}]').replace(' ', '').replace("'", '"')


def getJsonFromMsg(msg):
    return json.loads(msg[msg.find('{'):msg.rfind('}')+1])