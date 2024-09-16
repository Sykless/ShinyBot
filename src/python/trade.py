
import copy
import types

import img
import time
import action
import joypad
import pokemon
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

class Trade():
    def __init__(self, mainGame, mainGamePokemon, secondaryGame, secondaryGamePokemon):
        self. mainGame = mainGame
        self.secondaryGame = secondaryGame
        self.pokemonPositions = {self.mainGame : mainGamePokemon, self.secondaryGame: secondaryGamePokemon}
        self.originalPokemonPositions = copy.deepcopy(self.pokemonPositions)

        self.initialized = False
        self.pokemonTeams = {self.mainGame: [], self.secondaryGame: []}
        self.originalPokemonTeams = {self.mainGame: [], self.secondaryGame: []}
        self.originalSave = {self.mainGame: None, self.secondaryGame: None}


    ######################################################################################
    # Execute every action needed to trade Pokémon from the main instance to a secondary #
    ######################################################################################
    def tradeProcess(self):

        # Make sure all MelonDS windows are closed to properly setup the trade
        MELONDS.closeAllWindows()

        # Keep trying to trade until there's no error detected
        while True:
            try:
                # Make sure we're on the right position on both instances
                if (not self.initialized):
                    self.initTrade()

                # Launch first MelonDS instance, load game and enter Union Room
                MELONDS.initEmulator(self.mainGame)
                self.enterUnionRoom(MELONDS.mainWindow)

                # Go to the trade position on first instance
                emukeyboard.pressKey("B") # Start running
                emukeyboard.holdButton("Up", joypad.TURNAROUND_ANIMATION + int(1.5 * joypad.INPUTTIME["run"])) # Turn around and run 2 cells up
                emukeyboard.holdButton("Left", 4 * joypad.INPUTTIME["run"]) # Run 4 cells left
                emukeyboard.releaseKey("B") # Stop running

                # Launch second MelonDS instance, load game and enter Union Room
                MELONDS.initSecondEmulatorInstance(self.secondaryGame)
                self.enterUnionRoom(MELONDS.secondaryWindow)

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
                self.selectPokemon()

                # Quit trade menu on both instances
                self.quitTradeMenu(MELONDS.mainWindow)
                self.quitTradeMenu(MELONDS.secondaryWindow)

                # Mash B on both instances until we leave trade menu
                waitUntil(MELONDS.mainWindow, img.blackBackground, visible = True, specificProcess = SPECIFIC.LEAVE_TRADE_MENU)
                
                # Wait until we're back on selection menu
                waitUntil(MELONDS.mainWindow, img.selectionboxBackground, visible = True)

                # Mash B to close selection box until no dialog box is left open
                waitUntil(MELONDS.mainWindow, img.dialogboxBackground, visible = False, mashButton = "B")

                # Quit Union Room, save the game and close window on both instances
                self.saveAndQuit(MELONDS.mainWindow, ("Right", 4))
                self.saveAndQuit(MELONDS.secondaryWindow, ("Up", 1))

                # Make sure all Pokémon have been traded, only exit process if that's the case
                if (self.checkTradedPokemon()):
                    return True

            # Error in trade process : could be trouble saving, finding a template in the image, etc
            except Exception as exception:
                print("Error during Trade : " + str(exception))

                # Close every running instance
                BIZHAWK.closeAllWindows()
                MELONDS.closeAllWindows()
                
                # Make sure all Pokémon have been traded, only exit process if that's the case
                if (self.checkTradedPokemon()):
                    return True
                

    ###############################################################
    # Open game and check that every Pokémon was correctly traded #
    ###############################################################
    def checkTradedPokemon(self):
        print("\nChecking if trade was successful")

        # Import MelonDS save file in BizHawk
        backupMainSave = BIZHAWK.importSaveFile(self.mainGame)
        backupSecondarySave = BIZHAWK.importSaveFile(self.secondaryGame, secondaryExtension = True)

        # Keep original saves
        self.storeBackupSaves(backupMainSave, backupSecondarySave)

        # Load main game on BizHawk
        BIZHAWK.initEmulator(self.mainGame)
        action.loadGame()

        # Open menu and retrieve Pokémon team
        action.openMenu()
        waitFrames(20)
        pokemonTeam = pokemon.getPokemonTeam()

        # Keep track of the successfully traded Pokémon
        pokemonTraded = []
        restartProcess = False

        print(self.pokemonTeams[self.mainGame])
        print()
        print(pokemonTeam)
        print()

        # Make sure all Pokémon have been traded
        for pokemonId in range(len(pokemonTeam)):
            originalPokemon = self.pokemonTeams[self.mainGame][pokemonId]
            newPokemon = pokemonTeam[pokemonId]

            # New Pokémon in the team
            if (originalPokemon != newPokemon):

                # The Pokémon was supposed to be traded, check if the correct Pokémon was received
                if (pokemonId in self.pokemonPositions[self.mainGame]):

                    # Retrieve the traded Pokémon in the other instance and make sure they match
                    tradeIndex = self.pokemonPositions[self.mainGame].index(pokemonId)
                    tradedPokemonId = self.pokemonPositions[self.secondaryGame][tradeIndex]
                    tradedPokemon = self.pokemonTeams[self.secondaryGame][tradedPokemonId]

                    # Trade was successful, track the Pokémon position in the pokemonPositions list
                    if (newPokemon == tradedPokemon):
                        pokemonTraded.append(tradeIndex)
                        print("Successfully traded " + originalPokemon.name + " for " + newPokemon.name)

                    # We received a different Pokémon, go back to previous save
                    else:
                        restartProcess = True
                        print(newPokemon.name + " is not supposed to have been received")
                
                # We were not supposed to trade this Pokémon, go back to previous save
                else:
                    restartProcess = True
                    print(originalPokemon.name + " is not supposed to have been sent")

            # We're in an unwanted state, restore backup save and restart trade process from scratch
            if (restartProcess):
                self.restartTrade()
                return False

        # Remove traded Pokémon from the pokemonPositions list
        for pokemonPosition in sorted(pokemonTraded, reverse = True):
            del self.pokemonPositions[self.mainGame][pokemonPosition]
            del self.pokemonPositions[self.secondaryGame][pokemonPosition]

        # Pokémon left to trade : we need to keep trading
        if (self.pokemonPositions[self.mainGame]):
            
            # In case we need to keep trading from a different state than the base state, restart the init process
            if (self.pokemonPositions != self.originalPokemonPositions):
                self.initialized = False
            else:
                self.restartTrade()

            # There was an issue somewhere : keep trading
            return False
        
        # Trade successful
        return True
    

    #############################################################
    # Restart trade from scratch but skip trade initializatioln #
    #############################################################
    def restartTrade(self):

        # Close trade check window
        BIZHAWK.mainWindow.closeWindow()

        # Reset Pokémon to trade
        self.pokemonTeams = self.originalPokemonTeams
        self.pokemonPositions = copy.deepcopy(self.originalPokemonPositions)

        # Restore backup saves for both instances on BizHawk and MelonDS so we can skip initTrade
        if (self.originalSave[self.mainGame]):
            BIZHAWK.restoreBackupFile(self.mainGame, self.originalSave[self.mainGame])
        
        if (self.originalSave[self.secondaryGame]):
            BIZHAWK.restoreBackupFile(self.secondaryGame, self.originalSave[self.secondaryGame])

        MELONDS.importSaveFile(self.mainGame)
        MELONDS.importSaveFile(self.secondaryGame, secondaryExtension = True)


    #####################################################################################################
    # Setup the correct position and orientation with BizHawk so MelonDS always start on the same setup #
    #####################################################################################################
    def initTrade(self):

        # Add Pokémon Team in a list to make sure we find the traded Pokemon on the other instance after the trade
        self.pokemonTeams = {self.mainGame: [], self.secondaryGame: []}

        # Perform the same init setup on both games
        for game in [self.mainGame, self.secondaryGame]:
        
            # Make sure current instance is loaded
            print("\nInitializing Version " + game)
            BIZHAWK.initEmulator(game)
            action.loadGame()

            # Go to a specific cell in front of Union Room
            action.setupTradePosition()

            # Open menu and retrieve Pokémon we want to trade
            if (action.openMenu()):
                waitFrames(20)
                self.pokemonTeams[game] = pokemon.getPokemonTeam()

                if (not self.originalPokemonTeams[game]):
                    self.originalPokemonTeams[game] = self.pokemonTeams[game]
            else:
                print("Couldn't open menu on version " + game + ", traded canceled")
                return None
            
            # Save the game and quit the process if we couldn't
            if (not action.saveGame()):
                print("Couldn't save on version " + game + ", traded canceled")
                return None

            # Close current instance
            BIZHAWK.mainWindow.closeWindow()

            # Import BizHawk save file in MelonDS
            MELONDS.importSaveFile(game, secondaryExtension = (game == self.secondaryGame))

        # Both games ready to trade
        self.initialized = True


    ###################################################
    # Go from loading the game to entering Union Room #
    ###################################################
    def enterUnionRoom(self, melonWindow: Window):

        # Wait until the game starts
        waitUntil(melonWindow, img.whiteBackground, visible = False)

        # Mash A until we're in Union Room
        waitUntil(melonWindow, img.dialogboxBackground, visible = True, imagePosition = BOTTOMSCREEN, specificProcess = SPECIFIC.LOAD_GAME)


    #############################################################################################
    # Select all tradeable Pokémon, trade them with each other and wait until animation is over #
    #############################################################################################
    def selectPokemon(self):

        # Repeat the process for each trade
        for i in range(len(self.pokemonPositions[self.mainGame])):

            # Select Pokémon to trade on both instances
            self.selectpokemonTeams(MELONDS.mainWindow, self.pokemonPositions[self.mainGame][i])
            self.selectpokemonTeams(MELONDS.secondaryWindow, self.pokemonPositions[self.secondaryGame][i])

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

        
    #####################################################################################
    # Input sequence to selected the Pokémon at the provided position and confirm trade #
    #####################################################################################
    def selectpokemonTeams(self, melonWindow: Window, position):

        # Give focus on the window so it can accept inputs
        melonWindow.giveFocus()

        # Press Right once for odd positions
        if (position % 2 == 1):
            emukeyboard.pressButton("Right")

        # Press Down until we reach provided position
        for _ in range(position // 2):
            emukeyboard.pressButton("Down")

        # Select Pokémon
        emukeyboard.pressButton("A")

        # Wait until the confirmation dialog box opens
        waitUntil(melonWindow, img.confirmationboxBackground, visible = True)

        # Select "Trade"
        emukeyboard.pressButtons("Down", "A")


    ###################################################
    # Input sequence to go to Quit button and confirm #
    ###################################################
    def quitTradeMenu(self, melonWindow: Window):

        # Give focus on the window so it can accept inputs
        melonWindow.giveFocus()

        # Navigate to "Quit" and press A to confirm
        emukeyboard.pressButtons("Left", "Up", "A")

        # Wait until the confirmation dialog box opens
        waitUntil(melonWindow, img.confirmationboxBackground, visible = True)

        # Confirm Quit Trade
        emukeyboard.pressButton("A")


    ###############################################
    # Exit Union Room, save the game and close it #
    ###############################################
    def saveAndQuit(self, melonWindow: Window, inputs):

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


    ##############################################################################
    # Store backup saves in a variable if the variable was not already populated #
    #############################################################################
    def storeBackupSaves(self, backupMainSave, backupSecondarySave):
        if (not self.originalSave[self.mainGame] and backupMainSave):
            self.originalSave[self.mainGame] = backupMainSave
        if (not self.originalSave[self.secondaryGame] and backupSecondarySave):
            self.originalSave[self.secondaryGame] = backupSecondarySave
        

        
##########################################################################################
# Create Trade object and perform the whole trade process between the two provided games #
##########################################################################################
def performTrade(mainGame, mainGamePokemon, secondaryGame, secondaryGamePokemon):
    trade = Trade(mainGame, mainGamePokemon, secondaryGame, secondaryGamePokemon)
    
    if (trade.tradeProcess()):
        print("Trade success")
    else:
        print("Trade failed")


###################################################################################################################
# Wait until the image is visible or not visible, with a fail-safe that stops the process if running for too long #
###################################################################################################################
def waitUntil(window: Window, background: BackgroundTemplate, visible, mashButton = None, imagePosition = None, specificProcess = None):

    startTime = time.time()
    # print("Checking " + background.name + (" is visible" if visible else " is not visible"))

    # Wait until the image is visible (or not visible anymore)
    while (True):
        screenshot = window.captureWindowContent()

        # Condition is met : exit loop
        if (background.isOnScreen(screenshot, imagePosition) is visible):
            return True
        
        # If we spent more than a minute waiting (two minutes during actual trade), we are most likely stuck, stop the process
        elif (time.time() - startTime > (60 if specificProcess != SPECIFIC.TRADE_EVOLUTION else 120)):
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

                # Try to open menu every half of a second
                case SPECIFIC.OPEN_MENU:
                    emukeyboard.pressButton("X") 
                    waitFrames(30)

                # Trade evolution : mash A to skip dialog
                case SPECIFIC.TRADE_EVOLUTION:
                    mainWindowContent = MELONDS.mainWindow.captureWindowContent()
                    if (img.evolutionBackground.isOnScreen(mainWindowContent) or img.learnmoveBackground.isOnScreen(mainWindowContent)):
                        emukeyboard.pressButton("A")

                    secondaryWindowContent = MELONDS.secondaryWindow.captureWindowContent()
                    if (img.evolutionBackground.isOnScreen(secondaryWindowContent) or img.learnmoveBackground.isOnScreen(secondaryWindowContent)):
                        emukeyboard.pressButton("A")

                    waitFrames(FRAMES_TO_WAIT)

                # Mash B on both instances to skip Pal Pad dialogue and leave Trade Menu
                case SPECIFIC.LEAVE_TRADE_MENU:
                    MELONDS.mainWindow.giveFocus()
                    emukeyboard.pressButton("B")

                    MELONDS.secondaryWindow.giveFocus()
                    emukeyboard.pressButton("B")
        
        # If a button is provided : mash it until the above condition is met
        elif (mashButton):
            emukeyboard.pressButton(mashButton)
        
        # Default : just wait
        else:
            waitFrames(FRAMES_TO_WAIT)