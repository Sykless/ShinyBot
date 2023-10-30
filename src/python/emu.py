from pokemon import Pokemon
from utils import LoadJsonMmap

import img
    
# Parse JSON into an object with attributes corresponding to dict keys.

loadedPokemonPid = 0

while True:
    pokemon = Pokemon(**LoadJsonMmap(4096, "testfile")["pokemonData"])
    screenshot = img.getScreenshot()

    if (pokemon.pid != loadedPokemonPid):
        loadedPokemonPid = pokemon.pid

        print("New wild Pokemon !")
        print(pokemon)

    if (img.isFacingLeft(screenshot)):
        print("Facing left !") # TODO : Input up
    elif (img.isFacingRight(screenshot)):
        print("Facing right !") # TODO : Input down
    if (img.isFacingDown(screenshot)):
        print("Facing down !") # TODO : Input left
    elif (img.isFacingUp(screenshot)):
        print("Facing up !") # TODO : Input right

    # img.isTemplateInImage(screenshot, img.TRAINER_LEFT, 7000000)