

import mmap
import io
import numpy
import cv2

from PIL import Image, ImageFile

# https://stackoverflow.com/questions/42462431/oserror-broken-data-stream-when-reading-image-file
ImageFile.LOAD_TRUNCATED_IMAGES = True

class Template:
    def __init__(self, name, positionX, positionY, width, height, threshold, mask = None):
        self.image = cv2.imread("src/python/data/" + name + ".png")
        self.mask = mask and cv2.imread("src/python/data/" + name + "-mask.png")

        self.positionX = positionX
        self.positionY = positionY
        self.width = width
        self.height = height
        self.threshold = threshold

    def isOnScreen(self, screenshot):
        return isTemplateInImage(screenshot[
                self.positionY:self.positionY + self.height,
                self.positionX:self.positionX + self.width],
            self.image, self.threshold, mask = self.mask)[0]

trainerUp = Template("trainer-up", 119, 76, 17, 23, 3330000, mask = True)
trainerDown = Template("trainer-down", 119, 76, 17, 23, 3330000, mask = True)
trainerRight = Template("trainer-right", 120, 76, 17, 23, 5000000, mask = True)
trainerLeft = Template("trainer-left", 119, 76, 17, 23, 5000000, mask = True)
battleTouchscreen = Template("battle-touchscreen", 0, 192, 256, 192, 1, mask = True)

poketch = Template("poketch", 224, 225, 32, 126, 1)
runaway = Template("runaway", 100, 354, 56, 30, 1)
insideBag = Template("inside-bag", 135, 208, 114, 58, 1)
insideBalls = Template("inside-balls", 91, 348, 74, 32, 1)
pokeballLastUsed = Template("pokeball-last-used", 8, 352, 192, 26, 1)

firstPage = Template("first-page", 183, 359, 6, 10, 1)
secondPage = Template("second-page", 183, 359, 6, 10, 1)
thirdPage = Template("third-page", 183, 359, 6, 10, 1)
useItem = Template("use-item", 8, 351, 192, 27, 1)
newPokedexEntry = Template("new-pokedex-entry", 0, 0, 241, 15, 1)

def getPageNumber(screenshot):
    if (firstPage.isOnScreen(screenshot)): return 1
    elif (secondPage.isOnScreen(screenshot)): return 2
    elif (thirdPage.isOnScreen(screenshot)): return 3
    else: return None

def getPlayerPosition(screenshot):
    # Facing left
    if (trainerLeft.isOnScreen(screenshot)):
        return "l"

    # Facing right
    elif (trainerRight.isOnScreen(screenshot)):
        return "r"

    # Facing down
    elif (trainerDown.isOnScreen(screenshot)):
        return "d"

    # Facing up
    elif (trainerUp.isOnScreen(screenshot)):
        return "u"
    
    # Player not in the screenshot
    else:
        return None

def isTemplateInImage(image, template, threshold, mask = None):

    # Template matching using TM_SQDIFF : Perfect match -> minimum value around 0.0
    result = cv2.matchTemplate(image, template, cv2.TM_SQDIFF, mask = mask)

    # Get best match
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    # print(min_val)

    return min_val <= threshold, min_loc

ITEM_CURRENT_LOCATION_SELECTOR = cv2.imread('src/python/data/item-current-location-selector.png')

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

def getCurrentBagSectionSelectedPosition(screenshot):
    return getCursorPosition(screenshot, BAG_SECTION_SELECTION)

def getCurrentItemSelectedPosition(screenshot):
    return getCursorPosition(screenshot, ITEM_SELECTION)

def getCursorPosition(screenshot, sectionSize):
    selectorInImage, location = isTemplateInImage(screenshot[198:198+152 , 0:0+256], ITEM_CURRENT_LOCATION_SELECTOR, 1)

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
    
def getScreenshot():
    while True:
        screenshotBytes = io.BytesIO(mmap.mmap(0, 30486, "screenshot"))

        try:
            screenshotImage = Image.open(screenshotBytes)
            # screenshotImage.save("test.png")

            # Convert PIL image to CV2 image to enable image processing
            return cv2.cvtColor(numpy.array(screenshotImage), cv2.COLOR_RGB2BGR)
        except Exception as e:
            pass
            # print(screenshotBytes.read())
            # print(str(e))