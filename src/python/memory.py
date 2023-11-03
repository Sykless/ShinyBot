
import io
import json
import mmap

def readPokemonData():
    return readJsonData("pokemonData")

def readBagData():
    return readJsonData("bagData")

def readPositionData():
    return readJsonData("positionData")

def clearMemoryData(memoryfileName):
    writePokemonMmap = mmap.mmap(-1, 4096, tagname=memoryfileName, access=mmap.ACCESS_WRITE)
    writePokemonMmap.write(bytes("\x00" * 4096, encoding="utf-8"))

def readJsonData(memoryfileName):
    # Read memoryData as BytesIO object from memory file
    mmapData = mmap.mmap(0, 4096, memoryfileName)
    mmapByes = io.BytesIO(mmapData).read()

    try:
        # Convert BytesIO to string (UTF-8)
        memoryData = mmapByes.decode("utf-8").split("\x00")[0]

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
    except UnicodeDecodeError as e:
        # Cannot mmapByes.decode because junk data has been accumulated : clear memory file
        clearMemoryData(memoryfileName)
        print(str(e))
    except Exception as e:
        # pass
        print(mmapByes)
        print(str(e))

    return None