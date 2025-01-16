

import io
import os
import cv2
import mmap
import time
import numpy

from PIL import Image, ImageFile
from PyQt5.QtGui import QImage
from PyQt5.QtCore import Qt

from emu import BIZHAWK, MELONDS
from utils import waitFrames

# https://stackoverflow.com/questions/42462431/oserror-broken-data-stream-when-reading-image-file
ImageFile.LOAD_TRUNCATED_IMAGES = True

# Most important method : retrieve game screenshot from emulator memory
def getScreenshot():
    while True:
        screenshotBytes = io.BytesIO(mmap.mmap(0, 64000, "screenshot"))
        
        try:
            screenshotImage = Image.open(screenshotBytes)
            screenshotImage.save("bizhawk.png")

            # Convert RGB screenshot to BGR in order to be cv2-readable
            return cv2.cvtColor(numpy.array(screenshotImage), cv2.COLOR_RGB2BGR)
        except Exception as e:
            waitFrames(1) # Check one frame later after memory has been updated

def saveScreenshot(screenshot, filename):
    cv2.imwrite(os.path.join("backup/screenshots", time.strftime('%Y%m%d-%H%M%S') + "-" + filename + ".png"), screenshot)

def displayScreenshot(screenshot):
    cv2.imshow("image", screenshot)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


# Template class to search a specific image at a specific position
class Template:
    def __init__(self, name, positionX, positionY, width, height, threshold, mask = None):
        self.image = cv2.imread("data/img/" + name + ".png")
        self.mask = mask and cv2.imread("data/img/" + name + "-mask.png")
        self.name = name

        self.positionX = positionX
        self.positionY = positionY
        self.width = width
        self.height = height
        self.threshold = threshold

    def getSubScreenshot(self, screenshot):
        return screenshot[
                self.positionY:self.positionY + self.height,
                self.positionX:self.positionX + self.width]

    def isOnScreen(self, screenshot = None):
        return isTemplateInImage(self.getSubScreenshot(screenshot if screenshot is not None else getScreenshot()),
                                 self.image, self.threshold, templatemask = self.mask)[0]

    def waitUntilNotVisible(self):
        framesNotVisible = 0

        # Loop until the image is no longer visible
        while True:
            
            # Increment counter when the image is not visible
            if (not self.isOnScreen()):
                framesNotVisible += 1
            else:
                framesNotVisible = 0

            # Screenshot can be partially cropped so we only stop after 3 frames in a row
            if (framesNotVisible == 3):
                break

            # Only check screenshot once every frame
            waitFrames(1)


# Templates used for images different in the other Sinnoh games
class GameTemplate:
    def __init__(self, platinumTemplate, diamondPearlTemplate):
        self.templates = {
            "Platine": platinumTemplate,
            "Diamant": diamondPearlTemplate,
            "Perle": diamondPearlTemplate,
        }

    def isOnScreen(self, screenshot = None):
        return (self.templates[BIZHAWK.mainWindow.gameName if BIZHAWK.mainWindow else "Platine"]).isOnScreen(screenshot)
    
    def waitUntilNotVisible(self):
        return (self.templates[BIZHAWK.mainWindow.gameName if BIZHAWK.mainWindow else "Platine"]).waitUntilNotVisible()


# Templates used on MelonDS when we can only use the window screenshot, not knowing the screen resolution
class BackgroundTemplate:
    def __init__(self, name, xFractionStart, xFractionEnd, yFractionStart, yFractionEnd):
        self.name = name
        self.image = cv2.imread("data/img/background/" + name + ".png")

        # We don't know the MelonDS screenshot size so we're working with coordinate fractions
        self.xFractionStart = xFractionStart
        self.xFractionEnd = xFractionEnd
        self.yFractionStart = yFractionStart
        self.yFractionEnd = yFractionEnd
    
    def __eq__(self, other):
        return isinstance(other, BackgroundTemplate) and self.name == other.name
    
    def getSubScreenshot(self, screenshot, imageLocation):
        screenshotHeight = len(screenshot)
        screenshotWidth = len(screenshot[0])

        # If a specific image location is provided, crop the screenshot around this location
        if (imageLocation):
            subScreenshot = screenshot[
                    int(imageLocation[2] * screenshotHeight) : int(imageLocation[3] * screenshotHeight),
                    int(imageLocation[0] * screenshotWidth) : int(imageLocation[1] * screenshotWidth)]
            
        # Default : use object default image location
        else:
            subScreenshot = screenshot[
                    int(self.yFractionStart * screenshotHeight) : int(self.yFractionEnd * screenshotHeight),
                    int(self.xFractionStart * screenshotWidth) : int(self.xFractionEnd * screenshotWidth)]
        
        arrayScreenshot = numpy.array(subScreenshot, dtype=numpy.uint8)
        image = Image.fromarray(arrayScreenshot)
        image.save("sub.png")

        return subScreenshot
    
    def isOnScreen(self, windowContent, imageLocation = None):
        return isTemplateInImage(self.getSubScreenshot(windowContent, imageLocation), self.image)[0]


# Specific type of Template that returns the position of a cursor on the screen
class PositionTemplate:
    def __init__(self, name, linesNumber = None, menuWidth = None, width = None, height = None, mask = None):
        self.name = name
        self.image = cv2.imread("data/img/" + name + ".png")
        self.mask = mask and cv2.imread("data/img/" + name + "-mask.png")
        
        self.linesNumber = linesNumber
        self.menuWidth = menuWidth
        self.width = width
        self.height = height

    # Returns cursor position depending on the template image
    def getCursorPosition(self, screenshot = None):
        screenshot = screenshot if screenshot is not None else getScreenshot()

        if (self.name == "menu/map-cursor"):
            return self.__getMapCursorPosition(screenshot)
        elif (self.name == "menu/menu-selector"):
            return self.__getMenuPosition(screenshot)
        
    # Returns cursor position on the map
    def __getMapCursorPosition(self, screenshot):
        selectorInImage, location = isTemplateInImage(screenshot[0:0+170 , 20:20+216], self.image, 1, self.mask)

        if (selectorInImage):
            x = round((location[0] - 6) * 27 / 189)
            y = round((location[1] - 2) * 22 / 154)

            return x,y
        else:
            return None

    # Returns X menu cursor position
    def __getMenuPosition(self, screenshot):
        selectorInImage, location = isTemplateInImage(screenshot[8:8+168 , 158:158+3], self.image)

        if (selectorInImage):
            return round(location[1] / 24) + 1
        else:
            return 0


# Bag
bagTouchscreen = Template("bag/bag-menu-touchscreen", 0, 192, 256, 192, 1, mask = True)
bagItemSelector = Template("bag/bag-item-selector", 105, 15, 158, 113, 1, mask = True)
cdDouteuxSelected = Template("bag/cd-douteux-selected", 106, 15, 64, 113, 1)
closeBagMenuSelected = Template("bag/close-bag-selected", 106, 15, 42, 113, 1)
crocRasoirSelected = Template("bag/croc-rasoir-selected", 106, 15, 67, 113, 1)
griffeRasoirSelected = Template("bag/griffe-rasoir.selected", 106, 15, 68, 113, 1)
tissuFaucheSelected = Template("bag/tissu-fauche-selected", 106, 15, 73, 113, 1)

# Battle
cancelAttack = Template("battle/cancel-attack", 104, 365, 49, 10, 1)
insideBag = Template("battle/inside-battle-bag-menu", 174, 243, 35, 10, 1)
insideBalls = Template("battle/inside-battle-balls-menu", 113, 359, 30, 10, 1)
newPokedexEntry = Template("battle/new-pokedex-entry", 110, 3, 42, 10, 1)
pageOne = Template("battle/page-1", 183, 359, 6, 10, 1)
pageTwo = Template("battle/page-2", 183, 359, 6, 10, 1)
pageThree = Template("battle/page-3", 183, 359, 6, 10, 1)
pageFour = Template("battle/page-4", 183, 359, 6, 10, 1)
pokeballLastUsed = Template("battle/pokeball-last-used", 11, 357, 18, 18, 10)
returnButton = Template("battle/return-button", 223, 352, 26, 26, 10)
runaway = Template("battle/runaway", 111, 365, 35, 10, 1)
useItem = Template("battle/use-item", 80, 361, 46, 10, 1, mask = True)

# Dialog
confirmationBox = Template("dialog/confirmation-box", 200, 107, 25, 10, 10)
dialogConfirm = Template("dialog/dialog-confirm", 245, 173, 5, 8, 1, mask = True)
noDialog = Template("dialog/no-dialog", 16, 155, 10, 10, 1)
noFishFoundDialog = Template("dialog/no-fish-found", 16, 155, 76, 10, 1)
saveConfirmation = Template("dialog/save-confirmation", 16, 155, 225, 12, 1)
whiteBanner = Template("dialog/white-banner", 177, 170, 50, 10, 1)

# Menu
mapCursor = PositionTemplate("menu/map-cursor", mask = True)
menuCursor = PositionTemplate("menu/menu-selector")
pokemonMenu = Template("menu/pokemon-menu", 48, 192, 160, 192, 1)
worldMap = Template("menu/world-map", 103, 275, 50, 51, 1)

# Other
exclamationBox = Template("other/exclamation-box", 113, 57, 30, 25, 1)
hmAnimation = GameTemplate(
    platinumTemplate = Template("other/hm-animation", 104, 93, 48, 6, 1),
    diamondPearlTemplate = Template("other/hm-animation-diamondpearl", 104, 93, 48, 6, 1)
)
journalFooter = Template("other/journal-footer", 9, 176, 238, 4, 1)
poketch = GameTemplate(
    platinumTemplate = Template("other/poketch", 224, 225, 32, 126, 1),
    diamondPearlTemplate = Template("other/poketch-diamondpearl", 217, 278, 33, 92, 1)
)

# Background (melonDS)
blackBackground = BackgroundTemplate("black", 0, 1, 0.5, 1)
confirmationboxBackground = BackgroundTemplate("confirmationbox", 0.75, 1, 0.25, 0.4)
dialogboxBackground = BackgroundTemplate("dialogbox", 0, 1, 0.25, 0.43)
evolutionBackground = BackgroundTemplate("evolution", 0, 1, 0.5, 1)
journalBackground = BackgroundTemplate("journal", 0, 1, 0.25, 0.5)
learnmoveBackground = BackgroundTemplate("learnmove", 0, 1, 0.5, 1)
selectionboxBackground = BackgroundTemplate("selectionbox", 0.5, 1, 0, 0.4)
tradeBackground = BackgroundTemplate("trade", 0.5, 1, 0.5, 1)
whiteBackground = BackgroundTemplate("white", 0, 0.5, 0, 0.5)
TOPSCREEN = (0, 1, 0, 0.5)
BOTTOMSCREEN = (0, 1, 0.5, 1)


# Check if an image is present in the screenshot
def isTemplateInImage(image, templateImage, threshold = 1, templatemask = None):

    # Template matching using TM_SQDIFF : Perfect match -> minimum value around 0.0
    result = cv2.matchTemplate(image, templateImage, cv2.TM_SQDIFF, mask = templatemask)

    # Get best match
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    # Returns a boolean indicating if the template is present in the image, and its location
    return min_val <= threshold, min_loc


# Returns current bag item page in battle
def getPageNumber(screenshot):
    if (pageOne.isOnScreen(screenshot)): return 1
    elif (pageTwo.isOnScreen(screenshot)): return 2
    elif (pageThree.isOnScreen(screenshot)): return 3
    elif (pageFour.isOnScreen(screenshot)): return 4
    else: return None


# Crops top/bottom transparent pixels and scale the sprite to the dashboard height
def resizeDashboardSprite(imagePath, scale):
    image = QImage(imagePath)

    if image.isNull():
        return QImage()
    
    # Scale image to dashboard height
    scaledImage = image.scaled(scale, scale, aspectRatioMode = Qt.IgnoreAspectRatio, transformMode = Qt.SmoothTransformation)
    topPosition = 0
    bottomPosition = scaledImage.height() - 1

    # Find first non-transparent row from the top
    for y in range(scaledImage.height()):
        for x in range(scaledImage.width()):
            if scaledImage.pixelColor(x, y).alpha() > 0:
                topPosition = y
                break
        else:
            continue
        break

    # Find first non-transparent row from the bottom
    for y in range(scaledImage.height() - 1, -1, -1):
        for x in range(scaledImage.width()):
            if scaledImage.pixelColor(x, y).alpha() > 0:
                bottomPosition = y
                break
        else:
            continue
        break

    # Crop image to remove transparent pixels
    return scaledImage.copy(0, topPosition, scaledImage.width(), bottomPosition - topPosition + 1)