class Item:
    def __init__(self, name, quantity):
        self.name = name
        self.quantity = quantity

class Bag:
    def __init__(self, generalItems, keyItems, TMHM, mail, medecine, berries, balls, battleItems):
        self.generalItems = [Item(**jsonItem) for jsonItem in generalItems]
        self.keyItems = [Item(**jsonItem) for jsonItem in keyItems]
        self.TMHM = [Item(**jsonItem) for jsonItem in TMHM]
        self.mail = [Item(**jsonItem) for jsonItem in mail]
        self.medecine = [Item(**jsonItem) for jsonItem in medecine]
        self.berries = [Item(**jsonItem) for jsonItem in berries]
        self.balls = [Item(**jsonItem) for jsonItem in balls]
        self.battleItems = [Item(**jsonItem) for jsonItem in battleItems]