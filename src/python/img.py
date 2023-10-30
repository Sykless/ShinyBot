

import mmap
import io
import numpy
import cv2

from PIL import Image, ImageFile

# https://stackoverflow.com/questions/42462431/oserror-broken-data-stream-when-reading-image-file
ImageFile.LOAD_TRUNCATED_IMAGES = True

TRAINER_UP = cv2.imread('src/python/data/trainer-up.png')
TRAINER_RIGHT = cv2.imread('src/python/data/trainer-right.png')
TRAINER_DOWN = cv2.imread('src/python/data/trainer-down.png')
TRAINER_LEFT = cv2.imread('src/python/data/trainer-left.png')

def getScreenshot():
    screenshotBytes = io.BytesIO(mmap.mmap(0, 30486, "screenshot"))
    screenshotImage = Image.open(screenshotBytes)
    # screenshotImage.save("test.png")

    # Convert PIL image to CV2 image to enable image processing
    return cv2.cvtColor(numpy.array(screenshotImage), cv2.COLOR_RGB2BGR)

def isTemplateInImage(image, template, threshold):

    # Template matching using TM_SQDIFF : Perfect match -> minimum value around 0.0
    result = cv2.matchTemplate(image, template, cv2.TM_SQDIFF)

    # Get best match
    min_val = cv2.minMaxLoc(result)[0]

    # print(min_val)

    return min_val <= threshold

def isFacingDown(screenshot):
    return isTemplateInImage(screenshot, TRAINER_DOWN, 7000000)

def isFacingUp(screenshot):
    return isTemplateInImage(screenshot, TRAINER_UP, 6000000)

def isFacingLeft(screenshot):
    return isTemplateInImage(screenshot, TRAINER_LEFT, 8000000)

def isFacingRight(screenshot):
    return isTemplateInImage(screenshot, TRAINER_RIGHT, 8000000)