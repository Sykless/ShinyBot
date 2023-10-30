

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
RUNAWAY = cv2.imread('src/python/data/runaway.png')

TRAINER_UP_MASK = cv2.imread('src/python/data/trainer-up-mask.png')
TRAINER_RIGHT_MASK = cv2.imread('src/python/data/trainer-right-mask.png')
TRAINER_DOWN_MASK= cv2.imread('src/python/data/trainer-down-mask.png')
TRAINER_LEFT_MASK = cv2.imread('src/python/data/trainer-left-mask.png')

def getScreenshot():

    while True:
        screenshotBytes = io.BytesIO(mmap.mmap(0, 30486, "screenshot"))

        try:
            screenshotImage = Image.open(screenshotBytes)
            # screenshotImage.save("test.png")

            # Convert PIL image to CV2 image to enable image processing
            return cv2.cvtColor(numpy.array(screenshotImage), cv2.COLOR_RGB2BGR)
        except Exception:
            print(screenshotBytes.read())
            print(traceback.format_exc())


def isTemplateInImage(image, template, threshold, mask = None):

    # Template matching using TM_SQDIFF : Perfect match -> minimum value around 0.0
    result = cv2.matchTemplate(image, template, cv2.TM_SQDIFF, mask = mask)

    # Get best match
    min_val = cv2.minMaxLoc(result)[0]

    return min_val <= threshold

def isTrainerFacingDown(screenshot):
    return isTemplateInImage(screenshot[76:76+23 , 119:119+17], TRAINER_DOWN, 3300000, TRAINER_DOWN_MASK)

def isTrainerFacingUp(screenshot):
    return isTemplateInImage(screenshot[76:76+23 , 119:119+17], TRAINER_UP, 3330000, TRAINER_UP_MASK)

def isTrainerFacingLeft(screenshot):
    return isTemplateInImage(screenshot[76:76+23 , 119:119+17], TRAINER_LEFT, 5000000, TRAINER_LEFT_MASK)

def isTrainerFacingRight(screenshot):
    return isTemplateInImage(screenshot[76:76+23 , 120:120+17], TRAINER_RIGHT, 5000000, TRAINER_RIGHT_MASK)

def isRunAwayAvailable(screenshot):
    return isTemplateInImage(screenshot[354:354+30 , 100:100+56], RUNAWAY, 1)