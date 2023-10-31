
from pokemon import Pokemon
from utils import isShiny

import io
import json
import mmap

import img
import joypad

loadedPokemonPid = 0
pokemon = 0
        
while True:
    mmapData = mmap.mmap(0, 4096, "pokemonData")
    pokemonData = io.BytesIO(mmapData).read().decode("utf-8").split("\x00")[0]

    if (pokemonData):
        jsonPokemonData = json.loads(pokemonData)["pokemonData"]

        if (jsonPokemonData["pid"] not in [0, loadedPokemonPid]):
            pokemon = Pokemon(**jsonPokemonData)
            loadedPokemonPid = pokemon.pid

            print("New wild Pokemon !")
            print(pokemon)

    # Check input already sent
    joypadInput = joypad.readInput()

    # Only apply new input if no input is found in memory
    if (len(joypadInput) == 0):
        screenshot = img.getScreenshot()

        if (img.isTrainerFacingLeft(screenshot)):
            joypad.writeInput("uuuuu@@@@@") # Input up for 5 frames and release for 5 frames
        elif (img.isTrainerFacingRight(screenshot)):
            joypad.writeInput("ddddd@@@@@") # Input down for 5 frames and release for 5 frames
        elif (img.isTrainerFacingDown(screenshot)):
            joypad.writeInput("lllll@@@@@") # Input left for 5 frames and release for 5 frames
        elif (img.isTrainerFacingUp(screenshot)):
            joypad.writeInput("rrrrr@@@@@") # Input right for 5 frames and release for 5 frames
        elif (img.isBattleTouchscreenAvailable(screenshot)):
            joypad.writeInput("BBBBB@@@@@") # Mash B to skip dialogue
        elif (isShiny(pokemon)):
            pass # TODO : Catch Pokemon
        elif (img.isRunAwayAvailable(screenshot)):
            joypad.writeInput("lllll@@@@@lllll@@@@@rrrrr@@@@@AAAAA@@@@@") # Runaway sequence