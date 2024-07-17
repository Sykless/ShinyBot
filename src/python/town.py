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

BONAUGURE = Town("bonaugure", 411, None, None, [[2,21]], None, None)
LITTORELLA = Town("littorella", 418, 420, 419, [[4,20]], Position(177,842), Position(187,842))
FELICITE = Town("felicite", 3, 6, 4, [[3,17],[4,17],[3,18],[4,18]], Position(180,776), Position(179,766))
CHARBOURG = Town("charbourg", 45, 48, 46, [[7,17],[8,17],[8,18]], Position(303,756), Position(285,746))
FLORAVILLE = Town("floraville", 426, 428, 427, [[4,13],[4,14]], Position(176,666), Position(184,657))
VESTIGION = Town("vestigion", 65, 69, 66, [[8,10],[9,10],[8,11]], Position(305,530), Position(309,548))
UNIONPOLIS = Town("unionpolis", 86, 101, 87, [[13,15],[14,15],[13,16],[14,16]], Position(465,697), Position(477,710))
BONVILLE = Town("bonville", 433, 435, 434, [[16,14],[17,14]], Position(566,656), Position(571,665))
VOILAROC = Town("voilaroc", 132, 134, None, [[20,12],[21,12],[20,13],[21,13]], Position(717,611), None)
VERCHAMPS = Town("verchamps", 120, 123, 121, [[17,19],[18,19],[17,20],[18,20]], Position(600,815), Position(601,844))
CELESTIA = Town("celestia", 442, 443, 446, [[13,10]], Position(472,538), Position(450,515))
JOLIBERGES = Town("joliberges", 33, 36, 34, [[0,16],[0,17]], Position(58,722), Position(53,740))
FRIMAPIC = Town("frimapic", 165, 168, 166, [[10,0],[10,1]], Position(379,233), Position(353,232))
RIVAMAR = Town("rivamar", 150, 151, 153, [[25,17],[26,17],[25,18],[26,18]], Position(860,784), Position(853,768))
ROUTEVICTOIRE = Town("ligue", 172, 173, None, [[25,12]], Position(842,598), None)
LIGUEPOKEMON = Town("ligue", 172, None, None, [[25,11]], None, None)
AIREDECOMBAT = Town("airedecombat", 188, 189, 191, [[18,7],[19,7]], Position(647,429), Position(660,429))
AIREDESURVIE = Town("airedesurvie", 450, 452, 451, [[19,4]], Position(659,338), Position(663,338))
AIREDEDETENTE = Town("airededetente", 457, 459, None, [[24,8]], Position(802,472), None)