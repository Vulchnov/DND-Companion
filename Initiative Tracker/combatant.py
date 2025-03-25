class combatant:
    def __init__(self, initiative, dex, pName, isPlayer, health, ac, saveDC, connected):
        self.initiative = initiative
        self.dex = dex
        self.pName = pName
        self.isPlayer = isPlayer
        self.health = health
        self.ac = ac
        self.saveDC = saveDC
        self.connected = connected

    def setInitiative(self, initiative):
        self.initiative = initiative
    
    def setAC(self, ac):
        self.ac = ac