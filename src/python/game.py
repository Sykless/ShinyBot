import img
import bag
import memory

from encounter import SPECIALENCOUNTERS
from data import POKEMON_NAMES

CLOSEBAGMENU = 24

class Game:
    def __init__(self, hourOfDay, repelSteps, selectedBagSection, selectedBagItemId, swarmPokemon, marshPokemonList, gardenPokemonToday, gardenPokemonYesterday, gbaGame, encounterTables):
        self.hourOfDay = hourOfDay
        self.repelSteps = repelSteps
        self.selectedBagSection = None
        self.swarmPokemon = swarmPokemon
        self.marshPokemonList = [None] + marshPokemonList
        self.gardenPokemonToday = gardenPokemonToday
        self.gardenPokemonYesterday = gardenPokemonYesterday if gardenPokemonYesterday != 0xFFFF else None
        self.gbaGame = gbaGame
        self.encounterTables = encounterTables

        # Data only valid if in the bag menu
        if (0 <= selectedBagSection <= 7):
            self.selectedBagSection = selectedBagSection
            self.closeBag = False

            # Id 24 could be an item or the close menu button
            if (selectedBagItemId == CLOSEBAGMENU):
                if (selectedBagSection in [0,1]):
                    self.closeBag = img.closeBagMenuSelected.isOnScreen(img.getScreenshot())

                    # Regular itemId, get item from id
                    if (not self.closeBag):
                        self.selectedBagItem = bag.getItemFromBagId(selectedBagSection, selectedBagItemId)
                else:
                    self.closeBag = True

            # Retrieve item as usual
            else:
                self.selectedBagItem = bag.getItemFromBagId(selectedBagSection, selectedBagItemId)

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
                + "Swarm Pokémon : " + POKEMON_NAMES[SPECIALENCOUNTERS["swarm"][self.swarmPokemon]] + "\n"
                + "Garden Pokémon : Today : " + POKEMON_NAMES[SPECIALENCOUNTERS["garden"][self.gardenPokemonToday]] + (" - Yesterday : " + POKEMON_NAMES[SPECIALENCOUNTERS["garden"][self.gardenPokemonYesterday]] if self.gardenPokemonYesterday else "") + "\n"
                + "Marsh Pokémon : " + " - ".join("Zone " + str(zoneId) + " : " + POKEMON_NAMES[SPECIALENCOUNTERS["marsh"][self.marshPokemonList[zoneId]]] for zoneId in range(1,7)) + "\n"
                + "GBA Game : " + GBAGAME_NAMES[self.gbaGame])

def getGameData():
    return Game(**memory.readGameData())

GBAGAME_NAMES = ["None", "Saphir", "Rubis", "Émeraude", "Rouge Feu", "Vert Feuille"]