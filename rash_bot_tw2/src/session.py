class Session:
    def __init__(self, sUsername='fslucasfs', sPassword = '123456abc', sId = '', sWorldId = '', iHeaderId = 0, bLogged = False, bLogOff = False):
        self.sUsername = 'fslucasfs'
        self.sPassword = '123456abc'
        self.bLogged = True
        self.sId = ''
        self.sWorldId = ''
        self.iHeaderId = 0

        self.bAutomatic = False
        self.lVillagesPlayer = []
        self.aux = 0
        self.lVillagesBarbarians = []
        self.lInventory = []
        self.idToWorld = {
            '1': 'br43',
            '2': 'br44',
            '3': 'br46',
            '4': 'br47',
            '5': 'br48',
            '6': 'br49',
        }