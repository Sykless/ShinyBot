import mmap

def clearPokemonData():
    writePokemonMmap = mmap.mmap(-1, 4096, tagname="pokemonData", access=mmap.ACCESS_WRITE)
    writePokemonMmap.write(bytes("\x00" * 4096, encoding="utf-8"))