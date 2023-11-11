from bag import Bag

import time
import memory

def waitFrames(numberOfFrames):
    time.sleep(numberOfFrames / 60) # 60 frames per second

def formatNumber(number):
    stringNumber = str(number)

    if (len(stringNumber) == 1):
        return " " + stringNumber + " "
    elif (len(stringNumber) == 2):
        return " " + stringNumber
    else:
        return stringNumber

def getBits(a,b,d):
	return (a >> b) % (1 << d)
    
# Poke address 0x075EF0 first byte value to FF instead of 08 to increase shiny odds to 1/255
def getShinyValue(pid, OTId, OtSecretId):
    xorPid = getBits(pid,0,16) ^ getBits(pid,16,16)
    xorOT = OTId ^ OtSecretId
    shinyValue = xorPid ^ xorOT

    return shinyValue

def getPokeballLocation():
     # Read JSON Bag data from memory file and convert it to Bag object
    bag = Bag(**memory.readBagData())
    pokeballLocation = -1

    # Search for Poké Ball location
    for ballId in range(len(bag.balls)):
        if (bag.balls[ballId].name == "Poké Ball"):
            pokeballLocation = ballId

    return pokeballLocation