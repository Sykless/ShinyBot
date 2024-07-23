

import mmap
import io
import numpy
import cv2

from PIL import Image, ImageFile

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

    def setPosition(self,x,y):
        self.positionX = x
        self.positionY = y

    def getSubScreenshot(self, screenshot):
        return screenshot[
                self.positionY:self.positionY + self.height,
                self.positionX:self.positionX + self.width]

    def getPositionOnScreen(self,screenshot,mask):
        return getTemplatePosition(screenshot, self.image, templatemask = mask)

    def isOnScreen(self, screenshot):
        return isTemplateInImage(self.getSubScreenshot(screenshot),
            self.image, self.threshold, templatemask = self.mask)[0]

WEATHER_COLOR = [
    [243,235,227], # Snow
    [97,138,186],  # Sand
    [73,105,138]   # Ash
]

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
TRAINER_MINYPOSITION = 74

trainer = Template("trainer", TRAINER_MINXPOSITION, TRAINER_MINYPOSITION, 26, 22, None, mask = True)
trainerUp = Template("trainer-up", TRAINER_MINXPOSITION, TRAINER_MINYPOSITION, 18, 20, None, None)
trainerDown = Template("trainer-down", TRAINER_MINXPOSITION, TRAINER_MINYPOSITION, 18, 20, None, None)
trainerRight = Template("trainer-right", TRAINER_MINXPOSITION, TRAINER_MINYPOSITION, 18, 20, None, None)
trainerLeft = Template("trainer-left", TRAINER_MINXPOSITION, TRAINER_MINYPOSITION, 18, 20, None, None)
trainerOrientationMask = cv2.imread("src/python/data/img/trainer-orientation-mask.png")

battleTouchscreen = Template("battle-touchscreen", 0, 192, 256, 192, 1, mask = True)
poketch = Template("poketch", 224, 225, 32, 126, 1)
pokemonMenu = Template("pokemon-menu", 0, 192, 208, 80, 1)
hmAnimation = Template("hm-animation", 0, 56, 255, 80, 50000)
runaway = Template("runaway", 100, 354, 56, 30, 1)
insideBag = Template("inside-bag", 135, 208, 114, 58, 1)
insideBalls = Template("inside-balls", 91, 348, 74, 32, 1)
pokeballLastUsed = Template("pokeball-last-used", 8, 352, 192, 26, 1)

firstPage = Template("first-page", 183, 359, 6, 10, 1)
secondPage = Template("second-page", 183, 359, 6, 10, 1)
thirdPage = Template("third-page", 183, 359, 6, 10, 1)
useItem = Template("use-item", 8, 351, 192, 27, 1)
newPokedexEntry = Template("new-pokedex-entry", 0, 0, 241, 15, 1)

def printImage(image):
    cv2.imshow("Image avec un nom hyper long pour tester", image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def getTemplatePosition(image, templateImage, templatemask = None):

    # Template matching using TM_SQDIFF : Perfect match -> minimum value around 0.0
    result = cv2.matchTemplate(image, templateImage, cv2.TM_SQDIFF, mask = templatemask)

    # Get best match
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    return min_val, min_loc

def isTemplateInImage(image, templateImage, threshold, templatemask = None):
    min_val, min_loc = getTemplatePosition(image, templateImage, templatemask)
    return min_val <= threshold, min_loc

def getPlayerPosition(screenshot):

    redScreenshot = filterRed(trainer.getSubScreenshot(screenshot))
    #printImage(redScreenshot)

    # Get trainer position on subscreenshot
    trainerPosition = trainer.getPositionOnScreen(redScreenshot, trainer.mask)[1]

    # Calculate relative position on whole screen
    xPosition = trainerPosition[0] + TRAINER_MINXPOSITION
    yPosition = trainerPosition[1] + TRAINER_MINYPOSITION

    # Apply relative position to trainer templates
    trainerLeft.setPosition(xPosition,yPosition)
    trainerRight.setPosition(xPosition,yPosition)
    trainerDown.setPosition(xPosition,yPosition)
    trainerUp.setPosition(xPosition,yPosition)

    # Add weather particles to mask in order to ignore them
    weatherMask = createMaskWithWeather(trainerLeft.getSubScreenshot(screenshot),
                trainerOrientationMask.copy())
    
    # Compare trainer position templates to trainer in the screenshot
    leftTemplateValue = (trainerLeft.getPositionOnScreen(trainerLeft.getSubScreenshot(screenshot), weatherMask), "l")
    rightTemplateValue = (trainerRight.getPositionOnScreen(trainerRight.getSubScreenshot(screenshot), weatherMask), "r")
    downTemplateValue = (trainerDown.getPositionOnScreen(trainerDown.getSubScreenshot(screenshot), weatherMask), "d")
    upTemplateValue = (trainerUp.getPositionOnScreen(trainerUp.getSubScreenshot(screenshot), weatherMask), "u")

    # Lowest result is the closest result, so we sort all four results
    sortedList = sorted([leftTemplateValue, rightTemplateValue, downTemplateValue], key=lambda x: x[0][0])

    # Up template is hard to differenciate from the other templates
    # So if the lowest result is close to Up template result, we take Up as the closest
    if (sortedList[0][1] == "d" and upTemplateValue[0][0] / sortedList[0][0][0] < 1.4
        or sortedList[0][1] in ["l","r"] and upTemplateValue[0][0] / sortedList[0][0][0] < 1.05):
        orientation = "u"
    # Default behavior : return the lowest result
    else:
        orientation = sortedList[0][1]

    print(xPosition, yPosition)
    print("leftTemplateValue : " + str(leftTemplateValue))
    print("rightTemplateValue : " + str(rightTemplateValue))
    print("downTemplateValue : " + str(downTemplateValue))
    print("upTemplateValue : " + str(upTemplateValue))
    print(orientation)

    return orientation
    
def createMaskWithWeather(image, templatemask):

    # Create new temporary mask masking the weather partcles (snow, sand, etc)
    weatherMask = templatemask[:]

    for weatherParticle in WEATHER_COLOR:
        # Retrieve all weather particles from screenshot
        (Y,X) = numpy.where(numpy.all(image == weatherParticle, axis=2))
        snowflakeLocations = numpy.column_stack((Y,X))

        # Apply them to the new mask
        for snowflake in snowflakeLocations:
            weatherMask[snowflake[0]][snowflake[1]] = [0,0,0]

    return weatherMask

def filterRed(image):
    img_hsv=cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # lower mask (0-10)
    lower_red = numpy.array([0,50,50])
    upper_red = numpy.array([15,255,255])
    mask0 = cv2.inRange(img_hsv, lower_red, upper_red)

    # upper mask (170-180)
    lower_red = numpy.array([150,20,20])
    upper_red = numpy.array([180,255,255])
    mask1 = cv2.inRange(img_hsv, lower_red, upper_red)

    # join my masks
    mask = mask0+mask1

    # set my output img to zero everywhere except my mask
    output_img = image.copy()
    output_img[numpy.where(mask==0)] = 0
    output_hsv = img_hsv.copy()
    output_hsv[numpy.where(mask==0)] = 0

    return output_img



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
    
def getScreenshot():
    while True:
        screenshotBytes = io.BytesIO(mmap.mmap(0, 64000, "screenshot"))
        
        try:
            screenshotImage = Image.open(screenshotBytes)
            screenshotImage.save("test.png")

            # Convert RGB screenshot to BGR in order to be cv2-readable
            return cv2.cvtColor(numpy.array(screenshotImage), cv2.COLOR_RGB2BGR)
        except Exception as e:
            pass
            # print(screenshotBytes.read())
            # print(str(e))