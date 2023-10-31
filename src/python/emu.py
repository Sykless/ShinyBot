
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

        # Overworld : spin mode
        if (img.isPoketchAvailable(screenshot)):
            # Facing left : Input up for 5 frames and release for 5 frames
        if (img.isTrainerFacingLeft(screenshot)):
                joypad.writeInput("uuuuu@@@@@")

            # Facing right : Input down for 5 frames and release for 5 frames
        elif (img.isTrainerFacingRight(screenshot)):
                joypad.writeInput("ddddd@@@@@")

            # Facing down : Input left for 5 frames and release for 5 frames
        elif (img.isTrainerFacingDown(screenshot)):
                joypad.writeInput("lllll@@@@@")

            # Facing up : Input right for 5 frames and release for 5 frames
        elif (img.isTrainerFacingUp(screenshot)):
                joypad.writeInput("rrrrr@@@@@")

        # Battle screen at beginning/end : Mash B to skip dialogue
        elif (img.isBattleTouchscreenAvailable(screenshot)):
            joypad.writeInput("BBBBB@@@@@")

        # Shiny Pokemon : Catch sequence
        elif (isShiny(pokemon)):
            pass # TODO : Catch Pokemon

        # Runaway button displayed : Runaway sequence
        elif (img.isRunAwayAvailable(screenshot)):
            joypad.writeInput("lllll@@@@@lllll@@@@@rrrrr@@@@@AAAAA@@@@@")