import img
import bag
import memory

from pokemon import POKEMON_NAMES

CLOSEBAGMENU = 24

class Game:
    def __init__(self, repelSteps, selectedBagSection, selectedBagItemId, swarmPokemon, marshPokemonList, gardenPokemonToday, gardenPokemonYesterday, gbaGame):
        self.repelSteps = repelSteps
        self.selectedBagSection = None
        self.swarmPokemon = swarmPokemon
        self.marshPokemonList = [None] + marshPokemonList
        self.gardenPokemonToday = gardenPokemonToday
        self.gardenPokemonYesterday = gardenPokemonYesterday
        self.gbaGame = gbaGame

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

    def __str__(self):
        return (str(self.repelSteps) + " repel steps remaining\n"
                + "Swarm Pokémon : " + POKEMON_NAMES[self.swarmPokemon] + "\n"
                + "Garden Pokémon : Today : " + POKEMON_NAMES[self.gardenPokemonToday] + (" - Yesterday : " + POKEMON_NAMES[self.gardenPokemonYesterday] if self.gardenPokemonYesterday else "") + "\n"
                + "Marsh Pokémon : " + " - ".join("Zone " + str(zoneId) + " : " + POKEMON_NAMES[self.marshPokemonList[zoneId]] for zoneId in range(1,7)) + "\n"
                + "GBA Game : " + GBAGAME_NAMES[self.gbaGame])

def getGameData():
    return Game(**memory.readGameData())

GBAGAME_NAMES = ["None", "Saphir", "Rubis", "Émeraude", "Rouge Feu", "Vert Feuille"]