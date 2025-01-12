

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

class Template:
    def __init__(self, name, positionX, positionY, width, height, threshold, mask = None):
        self.image = cv2.imread("src/python/data/img/" + name + ".png")
        self.mask = mask and cv2.imread("src/python/data/img/" + name + "-mask.png")
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
    
    def getPositionOnScreen(self,screenshot):
        return getTemplatePosition(screenshot, self.image, cv2.TM_SQDIFF, templatemask = self.mask)

    def getNormedPositionOnScreen(self,screenshot):
        return getTemplatePosition(screenshot, self.image, cv2.TM_SQDIFF_NORMED, templatemask = self.mask)

    def isOnScreen(self, screenshot):
        return isTemplateInImage(self.getSubScreenshot(screenshot),
                                 self.image, self.threshold, templatemask = self.mask)[0]

class GameTemplate:
    def __init__(self, platinumTemplate, diamondPearlTemplate):
        self.templates = {
            "Platine": platinumTemplate,
            "Diamant": diamondPearlTemplate,
            "Perle": diamondPearlTemplate,
        }

    def isOnScreen(self, screenshot):
        return (self.templates[BIZHAWK.mainWindow.gameName if BIZHAWK.mainWindow else "Platine"]).isOnScreen(screenshot)
    
class BackgroundTemplate:
    def __init__(self, name, xFractionStart, xFractionEnd, yFractionStart, yFractionEnd):
        self.name = name
        self.image = cv2.imread("src/python/data/img/background/" + name + ".png")

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


ITEM_CURRENT_LOCATION_SELECTOR = cv2.imread('src/python/data/img/item-current-location-selector.png')
MENU_CURRENT_LOCATION_SELECTOR = cv2.imread('src/python/data/img/menu-selector.png')
MAP_CURSOR_ICON = cv2.imread('src/python/data/img/map-cursor.png')
MAP_CURSOR_ICON_MASK = cv2.imread('src/python/data/img/map-cursor-mask.png')

BAG_SECTION_SELECTION = {}
BAG_SECTION_SELECTION["linesNumber"] = 2
BAG_SECTION_SELECTION["menuWidth"] = 214
BAG_SECTION_SELECTION["width"] = 128
BAG_SECTION_SELECTION["height"] = 72

ITEM_SELECTION = {}
ITEM_SELECTION["linesNumber"] = 3
ITEM_SELECTION["menuWidth"] = 40
ITEM_SELECTION["width"] = 128
ITEM_SELECTION["height"] = 48

bagTouchscreen = Template("bag-menu-touchscreen", 0, 192, 256, 192, 1, mask = True)
bagItemSelector = Template("bagitem-selector", 105, 15, 158, 113, 1, mask = True)
cdDouteuxSelected = Template("cd-douteux-selected", 106, 15, 64, 113, 1)
tissuFaucheSelected = Template("tissu-fauche-selected", 106, 15, 73, 113, 1)
griffeRasoirSelected = Template("griffe-rasoir.selected", 106, 15, 68, 113, 1)
crocRasoirSelected = Template("croc-rasoir-selected", 106, 15, 67, 113, 1)
closeBagMenuSelected = Template("close-bag-selected", 106, 15, 42, 113, 1)

battleTouchscreen = Template("battle-touchscreen", 0, 192, 256, 192, 1, mask = True)
exclamationBox = Template("exclamation-box", 113, 57, 30, 25, 1)
noFishFoundDialog = Template("no-fish-found", 16, 155, 76, 10, 1)
pokemonMenu = Template("pokemon-menu", 48, 192, 160, 192, 1)
journalFooter = Template("journal-footer", 9, 176, 238, 4, 1)
runaway = Template("runaway", 100, 354, 56, 30, 1)
worldMap = Template("world-map", 103, 275, 50, 51, 1)
insideBag = Template("inside-battle-bag-menu", 135, 208, 114, 58, 1)
insideBalls = Template("inside-battle-balls-menu", 91, 348, 74, 32, 1)
pokeballLastUsed = Template("pokeball-last-used", 8, 352, 192, 26, 1)
saveConfirmation = Template("save-confirmation", 16, 155, 225, 12, 1)
whiteBanner = Template("white-banner", 177, 170, 50, 10, 1)
poketch = GameTemplate(
    platinumTemplate = Template("poketch", 224, 225, 32, 126, 1),
    diamondPearlTemplate = Template("poketch-diamondpearl", 217, 278, 33, 92, 1)
)
hmAnimation = GameTemplate(
    platinumTemplate = Template("hm-animation", 104, 93, 48, 6, 1),
    diamondPearlTemplate = Template("hm-animation-diamondpearl", 104, 93, 48, 6, 1)
)

firstPage = Template("first-page", 183, 359, 6, 10, 1)
secondPage = Template("second-page", 183, 359, 6, 10, 1)
thirdPage = Template("third-page", 183, 359, 6, 10, 1)
useItem = Template("use-item", 8, 351, 192, 27, 1)
newPokedexEntry = Template("new-pokedex-entry", 0, 0, 241, 15, 1)

# Templates used on MelonDS when we can only use the window screenshot, not knowing the screen resolution
TOPSCREEN = (0, 1, 0, 0.5)
BOTTOMSCREEN = (0, 1, 0.5, 1)
whiteBackground = BackgroundTemplate("white", 0, 0.5, 0, 0.5)
blackBackground = BackgroundTemplate("black", 0, 1, 0.5, 1)
dialogboxBackground = BackgroundTemplate("dialogbox", 0, 1, 0.25, 0.43)
journalBackground = BackgroundTemplate("journal", 0, 1, 0.25, 0.5)
selectionboxBackground = BackgroundTemplate("selectionbox", 0.5, 1, 0, 0.4)
confirmationboxBackground = BackgroundTemplate("confirmationbox", 0.75, 1, 0.25, 0.4)
tradeBackground = BackgroundTemplate("trade", 0.5, 1, 0.5, 1)
evolutionBackground = BackgroundTemplate("evolution", 0, 1, 0.5, 1)
learnmoveBackground = BackgroundTemplate("learnmove", 0, 1, 0.5, 1)


def waitUntilNotVisible(template):
    framesNotVisible = 0

    # Loop until the image is no longer visible
    while True:
        
        # Increment counter when the image is not visible
        if (not template.isOnScreen(getScreenshot())):
            framesNotVisible += 1
        else:
            framesNotVisible = 0

        # Screenshot can be partially cropped so we only stop after 3 frames in a row
        if (framesNotVisible == 3):
            break

        # Only check screenshot once every frame
        waitFrames(1)


def isTemplateInImage(image, templateImage, threshold = 1, templatemask = None):
    min_val, min_loc = getTemplatePosition(image, templateImage, cv2.TM_SQDIFF, templatemask)
    return min_val <= threshold, min_loc

def getTemplatePosition(image, templateImage, matchingMethod, templatemask = None):

    # Template matching using TM_SQDIFF : Perfect match -> minimum value around 0.0
    result = cv2.matchTemplate(image, templateImage, matchingMethod, mask = templatemask)

    # Get best match
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    return min_val, min_loc


def getPageNumber(screenshot):
    if (firstPage.isOnScreen(screenshot)): return 1
    elif (secondPage.isOnScreen(screenshot)): return 2
    elif (thirdPage.isOnScreen(screenshot)): return 3
    else: return None

def getCurrentBagSectionSelectedPosition(screenshot):
    return getCursorPosition(screenshot, BAG_SECTION_SELECTION)

def getCurrentItemSelectedPosition(screenshot):
    return getCursorPosition(screenshot, ITEM_SELECTION)

# Returns cursor position in bag menu in battle
def getCursorPosition(screenshot, sectionSize):
    selectorInImage, location = isTemplateInImage(screenshot[198:198+152 , 0:0+256], ITEM_CURRENT_LOCATION_SELECTOR)

    if (selectorInImage):
        y = round((location[1] + sectionSize["height"]) / sectionSize["height"]) - 1

        # Cursor on a item
        if (y < sectionSize["linesNumber"]):
            x = round((location[0] + sectionSize["width"]) / sectionSize["width"]) - 1
        # Cursor on a menu button
        else:
            x = min(round((location[0] + sectionSize["menuWidth"]) / sectionSize["menuWidth"]) - 1 , 2)

        return x,y
    else:
        return None
    
# Returns cursor position on the map
def getMapCursorPosition(screenshot):
    selectorInImage, location = isTemplateInImage(screenshot[0:0+170 , 20:20+216], MAP_CURSOR_ICON, 1, MAP_CURSOR_ICON_MASK)

    if (selectorInImage):
        x = round((location[0] - 6) * 27 / 189)
        y = round((location[1] - 2) * 22 / 154)

        return x,y
    else:
        return None

# Returns X menu cursor position
def getMenuPosition(screenshot):
    selectorInImage, location = isTemplateInImage(screenshot[8:8+168 , 158:158+3], MENU_CURRENT_LOCATION_SELECTOR)

    if (selectorInImage):
        return round(location[1] / 24) + 1
    else:
        return 0

def printImage(image):
    cv2.imshow("image", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

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

# Crops top/bottom transparent pixels and scale the sprite to the dashboard height
def resizeSprite(imagePath, scale):
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