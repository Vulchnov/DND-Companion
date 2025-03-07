class Combatent:
    def __init__(self, initiative, dex, pName, isPlayer, health):
        self.initiative = initiative
        self.dex = dex
        self.pName = pName
        self.isPlayer = isPlayer
        self.health = health

    def setInitiative(self, initiative):
        self.initiative = initiative