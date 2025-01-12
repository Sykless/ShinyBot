from utils import formatNumber
from utils import getShinyValue
from bag import Item

import data
import memory

FLY_ID = 19
DIG_ID = 91
DEFOG_ID = 432

class Move:
    def __init__(self, id, PP, PPUp):
        self.id = id
        self.name = data.MOVE_NAMES[id]
        self.PP = PP
        self.PPUp = PPUp
    
    def isHM(self):
            return self.id in HM_LIST

class Ability:
    def __init__(self, id):
        self.id = id
        self.name = data.ABILITY_LIST[id]

class Nature:
    def __init__(self, id):
        self.id = id
        self.name = data.NATURE_LIST[id]

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
    def __init__(self, experience = None, ribbons = None, stats = None, sealCoordinates = None, currentHP = None, moves = None, met = None,
                 alternateForms = None, pokedexId = None, IV = None, OT = None, status = None, level = None, EV = None, pokeballId = None,
                 contest = None, female = None, pokerus = None, originalLanguage = None, markings = None, nickname = None, capsule = None,
                 genderless = None, originGame = None, nicknamed = None, item = None, pid = None, friendship = None, abilityId = None,
                 isEgg = None):

        try:
            self.pid = pid
            self.pokedexId = pokedexId
            self.name = data.POKEMON_NAMES[pokedexId]
            self.level = level
            self.moves = [Move(**jsonMove) for jsonMove in moves]
            self.ability = Ability(abilityId)
            self.nature = Nature(pid % 25)
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
            self.pokeball = Item(pokeballId,1)
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
            self.isShiny = self.shinyValue < 255

            self.isValid = True

        # We might receive invalid data since team memory address is shared with other parameters when you're not in battle/menu
        except IndexError:
            self.isValid = False

    def __eq__(self, other):
        return isinstance(other, Pokemon) and self.isValid and other.isValid and self.pid == other.pid
        
    def __str__(self):
        return (str(self.name) + " " + ("♀" if self.female else "♂")
                + " level " + str(self.level) + " (" + self.ability.name + " - " + self.nature.name + ")" + " - PID = " + str(hex(self.pid)) + " - Shiny value : " + str(self.shinyValue)  + "\n"
                + " - " + self.moves[0].name + " (" + str(self.moves[0].PP) + ")\n"
                + (" - " + self.moves[1].name + " (" + str(self.moves[1].PP) + ")\n" if len(self.moves) >= 2 else "")
                + (" - " + self.moves[2].name + " (" + str(self.moves[2].PP) + ")\n" if len(self.moves) >= 3 else "")
                + (" - " + self.moves[3].name + " (" + str(self.moves[3].PP) + ")\n" if len(self.moves) >= 4 else "")
                + "\n"
                + " =============================================\n"
                + " =       =  HP = ATQ = DEF = SPA = SPD = SPE =\n"
                + " =============================================\n"
                + " = STATS = " + formatNumber(self.stats.HP) + " = " + formatNumber(self.stats.attack) + " = " + formatNumber(self.stats.defense) + " = " + formatNumber(self.stats.specialAttack) + " = " + formatNumber(self.stats.specialDefense) + " = " + formatNumber(self.stats.speed) + " =\n"
                + " =============================================\n"
                + " = IV    = " + formatNumber(self.IV.HP) + " = " + formatNumber(self.IV.attack) + " = " + formatNumber(self.IV.defense) + " = " + formatNumber(self.IV.specialAttack) + " = " + formatNumber(self.IV.specialDefense) + " = " + formatNumber(self.IV.speed) + " =\n"
                + " =============================================\n"
                + " = EV    = " + formatNumber(self.EV.HP) + " = " + formatNumber(self.EV.attack) + " = " + formatNumber(self.EV.defense) + " = " + formatNumber(self.EV.specialAttack) + " = " + formatNumber(self.EV.specialDefense) + " = " + formatNumber(self.EV.speed) + " =\n"
                + " =============================================\n") if hasattr(self, 'name') else ("Unknown Pokémon : " + str(self.pokedexId))
    
    def __repr__(self):
        return str(self.nickname + " - " + self.name + " level " + str(self.level) + " (" + str(hex(self.pid)).upper().replace("X","x") + ")\n")

def getPokemonTeam():
    pokemonTeam = []
    jsonTeamData = memory.readPokemonTeamData()

    for jsonPokemon in jsonTeamData:
        pokemonTeam.append(Pokemon(**jsonPokemon))

    return pokemonTeam


def isHMAvailable(hmId):
    jsonTeamData = memory.readPokemonTeamData()

    for pokemonPosition in range(len(jsonTeamData)):
        movePosition = 0
        pokemon = Pokemon(**jsonTeamData[pokemonPosition])

        if (pokemon.isValid):
            for move in pokemon.moves:
                if (move.isHM()):
                    movePosition += 1

                    # Return first pokemon with Fly available
                    if (move.id == hmId):
                        return [pokemonPosition, movePosition]
    
    # No Pokemon with Fly
    print("No Pokemon with HM " + data.MOVE_NAMES[hmId] + " !")
    return [None, None]

HM_LIST = [
    FLY_ID, # Vol
    DIG_ID, # Tunnel
    DEFOG_ID, # Anti-Brume
    15,  # Coupe
    29,  # Coup d'Boule
    57,  # Surf
    70,  # Force
    100, # Téléport
    127, # Cascade
    135, # E-Coque
    148, # Flash
    208, # Lait à Boire
    230, # Doux Parfum
    249, # Éclate-Roc
    250, # Siphon
    290, # Force Cachée
    291, # Plongée
    431, # Escalade
    448, # Babil
] 