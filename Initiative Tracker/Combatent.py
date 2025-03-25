class Combatent:
    def __init__(self, initiative, dex, pName, isPlayer, health, ac, saveDC):
        self.initiative = initiative
        self.dex = dex
        self.pName = pName
        self.isPlayer = isPlayer
        self.health = health
        self.ac = ac
        self.saveDC = saveDC

    def setInitiative(self, initiative):
        self.initiative = initiative
    
    def setAC(self, ac):
        self.ac = ac