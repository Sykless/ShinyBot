

import mmap
import io
import numpy
import cv2

from PIL import Image, ImageFile

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

BLACK_COLOR = [0,0,0]

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

TRAINER_MINXPOSITION = 115
TRAINER_MINYPOSITION = 66

trainerUp = Template("trainer-up-bluegreen", TRAINER_MINXPOSITION, TRAINER_MINYPOSITION, 28, 32, None, mask = True)
trainerDown = Template("trainer-down-bluegreen", TRAINER_MINXPOSITION, TRAINER_MINYPOSITION, 28, 32, None, mask = True)
trainerRight = Template("trainer-right-bluegreen", TRAINER_MINXPOSITION, TRAINER_MINYPOSITION, 28, 32, None, mask = True)
trainerLeft = Template("trainer-left-bluegreen", TRAINER_MINXPOSITION, TRAINER_MINYPOSITION, 28, 32, None, mask = True)

bagTouchscreen = Template("bag-menu-touchscreen", 0, 192, 256, 192, 1, mask = True)
bagItemSelector = Template("bagitem-selector", 105, 15, 158, 113, 1, mask = True)
cdDouteuxSelected = Template("cd-douteux-selected", 106, 15, 64, 113, 1)
tissuFaucheSelected = Template("tissu-fauche-selected", 106, 15, 73, 113, 1)
griffeRasoirSelected = Template("griffe-rasoir.selected", 106, 15, 68, 113, 1)
crocRasoirSelected = Template("croc-rasoir-selected", 106, 15, 67, 113, 1)
closeBagMenuSelected = Template("close-bag-selected", 106, 15, 42, 113, 1)

battleTouchscreen = Template("battle-touchscreen", 0, 192, 256, 192, 1, mask = True)
poketch = Template("poketch", 224, 225, 32, 126, 1)
pokemonMenu = Template("pokemon-menu", 0, 192, 208, 80, 1)
hmAnimation = Template("hm-animation", 0, 56, 255, 80, 50000)
runaway = Template("runaway", 100, 354, 56, 30, 1)
insideBag = Template("inside-battle-bag-menu", 135, 208, 114, 58, 1)
insideBalls = Template("inside-battle-balls-menu", 91, 348, 74, 32, 1)
pokeballLastUsed = Template("pokeball-last-used", 8, 352, 192, 26, 1)

firstPage = Template("first-page", 183, 359, 6, 10, 1)
secondPage = Template("second-page", 183, 359, 6, 10, 1)
thirdPage = Template("third-page", 183, 359, 6, 10, 1)
useItem = Template("use-item", 8, 351, 192, 27, 1)
newPokedexEntry = Template("new-pokedex-entry", 0, 0, 241, 15, 1)

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


def isTemplateInImage(image, templateImage, threshold, templatemask = None):
    min_val, min_loc = getTemplatePosition(image, templateImage, cv2.TM_SQDIFF, templatemask)
    return min_val <= threshold, min_loc

def getTemplatePosition(image, templateImage, matchingMethod, templatemask = None):

    # Template matching using TM_SQDIFF : Perfect match -> minimum value around 0.0
    result = cv2.matchTemplate(image, templateImage, matchingMethod, mask = templatemask)

    # Get best match
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    return min_val, min_loc


def getPlayerOrientation(screenshot):

    # Make a first mask in order to only keep red-ish colors on a trainer-centered subscreenshot
    redScreenshot = filterRedPixels(trainerLeft.getSubScreenshot(screenshot))

    # Retrieve cap colors (light red + dark red)
    redColors = getRedsValues(redScreenshot)

    # No red colour has been found 
    if (redColors is None):
        return None, None

    # Change all light red pixels to green, dark red pixels to blue and the rest to black
    capImage = filterCap(redScreenshot, redColors["lightRed"], redColors["darkRed"])

    # Compare trainer position templates to trainer in the screenshot
    leftTemplateValue = (trainerLeft.getNormedPositionOnScreen(capImage), "l")
    rightTemplateValue = (trainerRight.getNormedPositionOnScreen(capImage), "r")
    downTemplateValue = (trainerDown.getNormedPositionOnScreen(capImage), "d")
    upTemplateValue = (trainerUp.getNormedPositionOnScreen(capImage), "u")

    # Lowest result is the closest result, so we sort all four results and take the first one
    sortedList = sorted([upTemplateValue, leftTemplateValue, rightTemplateValue, downTemplateValue], key=lambda x: x[0][0])
    orientation = sortedList[0][1]
    spritePosition = sortedList[0][0][1]

    return orientation, spritePosition


def getRedsValues(image):
    # Get number of occurences for each pixel
    colors, count = numpy.unique(image.reshape(-1,image.shape[-1]), axis=0, return_counts=True)

    # Sort colors by number of occurrences in order to get the most common pixels
    sorter = (-count).argsort()
    sortedColors = colors[sorter]

    # print(count)
    # print(colors)
    # print(sortedColors)
    # printImage(image)

    hsvLightRed = None
    bgrLightRed = None

    for bgrColor in sortedColors:
        # print()
        # print(bgrColor)

        # Black pixel is most likely the most common pixel since we applied a mask, skip it
        if (bgrColor != BLACK_COLOR).all():

            # Get all locations of current color in the image
            colorLocation = numpy.where(numpy.all(image == bgrColor, axis=2))

            # Retrieve minimum and maximum position
            minYposition = min(colorLocation[0])
            maxYposition = max(colorLocation[0])
            minXposition = min(colorLocation[1])
            maxXposition = max(colorLocation[1])

            # print(minXposition, maxXposition)
            # print(minYposition, maxYposition)

            # Red cap should be at least 8 pixels long but no longer than 15
            # Also should be at least 4 pixels wide but no longer than 22
            if (4 <= maxYposition - minYposition <= 22       
                and 8 <= maxXposition - minXposition <= 15):

                # print("Potential red")
                # print(bgrColor)

                # Convert pixel to HSV, easier to compare darker shades with Saturation and Brightness
                hsvColor = convertBgrPixelToHsv(bgrColor)

                # First pixel to match cap position conditions : keep it for later
                if (bgrLightRed is None):
                    bgrLightRed = bgrColor
                    hsvLightRed = hsvColor

                # Current color has higher saturation and lower brightness : current color is dark red
                elif (hsvColor[1] >= hsvLightRed[1] and hsvColor[2] <= hsvLightRed[2]):
                    return {"lightRed": bgrLightRed, "darkRed": bgrColor}
                
                # Current color has lower saturation and higher brightness : current color is light red
                elif (hsvColor[1] <= hsvLightRed[1] and hsvColor[2] >= hsvLightRed[2]):
                    return {"lightRed": bgrColor, "darkRed": bgrLightRed}
                
                # Higher saturation and brightness or lower saturation and brigthness : cannot compare
                else:
                    print("Cannot determine which red is darker : ")
                    print(bgrLightRed)
                    print(bgrColor)
                    print()
                    # printImage(image)

    # No red colors found                
    return None


def filterRedPixels(image):
    hsvImage = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Lower mask (Hue between 0 and 15)
    lowerRed = numpy.array([0,0,50])
    upperRed = numpy.array([15,255,255])
    lowHueMask = cv2.inRange(hsvImage, lowerRed, upperRed)

    # Upper mask (Hue between 150 and 180)
    lowerRed = numpy.array([150,0,20])
    upperRed = numpy.array([180,255,255])
    higHuehMask = cv2.inRange(hsvImage, lowerRed, upperRed)

    # Join the two masks
    redMask = lowHueMask + higHuehMask

    # Set the pixels to black everywhere except the red mask
    redImage = image.copy()
    redImage[numpy.where(redMask == 0)] = 0

    return redImage


def filterCap(image, lightRed, darkRed):

    # Create masks for lightRed and darkRed colors
    lightRedMask = numpy.all(image == lightRed, axis=2)
    darkRedMask = numpy.all(image == darkRed, axis=2)

    # Create a new image with only black pixels
    blackImage = numpy.full_like(image, BLACK_COLOR)

    # Apply lightRed mask and insert green pixels instead
    blackImage[lightRedMask, :] = [0,255,0]

    # Apply darkRed mask and insert blue pixels instead
    blackImage[darkRedMask, :] = [255,0,0]

    return blackImage


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
    selectorInImage, location = isTemplateInImage(screenshot[8:8+168 , 158:158+3], MENU_CURRENT_LOCATION_SELECTOR, 1)

    if (selectorInImage):
        return round(location[1] / 24) + 1
    else:
        return 0


def convertBgrPixelToHsv(pixel):
    return cv2.cvtColor(numpy.uint8([[pixel]]), cv2.COLOR_BGR2HSV)[0][0]

def printImage(image):
    cv2.imshow("image", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def getScreenshot():
    while True:
        screenshotBytes = io.BytesIO(mmap.mmap(0, 64000, "screenshot"))
        
        try:
            screenshotImage = Image.open(screenshotBytes)
            screenshotImage.save("test.png")

            # Convert RGB screenshot to BGR in order to be cv2-readable
            return cv2.cvtColor(numpy.array(screenshotImage), cv2.COLOR_RGB2BGR)
        except Exception as e:
            waitFrames(1) # Check one frame later after memory has been updated