
import cv2
import time
import types

import img
import action
import joypad
import emukeyboard

from utils import waitFrames
from img import BOTTOMSCREEN, TOPSCREEN, BackgroundTemplate
from emu import BIZHAWK, MELONDS, Window

SPECIFIC = types.SimpleNamespace()
SPECIFIC.LOAD_GAME = 1
SPECIFIC.OPEN_MENU = 2
SPECIFIC.TRADE_EVOLUTION = 3
SPECIFIC.LEAVE_TRADE_MENU = 4

FRAMES_TO_WAIT = 5

def waitUntil(window: Window, background: BackgroundTemplate, visible, mashButton = None, imagePosition = None, specificProcess = None):
    framesWaited = 0

    # Wait until the image is visible (or not visible anymore)
    while (True):
        screenshot = window.captureWindowContent()

        print("Checking " + background.name + (" is visible" if visible else " is not visible"))

        # Condition is met : exit loop
        if (background.isOnScreen(screenshot, imagePosition) is visible):
            return True
        
        # If we spent more than one minute waiting, we are most likely stuck, stop the process
        elif (framesWaited > 3600):
            img.saveScreenshot(screenshot, background.name)
            raise Exception(background.name + (" cannot be found in the image" if visible else " still visible in the image"))
        
        # Process that needs a specific condition
        elif (specificProcess):
            match specificProcess:

                # Mash A to load game, and press B if on Journal
                case SPECIFIC.LOAD_GAME:
                    if (img.journalBackground.isOnScreen(screenshot)):
                        emukeyboard.pressButton("B")
                    else:
                        emukeyboard.pressButton("A")
                    framesWaited += 2 * FRAMES_TO_WAIT

                # Try to open menu every half of a second
                case SPECIFIC.OPEN_MENU:
                    emukeyboard.pressButton("X") 
                    framesWaited += 30
                    waitFrames(30)

                # Trade evolution : mash A to skip dialog
                case SPECIFIC.TRADE_EVOLUTION:
                    mainWindowContent = MELONDS.mainWindow.captureWindowContent()
                    if (img.evolutionBackground.isOnScreen(mainWindowContent) or img.learnmoveBackground.isOnScreen(mainWindowContent)):
                        emukeyboard.pressButton("A")

                    secondaryWindowContent = MELONDS.secondaryWindow.captureWindowContent()
                    if (img.evolutionBackground.isOnScreen(secondaryWindowContent) or img.learnmoveBackground.isOnScreen(secondaryWindowContent)):
                        emukeyboard.pressButton("A")

                    framesWaited += FRAMES_TO_WAIT
                    waitFrames(FRAMES_TO_WAIT)

                # Mash B on both instances to skip Pal Pad dialogue and leave Trade Menu
                case SPECIFIC.LEAVE_TRADE_MENU:
                    MELONDS.mainWindow.giveFocus()
                    emukeyboard.pressButton("B")

                    MELONDS.secondaryWindow.giveFocus()
                    emukeyboard.pressButton("B")
                    framesWaited += 4 * FRAMES_TO_WAIT
        
        # If a button is provided : mash it until the above condition is met
        elif (mashButton):
            emukeyboard.pressButton(mashButton)
            framesWaited += 2 * FRAMES_TO_WAIT
        
        # Default : just wait
        else:
            waitFrames(FRAMES_TO_WAIT)
            framesWaited += FRAMES_TO_WAIT


def initTrade(mainGame, secondaryGame):

    # Perform the same init setup on both games
    for game in [mainGame, secondaryGame]:
    
        # Make sure current instance is loaded
        BIZHAWK.initEmulator(game)
        action.loadGame()

        # Go to a specific cell in front of Union Room and save the game
        if (not action.setupTradePosition()):
            print("Couldn't save on version " + game + ", traded canceled")
            return False

        # Close current instance
        BIZHAWK.mainWindow.closeWindow()

        # Import BizHawk save file in MelonDS
        MELONDS.importSaveFile(game, secondaryExtension = (game == secondaryGame))

    # Both games ready to trade
    return True


def enterUnionRoom(melonWindow: Window):

    # Wait until the game starts
    waitUntil(melonWindow, img.whiteBackground, visible = False)

    # Mash A until we're in Union Room
    waitUntil(melonWindow, img.dialogboxBackground, visible = True, imagePosition = BOTTOMSCREEN, specificProcess = SPECIFIC.LOAD_GAME)


def performTrade(mainGame, mainGamePokemon, secondaryGame, secondaryGamePokemon):

    # Make sure we're on the right position on both instances
    initTrade(mainGame, secondaryGame)

    # Launch first MelonDS instance, load game and enter Union Room
    MELONDS.initEmulator(mainGame)
    enterUnionRoom(MELONDS.mainWindow)

    # Go to the trade position on first instance
    emukeyboard.pressKey("B") # Start running
    emukeyboard.holdButton("Up", joypad.TURNAROUND_ANIMATION + int(1.5 * joypad.INPUTTIME["run"])) # Turn around and run 2 cells up
    emukeyboard.holdButton("Left", 4 * joypad.INPUTTIME["run"]) # Run 4 cells left
    emukeyboard.releaseKey("B") # Stop running

    # Launch second MelonDS instance, load game and enter Union Room
    MELONDS.initSecondEmulatorInstance(secondaryGame)
    enterUnionRoom(MELONDS.secondaryWindow)

    # Mash A on first instance until we start dialog with the other
    waitUntil(MELONDS.mainWindow, img.dialogboxBackground, visible = True, mashButton = "A")

    # Wait until selection box is open
    waitUntil(MELONDS.mainWindow, img.selectionboxBackground, visible = True)

    # Navigate to "Trade" and press A to confirm
    emukeyboard.pressButtons("Down", "Down", "Down", "A")

    # Mash A to confirm trade on secondary instance until we're in the transition screen
    waitUntil(MELONDS.secondaryWindow, img.blackBackground, visible = True, mashButton = "A")

    # Wait until trade menu is open
    waitUntil(MELONDS.mainWindow, img.tradeBackground, visible = True)

    # Wait until communication dialog box closes
    waitUntil(MELONDS.mainWindow, img.dialogboxBackground, visible = False)
    waitFrames(5) # Small lag after box closes

    # Trade each Pokémon in the list
    selectPokemon(mainGamePokemon, secondaryGamePokemon)

    # Quit trade menu on both instances
    quitTradeMenu(MELONDS.mainWindow)
    quitTradeMenu(MELONDS.secondaryWindow)

    # Mash B on both instances until we leave trade menu
    waitUntil(MELONDS.mainWindow, img.blackBackground, visible = True, specificProcess = SPECIFIC.LEAVE_TRADE_MENU)
    
    # Wait until we're back on selection menu
    waitUntil(MELONDS.mainWindow, img.selectionboxBackground, visible = True)

    # Mash B to close selection box until no dialog box is left open
    waitUntil(MELONDS.mainWindow, img.dialogboxBackground, visible = False, mashButton = "B")

    # Quit Union Room, save the game and close window on both instances
    saveAndQuit(MELONDS.mainWindow, ("Right", 4))
    saveAndQuit(MELONDS.secondaryWindow, ("Up", 1))

    # Import MelonDS save file in BizHawk
    BIZHAWK.importSaveFile(mainGame)
    BIZHAWK.importSaveFile(secondaryGame, secondaryExtension = True)

    
def saveAndQuit(melonWindow: Window, inputs):

    # Give focus on the window so it can accept inputs
    melonWindow.giveFocus()

    # Exit Union Room
    emukeyboard.pressKey("B") # Start running
    emukeyboard.holdButton(inputs[0], joypad.TURNAROUND_ANIMATION + inputs[1] * joypad.INPUTTIME["run"]) # Turn around and run so we're above exit
    emukeyboard.holdButton("Down", 2 * joypad.INPUTTIME["run"]) # Run 2 cells down to exit Union Room
    emukeyboard.releaseKey("B") # Stop running

    # Wait until we left Union Room and menu opening is available
    waitUntil(melonWindow, img.selectionboxBackground, visible = True, specificProcess = SPECIFIC.OPEN_MENU)

    # Go to save button
    emukeyboard.pressButtons("Down", "Down", "Down", "Down", "A")

    # Wait until confirmation box appears
    waitUntil(melonWindow, img.confirmationboxBackground, visible = True)

    # Mash A until save menu closes
    waitUntil(melonWindow, img.dialogboxBackground, visible = False, mashButton = "A", imagePosition = TOPSCREEN)

    # Close the game
    melonWindow.closeWindow()


def selectPokemon(mainGamePokemon, secondaryGamePokemon):

    # Repeat the process for each trade
    for i in range(len(mainGamePokemon)):

        # Select Pokémon to trade on both instances
        selectPokemonToTrade(MELONDS.mainWindow, mainGamePokemon[i])
        selectPokemonToTrade(MELONDS.secondaryWindow, secondaryGamePokemon[i])

        # Wait until confirmation box appears
        waitUntil(MELONDS.mainWindow, img.confirmationboxBackground, visible = True)

        # Confirm trade on both instances
        emukeyboard.pressButton("A")
        MELONDS.secondaryWindow.giveFocus()
        emukeyboard.pressButton("A")

        # Wait until trade animation starts
        waitUntil(MELONDS.mainWindow, img.blackBackground, visible = True)

        # Wait until trade screen is visible again
        waitUntil(MELONDS.mainWindow, img.tradeBackground, visible = True, specificProcess = SPECIFIC.TRADE_EVOLUTION)

        # Wait until communication dialog box closes
        waitUntil(MELONDS.mainWindow, img.dialogboxBackground, visible = False)
        waitFrames(5) # Small lag after box closes

    

def selectPokemonToTrade(melonWindow: Window, position):

    # Give focus on the window so it can accept inputs
    melonWindow.giveFocus()

    # Press Right once for even positions
    if (position % 2 == 0):
        emukeyboard.pressButton("Right")

    # Press Down until we reach provided position
    for _ in range((position - 1) // 2):
        emukeyboard.pressButton("Down")

    # Select Pokémon
    emukeyboard.pressButton("A")

    # Wait until the confirmation dialog box opens
    waitUntil(melonWindow, img.confirmationboxBackground, visible = True)

    # Select "Trade"
    emukeyboard.pressButtons("Down", "A")


def quitTradeMenu(melonWindow: Window):

    # Give focus on the window so it can accept inputs
    melonWindow.giveFocus()

    # Navigate to "Quit" and press A to confirm
    emukeyboard.pressButtons("Left", "Up", "A")

    # Wait until the confirmation dialog box opens
    waitUntil(melonWindow, img.confirmationboxBackground, visible = True)

    # Confirm Quit Trade
    emukeyboard.pressButton("A")