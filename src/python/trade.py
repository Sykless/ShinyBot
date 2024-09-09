import action
from emu import BIZHAWK, MELONDS

def initTrade(currentGame, tradeGame):

    # Perform the same init setup on both games
    for game in [currentGame, tradeGame]:
    
        # Make sure current instance is loaded
        BIZHAWK.initEmulator(game)
        action.loadGame()

        # Go to a specific cell in front of Union Room and save the game
        if (not action.setupTradePosition()):
            print("Couldn't save on version " + game + ", traded canceled")
            return False

        # Close current instance
        BIZHAWK.mainWindow.closeWindow()

    # Both games ready to trade
    return True