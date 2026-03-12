import img
import bag
import memory

from encounter import SPECIALGRASSENCOUNTERS
from data import POKEMON_NAMES, GBAGAME_NAMES
from zone import MONTCOURONNE_SALLE8, HONEYTREES_POSITIONS, Position, HoneyTree

FOG_WEATHER = 14
DARK_WEATHER = 16
CLOSEBAGMENU = 24
FEEBAS_ROCK_POSITIONS = [51, 56, 184, 203, 203, 203, 203, 203, 203, 203, 214, 214, 214,
                         214, 214, 214, 214, 225, 225, 225, 225, 225, 225, 225, 230, 230,
                         234, 234, 234, 234, 234, 234, 234, 239, 239, 243, 243, 243, 243,
                         243, 243, 243, 254, 254, 254, 254, 254, 254, 254, 265, 265, 265,
                         265, 265, 265, 265, 280, 280, 296, 296, 349, 349, 349, 364, 364,
                         364, 379, 379, 379, 409, 419, 419, 419, 434, 434, 434, 449, 449,
                         449, 455, 455, 471, 471, 477]

class Game:
    def __init__(self, hourOfDay, repelSteps, selectedBagSection, selectedBagItemId, registeredKeyItem, fogType, strengthUsed, feebasSeed, honeyTreesCountdown, swarmPokemon, marshPokemonList, gardenPokemonToday, gardenPokemonYesterday, gbaGame, encounterTables):
        self.hourOfDay = hourOfDay
        self.repelSteps = repelSteps
        self.selectedBagSection = None
        self.registeredKeyItem = registeredKeyItem
        self.isFoggy = fogType == FOG_WEATHER
        self.isDark = fogType == DARK_WEATHER
        self.strengthUsed = bool(strengthUsed)
        self.feebasSeed = feebasSeed
        self.honeyTreeList = []
        self.swarmPokemon = swarmPokemon
        self.marshPokemonList = marshPokemonList
        self.gardenPokemonToday = gardenPokemonToday
        self.gardenPokemonYesterday = gardenPokemonYesterday if gardenPokemonYesterday != 0xFFFF else None
        self.gbaGame = gbaGame
        self.encounterTables = encounterTables

        # Refresh every Honey Tree countdown
        for honeyTreeId in range(21):
            self.honeyTreeList.append(HoneyTree(HONEYTREES_POSITIONS[honeyTreeId], honeyTreesCountdown[honeyTreeId]))

        # Data only valid if in the bag menu
        if (0 <= selectedBagSection <= 7):
            self.selectedBagSection = selectedBagSection
            self.closeBag = False

            # Id 24 could be an item or the close menu button
            if (selectedBagItemId == CLOSEBAGMENU):
                if (selectedBagSection in [0,1]):
                    self.closeBag = img.closeBagMenuSelected.isOnScreen()

                    # Regular itemId, get item from id
                    if (not self.closeBag):
                        self.selectedBagItem = bag.getItemFromBagId(selectedBagSection, selectedBagItemId)
                else:
                    self.closeBag = True

            # Retrieve item as usual
            else:
                self.selectedBagItem = bag.getItemFromBagId(selectedBagSection, selectedBagItemId)

    def getFeebasTiles(self):
        feebasTiles = []

        # Find Feebas tiles from the Feebas seed, excluding rocks position
        for i in range(4):
            feebasPosition = (((self.feebasSeed >> (24 - 8*i)) & 0xff) % 0x84) + 0x84*i
            feedbasAdjustedPosition = feebasPosition + sum(1 for rockPosition in FEEBAS_ROCK_POSITIONS if rockPosition <= feebasPosition)
            
            # Convert position (0 -> 611) to Position object with X,Y coordinates
            feebasTiles.append(Position(9 + feedbasAdjustedPosition % 18, 18 + feedbasAdjustedPosition // 18, MONTCOURONNE_SALLE8))

        return feebasTiles

    def displayEncounters(self):
        for zoneType, encounterTable in self.encounterTables.items():
            print(zoneType)

            if (len(encounterTable) > 0):
                for encounterType, encounters in encounterTable.items():
                    print(encounterType)
                    print(encounters)

            print("\n\n")

    def __str__(self):
        return (str(self.repelSteps) + " repel steps remaining\n"
                + "Swarm Pokémon : " + POKEMON_NAMES[SPECIALGRASSENCOUNTERS["swarm"][self.swarmPokemon]] + "\n"
                + "Garden Pokémon : Today : " + POKEMON_NAMES[SPECIALGRASSENCOUNTERS["garden"][self.gardenPokemonToday]] + (" - Yesterday : " + POKEMON_NAMES[SPECIALGRASSENCOUNTERS["garden"][self.gardenPokemonYesterday]] if self.gardenPokemonYesterday else "") + "\n"
                + "Marsh Pokémon : " + " - ".join("Zone " + str(zoneId) + " : " + POKEMON_NAMES[SPECIALGRASSENCOUNTERS["marsh"][self.marshPokemonList[zoneId]]] for zoneId in range(6)) + "\n"
                + "GBA Game : " + GBAGAME_NAMES[self.gbaGame])

def getGameData():
    return Game(**memory.readGameData())