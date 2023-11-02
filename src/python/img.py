

import mmap
import io
import numpy
import cv2
import traceback

from PIL import Image, ImageFile

# https://stackoverflow.com/questions/42462431/oserror-broken-data-stream-when-reading-image-file
ImageFile.LOAD_TRUNCATED_IMAGES = True

TRAINER_UP = cv2.imread('src/python/data/trainer-up.png')
TRAINER_RIGHT = cv2.imread('src/python/data/trainer-right.png')
TRAINER_DOWN = cv2.imread('src/python/data/trainer-down.png')
TRAINER_LEFT = cv2.imread('src/python/data/trainer-left.png')

POKETCH = cv2.imread('src/python/data/poketch.png')

BATTLE_TOUCHSCREEN = cv2.imread('src/python/data/battle-touchscreen.png')
RUNAWAY = cv2.imread('src/python/data/runaway.png')
POKEBALL_LAST_USED = cv2.imread('src/python/data/pokeball-last-used.png')
INSIDE_BAG = cv2.imread('src/python/data/inside-bag.png')
INSIDE_BALLS = cv2.imread('src/python/data/inside-balls.png')

ITEM_CURRENT_LOCATION_SELECTOR = cv2.imread('src/python/data/item-current-location-selector.png')
FIRST_PAGE = cv2.imread('src/python/data/first-page.png')
SECOND_PAGE = cv2.imread('src/python/data/second-page.png')
THIRD_PAGE = cv2.imread('src/python/data/third-page.png')
USE_ITEM = cv2.imread('src/python/data/use-item.png')
NEW_POKEDEX_ENTRY = cv2.imread('src/python/data/new-pokedex-entry.png')

TRAINER_UP_MASK = cv2.imread('src/python/data/trainer-up-mask.png')
TRAINER_RIGHT_MASK = cv2.imread('src/python/data/trainer-right-mask.png')
TRAINER_DOWN_MASK= cv2.imread('src/python/data/trainer-down-mask.png')
TRAINER_LEFT_MASK = cv2.imread('src/python/data/trainer-left-mask.png')
ITEM_CURRENT_LOCATION_MASK = cv2.imread('src/python/data/item-current-location-mask.png')
BATTLE_TOUCHSCREEN_MASK = cv2.imread('src/python/data/battle-touchscreen-mask.png')

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


def isTemplateInImage(image, template, threshold, mask = None):

    # Template matching using TM_SQDIFF : Perfect match -> minimum value around 0.0
    result = cv2.matchTemplate(image, template, cv2.TM_SQDIFF, mask = mask)

    # Get best match
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    # print(min_val)

    return min_val <= threshold, min_loc

def isTrainerFacingDown(screenshot):
    return isTemplateInImage(screenshot[76:76+23 , 119:119+17], TRAINER_DOWN, 3300000, TRAINER_DOWN_MASK)[0]

def isTrainerFacingUp(screenshot):
    return isTemplateInImage(screenshot[76:76+23 , 119:119+17], TRAINER_UP, 3330000, TRAINER_UP_MASK)[0]

def isTrainerFacingLeft(screenshot):
    return isTemplateInImage(screenshot[76:76+23 , 119:119+17], TRAINER_LEFT, 5000000, TRAINER_LEFT_MASK)[0]

def isTrainerFacingRight(screenshot):
    return isTemplateInImage(screenshot[76:76+23 , 120:120+17], TRAINER_RIGHT, 5000000, TRAINER_RIGHT_MASK)[0]

def isRunAwayAvailable(screenshot):
    return isTemplateInImage(screenshot[354:354+30 , 100:100+56], RUNAWAY, 1)[0]

def isBattleTouchscreenAvailable(screenshot):
    return isTemplateInImage(screenshot[192:192+192 , 0:0+256], BATTLE_TOUCHSCREEN, 1, BATTLE_TOUCHSCREEN_MASK)[0]

def isPoketchAvailable(screenshot):
    return isTemplateInImage(screenshot[225:225+126 , 224:224+32], POKETCH, 1)[0]

def isInsideBag(screenshot):
    return isTemplateInImage(screenshot[208:208+58 , 135:135+114], INSIDE_BAG, 1)[0]

def isPokeballLastUsed(screenshot):
    return isTemplateInImage(screenshot[352:352+26 , 8:8+192], POKEBALL_LAST_USED, 1)[0]

def isInsideBalls(screenshot):
    return isTemplateInImage(screenshot[348:348+32 , 91:91+74], INSIDE_BALLS, 1)[0]

def getPageNumber(screenshot):
    if (isFirstPage(screenshot)): return 1
    elif (isSecondPage(screenshot)): return 2
    elif (isThirdPage(screenshot)): return 3
    else: return None

def isFirstPage(screenshot):
    return isTemplateInImage(screenshot[359:359+10 , 183:183+6], FIRST_PAGE, 1)[0]

def isSecondPage(screenshot):
    return isTemplateInImage(screenshot[359:359+10 , 183:183+6], SECOND_PAGE, 1)[0]

def isThirdPage(screenshot):
    return isTemplateInImage(screenshot[359:359+10 , 183:183+6], THIRD_PAGE, 1)[0]

def isUseItems(screenshot):
    return isTemplateInImage(screenshot[351:351+27 , 8:8+192], USE_ITEM, 1)[0]

def isNewPokedexEntry(screenshot):
    return isTemplateInImage(screenshot[0:0+15 , 0:0+241], NEW_POKEDEX_ENTRY, 1)[0]

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