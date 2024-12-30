from emu import BIZHAWK, MELONDS, PLATINE, DIAMANT, PERLE
from pokeboard import PokemonDashboard

from threading import Thread, Event
from PyQt5.QtWidgets import QApplication

import sys

import action
import shinybot

class Main:
    def __init__(self):
        self.dashboardReady = Event()

    # Start every Shinybot component (Pokémon game in emulator, dashboard and main script)
    def run(self):
        # Launch BizHawk and make sure the game is ready to be run
        BIZHAWK.initEmulator(PLATINE, fullscreen = False)
        action.loadGame()

        # Init and display Dashboard
        app = QApplication(sys.argv)
        dashboard = PokemonDashboard()
        dashboard.show()

        # Give Dashboard focus so it appears on top
        dashboard.showMinimized()
        dashboard.showNormal()

        # Give back focus to emulator so it can receive keyboard instructions
        (BIZHAWK if BIZHAWK.mainWindow else MELONDS).mainWindow.giveFocus()

        # Start Shinybot main logic in a separate thread
        self.main()

        # Make sure the script stops when dashboard is closed
        sys.exit(app.exec_())

    # Shinybot main app
    def main(self):
        shinybotThread = Thread(target = shinybot.startShinybot, daemon = True)
        shinybotThread.start()

# Launch this script to start the bot
if __name__ == "__main__":
    launcher = Main()
    launcher.run()