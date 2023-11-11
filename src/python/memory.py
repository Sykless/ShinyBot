
import io
import json
import mmap

def readPokemonData():
    return readJsonData("pokemonData")

def readBagData():
    return readJsonData("bagData")

def readPositionData():
    return readJsonData("positionData")

def readJoypadData():
    return readMemoryData("joypad")

def setMemoryFlag(runFlag = None):
    flagData = list(readMemoryData("flagsData"))

    # Convert boolean to "0" or "1"
    if (runFlag != None):
        flagData[0] = str(int(runFlag))

    writeMemoryData("flagsData", "".join(flagData))

def clearMemoryData(memoryfileName):
    writeMemoryData(memoryfileName, "\x00" * 4096)

def writeMemoryData(memoryfileName, input):
    writeMemoryMmap = mmap.mmap(-1, 4096, tagname=memoryfileName, access=mmap.ACCESS_WRITE)
    writeMemoryMmap.write(bytes(input, encoding="utf-8"))

def readMemoryData(memoryfileName):
    # Read memoryData as BytesIO object from memory file
    mmapData = mmap.mmap(0, 4096, memoryfileName)
    mmapByes = io.BytesIO(mmapData).read()

    try:
        # Convert BytesIO to string (UTF-8)
        memoryData = mmapByes.decode("utf-8").split("\x00")[0]
        return memoryData
        
    except UnicodeDecodeError as e:
        # Cannot mmapByes.decode because junk data has been accumulated : clear memory file
        clearMemoryData(memoryfileName)
        print(str(e))
    except Exception as e:
        # pass
        print(mmapByes)
        print(str(e))

def readJsonData(memoryfileName):
    # Convert BytesIO to string (UTF-8)
    memoryData = readMemoryData(memoryfileName)

    if (memoryData):
        try:
            # Convert string memoryData to JSON
            jsonMemoryData = json.loads(memoryData)[memoryfileName]
            return jsonMemoryData

        except json.JSONDecodeError as e:
            # Cannot json.loads because junk data has been accumulated : clear memory file
            clearMemoryData(memoryfileName)
            print(str(e))
        except Exception as e:
            # pass
            print(memoryData)
            print(str(e))

    return None