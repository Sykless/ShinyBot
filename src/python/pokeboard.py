from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QGridLayout, QSizePolicy)
from PyQt5.QtGui import QPixmap, QFontDatabase, QFont, QImage
from PyQt5.QtCore import Qt
import sys

import img
from emu import BIZHAWK, MELONDS
from data import POKEMON_NAMES

class PokemonDashboard(QWidget):
    def __init__(self):
        super().__init__()

        # Retrieve emulator currently running
        EMULATOR = BIZHAWK if BIZHAWK.mainWindow else MELONDS

        # Retrieve screen size
        app = QApplication.instance()
        screenWidth = app.primaryScreen().size().width()

        # Fullscreen mode : hide title bar and stay on top
        if (EMULATOR.fullscreen):
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
            windowWidth = screenWidth - EMULATOR.mainWindow.width
            windowHeight = EMULATOR.mainWindow.height
            windowPositionY = 0
        
        # Windowed mode : take borders and title bar into account
        else:
            windowWidth = screenWidth - EMULATOR.mainWindow.width + 2 * EMULATOR.mainWindow.borderSize
            windowHeight = EMULATOR.mainWindow.height - EMULATOR.mainWindow.titleBarHeight - EMULATOR.mainWindow.borderSize
            windowPositionY = EMULATOR.mainWindow.titleBarHeight + EMULATOR.mainWindow.top

        # Set up the main window title, size and position
        self.setWindowTitle("ShinyBot Dashboard - Pokémon Version " + EMULATOR.mainWindow.gameName)
        self.setGeometry(screenWidth - windowWidth, windowPositionY, windowWidth, windowHeight)

        # Set dark background color and white text for the whole widget
        self.setStyleSheet("background-color: #333333; color: white;")
        
        # Load custom Pokémon font
        fontId = QFontDatabase.addApplicationFont("pokemon-gen-4-regular.ttf")
        fontFamily = QFontDatabase.applicationFontFamilies(fontId)[0]
        customFont = QFont(fontFamily, 12)

        # Create main layout
        mainLayout = QVBoxLayout()
        mainLayout.setAlignment(Qt.AlignTop)
        mainLayout.setContentsMargins(0, 0, 0, 0)

        # Main QWidget, make sure it doesn't stretch with window size
        self.mainSection = QWidget()
        self.mainSection.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        # Dashboard layout : Array with 12 lines
        self.encountersLayout = QGridLayout()
        self.encountersLayout.setContentsMargins(0, 0, 0, 0)
        self.encountersLayout.setHorizontalSpacing(20)
        self.encountersLayout.setVerticalSpacing(10)
        self.encountersLayout.setContentsMargins(10, 10, 0, 0) # Add left/top margin

        averageHeigth = 0
        spriteList = []

        # First loop to retrieve every Pokémon sprite and calculate average sprite heigth
        for i in range(12):

            # Retrieve sprite and remove top/bottom transparent pixels
            croppedImage = img.cropSprite(f"sprites/nonshiny/{i + 1}.png")
            spritePixmap = QPixmap.fromImage(croppedImage)

            spriteList.append(spritePixmap)

            # Sum sprite heights
            averageHeigth += spritePixmap.height()

        # Calculate average sprite height
        averageHeigth //= 12

        # Second loop to display each encounter data
        for i in range(12):

            # Sprite column
            spriteLabel = QLabel()
            spriteLabel.setPixmap(spriteList[i])
            spriteLabel.setAlignment(Qt.AlignVCenter)
            self.encountersLayout.addWidget(spriteLabel, i, 0)

            # Pokémon name column
            nameLabel = QLabel(POKEMON_NAMES[i + 1])
            nameLabel.setFont(customFont)
            nameLabel.setAlignment(Qt.AlignVCenter)
            self.encountersLayout.addWidget(nameLabel, i, 1)

            # Encounter rate column
            numberLabel = QLabel(f"{i * 10}%")
            numberLabel.setFont(customFont)
            numberLabel.setAlignment(Qt.AlignVCenter)
            self.encountersLayout.addWidget(numberLabel, i, 2)

            # Update line height based on average cropped sprite height
            self.encountersLayout.setRowMinimumHeight(i, averageHeigth)

        self.mainSection.setLayout(self.encountersLayout)
        mainLayout.addWidget(self.mainSection)

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