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
    
# Poke address 0x075EF0 to FF2801D2 instead of 082801D2
def getShinyValue(pid, OTId, OtSecretId):
    xorPid = getBits(pid,0,16) ^ getBits(pid,16,16)
    xorOT = OTId ^ OtSecretId
    shinyValue = xorPid ^ xorOT

    return shinyValue

def isShiny(pokemon):
    return hasattr(pokemon, 'isShiny') and pokemon.isShiny < 255