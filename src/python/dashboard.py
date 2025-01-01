from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QGridLayout, QSizePolicy
from PyQt5.QtGui import QPixmap, QPainter, QFontDatabase, QFont, QBrush, QPalette, QColor
from PyQt5.QtCore import Qt, pyqtSignal
import sys

import img
from emu import BIZHAWK, MELONDS
from data import POKEMON_NAMES

class FilteredBackgroundWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAutoFillBackground(True)  # Use the QPalette as the base background

    def paintEvent(self, event):
        # Draw the default palette background
        super().paintEvent(event)

        # Add a semi-transparent dark filter
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Semi-transparent overlay color (RGBA)
        darkOverlay = QColor(0, 0, 0, 100)  # 100 = 40% transparency
        painter.fillRect(self.rect(), darkOverlay)
        painter.end()

class Dashboard(QWidget):
    encounterSignal = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.encounterSignal.connect(self.updateEncounters)

    def initDashboard(self):
        # Retrieve emulator currently running
        EMULATOR = BIZHAWK if BIZHAWK.mainWindow else MELONDS

        # Retrieve screen size
        app = QApplication.instance()
        screenWidth = app.primaryScreen().size().width()

        # Fullscreen mode : hide title bar and stay on top
        if (EMULATOR.fullscreen):
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
            self.windowWidth = screenWidth - EMULATOR.mainWindow.width
            self.windowHeight = EMULATOR.mainWindow.height
            windowPositionY = 0
        
        # Windowed mode : take borders and title bar into account
        else:
            self.windowWidth = screenWidth - EMULATOR.mainWindow.width + 2 * EMULATOR.mainWindow.borderSize
            self.windowHeight = EMULATOR.mainWindow.height - EMULATOR.mainWindow.titleBarHeight - EMULATOR.mainWindow.borderSize
            windowPositionY = EMULATOR.mainWindow.titleBarHeight + EMULATOR.mainWindow.top

        # Set up the main window title, size and position
        self.setWindowTitle("ShinyBot Dashboard - Pokémon Version " + EMULATOR.mainWindow.gameName)
        self.setGeometry(screenWidth - self.windowWidth, windowPositionY, self.windowWidth, self.windowHeight - 200)

        # Set dark background color and white text for the whole widget
        self.setStyleSheet("color: white") # ;background-color: #333333; 
        
        # Load custom Pokémon font
        fontId = QFontDatabase.addApplicationFont("pokemon-gen-4-regular.ttf")
        fontFamily = QFontDatabase.applicationFontFamilies(fontId)[0]
        customFont = QFont(fontFamily, 12)

        # Create main layout
        mainLayout = QVBoxLayout()
        mainLayout.setAlignment(Qt.AlignTop)
        mainLayout.setContentsMargins(0, 0, 0, 0)

        # Main QWidget, make sure it doesn't stretch with window size
        self.grassEncountersContainer = FilteredBackgroundWidget(self)
        self.grassEncountersContainer.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # Dashboard layout : Array with 12 lines
        self.grassEncountersLayout = QGridLayout()
        self.grassEncountersLayout.setContentsMargins(0, 0, 0, 0)
        self.grassEncountersLayout.setHorizontalSpacing(20)
        self.grassEncountersLayout.setVerticalSpacing(10)
        self.grassEncountersLayout.setContentsMargins(10, 0, 10, 0) # Default : no top/bottom margin

        # Create 12 empty slots for each possible encounter
        for i in range(12):

            # Sprite column
            spriteLabel = QLabel()
            spriteLabel.setAlignment(Qt.AlignVCenter)
            self.grassEncountersLayout.addWidget(spriteLabel, i, 0)

            # Pokémon name column
            nameLabel = QLabel()
            nameLabel.setFont(customFont)
            nameLabel.setAlignment(Qt.AlignVCenter)
            self.grassEncountersLayout.addWidget(nameLabel, i, 1)

            # Encounter rate column
            rateLabel = QLabel()
            rateLabel.setFont(customFont)
            rateLabel.setAlignment(Qt.AlignVCenter)
            self.grassEncountersLayout.addWidget(rateLabel, i, 2)

        self.grassEncountersContainer.setLayout(self.grassEncountersLayout)
        mainLayout.addWidget(self.grassEncountersContainer)

        # Add empty layout stretching to max available size so bottom section is actually at the very bottom
        mainLayout.addStretch()

        # Placeholder for bottom section
        self.bottomSection = QLabel("Bottom Section Placeholder")
        self.bottomSection.setFixedHeight(100)  # Adjustable height
        self.bottomSection.setAlignment(Qt.AlignCenter)
        self.bottomSection.setStyleSheet("background-color: rgba(255, 255, 255, 0.5);")
        mainLayout.addWidget(self.bottomSection)

        # Set the main layout
        self.setLayout(mainLayout)

    def sendEncountersData(self, encounterList):
        self.updateSignal.emit(encounterList)

    def setEncounterSprite(self, lineNumber, pokemonSprite):
        spriteLabel = self.grassEncountersLayout.itemAtPosition(lineNumber, 0).widget()

        if (pokemonSprite):
            spriteLabel.setPixmap(pokemonSprite)
        else:
            spriteLabel.clear()

    def setEncounterName(self, lineNumber, pokemonName):
        nameLabel = self.grassEncountersLayout.itemAtPosition(lineNumber, 1).widget()
        nameLabel.setText(pokemonName)

    def setEncounterRate(self, lineNumber, pokemonRate):
        rateLabel = self.grassEncountersLayout.itemAtPosition(lineNumber, 2).widget()
        rateLabel.setText(pokemonRate)

    def updateEncounters(self, encounterList):
        averageHeigth = 0
        spriteList = []

        # First loop to retrieve every Pokémon sprite and calculate average sprite heigth
        for i, (pokedexId, encounter) in enumerate(encounterList.items()):

            # Retrieve sprite and remove top/bottom transparent pixels
            croppedImage = img.cropSprite(f"sprites/nonshiny/{pokedexId}.png")
            spritePixmap = QPixmap.fromImage(croppedImage)

            spriteList.append(spritePixmap)

            # Sum sprite heights
            averageHeigth += spritePixmap.height()

        # Calculate average sprite height
        averageHeigth = averageHeigth // len(encounterList) if len(encounterList) else 0

        # Second loop to display each encounter data
        for i, (pokedexId, encounter) in enumerate(encounterList.items()):

            # Update Encounter sprite, name
            self.setEncounterSprite(i, spriteList[i])
            self.setEncounterName(i, POKEMON_NAMES[pokedexId])
            self.setEncounterRate(i, f"{encounter.rate} %")

            # Update line height based on average cropped sprite height
            self.grassEncountersLayout.setRowMinimumHeight(i, averageHeigth)

        # Final loop to clear the remaining lines
        for i in range(len(encounterList), 12):

            # Update Encounter sprite, name
            self.setEncounterSprite(i, None)
            self.setEncounterName(i, None)
            self.setEncounterRate(i, None)

        # Only add background if encounters are present
        self.grassEncountersContainer.setAutoFillBackground(len(encounterList) > 0)
            
    def createTiledBackground(self, tilePath):
        # Load the tile sprite
        tilePixmap = QPixmap(tilePath)
        if tilePixmap.isNull():
            raise ValueError(f"Tile image {tilePath} could not be loaded")

        # Create a QPixmap the size of the desired background
        backgroundPixmap = QPixmap(self.windowWidth, self.windowHeight)
        backgroundPixmap.fill(Qt.transparent)  # Optional, clear the pixmap

        # Use QPainter to tile the sprite
        painter = QPainter(backgroundPixmap)
        for x in range(0, self.windowWidth, tilePixmap.width()):
            for y in range(0, self.windowHeight, tilePixmap.height()):
                painter.drawPixmap(x, y, tilePixmap)
                
        painter.end()

        return backgroundPixmap

    def getPaletteBackground(self, widgetContainer, tileName):
        tiledBackground = self.createTiledBackground(f"sprites/background/{tileName}.png")

        # Set the tiled background on a QLabel
        backgroundLabel = QLabel()
        backgroundLabel.setPixmap(tiledBackground)

        # Cover palette with tile background
        palette = QPalette()
        palette.setBrush(widgetContainer.backgroundRole(), QBrush(tiledBackground))

        return palette


Q_APP = QApplication(sys.argv)
DASHBOARD = Dashboard()