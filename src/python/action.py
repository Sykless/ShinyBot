import img
import bag
import zone
import game
import joypad
import memory
import pokemon

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

def openMenu():

    # If not on overworld, don't even try to open menu, just mash B
    openMenuTries = 3 * (not img.poketch.isOnScreen(img.getScreenshot()))
    mashExitTries = 0
    waitAfterPress = False

    while True:
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


def useRepel():

    # Check if we have repel in the bag
    repelPosition = bag.getRepelLocation()

    if (repelPosition is not None):

        # Need to open menu first
        menuPosition = openMenu()

        # Cannot open menu, let the main loop handle it
        if (menuPosition > 0):

            # Open bag menu
            goToMenuSection(MENU_BAG, menuPosition)

            bagOpened = False
            repelUsed = False

            while True:
                # Only apply new input if no input is found in memory
                if (len(memory.readJoypadData()) == 0):
                    screenshot = img.getScreenshot()

                    # Bag menu has been opened
                    if (not bagOpened and img.bagTouchscreen.isOnScreen(screenshot)):
                        waitFrames(10) #  Small lag after Bag menu is displayed
                        bagOpened = True

                    # Repel has been used, go back to main menu
                    elif (repelUsed):

                        # Exit bag
                        if (img.bagTouchscreen.isOnScreen(screenshot)):
                            joypad.writeInput("B")
                        
                        # We're back on the overworld after repel has been used, exit menu
                        elif (img.poketch.isOnScreen(screenshot)):
                            waitFrames(10) # Small lag after closing the bag
                            joypad.writeInput("B") # Exit menu
                            return None

                    # Cursor is visible, we can move between sections or items
                    elif (bagOpened and img.bagItemSelector.isOnScreen(screenshot)):

                        # Repel hasn't been used, move the cursor and use it
                        if (not repelUsed):
                            gameData = game.getGameData()

                            # We're in the Items section, search for Repel
                            if (gameData.selectedBagSection == bag.ITEMS_SECTION):

                                # If we're on the close bag button, our current position is after every item
                                if (gameData.closeBag):
                                    currentPosition = len(bag.getBagData().items[bag.ITEMS_SECTION])
                                else:
                                    currentPosition = bag.findItemInBag(gameData.selectedBagItem.id)

                                positionDiff = currentPosition - repelPosition

                                # Move the cusor by the difference between current and Repel position
                                if (positionDiff > 0):
                                    joypad.writeInput("u" * positionDiff)
                                elif (positionDiff < 0):
                                    joypad.writeInput("d" * (-1 * positionDiff))

                                # Found Repel : use it and skip dialogue
                                else:
                                    joypad.writeInput("AA@@@A")
                                    repelUsed = True

                            # Go left or right depending on the current bag section
                            elif (gameData.selectedBagSection < bag.MAIL_SECTION):
                                joypad.writeInput("l")
                            else:
                                joypad.writeInput("r")
        
        # Menu not opened, let the main loop handle it
        else:
            return None
        
    # No repel in the bag, TODO go buy some
    else:
        print("No repel in the bag !")
        return None


def flyToCity(city):

    # Need to open menu first
    menuPosition = openMenu()

    # Menu open
    if (menuPosition > 0):

        # Check if there is a Pokemon than can fly in our team
        pokemonPosition, movePosition = pokemon.isFlyAvailable()

        # Fly is available
        if (pokemonPosition is not None):

            # Open Pokémon menu
            goToMenuSection(MENU_POKEMON, menuPosition)

            while True:
                # Only apply new input if no input is found in memory
                if (len(memory.readJoypadData()) == 0):
                    screenshot = img.getScreenshot()
                    
                    # Pokemon menu : go to map menu through Fly
                    if (img.pokemonMenu.isOnScreen(screenshot)):
                        waitFrames(20) # Small lag after Pokémon menu is displayed
                        pokemonSelectionSequence = ""

                        # Only press right if pokemonPosition is odd
                        if (pokemonPosition % 2 == RIGHT_ROW):
                            pokemonSelectionSequence += "r"

                        # Press down depending on the Fly Pokémon position
                        pokemonSelectionSequence += "d" * int(pokemonPosition / 2) + "A" + "d" * movePosition + "A"
                        joypad.writeInput(pokemonSelectionSequence)

                    # Fly used : exit function
                    elif (img.hmAnimation.isOnScreen(screenshot)):

                        # Wait until Poketch is no longer visible (transition screen)
                        while (img.poketch.isOnScreen(img.getScreenshot())):
                            pass

                        # Wait until Poketch is visible again (Fly ended)
                        while (not img.poketch.isOnScreen(img.getScreenshot())):
                            pass

                        # Flying Pokémon goes back in the Pokéball animation
                        waitFrames(150)

                        return True
                        
                    else:
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
                            joypad.writeInput(pokemonSelectionSequence + "A")
        
        # No Pokémon with Fly, TODO go to the nearest Pokémon Center
        else:
            print("No flying Pokémon !")
            return None