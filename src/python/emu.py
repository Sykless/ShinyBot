
from pokemon import Pokemon
from trainer import Position

import time

import img
import utils
import joypad
import memory

LEFT_ROW = 0
RIGHT_ROW = 1
FIRST_LINE = 0
MENU_LINE = 3

NEXT_PAGE_BUTTON = 0
PREVIOUS_PAGE_BUTTON = 1
CANCEL_BUTTON = 2

screenshotMode = False
freeMode = True
catchAllMode = False

pokemon = Pokemon()
loadedPokemonPid = 0
pokeballLocation = -1

mapFile = open('src/python/data/platinumMap.map')
map = mapFile.readlines()

while True:
    # Read JSON Pokemon data from memory file
    jsonPokemonData = memory.readPokemonData()

    # Check if a new wild Pokemon has been found
    if (jsonPokemonData and jsonPokemonData["pid"] not in [0, loadedPokemonPid]):
        # Convert JSON data to Pokemon object
        pokemon = Pokemon(**jsonPokemonData)
        loadedPokemonPid = pokemon.pid

        print("New wild Pokemon !")
        print(pokemon)

    # Check input previsouy saved
    joypadInput = memory.readJoypadData()

    # Debug screenshot mode : only save the screenshot
    if (freeMode):
        screenshot = img.getScreenshot()
        playerPosition = Position(**memory.readPositionData())

    # Only apply new input if no input is found in memory
    elif (len(joypadInput) == 0):
        screenshot = img.getScreenshot()
        playerPosition = Position(**memory.readPositionData())
        
        # Overworld : spin mode
        if (img.poketch.isOnScreen(screenshot)):
            playerDirection = img.getPlayerPosition(screenshot)

            # Facing left : Input up for 5 frames and release for 5 frames
            if (playerDirection == "l"):
                joypad.writeInput("u")

            # Facing right : Input down for 5 frames and release for 5 frames
            elif (playerDirection == "r"):
                joypad.writeInput("d")

            # Facing down : Input left for 5 frames and release for 5 frames
            elif (playerDirection == "d"):
                joypad.writeInput("l")

            # Facing up : Input right for 5 frames and release for 5 frames
            elif (playerDirection == "u"):
                joypad.writeInput("r")

        # New Pokedex entry : Press A
        elif (img.newPokedexEntry.isOnScreen(screenshot)):
            joypad.writeInput("A")

        # Screen during battle dialogue : Mash B to skip dialogue
        elif (img.battleTouchscreen.isOnScreen(screenshot)):
            joypad.writeInput("B")

        # Runaway button displayed : Runaway or catch Pokemon
        # TODO : Weaken Pokemon (False Swipe + Status ?)
        elif (img.runaway.isOnScreen(screenshot)):
            # Shiny Pokemon : Go to bag sequence
            if (pokemon.isShiny or catchAllMode):
                joypad.writeInput("llA", endSequence = "@@@@@@@@@@")
            
            # Not Shiny : Runaway sequence
            else:
                joypad.writeInput("llrA", endSequence = "@@@@@@@@@@")

        # Inside bag : Go to Balls sequence
        elif (img.insideBag.isOnScreen(screenshot)):
            # Get cursor location (None if not present)
            cursorLocation = img.getCurrentBagSectionSelectedPosition(screenshot)

            # No cursor on screen : input left to make it appear
            if (not cursorLocation):
                joypad.writeInput("l")
            else:
                selectSectionSequence = ""

                # Go to last used item
                if (img.pokeballLastUsed.isOnScreen(screenshot)):

                    # Press left if cursor is on the right row
                    selectSectionSequence += "l" * cursorLocation[0]

                    # Go down enough times to go on the menu line
                    selectSectionSequence += "d" * (2 - cursorLocation[1])
                    
                # Go to Balls menu
                else:
                    # Go up enough times to go on the first line
                    selectSectionSequence += "u" * cursorLocation[1]

                    # Press right if cursor is on the left row
                    selectSectionSequence += "r" * (1 - cursorLocation[0])

                # Wait 10 more frames after A press since press animation
                # loops back to default screen just before transitioning
                selectSectionSequence += "A"
                joypad.writeInput(selectSectionSequence, endSequence = "@@@@@@@@@@")

        elif (img.insideBalls.isOnScreen(screenshot)):
            # Get Poké Ball location in bag
            pokeballLocation = utils.getPokeballLocation()

            # I'd rather crash than miss a Shiny
            if (pokeballLocation == -1):
                raise Exception('No Poké Ball available !')

            # Get cursor location (None if not present)
            cursorLocation = img.getCurrentItemSelectedPosition(screenshot)

            # No cursor on screen : input left to make it appear
            if (not cursorLocation):
                joypad.writeInput("l")
            else:
                pageNuber = img.getPageNumber(screenshot)
                pokeballPageLocation = int(pokeballLocation / 6) + 1

                if (pageNuber):
                    # Input Use Poké Ball sequence depending on the position in the bag
                    itemNavigationSequence = ""

                    # Check if Poké Ball are displayed on this page
                    if (pageNuber == pokeballPageLocation):

                        # If cursor is on a menu button, press up to set it on position (0,2)
                        if (cursorLocation[1] == MENU_LINE):
                            itemNavigationSequence += "u"
                            cursorLocation = [LEFT_ROW, 2]
                        
                        # Only press right if cursor is on left row and Pokéball is on right row
                        if (cursorLocation[0] == LEFT_ROW and pokeballLocation % 2 == RIGHT_ROW):
                            itemNavigationSequence += "r"

                        # Press up or down depending on the cursor and Pokéball position
                        cursorDifferential = cursorLocation[1] - int(pokeballLocation / 2)

                        if (cursorDifferential < 0):
                            itemNavigationSequence += "d" * (cursorDifferential * -1)
                        elif (cursorDifferential > 0):
                            itemNavigationSequence += "u" * cursorDifferential

                    # Poké Ball are on a different page, navigate to menu button
                    else:
                        # Only reason to use "Previous page" button is
                        # we're currently on page 3 and want to go back to page 1
                        previousPagePress = pageNuber - pokeballPageLocation == 2

                        # Cursor is on an item
                        if (cursorLocation[1] < MENU_LINE):
                            # If cursor in the right row, press left to go to left row
                            if (cursorLocation[0] == RIGHT_ROW):
                                itemNavigationSequence += "l"
                            
                            # Go down enough times to go to Menu line
                            itemNavigationSequence += "d" * (3 - cursorLocation[1])

                            # Default menu button might be "Previous page"
                            # so we press left to insure cursor is on "Next page"
                            itemNavigationSequence += "l"

                            # Now that we're sure of the cursor position, press right to go to "Previous page"
                            if (previousPagePress):
                                itemNavigationSequence += "r"

                        # Cursor in a menu button
                        else:
                            # If we want to press "Previous page" button, the input depends on the current position
                            if (previousPagePress):
                                if (cursorLocation[1] == CANCEL_BUTTON):
                                    itemNavigationSequence += "l"
                                elif (cursorLocation[1] == NEXT_PAGE_BUTTON):
                                    itemNavigationSequence += "r"
                            else:
                                # Press left enough times to be on "Next Page" button
                                itemNavigationSequence += "l" * cursorLocation[0]
                                
                    # Validate input and wait 10 more frames
                    itemNavigationSequence += "A"
                    joypad.writeInput(itemNavigationSequence, endSequence = "@@@@@@@@@@")
                else:
                    raise Exception('Inside Balls menu but no page number displayed ?')
                
        elif (img.useItem.isOnScreen(screenshot)):
            joypad.writeInput("AA", endSequence = "@@@@@")