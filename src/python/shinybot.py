
from utils import waitFrames
from pokemon import Pokemon
from bag import SUPERROD_ID
from emu import BIZHAWK, MELONDS, PLATINE, DIAMANT, PERLE

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

FREE_MODE = True
SPIN_MODE = True
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

    # Free mode : don't let the script interact with the game
    if (FREE_MODE):
        print("Free mode")

    # Bot mode : the script is controlling the game
    while True:
        # Don't check memory more than once a frame to avoid overloading the CPU
        waitFrames(1)

        playerData = player.getPlayerData()
        gameData = game.getGameData()

        # Debug screenshot mode : only save the screenshot
        if (FREE_MODE):
            pass
        
        # Only apply new input when all inputs have been processed
        else:
            screenshot = img.getScreenshot()
            playerData = player.getPlayerData()

            # Check if a new wild Pokémon has been found
            wildPokemon = pokemon.getWildPokemon()
                
            # Start battle if a wild Pokémon is found
            if (wildPokemon):
                action.battle(wildPokemon)

            # Overworld : find Pokémon
            if (img.poketch.isOnScreen(screenshot)):

                # Spin to encounter wild Pokemon
                if (SPIN_MODE):
                    nextOrientation = {"l":"u", "r":"d", "d":"l", "u":"r"}[playerData.orientation]
                    joypad.writeInput(nextOrientation, wait = True)
            
        


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