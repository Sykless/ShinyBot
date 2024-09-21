import tkinter
import pyglet
import time
import os

from PIL import Image, ImageTk
from threading import Thread

from emu import BIZHAWK, MELONDS
from data import POKEMON_NAMES

# Allow code to use custom font
pyglet.options['win32_gdi_font'] = True
pyglet.font.add_file('pokemon-gen-4-regular.ttf')

DARK_BACKGROUND = "#232223"
POKEMON_FONT = "Pokemon\nGen 4 Regular"

class Dashboard():
    def __init__(self):
        self.root = None
        self.spriteLabels = []
        self.nameLabels = []
        self.chanceLabels = []
        self.updatesPending = False

    # Run the dashboard GUI in a separate thread
    def runDashboard(self):
        dashboardThread = Thread(target = self.initDashboard, daemon = True)
        dashboardThread.start()

    # Init window and add empty placeholders
    def initDashboard(self):
        EMULATOR = BIZHAWK if BIZHAWK.mainWindow else MELONDS
        dashboardTitle = "ShinyBot Dashboard - Pokémon Version " + EMULATOR.mainWindow.gameName

        # Initialize the main window
        self.root = tkinter.Tk()
        self.root.title(dashboardTitle)
        self.root.configure(bg = DARK_BACKGROUND)

        screenWidth = self.root.winfo_screenwidth()
        screenHeight = self.root.winfo_screenheight()

        # Fullscreen mode : hide title bar and stay on top
        if (EMULATOR.fullscreen):
            self.root.overrideredirect(True) # Hide title bar
            self.root.attributes('-topmost', True) # Keep on top
            windowWidth = screenWidth - EMULATOR.mainWindow.width
            windowHeight = EMULATOR.mainWindow.height
        else:
            windowWidth = screenWidth - EMULATOR.mainWindow.width + 2 * EMULATOR.mainWindow.borderSize
            windowHeight = EMULATOR.mainWindow.height - EMULATOR.mainWindow.titleBarHeight - EMULATOR.mainWindow.borderSize + EMULATOR.mainWindow.top

        # Set the window to full height with width depending on emulator window
        self.root.geometry(f'{windowWidth}x{windowHeight}+{screenWidth - windowWidth + EMULATOR.mainWindow.left}+{EMULATOR.mainWindow.top}')

        # Create frames for Pokémon encounters and bottom generic data
        encounterFrame = tkinter.Frame(self.root)
        encounterFrame.pack(fill = tkinter.BOTH, expand = True)
        encounterFrame.configure(bg = DARK_BACKGROUND)

        bottomFrame = tkinter.Frame(self.root, height = int(screenHeight * 0.2))
        bottomFrame.pack(fill = tkinter.BOTH, side = tkinter.BOTTOM)
        bottomFrame.configure(bg = DARK_BACKGROUND)

        # Create the encounter list layout with 12 empty rows
        for i in range(12):

            # Empty sprite placeholders
            spriteLabel = tkinter.Label(encounterFrame, image = None, bg = DARK_BACKGROUND)
            spriteLabel.grid(row=i, column = 0, padx = 10, pady = 0)
            self.spriteLabels.append(spriteLabel)

            # Empty name placeholders
            nameLabel = tkinter.Label(encounterFrame, text = "", font = (POKEMON_FONT, 12), fg = "white", bg = DARK_BACKGROUND)
            nameLabel.grid(row = i, column = 1, padx = 10, pady = 0)
            self.nameLabels.append(nameLabel)

            # Empty chance placeholders
            chanceLabel = tkinter.Label(encounterFrame, text = "", font = (POKEMON_FONT, 12), fg = "white", bg = DARK_BACKGROUND)
            chanceLabel.grid(row = i, column = 2, padx = 10, pady = 0)
            self.chanceLabels.append(chanceLabel)

        # Add a sample bottom section for generic game data
        genericLabel = tkinter.Label(bottomFrame, text="Generic Game Data: HP, Levels, etc.", font = (POKEMON_FONT, 12), fg = "white", bg = DARK_BACKGROUND)
        genericLabel.pack(pady = 0)

        # Associate Dashboard with current emulator and give dashboard focus once dashboard is open
        self.root.after(500, EMULATOR.setDashboardWindow)

        # Start the update loop on a dedicated thread
        self.updateThread = Thread(target = self.updateLoop, daemon = True)
        self.updateThread.start()

        # Launch dashboard
        self.root.mainloop()

    # Secondary loop needed to update the dashboard
    def updateLoop(self):
        while True:
            if self.updatesPending:
                self.root.after(0, self.processUpdates) # Process and apply updates in the main thread
            time.sleep(0.1)  # Avoid excessive CPU usage

    # Update the encounter list so the secondary thread can update the dashboard
    def updateEncounters(self, encounterList):
        self.encounterList = encounterList
        self.updatesPending = True

    # Clear dashboard and display encounter list with sprites, names and encounter chance
    def processUpdates(self):
        self.clearAllLines()
        self.updatesPending = False

        # If in a zone with encounters, display them
        if (self.encounterList):
            for i, (pokedexId, encounter) in enumerate(self.encounterList.items()):
                spriteImage = Image.open(os.path.join("sprites/nonshiny", str(pokedexId) + ".png"))
                spritePhoto = ImageTk.PhotoImage(spriteImage)

                self.spriteLabels[i].image = spritePhoto
                self.spriteLabels[i].config(image = spritePhoto)
                self.nameLabels[i].config(text = POKEMON_NAMES[pokedexId])
                self.chanceLabels[i].config(text = str(encounter.rate) + " %")

    # Reset dashboard
    def clearAllLines(self):
        for label in self.spriteLabels:
            label.image = None # Reset image references
            label.config(image = None)  # Clear image
        for label in self.nameLabels:
            label.config(text = "")  # Clear text
        for label in self.chanceLabels:
            label.config(text = "")  # Clear text

    # Exit the application
    def exitFullscreen(self, event):
        self.stopEvent.set()
        self.root.quit()