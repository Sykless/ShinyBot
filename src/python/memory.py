
import io
import json
import mmap

def clearPokemonData():
    writePokemonMmap = mmap.mmap(-1, 4096, tagname="pokemonData", access=mmap.ACCESS_WRITE)
    writePokemonMmap.write(bytes("\x00" * 4096, encoding="utf-8"))

def readPokemonData():
    # Read pokemonData as BytesIO object from memory file
    mmapData = mmap.mmap(0, 4096, "pokemonData")
    mmapByes = io.BytesIO(mmapData).read()

    try:
        # Convert BytesIO to string (UTF-8)
        pokemonData = mmapByes.decode("utf-8").split("\x00")[0]

        if (pokemonData):
            try:
                # Convert string pokemonData to JSON
                jsonPokemonData = json.loads(pokemonData)["pokemonData"]
                return jsonPokemonData

            except json.JSONDecodeError as e:
                # Cannot json.loads because junk data has been accumulated : clear memory file
                clearPokemonData()
                print(str(e))
            except Exception as e:
                # pass
                print(pokemonData)
                print(str(e))
    except UnicodeDecodeError as e:
        # Cannot mmapByes.decode because junk data has been accumulated : clear memory file
        clearPokemonData()
        print(str(e))
    except Exception as e:
        # pass
        print(mmapByes)
        print(str(e))

    return None