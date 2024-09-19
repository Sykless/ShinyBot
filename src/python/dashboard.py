import tkinter as tk
import pyglet
import time
import os

from PIL import Image, ImageTk
from threading import Thread

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
        self.running = True

    # Run the dashboard GUI in a separate thread
    def runDashboard(self):
        dashboardThread = Thread(target = self.dashboardThread, daemon = True)
        dashboardThread.start()

    # Start the GUI event loop
    def dashboardThread(self):
        self.initDashboard()
        self.root.mainloop()

    # Init window and add empty placeholders
    def initDashboard(self):

        # Initialize the main window
        self.root = tk.Tk()
        self.root.title("Pokémon Encounter Dashboard")
        self.root.configure(bg = DARK_BACKGROUND)

        # Hide title bar
        # root.overrideredirect(True)

        # Set the window to full height but smaller width
        screenWidth = self.root.winfo_screenwidth()
        screenHeight = self.root.winfo_screenheight()
        windowWidth = int(screenWidth / 2)
        self.root.geometry(f'{windowWidth} x {screenHeight} + {screenWidth - windowWidth} + 0')
        self.root.attributes('-topmost', True)

        # Create frames for Pokémon encounters and bottom generic data
        encounterFrame = tk.Frame(self.root)
        encounterFrame.pack(fill=tk.BOTH, expand = True)
        encounterFrame.configure(bg = DARK_BACKGROUND)

        bottomFrame = tk.Frame(self.root, height = int(screenHeight * 0.2))
        bottomFrame.pack(fill=tk.BOTH, side=tk.BOTTOM)
        bottomFrame.configure(bg = DARK_BACKGROUND)

        # Create the encounter list layout with 12 empty rows
        for i in range(12):

            # Empty sprite placeholders
            spriteLabel = tk.Label(encounterFrame, image = None, bg = DARK_BACKGROUND)
            spriteLabel.grid(row=i, column=0, padx=10, pady=0)
            self.spriteLabels.append(spriteLabel)

            # Empty name placeholders
            nameLabel = tk.Label(encounterFrame, text = "", font = (POKEMON_FONT, 12), fg = "white", bg = DARK_BACKGROUND)
            nameLabel.grid(row=i, column=1, padx=10, pady=0)
            self.nameLabels.append(nameLabel)

            # Empty chance placeholders
            chanceLabel = tk.Label(encounterFrame, text = "", font=(POKEMON_FONT, 12), fg = "white", bg = DARK_BACKGROUND)
            chanceLabel.grid(row=i, column=2, padx=10, pady=0)
            self.chanceLabels.append(chanceLabel)

        # Add a sample bottom section for generic game data
        genericLabel = tk.Label(bottomFrame, text="Generic Game Data: HP, Levels, etc.", font = (POKEMON_FONT, 12), fg = "white", bg = DARK_BACKGROUND)
        genericLabel.pack(pady = 0)

        # Bind the Escape key to exit full-screen
        self.root.bind('<Escape>', self.exitFullscreen)

        # Start the update loop
        self.updateThread = Thread(target = self.updateLoop, daemon = True)
        self.updateThread.start()

    # Secondary loop needed to update the dashboard
    def updateLoop(self):
        while self.running:
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