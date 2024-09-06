
import io
import json
import mmap
import pickle

from encounter import SPECIALGRASSENCOUNTERS
from data import POKEMON_NAMES
from utils import waitFrames

MEMORYSIZE = {
    "pokemonTeamData": 20480,
    "bagData": 20480,
    "joypad": 8192,
    "gameData": 4096,
    "wildPokemonData": 2048,
    "playerData": 256,
    "runSections": 256,
    "specialPokemon": 256,
    "titleScreen": 8,
}

# Serialize the graph to a file
def saveGraph(graph, filename):
    with open(filename, 'wb') as f:
        pickle.dump(graph, f)

# Deserialize the graph from a file
def loadGraph(filename):
    with open(filename, 'rb') as f:
        return pickle.load(f)

# WARNING : Pokemon Team data is only available during battle or if menu is open
def readPokemonTeamData():
    return readJsonData("pokemonTeamData")

def readWildPokemonData():
    return readJsonData("wildPokemonData")

def readBagData():
    return readJsonData("bagData")

def readPlayerData():
    return readJsonData("playerData")

def readGameData():
    return readJsonData("gameData")

def readJoypadData():
    return readMemoryData("joypad")

def readRunSectionsData():
    return readMemoryData("runSections")

def isOnTitleScreen():
    return readMemoryData("titleScreen") != "0"

def clearJoypadInputs():
    clearMemoryData("joypad")
    clearMemoryData("runSections")

def clearMemoryData(memoryfileName):
    writeMemoryData(memoryfileName, "\x00" * MEMORYSIZE[memoryfileName])

def writeMemoryData(memoryfileName, input):
    writeMemoryMmap = mmap.mmap(-1, MEMORYSIZE[memoryfileName], tagname=memoryfileName, access=mmap.ACCESS_WRITE)
    writeMemoryMmap.write(bytes(input, encoding="utf-8"))

def readMemoryData(memoryfileName):
    # Read memoryData as BytesIO object from memory file
    mmapData = mmap.mmap(0, MEMORYSIZE[memoryfileName], memoryfileName)
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

def isLuaScriptRunning():
    clearMemoryData("playerData")
    waitFrames(2)

    # If player data is still null 2 frames after being emptied, the lua script is not running
    return True if readPlayerData() else False

def updateSpecialPokemon(marshPokemonId = None, swarmPokemonId = None, gardenPokemonIdToday = None, gardenPokemonIdYesterday = None, gbaGameId = None):
    specialPokemon = []

    if (marshPokemonId is not None):
        marshPokemonId = marshPokemonId if isinstance(marshPokemonId, int) else POKEMON_NAMES.index(marshPokemonId)
        specialPokemon.append("MARSH-" + str(SPECIALGRASSENCOUNTERS["marsh"].index(marshPokemonId)))

    if (swarmPokemonId is not None):
        swarmPokemonId = swarmPokemonId if isinstance(swarmPokemonId, int) else POKEMON_NAMES.index(swarmPokemonId)
        specialPokemon.append("SWARM-" + str(SPECIALGRASSENCOUNTERS["swarm"].index(swarmPokemonId)))

    if (gardenPokemonIdToday is not None):
        gardenPokemonIdToday = gardenPokemonIdToday if isinstance(gardenPokemonIdToday, int) else POKEMON_NAMES.index(gardenPokemonIdToday)
        specialPokemon.append("GARDENTODAY-" + str(SPECIALGRASSENCOUNTERS["garden"].index(gardenPokemonIdToday)))

    if (gardenPokemonIdYesterday is not None):
        gardenPokemonIdYesterday = gardenPokemonIdYesterday if isinstance(gardenPokemonIdYesterday, int) else POKEMON_NAMES.index(gardenPokemonIdYesterday)
        specialPokemon.append("GARDENYESTERDAY-" + str(SPECIALGRASSENCOUNTERS["garden"].index(gardenPokemonIdYesterday)))

    if (gbaGameId is not None):
        specialPokemon.append("GBAGAME-" + str(gbaGameId))

    if (specialPokemon):
        print("/".join(specialPokemon))
        writeMemoryData("specialPokemon", "/".join(specialPokemon))

    # Values are only updated by emulator once every frame, wait 5 to make sure the values are updated
    waitFrames(5)