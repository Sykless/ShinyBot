from position import Position

class Town():
    def __init__(self, name, zone, shopZone, shopLocation, flyCoordinates, pokemonCenterZone, pokemonCenterLocation):

        self.name = name
        self.zone = zone
        self.flyCoordinates = flyCoordinates

        self.pokemonCenterZone = pokemonCenterZone
        self.pokemonCenterLocation = pokemonCenterLocation
        if pokemonCenterZone is not None:
            self.pokemonCenterMap = open('src/python/data/map/' + name + '-centrePokemon.map').readlines()

        self.shopZone = shopZone
        self.shopLocation = shopLocation
        if shopZone is not None:
            self.shopMap = open('src/python/data/map/' + name + '-shop.map').readlines()