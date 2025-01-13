from emu import BIZHAWK, MELONDS, PLATINE, DIAMANT, PERLE
from dashboard import Q_APP, DASHBOARD

from threading import Thread, Event
from multiprocessing import Process, Manager, Event

import sys

import action
import shinybot

class DashboardData:
    def __init__(self, encounterData):
        self.encounterData = encounterData
        self.dataReady = Event()

    def ready(self):
        self.dataReady.set()
        self.dataReady.clear()
        

class Main:
    def __init__(self):
        manager = Manager()
        self.emulatorWindow = manager.dict()
        self.emulatorReady = Event()
        self.dashboardReady = Event()
        self.dashboardData = DashboardData(manager.dict({"encounterTables": {}, "isCave": False}),)

    # Start every Shinybot component (Pokémon game in emulator, dashboard and main script)
    def run(self):
        
        # Start Shinybot main logic in a separate process
        shinybotProcess = Process(target = self.main)
        shinybotProcess.start()

        # Wait until emulator is ready
        self.emulatorReady.wait()

        # Init and display Dashboard
        DASHBOARD.initDashboard(self.emulatorWindow)
        DASHBOARD.show()

        # Give Dashboard focus so it appears on top
        DASHBOARD.showMinimized()
        DASHBOARD.showNormal()

        # Signal shinybot process that the dashboard is ready
        self.dashboardReady.set()

        # Process Dashboard updates in a dedicated thread
        updateDashboardThread = Thread(target = self.updateDashboard, daemon = True)
        updateDashboardThread.start()

        # Make sure the script stops when dashboard is closed
        sys.exit(Q_APP.exec_())

        
    # Separate thread on the main process to handle dashboard update
    def updateDashboard(self):
        while True:
            self.dashboardData.dataReady.wait()
            DASHBOARD.updateEncounters(self.dashboardData.encounterData)

    # Shinybot main app
    def main(self):

        # Launch BizHawk and make sure the game is ready to be run
        BIZHAWK.initEmulator(PLATINE, self.emulatorWindow, fullscreen = False)
        action.loadGame()

        # Wait for the dashboard to be ready to receive data
        self.emulatorReady.set()
        self.dashboardReady.wait()

        # Give back focus to emulator so it can receive keyboard instructions
        (BIZHAWK if BIZHAWK.mainWindow else MELONDS).mainWindow.giveFocus()

        # Launch main script
        shinybot.startShinybot(self.dashboardData)

# Launch this script to start the bot
if __name__ == "__main__":
    launcher = Main()
    launcher.run()