from pokemon import Pokemon
from utils import LoadJsonMmap
    
# Parse JSON into an object with attributes corresponding to dict keys.
pokemonData = LoadJsonMmap(4096, "testfile")["pokemonData"]
newPokemon = Pokemon(**pokemonData)

print(newPokemon)
# print(json.dumps(pokemonData, indent=4))