from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QGridLayout, QSizePolicy, QSpacerItem
from PyQt5.QtGui import QPixmap, QPainter, QFontDatabase, QFont, QBrush, QPalette, QColor
from PyQt5.QtCore import Qt, pyqtSignal
from itertools import chain
import sys

import img
from emu import BIZHAWK, MELONDS
from data import POKEMON_NAMES

SPRITE_COLUMN = 0
NAME_COLUMN = 1
RATE_COLUMN = 2
ITEM_COLUMN = 3

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

        # Set white text for the whole widget
        self.setStyleSheet("color: white")
        
        # Load custom Pokémon font
        fontId = QFontDatabase.addApplicationFont("pokemon-gen-4-regular.ttf")
        fontFamily = QFontDatabase.applicationFontFamilies(fontId)[0]
        self.pokemonFont = QFont(fontFamily, self.windowHeight // 80)

        # Create main layout
        mainLayout = QVBoxLayout()
        mainLayout.setContentsMargins(0, 0, 0, 0)

        # Create encounters (walk + water) layout
        encountersLayout = QHBoxLayout()
        encountersLayout.setContentsMargins(0, 0, 0, 0)
        encountersLayout.setSpacing(0)

        # Init encounters containers that fills all space and sets a custom backgroup
        self.walkEncountersContainer = self.initEncounterContainer("grass")
        self.waterEncountersContainer = self.initEncounterContainer("water")

        # Init encounters layouts that setup 12 rows for potential encounters
        self.walkEncountersLayout = self.initEncounterLayout()
        self.waterEncountersLayout = self.initEncounterLayout()

        # Add walk/water encounters layouts to the main dashboard
        self.walkEncountersContainer.setLayout(self.walkEncountersLayout)
        self.waterEncountersContainer.setLayout(self.waterEncountersLayout)
        encountersLayout.addWidget(self.walkEncountersContainer)
        encountersLayout.addWidget(self.waterEncountersContainer)
        mainLayout.addLayout(encountersLayout)

        # Placeholder for bottom section
        self.bottomSection = QLabel("Bottom Section Placeholder")
        self.bottomSection.setFixedHeight(100)  # Adjustable height
        self.bottomSection.setAlignment(Qt.AlignCenter)
        self.bottomSection.setStyleSheet("background-color: rgba(255, 255, 255, 0.5);")
        self.bottomSection.hide()
        mainLayout.addWidget(self.bottomSection)

        # Set the main layout
        self.setLayout(mainLayout)

    def initEncounterContainer(self, tileType):
        encountersContainer = FilteredBackgroundWidget(self)

        # Take all available size
        encountersContainer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Apply grass/water background
        encountersContainer.defaultBackground = self.getPaletteBackground(encountersContainer, tileType)
        encountersContainer.setPalette(encountersContainer.defaultBackground)

        # Set another type of background for cave encounters
        if (tileType == "grass"):
            encountersContainer.caveBackground = self.getPaletteBackground(encountersContainer, "cave")

        return encountersContainer

    def initEncounterLayout(self):
        encountersLayout = QGridLayout()
        encountersLayout.setContentsMargins(10, 10, 10, 0) # Default : no top/bottom margin
        encountersLayout.setHorizontalSpacing(20)
        encountersLayout.setVerticalSpacing(10)

        # Create 12 empty slots for each possible encounter
        for i in range(12):

            # Sprite column
            spriteLabel = QLabel()
            spriteLabel.setAlignment(Qt.AlignVCenter)
            encountersLayout.addWidget(spriteLabel, i, 0)

            # Pokémon name column
            nameLabel = QLabel()
            nameLabel.setFont(self.pokemonFont)
            nameLabel.setAlignment(Qt.AlignVCenter)
            encountersLayout.addWidget(nameLabel, i, 1)

            # Encounter rate column
            rateLabel = QLabel()
            rateLabel.setFont(self.pokemonFont)
            rateLabel.setAlignment(Qt.AlignVCenter)
            encountersLayout.addWidget(rateLabel, i, 2)

            # Item column
            itemLabel = QLabel()
            itemLabel.setAlignment(Qt.AlignVCenter)
            encountersLayout.addWidget(itemLabel, i, 3)

        # Add a spacer in the last row to fill the rest with empty space
        spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding)
        encountersLayout.addItem(spacer, encountersLayout.rowCount(), encountersLayout.columnCount())

        return encountersLayout
    
    def sendEncountersData(self, encounterList):
        self.updateSignal.emit(encounterList)

    def setWidgetText(self, encounterLayout, columnNumber, lineNumber, textValue):
        textWidget = encounterLayout.itemAtPosition(lineNumber, columnNumber).widget()
        textWidget.setText(textValue)

    def setWidgetImage(self, encounterLayout, columnNumber, lineNumber, image):
        imageWidget = encounterLayout.itemAtPosition(lineNumber, columnNumber).widget()

        if (image):
            imageWidget.setPixmap(image)
        else:
            imageWidget.clear()

    def updateEncounters(self, encounterTables, isCave):

        # Concatenate all water encounters in one list
        if (encounterTables):
            encounterLists = [(("walk", f"walk_{pokedexId}", encounter) for pokedexId, encounter in encounterTables["walkTable"].items()),
                            chain(
                                (("surf", f"surf_{pokedexId}", encounter) for pokedexId, encounter in encounterTables["surfTable"].items()),
                                (("old-rod", f"oldRod_{pokedexId}", encounter) for pokedexId, encounter in encounterTables["oldRodTable"].items()),
                                (("good-rod", f"goodRod_{pokedexId}", encounter) for pokedexId, encounter in encounterTables["goodRodTable"].items()),
                                (("super-rod", f"superRod_{pokedexId}", encounter) for pokedexId, encounter in encounterTables["superRodTable"].items()))]
        else:
            encounterLists = [{},{}]

        # One loop for walk encounters, one loop for water encounters
        for isWater in range(2):
            encounterList = list(encounterLists[isWater])
            encounterLayout = self.waterEncountersLayout if isWater else self.walkEncountersLayout
            averageHeigth = 0
            spriteList = []

            # First loop to retrieve every Pokémon sprite and calculate average sprite heigth
            for i, (source, uniqueId, encounter) in enumerate(encounterList):

                # Retrieve sprite and remove top/bottom transparent pixels
                croppedImage = img.resizeSprite(f"sprites/nonshiny/{encounter.pokedexId}.png", self.windowHeight // 11)
                spritePixmap = QPixmap.fromImage(croppedImage)

                spriteList.append(spritePixmap)

                # Sum sprite heights
                averageHeigth += spritePixmap.height()

            # Calculate average sprite height
            averageHeigth = averageHeigth // len(encounterList) if len(encounterList) else 0

            # Second loop to display each encounter data
            for i, (source, uniqueId, encounter) in enumerate(encounterList):

                # Update Encounter sprite, name
                self.setWidgetImage(encounterLayout, SPRITE_COLUMN, i, spriteList[i])
                self.setWidgetText(encounterLayout, NAME_COLUMN, i, POKEMON_NAMES[encounter.pokedexId])
                self.setWidgetText(encounterLayout, RATE_COLUMN, i, f"{encounter.rate} %")
                self.setWidgetImage(encounterLayout, ITEM_COLUMN, i, QPixmap(f"sprites/items/{source}.png"))

                # Update line height based on average cropped sprite height
                encounterLayout.setRowMinimumHeight(i, averageHeigth)

            # Final loop to clear the remaining lines
            for i in range(len(encounterList), 12):

                # Update Encounter sprite, name
                self.setWidgetImage(encounterLayout, SPRITE_COLUMN, i, None)
                self.setWidgetText(encounterLayout, NAME_COLUMN, i, None)
                self.setWidgetText(encounterLayout, RATE_COLUMN, i, None)
                self.setWidgetImage(encounterLayout, ITEM_COLUMN, i, None)

        # Update background if zone is outside or in a cave
        if (isCave):
            self.walkEncountersContainer.setPalette(self.walkEncountersContainer.caveBackground)
        else:
            self.walkEncountersContainer.setPalette(self.walkEncountersContainer.defaultBackground)
            
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