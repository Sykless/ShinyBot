import img
import zone
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
    openMenuTries = 3 * (1 - int(img.poketch.isOnScreen(img.getScreenshot())))
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
            
def flyToCity(city):

    # Need to open menu first
    menuPosition = openMenu()

    # Menu open
    if (menuPosition > 0):

        # Check if there is a Pokemon than can fly in our team
        pokemonPosition, movePosition = pokemon.isFlyAvailable()

        # Fly is available
        if (pokemonPosition is not None):
            menuNavigationSequence = ""
            cursorDifferential = MENU_POKEMON - menuPosition

            if (cursorDifferential < 0):
                menuNavigationSequence = "u" * (cursorDifferential * -1)
            elif (cursorDifferential > 0):
                menuNavigationSequence = "d" * cursorDifferential

            # Go up or down depending on current menu position, then press A to open Pokemon menu
            joypad.writeInput(menuNavigationSequence + "A")

            while True:
                # Only apply new input if no input is found in memory
                if (len(memory.readJoypadData()) == 0):
                    screenshot = img.getScreenshot()
                    
                    # Pokemon menu : go to map menu through Fly
                    if (img.pokemonMenu.isOnScreen(screenshot)):
                        waitFrames(20) #  Small lag after Pokémon menu is displayed
                        pokemonSelectionSequence = ""

                        # Only press right if pokemonPosition is odd
                        if (pokemonPosition % 2 == RIGHT_ROW):
                            pokemonSelectionSequence += "r"

                        # Press down depending on the Fly Pokémon position
                        pokemonSelectionSequence += "d" * int(pokemonPosition / 2) + "A" + "d" * movePosition + "A"
                        joypad.writeInput(pokemonSelectionSequence)

                    # Fly used : exit function
                    elif (img.hmAnimation.isOnScreen(screenshot)):
                        print("Flyyyyyy")
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