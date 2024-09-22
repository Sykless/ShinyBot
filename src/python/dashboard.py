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
            spriteLabel.grid(row=i, column = 0, padx = 10, pady = 10)
            self.spriteLabels.append(spriteLabel)

            # Empty name placeholders
            nameLabel = tkinter.Label(encounterFrame, text = "", font = (POKEMON_FONT, 12), fg = "white", bg = DARK_BACKGROUND)
            nameLabel.grid(row = i, column = 1, padx = 10, pady = 10)
            self.nameLabels.append(nameLabel)

            # Empty chance placeholders
            chanceLabel = tkinter.Label(encounterFrame, text = "", font = (POKEMON_FONT, 12), fg = "white", bg = DARK_BACKGROUND)
            chanceLabel.grid(row = i, column = 2, padx = 10, pady = 10)
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
        self.updatesPending = False
        averageHeigth = 0
        spriteList = []
        
        # Clear all lines by resetting content
        for i in range(len(self.spriteLabels)):
            self.spriteLabels[i].image = None
            self.spriteLabels[i].config(image = None)
            self.nameLabels[i].config(text = "")
            self.chanceLabels[i].config(text = "")

        # If in a zone with encounters, display Pokémon sprites, names and encounter chance
        if self.encounterList:

            # First loop to retrieve every Pokémon sprite and calculate average sprite heigth
            for i, (pokedexId, encounter) in enumerate(self.encounterList.items()):

                # Load sprite
                originalSprite = Image.open(os.path.join("sprites/nonshiny", str(pokedexId) + ".png")).convert("RGBA")

                # Crop top/bottom transparent pixels
                croppedCoordinates = originalSprite.getbbox()
                spriteImage = originalSprite.crop((0, croppedCoordinates[1], originalSprite.width - 1, croppedCoordinates[3]))
                spriteList.append(spriteImage)

                # Sum sprite heights
                averageHeigth += spriteImage.height

            # Calculate average sprite heigth
            averageHeigth //= len(self.encounterList)

            # Second loop to display each encounter data
            for i, (pokedexId, encounter) in enumerate(self.encounterList.items()):

                # Convert sprite to Tkinter photo
                spritePhoto = ImageTk.PhotoImage(spriteList[i])

                # Display Pokémon sprite and set row heigth to sprite heigth (or average heigth if too low)
                self.spriteLabels[i].image = spritePhoto
                self.spriteLabels[i].config(image = spritePhoto, height = max(averageHeigth, spriteList[i].height))

                # Display Pokémon name and encounter chance
                self.nameLabels[i].config(text = POKEMON_NAMES[pokedexId])
                self.chanceLabels[i].config(text = f"{encounter.rate} %")

                # Place in grid if not already (ensures visibility)
                self.spriteLabels[i].grid(row = i, column = 0, padx = 10, pady = (10 if i else 20, 10))
                self.nameLabels[i].grid(row = i, column = 1, padx = 10, pady = (10 if i else 20, 10), sticky = 'w')
                self.chanceLabels[i].grid(row = i, column = 2, padx = 10, pady = (10 if i else 20, 10), sticky = 'w')

    # Exit the application
    def exitFullscreen(self, event):
        self.stopEvent.set()
        self.root.quit()