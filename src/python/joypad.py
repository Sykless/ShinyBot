import mmap

FRAMES_RELEASE_TIME = 5

def writeInput(inputSequence, endSequence = None):

    frameByFrameInputSequence = "".join(
        [input * FRAMES_RELEASE_TIME # Press button for FRAMES_RELEASE_TIME frames
         + "@" * FRAMES_RELEASE_TIME # Release input for FRAMES_RELEASE_TIME frames
         for input in inputSequence])
    
    if (endSequence):
        frameByFrameInputSequence += endSequence
    
    print(frameByFrameInputSequence)

    writeInputMmap = mmap.mmap(-1, 4096, tagname="joypad", access=mmap.ACCESS_WRITE)
    writeInputMmap.write(bytes(frameByFrameInputSequence, encoding="utf-8"))

def readInput():
    readInputMmap = mmap.mmap(-1, 4096, tagname="joypad", access=mmap.ACCESS_READ)
    return readInputMmap.read().decode("utf-8").split("\x00")[0]