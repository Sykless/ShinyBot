import img
import bag
import game
import zone
import player
import joypad
import memory
import pokemon
import pathfinding

from bag import ITEMS_SECTION, KEYITEMS_SECTION, OLDROD_ID, GOODROD_ID, SUPERROD_ID
from zone import MONTCOURONNE_SALLE8, Position
from data import ITEM_NAMES
from utils import waitFrames

MENU_POKEDEX = 1
MENU_POKEMON = 2
MENU_BAG = 3
MENU_TRAINER = 4
MENU_SAVE = 5
MENU_OPTIONS = 6
MENU_QUIT = 7

RIGHT_ROW = 1

BIKEFAST = 4
BIKEREGULAR = 3

# Mash A to load save or B if journal is on screen
def loadGame():

    # If game is already loaded, don't do anything
    if (memory.isOnTitleScreen()):

        # Wait until game is loaded
        while (memory.isOnTitleScreen()):
            if (not memory.readJoypadData()):
                joypad.writeInput("A" if not img.journalFooter.isOnScreen(img.getScreenshot()) else "B")
            waitFrames(1)

        # Wait until Poketch is visible
        while (not img.poketch.isOnScreen(img.getScreenshot())):
            waitFrames(1)


# Input sequence to open menu
def openMenu():

    # If not on overworld, don't even try to open menu, just mash B
    openMenuTries = 3 * (not img.poketch.isOnScreen(img.getScreenshot()))
    mashExitTries = 0
    waitAfterPress = False

    while True:
        # Don't check memory more than once a frame to avoid overloading the CPU
        waitFrames(1)

        # Only apply new input if no input is found in memory
        if (len(memory.readJoypadData()) == 0):
            screenshot = img.getScreenshot()
            menuPosition = img.getMenuPosition(screenshot)

            # Menu is not open
            if (menuPosition == 0):

                # Wait for potential dialogue closing time
                if (waitAfterPress):
                    waitFrames(10) #  Wait 10 frames
                    waitAfterPress = False

                # Try to open menu the regular way
                elif (openMenuTries < 3):
                    joypad.writeInput("X") # Press X to open menu
                    openMenuTries += 1
                    waitAfterPress = True

                # Menu won't open, maybe stuck in dialogue
                elif (mashExitTries < 3):
                    joypad.writeInput("BBBBBBBBBBX") # Mash B to exit then try pressing X again
                    mashExitTries += 1
                    waitAfterPress = True

                # Menu definitely won't open, go back to main loop
                else:
                    return 0

            # Menu open, exit function
            else:
                return menuPosition


# Go up or down depending on current menu position, then press A to open Pokemon menu
def goToMenuSection(menuSection, menuPosition):
    menuNavigationSequence = ""
    cursorDifferential = menuSection - menuPosition

    if (cursorDifferential < 0):
        menuNavigationSequence = "u" * (cursorDifferential * -1)
    elif (cursorDifferential > 0):
        menuNavigationSequence = "d" * cursorDifferential

    # Go up or down depending on current menu position, then press A to open Pokemon menu
    joypad.writeInput(menuNavigationSequence + "A")


# Input sequence to save the game
def saveGame():

    # Need to open menu first
    menuPosition = openMenu()

    # Cannot open menu, let the main loop handle it
    if (menuPosition > 0):

        # Open bag menu
        goToMenuSection(MENU_SAVE, menuPosition)

        dialogBoxOpen = False
        saveConfirm = False

        while True:
            # Don't check memory more than once a frame to avoid overloading the CPU
            waitFrames(1)

            # Only apply new input if no input is found in memory
            if (len(memory.readJoypadData()) == 0):
                screenshot = img.getScreenshot()

                # Make sure we have the save confirmation before leaving the method
                if (img.saveConfirmation.isOnScreen(screenshot)):
                    saveConfirm = True

                # Mash A as long as a dialog box is open
                if (img.whiteBanner.isOnScreen(screenshot)):
                    joypad.writeInput("A")
                    dialogBoxOpen = True

                # Dialog box is closed, exit the function
                elif (dialogBoxOpen):
                    return saveConfirm

    # Cannot open menu
    return None

# Input sequence to use an item
def useItem(itemId = None, repel = False, register = False, use = True):

    # Default : find the provided item in the bag
    if (itemId):
        itemPosition = bag.findItemInBag(itemId)

        # Item cannot be found, TODO go buy item
        if (itemPosition is None):
            print(f"Item {ITEM_NAMES[itemId]} cannot be found in the bag")
            return None
        
    # Particular case : repel - find any repel in the bag, prioritizing the best ones
    elif (repel):
        itemPosition = bag.getRepelLocation()

        # No repel in the bag, TODO go buy some
        if (itemPosition is None):
            print("No repel in the bag !")
            return None
        
    # No itemId provided
    else:
        print("No itemId provided")
        return None
    
    #   Don't register an already registered key item
    if (register and itemId == game.getGameData().registeredKeyItem):
        if (use):
            register = False
        else:
            return True
    
    # Need to open menu first
    menuPosition = openMenu()

    # Cannot open menu, let the main loop handle it
    if (menuPosition == 0):
        return None
    
    # Open bag menu
    goToMenuSection(MENU_BAG, menuPosition)
    
    bagOpened = False
    itemUsed = False
    bagSection = bag.getBagSection(itemId) if itemId else ITEMS_SECTION

    # Loop until the item is used and we're back on overworld
    while True:
        waitFrames(1) # Don't check memory more than once a frame to avoid overloading the CPU

        # Only apply new input if no input is found in memory
        if (len(memory.readJoypadData()) == 0):
            screenshot = img.getScreenshot()

            # Bag menu has been opened
            if (not bagOpened and img.bagTouchscreen.isOnScreen(screenshot)):
                waitFrames(10) #  Small lag after Bag menu is displayed
                bagOpened = True

            # Item has been used, go back to main menu
            elif (itemUsed):

                # Exit bag
                if (img.bagTouchscreen.isOnScreen(screenshot)):
                    joypad.writeInput("B")
                
                # We're back on the overworld after item has been used, exit menu
                elif (img.poketch.isOnScreen(screenshot)):
                    waitFrames(10) # Small lag after closing the bag

                    # We don't have to close the menu if we used a key item
                    if (bagSection != KEYITEMS_SECTION or not use):
                        joypad.writeInput("B") # Exit menu

                    # Wait until the menu is actually closed
                    while (img.getMenuPosition(img.getScreenshot())):
                        waitFrames(1)

                    return True

            # Cursor is visible, we can move between sections or items
            elif (bagOpened and img.bagItemSelector.isOnScreen(screenshot)):

                # Item hasn't been used, move the cursor and use it
                if (not itemUsed):
                    gameData = game.getGameData()

                    # We're in the correct section, search for the item to use
                    if (gameData.selectedBagSection == bagSection):

                        # If we're on the close bag button, our current position is after every item
                        if (gameData.closeBag):
                            currentPosition = len(bag.getBagData().items[bagSection])
                        else:
                            currentPosition = bag.findItemInBag(gameData.selectedBagItem.id)

                        positionDiff = currentPosition - itemPosition

                        # Move the cusor by the difference between current and Repel position
                        if (positionDiff > 0):
                            joypad.writeInput("u" * positionDiff)
                        elif (positionDiff < 0):
                            joypad.writeInput("d" * (-1 * positionDiff))

                        # Found item : use it and skip dialogue
                        elif register:
                            joypad.writeInput("AdA@")
                            register = False

                        # Found item
                        else:
                            inputSequence = ""
                            itemUsed = True

                            # Item section : Use item and skip dialogue
                            if (bagSection == ITEMS_SECTION):
                                inputSequence += "AA@@@A"

                            # Key Item section : register item if needed then use item - no skip needed
                            elif (bagSection == KEYITEMS_SECTION):
                                if (register):
                                    inputSequence += "AdA@"

                                if (use):
                                    inputSequence += "AA"

                            joypad.writeInput(inputSequence)

                    # Go left or right depending on the current bag section
                    elif (gameData.selectedBagSection <= (4 + bagSection) % 8):
                        joypad.writeInput("l")
                    else:
                        joypad.writeInput("r")


def useHM(hmId, city = None):

    # Need to open menu first
    menuPosition = openMenu()

    # Cannot open menu, let the main loop handle it
    if (menuPosition == 0):
        print("Can't open menu")
        return None

    # For performance purpose, we only upload team data once every 20 frames
    # So we wait to make sure the team data is valid
    waitFrames(20)

    # Check if there is a Pokemon than can use the HM in our team
    pokemonPosition, movePosition = pokemon.isHMAvailable(hmId)

    # No Pokémon with the HM, TODO go to the nearest Pokémon Center
    if (not pokemonPosition):
        print("No Pokémon with Hm " + pokemon.MOVE_NAMES[hmId] + " !")
        return None

    # Open Pokémon menu
    goToMenuSection(MENU_POKEMON, menuPosition)

    while True:
        # Don't check memory more than once a frame to avoid overloading the CPU
        waitFrames(1)

        # Only apply new input if no input is found in memory
        if (len(memory.readJoypadData()) == 0):
            screenshot = img.getScreenshot()
            
            # Pokemon menu : use HM
            if (img.pokemonMenu.isOnScreen(screenshot)):
                waitFrames(20) # Small lag after Pokémon menu is displayed
                pokemonSelectionSequence = ""

                # Only press right if pokemonPosition is odd
                if (pokemonPosition % 2 == RIGHT_ROW):
                    pokemonSelectionSequence += "r"

                # Press down depending on the HM Pokémon position
                pokemonSelectionSequence += "d" * int(pokemonPosition / 2) + "A" + "d" * movePosition + "A"
                joypad.writeInput(pokemonSelectionSequence)

            # HM used : exit function
            elif (img.hmAnimation.isOnScreen(screenshot)):
                    
                # Fly : transition screen between flying and landing animation
                if (hmId == pokemon.FLY_ID):

                    # Wait until Poketch is no longer visible (transition screen)
                    img.waitUntilNotVisible(img.poketch)

                    # Wait until Poketch is visible again (Fly ended)
                    while (not img.poketch.isOnScreen(img.getScreenshot())):
                        waitFrames(1)

                # Animation time before player can move again (flying Pokemon goes back to pokeball, etc)
                waitFrames(150)

                return True
            
            # Only for Defog : confirm dialog
            elif (hmId == pokemon.DEFOG_ID and img.dialogConfirm.isOnScreen(screenshot)):
                joypad.writeInput("A")
            
            # Only for Fly : move cursor to the city we need to fly to
            elif (hmId == pokemon.FLY_ID and img.worldMap.isOnScreen(screenshot)):
                cursorPosition = img.getMapCursorPosition(screenshot)

                # Map menu : move cursor to selected city
                if (cursorPosition):

                    # Find closest Fly coordinates
                    closestDistance = 99
                    closestPosition = [0,0]

                    for cityPosition in city.flyCoordinates:
                        if (abs(cityPosition[0] - cursorPosition[0]) + abs(cityPosition[1] - cursorPosition[1]) < closestDistance):
                            closestDistance = abs(cityPosition[0] - cursorPosition[0]) + abs(cityPosition[1] - cursorPosition[1])
                            closestPosition = cityPosition

                    # Generate input sequence from closest position
                    pokemonSelectionSequence = ""
                    moveX = closestPosition[0] - cursorPosition[0]
                    moveY = closestPosition[1] - cursorPosition[1]

                    if (moveX > 0):
                        pokemonSelectionSequence += "r" * moveX
                    if (moveX < 0):
                        pokemonSelectionSequence += "l" * (moveX * -1)
                    if (moveY > 0):
                        pokemonSelectionSequence += "d" * moveY
                    if (moveY < 0):
                        pokemonSelectionSequence += "u" * (moveY * -1)

                    # Play input sequence and press A to fly to the selected city
                    if (pokemonSelectionSequence):
                        joypad.writeInput(pokemonSelectionSequence)
                    else:
                        joypad.writeInput("A")


def useRod(rodType):
    gameData = game.getGameData()
    registeredKeyItem = gameData.registeredKeyItem
    fishFound = False

    # Make sure we are using a rod
    if (rodType not in [OLDROD_ID, GOODROD_ID, SUPERROD_ID]):
        print(f"{ITEM_NAMES[rodType]} is not a rod")
        return None

    # Register rod as key item, press Y if already the case
    if (registeredKeyItem != rodType):
        useItem(itemId = rodType, register = True, use = True)
    else:
        joypad.writeInput("Y")

    # Keep fishing until a Pokémon is found
    while (not fishFound):
        screenshot = img.getScreenshot()

        # Fish found, exit loop
        if (img.exclamationBox.isOnScreen(screenshot)):
            fishFound = True

        # No fish found, exit dialog and keep fishing
        elif (img.noFishFoundDialog.isOnScreen(screenshot)):
            joypad.writeInput("AY")

        waitFrames(1)

    # Press A to reel fish, then confirm dialog to start battle
    joypad.writeInput("A@@@@@@A")

    # Wait until the inputs have been processed
    while (not memory.readJoypadData()):
        waitFrames(1)


###################################################################################################
# Go in front of Union Room and prepare the exact setup MelonDS emulator needs to perform trading #
###################################################################################################
def setupTradePosition():
    
    # Retrieve Union Room position from Interactable object
    unionRoom = zone.LITTORELLA_CENTREPOKEMON_ETAGE.getInteractableByType(zone.UNIONROOM)
    unionRoomPosition = unionRoom.getInteractionPosition()

    # Make sure we're in front of Union Room
    while (player.getPlayerData().position != unionRoomPosition):
        pathfinding.goToWorldLocation(unionRoomPosition)

    # Make sure we're facing up
    while (player.getPlayerData().orientation != "u"):
        joypad.writeInput("u")


def setupFeebasFishingPosition():
    shortestDistance = 9999
    startingPosition = None
    closestNeighbourg = None
    orientation = None

    # Retrieve Feebas tiles positions from memory
    gameData = game.getGameData()
    playerPosition = player.getPlayerData().position
    feebasTiles = gameData.getFeebasTiles()

    # If we're already in the area, start there
    if (playerPosition.zone == MONTCOURONNE_SALLE8):
        startingPosition = playerPosition

    # If we're outside, find which door is closest
    else:
        shortestStartingPosition = 9999

        # Iterate on each door to find the closest one to our current position
        for door in MONTCOURONNE_SALLE8.doorList:
            startingPositionScore = pathfinding.calculateWorldPathCost(door)

            if (startingPositionScore < shortestStartingPosition):
                shortestStartingPosition = startingPositionScore
                startingPosition = door.position

    # Find best position to fish
    for feebasTile in feebasTiles:
        for neighbour in [(-1,0,"r"),(1,0,"l"),(0,-1,"d"),(0,1,"u")]:
            neighbourPosition = Position(feebasTile.X + neighbour[0], feebasTile.Y + neighbour[1], feebasTile.zone)
            neighbourPath = pathfinding.getMostEfficientPath(startingPosition, neighbourPosition)

            if (neighbourPath and neighbourPath[-1].g < shortestDistance):
                shortestDistance = neighbourPath[-1].g
                closestNeighbourg = neighbourPosition
                orientation = neighbour

    # Go to fishing spot and make sure we're stopped
    pathfinding.goToWorldLocation(closestNeighbourg)
    waitFrames(10)

    # Make sure we're facing the fishing spot
    if (player.getPlayerData().orientation != orientation[2]):
        joypad.writeInput(orientation[2])