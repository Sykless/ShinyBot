import img
import action
import joypad
import emukeyboard

from utils import waitFrames
from emu import BIZHAWK, MELONDS, Window

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
    while (img.whiteBackground.isOnScreen(melonWindow.captureWindowContent())):
        waitFrames(5)

    windowContent = melonWindow.captureWindowContent()

    # Mash A until we're in Union Room
    while (not img.dialogboxBackground.isOnScreen(windowContent, img.BOTTOMSCREEN)):

        # Journal is on screen : press B to skip
        if (img.journalBackground.isOnScreen(windowContent)):
            emukeyboard.pressButton("B")

        # Default : mash A
        else:
            emukeyboard.pressButton("A")

        # Check the screen 5 frames later
        windowContent = melonWindow.captureWindowContent()


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
    while (not img.dialogboxBackground.isOnScreen(MELONDS.mainWindow.captureWindowContent())):
        emukeyboard.pressButton("A")

    # Wait until selection box is open
    while (not img.selectionboxBackground.isOnScreen(MELONDS.mainWindow.captureWindowContent())):
        waitFrames(5)

    # Navigate to "Trade" and press A to confirm
    emukeyboard.pressButtons("Down", "Down", "Down", "A")

    # Mash A to confirm trade on secondary instance until we're in the transition screen
    while (not img.blackBackground.isOnScreen(MELONDS.secondaryWindow.captureWindowContent())):
        emukeyboard.pressButton("A")

    # Wait until trade menu is open
    while (not img.tradeBackground.isOnScreen(MELONDS.mainWindow.captureWindowContent())):
        waitFrames(5)

    # Wait until communication dialog box closes
    while (img.dialogboxBackground.isOnScreen(MELONDS.mainWindow.captureWindowContent())):
        waitFrames(5)
    waitFrames(5) # Small lag after box closes

    # Trade each Pokémon in the list
    selectPokemon(mainGamePokemon, secondaryGamePokemon)

    # Quit trade menu on both instances
    quitTradeMenu(MELONDS.mainWindow)
    quitTradeMenu(MELONDS.secondaryWindow)

    # Mash B on both instances until we left trade menu
    while (not img.blackBackground.isOnScreen(MELONDS.mainWindow.captureWindowContent())):
        MELONDS.mainWindow.giveFocus()
        emukeyboard.pressButton("B")

        MELONDS.secondaryWindow.giveFocus()
        emukeyboard.pressButton("B")

    # Wait until we're back on selection menu
    while (not img.selectionboxBackground.isOnScreen(MELONDS.mainWindow.captureWindowContent())):
        waitFrames(5)

    # Mash B to close selection box until no dialog box is left open
    while (img.dialogboxBackground.isOnScreen(MELONDS.mainWindow.captureWindowContent())):
        emukeyboard.pressButton("B")

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
    while (not img.selectionboxBackground.isOnScreen(melonWindow.captureWindowContent())):
        emukeyboard.pressButton("X") # Try to open menu every half of a second
        waitFrames(30)

    # Go to save button
    emukeyboard.pressButtons("Down", "Down", "Down", "Down", "A")

    # Wait until confirmation box appears
    while (not img.confirmationboxBackground.isOnScreen(melonWindow.captureWindowContent())):
        waitFrames(5)

    # Mash A until save menu closes
    while (img.dialogboxBackground.isOnScreen(melonWindow.captureWindowContent(), img.TOPSCREEN)):
        emukeyboard.pressButton("A")

    # Close the game
    melonWindow.closeWindow()

def selectPokemon(mainGamePokemon, secondaryGamePokemon):

    # Repeat the process for each trade
    for i in range(len(mainGamePokemon)):

        # Select Pokémon to trade on both instances
        selectPokemonToTrade(MELONDS.mainWindow, mainGamePokemon[i])
        selectPokemonToTrade(MELONDS.secondaryWindow, secondaryGamePokemon[i])

        # Wait until confirmation box appears
        while (not img.confirmationboxBackground.isOnScreen(MELONDS.mainWindow.captureWindowContent())):
            waitFrames(5)

        # Confirm trade on both instances
        emukeyboard.pressButton("A")
        MELONDS.secondaryWindow.giveFocus()
        emukeyboard.pressButton("A")

        # Wait until trade animation starts
        while (not img.blackBackground.isOnScreen(MELONDS.mainWindow.captureWindowContent())):
            waitFrames(5)

        # Wait until trade screen is visible again
        while (not img.tradeBackground.isOnScreen(MELONDS.mainWindow.captureWindowContent())):

            # Particular case : trade evolution : mash A to skip dialog
            mainWindowContent = MELONDS.mainWindow.captureWindowContent()
            if (img.evolutionBackground.isOnScreen(mainWindowContent) or img.learnmoveBackground.isOnScreen(mainWindowContent)):
                emukeyboard.pressButton("A")

            secondaryWindowContent = MELONDS.secondaryWindow.captureWindowContent()
            if (img.evolutionBackground.isOnScreen(secondaryWindowContent) or img.learnmoveBackground.isOnScreen(secondaryWindowContent)):
                emukeyboard.pressButton("A")

            waitFrames(5)

        # Wait until communication dialog box closes
        while (img.dialogboxBackground.isOnScreen(MELONDS.mainWindow.captureWindowContent())):
            waitFrames(5)
        waitFrames(5)

    

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
    while (not img.confirmationboxBackground.isOnScreen(melonWindow.captureWindowContent())):
        waitFrames(5)

    # Select "Trade"
    emukeyboard.pressButtons("Down", "A")


def quitTradeMenu(melonWindow: Window):

    # Give focus on the window so it can accept inputs
    melonWindow.giveFocus()

    # Navigate to "Quit" and press A to confirm
    emukeyboard.pressButtons("Left", "Up", "A")

    # Wait until the confirmation dialog box opens
    while (not img.confirmationboxBackground.isOnScreen(melonWindow.captureWindowContent())):
        waitFrames(5)

    # Confirm Quit Trade
    emukeyboard.pressButton("A")