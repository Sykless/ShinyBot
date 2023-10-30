import mmap

def writeInput(inputSequence):
    writeInputMmap = mmap.mmap(-1, 4096, tagname="joypad", access=mmap.ACCESS_WRITE)
    writeInputMmap.write(bytes(inputSequence, encoding="utf-8"))

def readInput():
    readInputMmap = mmap.mmap(-1, 4096, tagname="joypad", access=mmap.ACCESS_READ)
    return readInputMmap.read().decode("utf-8").split("\x00")[0]