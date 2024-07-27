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
            
def flyToTown(town):

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

                        # Map menu : move cursor to selected town
                        if (cursorPosition):

                            # Find closest Fly coordinates
                            closestDistance = 99
                            closestPosition = [0,0]

                            for townPosition in town.flyCoordinates:
                                if (abs(townPosition[0] - cursorPosition[0]) + abs(townPosition[1] - cursorPosition[1]) < closestDistance):
                                    closestDistance = abs(townPosition[0] - cursorPosition[0]) + abs(townPosition[1] - cursorPosition[1])
                                    closestPosition = townPosition

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

                            # Play input sequence and press A to fly to the selected town
                            joypad.writeInput(pokemonSelectionSequence + "A")

                            
def isTrainerOnBike(trainerPosition, stayOnBike = False):

    bikeSpeed = None
    zoneMap = trainerPosition.zone.map
    cellValue = zoneMap[trainerPosition.Y][trainerPosition.X]

    # Can only use bike on regular cell or grass
    if (cellValue in ["O","G","A"]):

        # Retrieve sprite current orientation and position
        playerOrientation, spritePosition = img.getPlayerOrientation(img.getScreenshot())

        # Press Y to use bike or go back on foot, then wait for animation to end
        joypad.writeInput("Y")
        waitFrames(20)

        # Retrieve sprite new position
        newSpritePosition = img.getPlayerOrientation(img.getScreenshot())[1]

        # Sprite hasn't moved, we can't use bike
        if (newSpritePosition == spritePosition):
            joypad.writeInput("Y") # Skip potential dialogue
            return False, None

        # If facing right or down, bike sprite goes forward
        elif (playerOrientation in ["r","d"]):
            isOnBike = (newSpritePosition[0] > spritePosition[0])

        # If facing left or up, bike sprite goes backwards
        elif (playerOrientation in ["l","u"]):
            isOnBike = (newSpritePosition[0] < spritePosition[0])

        # Started on bike, go back to test speed
        if (not isOnBike):
            joypad.writeInput("Y")
            waitFrames(20)

        # Search for free cells to check the bike speed
        freeCells = []

        # Sort the orientations to start with the current orientation
        for orientation in sorted([(1,0,"r"), (-1,0,"l"), (0,1,"d"), (0,-1,"u")], key=lambda x: abs(ord(x[2]) - ord(playerOrientation))):

            # Check if we can go on the next 2 cells on bike
            for i in range(0,3):
                cell = zoneMap[trainerPosition.Y + i * orientation[1]][trainerPosition.X + i * orientation[0]]

                # Three cells in a row : keep that orientation
                if (cell not in ["O","G","A"]):
                    break
                elif (i == 2):
                    # Make sure we're not running into a sign during the speed test
                    if (orientation[2] != "u" or zoneMap[trainerPosition.Y-3][trainerPosition.X] != "s"):
                        freeCells = orientation

            if (len(freeCells) > 0):
                break

        # Found 2 free cells to test speed
        if (len(freeCells) > 0):
            # Enough input frames to move 1 cell with fast bike and 2 cells with regular bike 
            bikeSpeedTestInputs = (joypad.getStartingAnimationInputs(freeCells[2], playerOrientation) + 2 * freeCells[2])
            joypad.writeRawInput(bikeSpeedTestInputs)

            # Check position after moving animation
            waitFrames(12 + len(bikeSpeedTestInputs))
            newPlayerPosition = zone.getPlayerPosition()
            newPlayerPosition.setDistanceTo(trainerPosition)

            # Speed bike
            if (newPlayerPosition.distance == 1):
                bikeSpeed = BIKEFAST
            # Regular bike
            elif (newPlayerPosition.distance == 2):
                bikeSpeed = BIKEREGULAR

            # Go back to original position
            oppositeDirection = {"l":"r", "r":"l", "u":"d", "d":"u"}[freeCells[2]]
            goBackToPositionInputs = (joypad.getStartingAnimationInputs(oppositeDirection, None) + 2 * oppositeDirection)
            joypad.writeRawInput(goBackToPositionInputs)
            waitFrames(12 + len(goBackToPositionInputs))

        # Started on foot, go back to original state
        if (isOnBike and not stayOnBike):
            joypad.writeInput("Y")
            waitFrames(20)

        # Return original state (on foot/bike) and bike speed
        return not isOnBike, bikeSpeed

    # Cannot be on bike on this cell
    else:
        return False, None









