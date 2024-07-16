import img
import joypad
import memory

from utils import waitFrames

def openMenu():
    openMenuTries = 0
    mashExitTries = 0
    waitAfterPress = False

    while True:
        # Check input previsouy saved
        joypadInput = memory.readJoypadData()

        # Only apply new input if no input is found in memory
        if (len(joypadInput) == 0):
            screenshot = img.getScreenshot()

            # Overworld
            if (img.poketch.isOnScreen(screenshot)):
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
                        
            # Not in overworld : go back to main loop
            else:
                return 0