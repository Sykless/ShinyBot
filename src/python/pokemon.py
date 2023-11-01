from utils import formatNumber
from utils import getShinyValue

class Move:
    def __init__(self, name, PP, PPUp):
        self.name = name
        self.PP = PP
        self.PPUp = PPUp

class Contest:
    def __init__(self, cool, beauty, cute, smart, tough, sheen):
        self.cool = cool
        self.cool = beauty
        self.cool = cute
        self.cool = smart
        self.cool = tough
        self.cool = sheen

class Met:
    def __init__(self, level, date, location, dateEggReceived, locationEggReceived):
        self.level = level
        self.date = date
        self.location = location
        self.dateEggReceived = dateEggReceived
        self.locationEggReceived = locationEggReceived

class Trainer:
    def __init__(self, ID, secretID, name, female):
        self.ID = ID
        self.secretID = secretID
        self.name = name
        self.female = female

class Ribbons:
    def __init__(self, sinnohRibbon1, sinnohRibbon2, sinnohRibbon3, sinnohRibbon4, hoennRibbon1, hoennRibbon2):
        self.sinnohRibbon1 = sinnohRibbon1
        self.sinnohRibbon2 = sinnohRibbon2
        self.sinnohRibbon3 = sinnohRibbon3
        self.sinnohRibbon4 = sinnohRibbon4
        self.hoennRibbon1 = hoennRibbon1
        self.hoennRibbon2 = hoennRibbon2

class Stats:
    def __init__(self, HP, attack, defense, speed, specialAttack, specialDefense):
        self.HP = HP
        self.attack = attack
        self.defense = defense
        self.speed = speed
        self.specialAttack = specialAttack
        self.specialDefense = specialDefense

    def __str__(self):
        statsString = ("HP : " + str(self.HP)
                + " - ATQ : " + str(self.attack)
                + " - DEF : " + str(self.defense)
                + " - SPA : " + str(self.specialAttack)
                + " - SPD : " + str(self.specialDefense)
                + " - SPE : " + str(self.speed))
        return statsString

class Status:
    def __init__(self, poisoned, paralyzed, toxic, asleep, frozen, burned):
        self.poisoned = poisoned
        self.paralyzed = paralyzed
        self.toxic = toxic
        self.asleep = asleep
        self.frozen = frozen
        self.burned = burned 

class Pokemon:

    def __init__(self):
        self.pid = 0

        self.pokedexID = 0
        self.name = None
        self.level = 0
        self.moves = []
        self.ability = None
        self.item = None
        self.currentHP = 0
        self.stats = None
        self.IV = None
        self.EV = None
        self.experience = 0
        self.status = None

        self.OT = None
        self.met = None
        self.nicknamed = False
        self.nickname = None
        self.isEgg = False
        self.pokeball = None
        self.female = False
        self.genderless = False
        self.friendship = 0
        self.pokerus = 0
        self.alternateForms = 0
        self.originalLanguage = None
        self.originGame = None

        self.ribbons = None
        self.contest = None
        self.markings = 0
        self.capsule = 0
        self.sealCoordinates = 0

        self.shinyValue = 0
        self.isShiny = False

    def __init__(self, experience = None, ribbons = None, stats = None, sealCoordinates = None, currentHP = None, moves = None, met = None,
                 alternateForms = None, pokedexID = None, IV = None, OT = None, status = None, level = None, EV = None, pokeball = None,
                 contest = None, female = None, pokerus = None, originalLanguage = None, markings = None, nickname = None, capsule = None,
                 genderless = None, originGame = None, nicknamed = None, item = None, pid = None, friendship = None, name = None, ability = None,
                 isEgg = None):
        
        # Allow empty Pokemon creation if pid is None
        if (pid != None):
            self.pid = pid

            self.pokedexID = pokedexID
            self.name = name
            self.level = level
            self.moves = [Move(**jsonMove) for jsonMove in moves]
            self.ability = ability
            self.item = item
            self.currentHP = currentHP
            self.stats = Stats(**stats)
            self.IV = Stats(**IV)
            self.EV = Stats(**EV)
            self.experience = experience
            self.status = Status(**status)

            self.OT = Trainer(**OT)
            self.met = Met(**met)
            self.nicknamed = nicknamed
            self.nickname = nickname
            self.isEgg = isEgg
            self.pokeball = pokeball
            self.female = female
            self.genderless = genderless
            self.friendship = friendship
            self.pokerus = pokerus
            self.alternateForms = alternateForms
            self.originalLanguage = originalLanguage
            self.originGame = originGame

            self.ribbons = Ribbons(**ribbons)
            self.contest = Contest(**contest)
            self.markings = markings
            self.capsule = capsule
            self.sealCoordinates = sealCoordinates

            self.shinyValue = getShinyValue(pid, self.OT.ID, self.OT.secretID)
        
        # Pokemon not shiny by default if pid is None
        self.isShiny = pid != None and self.shinyValue < 255

    def __str__(self):
        return (str(self.name) + " " + ("♀" if self.female else "♂")
                + " level " + str(self.level) + " (" + self.ability + ")" + " - PID = " + str(hex(self.pid)) + " - Shiny value : " + str(self.shinyValue)  + "\n"
                + " - " + self.moves[0].name + " (" + str(self.moves[0].PP) + ")\n"
                + (" - " + self.moves[1].name + " (" + str(self.moves[1].PP) + ")\n" if len(self.moves) == 2 else "")
                + (" - " + self.moves[2].name + " (" + str(self.moves[2].PP) + ")\n" if len(self.moves) == 3 else "")
                + (" - " + self.moves[3].name + " (" + str(self.moves[3].PP) + ")\n" if len(self.moves) == 4 else "")
                + "\n"
                + " =============================================\n"
                + " =       =  HP = ATQ = DEF = SPA = SPD = SPE =\n"
                + " =============================================\n"
                + " = STATS = " + formatNumber(self.stats.HP) + " = " + formatNumber(self.stats.attack) + " = " + formatNumber(self.stats.defense) + " = " + formatNumber(self.stats.specialAttack) + " = " + formatNumber(self.stats.specialDefense) + " = " + formatNumber(self.stats.speed) + " =\n"
                + " =============================================\n"
                + " = IV    = " + formatNumber(self.IV.HP) + " = " + formatNumber(self.IV.attack) + " = " + formatNumber(self.IV.defense) + " = " + formatNumber(self.IV.specialAttack) + " = " + formatNumber(self.IV.specialDefense) + " = " + formatNumber(self.IV.speed) + " =\n"
                + " =============================================\n"
                + " = EV    = " + formatNumber(self.EV.HP) + " = " + formatNumber(self.EV.attack) + " = " + formatNumber(self.EV.defense) + " = " + formatNumber(self.EV.specialAttack) + " = " + formatNumber(self.EV.specialDefense) + " = " + formatNumber(self.EV.speed) + " =\n"
                + " =============================================\n")