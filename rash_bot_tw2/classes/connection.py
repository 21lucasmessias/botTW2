class Connection:
   def __init__(self, iHeaderId, bLogged, bAuth, bLogOff):
      self.iHeaderId = iHeaderId
      self.bLogged   = bLogged
      self.bLogOff   = bLogOff

   def getHeaders(self, iHeaderId):
      self.iHeaderId = self.iHeaderId + 1
      return ',"id":' + str(self.iHeaderId) + ',"headers":{"traveltimes":[["browser_send"]]}}]'