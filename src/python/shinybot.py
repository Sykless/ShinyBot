
from utils import waitFrames
from pokemon import Pokemon
from dashboard import DASHBOARD
from emu import BIZHAWK, MELONDS, PLATINE

from threading import Thread
import time

import bag
import img
import zone
import game
import action
import player
import joypad
import memory
import pokemon
import pathfinding

LEFT_ROW = 0
RIGHT_ROW = 1
FIRST_LINE = 0
MENU_LINE = 3

NEXT_PAGE_BUTTON = 0
PREVIOUS_PAGE_BUTTON = 1
CANCEL_BUTTON = 2

BOT_MODE = True
FREE_MODE = True
SPIN_MODE = True
CATCH_ALL_MODE = False
GENERATE_GRAPH = False

def startShinybot(dashboardData = None):

    # If Dashboard is enabled
    if (dashboardData is not None):
        updateDashboardThread = Thread(target = updateDashboard, args = (dashboardData,), daemon = True)
        updateDashboardThread.start()

    # If Dashboard is not enabled, let this script launch BizHawk and setup the game
    else:
        BIZHAWK.initEmulator(PLATINE, fullscreen = False)
        action.loadGame()

    startTime = time.time()

    # Generate Door Graph that contains every door-to-door path in the map
    if (GENERATE_GRAPH):
        pathfinding.initDoorGraph()
        print("Graph generated in " + str(round(time.time() - startTime,2)) + " seconds")
    else:
        pathfinding.DOOR_GRAPH = memory.loadGraph('data/pkl/graph.pkl')
        print("Graph loaded in " + str(round(time.time() - startTime,2)) + " seconds")

    jsonPokemonData = memory.readWildPokemonData()
    jsonTeamData = memory.readPokemonTeamData()
    playerData = player.getPlayerData()
    gameData = game.getGameData()

    loadedPokemonPid = 0
    backToShop = True

    # Free mode : don't let the script interact with the game
    if (FREE_MODE and BOT_MODE):
        print("Free mode")

    # Bot mode : the script is controlling the game
    while BOT_MODE:
        # Don't check memory more than once a frame to avoid overloading the CPU
        waitFrames(1)

        # Read JSON Pokemon data from memory file
        jsonPokemonData = memory.readWildPokemonData()

        # Check if a new wild Pokemon has been found
        if (jsonPokemonData and jsonPokemonData["pid"] not in [0, loadedPokemonPid]):
            # Convert JSON data to Pokemon object
            wildPokemon = Pokemon(**jsonPokemonData)
            loadedPokemonPid = wildPokemon.pid

            # Stop pathfinding
            memory.clearJoypadInputs()

            print("New wild Pokemon !")
            print(wildPokemon)

        # Debug screenshot mode : only save the screenshot
        if (FREE_MODE):
            pass
            
        # Only apply new input when all inputs have been processed
        elif (not memory.readJoypadData()):
            screenshot = img.getScreenshot()
            playerData = player.getPlayerData()

            # Overworld
            if (img.poketch.isOnScreen(screenshot)):

                # Spin to encounter wild Pokemon
                if (SPIN_MODE):
                    # Facing left : Input up for 5 frames and release for 5 frames
                    if (playerData.orientation == "l"):
                        joypad.writeInput("u")

                    # Facing right : Input down for 5 frames and release for 5 frames
                    elif (playerData.orientation == "r"):
                        joypad.writeInput("d")

                    # Facing down : Input left for 5 frames and release for 5 frames
                    elif (playerData.orientation == "d"):
                        joypad.writeInput("l")

                    # Facing up : Input right for 5 frames and release for 5 frames
                    elif (playerData.orientation == "u"):
                        joypad.writeInput("r")

                # Go back to shop
                elif (backToShop):
                    pathfinding.goToLocation(zone.FELICITE_CITY.shopLocation)

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
                if (not backToShop and (wildPokemon.isShiny or CATCH_ALL_MODE)):
                    joypad.writeInput("llA", endSequence = "@@@@@@@@@@")
                
                # Not Shiny : Runaway sequence
                else:
                    joypad.writeInput("llrA", endSequence = "@@@@@@@@@@")

            # Inside bag : Go to Balls sequence
            elif (img.insideBag.isOnScreen(screenshot)):
                # Get cursor location (None if not present)
                cursorLocation = img.bagSectionCursor.getCursorPosition(screenshot)

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
                pokeballLocation, quantity = bag.findItemInBag(bag.POKEBALL_ID)

                # I'd rather crash than miss a Shiny
                if (pokeballLocation == None):
                    backToShop = True

                # Get cursor location (None if not present)
                cursorLocation = img.itemSelectionCursor.getCursorPosition(screenshot)

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

            # Default : mash B
            else:
                joypad.writeInput("B")


# Send encounters data to dashboard in a separate thread
def updateDashboard(dashboardData):
    currentZone = None
    currentHour = None

    # Infinite loop to update dashboard
    while True:
        waitFrames(1)

        # Retrieve current game state
        playerData = player.getPlayerData()
        gameData = game.getGameData()

        # Update dashboard
        if (gameData.hourOfDay != currentHour or playerData.zoneId != currentZone):
            currentZone = playerData.zoneId
            currentHour = gameData.hourOfDay

            if (playerData.position.zone):
                encounterTable = playerData.position.zone.getEncounterTables(currentZone)

                if (encounterTable):
                    currentTables = encounterTable.generateCurrentTables(gameData, currentZone)
                    dashboardData.encounterData["encounterTables"] = currentTables
                else:
                    dashboardData.encounterData["encounterTables"] = {}

                dashboardData.encounterData["isCave"] = playerData.position.zone.isCave
                dashboardData.ready()

# Launch this script to start the bot without the emulator and the dashboard
if __name__ == "__main__":
    startShinybot()