import img
import memory

OVERWORLD_ID = 999
ZONELIST = {}

LIGUEPOKEMON_ID = 172
PISTECYCLABLE_ID = 350
ROUTE213_ID = 373

class Zone():
    def __init__(self, name, zoneId, mapFile, canBike, canFly):
        self.name = name
        self.zoneId = zoneId
        self.map = open('src/python/data/map/' + mapFile + '.map').readlines()
        self.doorList = []
        
        self.canBike = canBike
        self.canFly = canFly

    def addDoor(self, door):
        self.doorList.append(door)

    def getDoorByDestination(self, zone):
        for door in self.doorList:
            if (door.destination.zone.zoneId == zone.zoneId):
                return door

class Position:
    def __init__(self, positionX, positionY, zone):
        self.X = positionX
        self.Y = positionY

        # Provide actual Zone object
        if isinstance(zone, Zone):
            self.zone = zone

        # Provide Zone ID, search for the Zone object in ZONELIST
        elif (isinstance(zone, int) and zone in ZONELIST):

            # Check exceptions before going in ZONELIST
            if (zone == LIGUEPOKEMON_ID):
                self.zone = checkLiguePokemon(positionY)

            elif (zone == ROUTE213_ID):
                self.zone = checkRoute213(positionX, positionY)

            elif (zone == PISTECYCLABLE_ID):
                self.zone = checkPisteCyclable(positionX, positionY)
            else:
                self.zone = ZONELIST[zone]

        # Not Zone object nor known ZoneID
        else:
            self.zone = None
            print("Unknown zone :", end = " ")

    def setDistanceTo(self, position):
        self.distance = abs(self.X - position.X) + abs(self.Y - position.Y)

    def __eq__(self, other):
        if isinstance(other, Position):
            return self.X == other.X and self.Y == other.Y and self.zone.zoneId == other.zone.zoneId
        return False

    def __str__(self):
        return "Position (" + str(self.X) + "," + str(self.Y) + " à " + self.zone.name
    
    def __repr__(self):
        return str(self)

class Door():
    def __init__(self, position: Position, destination: Position):
        self.position = position
        self.destination = destination

class City():
    def __init__(self, name, zoneId, pokemonCenterZone, shopZone, flyCoordinates, pokemonCenterPosition: Position, shopPosition: Position):

        self.name = name
        self.zoneId = zoneId
        self.flyCoordinates = flyCoordinates

        self.pokemonCenterZone = pokemonCenterZone
        self.pokemonCenterLocation = pokemonCenterPosition
        if pokemonCenterZone is not None:
            self.pokemonCenterMap = open('src/python/data/map/city/' + name + '-centrePokemon.map').readlines()

        self.shopZone = shopZone
        self.shopLocation = shopPosition
        if shopZone is not None:
            self.shopMap = open('src/python/data/map/city/' + name + '-shop.map').readlines()

class Orientation():
    def __init__(self, wantedOrientation, currentOrientation):
        self.wantedOrientation = wantedOrientation
        self.currentOrientation = currentOrientation

def getPlayerPosition():
    return Position(**memory.readPositionData())

def getPlayerOrientation():
    return Orientation(**memory.readOrientationData())

# Separation between Pokemon League and Overword is purely based on Y position
def checkLiguePokemon(positionY):
    return LIGUEPOKEMON if positionY < 592 else EAST

# Directly check on Route 213 map if we're on it
def checkRoute213(positionX, positionY):
    return SOUTHEAST if ROUTE213.map[positionY][positionX] == " " else ROUTE213

# Cycling Road shares positions with Route 206 so differentiate them is more complex
def checkPisteCyclable(positionX, positionY):

    # Too high for Route 206 or too low for Cycling Road
    if (positionY < 606):
        return PISTECYCLABLE
    elif (positionY > 681):
        return SOUTHCENTER
    
    # Overlap between Cycling Road and Route 206
    elif (299 <= positionX <= 306):
        if (PISTECYCLABLE.map[positionY][positionX] in ["X","N"]):
            return SOUTHCENTER
        elif (SOUTHCENTER.map[positionY][positionX] in ["X","N"]):
            return PISTECYCLABLE
        # Blind spot : no real reason to be here on route 206, so most likely on Cycling Road
        elif (648 <= positionY <= 654):
            return PISTECYCLABLE
        # Can be under or on the bridge, check if trainer is visible
        else:
            screenshot = img.getScreenshot()
            spritePosition = img.getPlayerOrientation(screenshot)[1]

            # Player not visible, we're under the bridge
            return SOUTHCENTER if spritePosition is None else PISTECYCLABLE
            
    # Every Cycling Road position has been checked, we're on Overworld
    else:
        return SOUTHCENTER

# Overworld
EAST = Zone("East", OVERWORLD_ID, "overworld/east", True, True)
NORTH = Zone("North", OVERWORLD_ID, "overworld/north", False, True)
NORTHCENTER = Zone("Northcenter", OVERWORLD_ID, "overworld/northcenter", True, True)
NORTHEAST = Zone("Northeast", OVERWORLD_ID, "overworld/northeast", True, True)
NORTHWEST = Zone("Northwest", OVERWORLD_ID, "overworld/northwest", True, True)
SOUTH = Zone("South", OVERWORLD_ID, "overworld/south", True, True)
SOUTHCENTER = Zone("Southcenter", OVERWORLD_ID, "overworld/southcenter", True, True)
SOUTHEAST = Zone("Southeast", OVERWORLD_ID, "overworld/southeast", True, True)
SOUTHWEST = Zone("Southwest", OVERWORLD_ID, "overworld/southwesh", True, True)
SECTEURCOMBAT_NORTHWEST = Zone("Secteur Combat - Northwest", OVERWORLD_ID, "overworld/secteurCombat-northwest", True, True)
SECTEURCOMBAT_SOUTHEAST = Zone("Secteur Combat - Southeast", OVERWORLD_ID, "overworld/secteurCombat-southeast", True, True)

# Littorella
LITTORELLA_CENTREPOKEMON = Zone("Littorella - Centre Pokémon", 420, "city/littorella-centrePokemon", False, False)
LITTORELLA_CENTREPOKEMON.addDoor(Door(Position(8,13,LITTORELLA_CENTREPOKEMON), Position(177,843,SOUTHWEST)))
LITTORELLA_SHOP = Zone("Littorella - Shop", 419, "city/littorella-shop", False, False)
LITTORELLA_SHOP.addDoor(Door(Position(3,12,LITTORELLA_SHOP), Position(187,843,SOUTHWEST)))
SOUTHWEST.addDoor(Door(Position(177,842,SOUTHWEST), Position(8,12,LITTORELLA_CENTREPOKEMON)))
SOUTHWEST.addDoor(Door(Position(187,842,SOUTHWEST), Position(3,11,LITTORELLA_SHOP)))

# Féli-Cité
FELICITE_CENTREPOKEMON = Zone("Féli-Cité - Centre Pokémon", 6, "city/felicite-centrePokemon", False, False)
FELICITE_CENTREPOKEMON.addDoor(Door(Position(8,13,FELICITE_CENTREPOKEMON), Position(180,777,SOUTHWEST)))
FELICITE_SHOP = Zone("Féli-Cité - Shop", 4, "city/felicite-shop", False, False)
FELICITE_SHOP.addDoor(Door(Position(3,12,FELICITE_SHOP), Position(179,767,SOUTHWEST)))
SOUTHWEST.addDoor(Door(Position(180,776,SOUTHWEST), Position(8,12,FELICITE_CENTREPOKEMON)))
SOUTHWEST.addDoor(Door(Position(179,766,SOUTHWEST), Position(3,11,FELICITE_SHOP)))

# Charbourg
CHARBOURG_CENTREPOKEMON = Zone("Charbourg - Centre Pokémon", 48, "city/charbourg-centrePokemon", False, False)
CHARBOURG_CENTREPOKEMON.addDoor(Door(Position(8,13,CHARBOURG_CENTREPOKEMON), Position(303,757,SOUTHCENTER)))
CHARBOURG_SHOP = Zone("Charbourg - Shop", 46, "city/charbourg-shop", False, False)
CHARBOURG_SHOP.addDoor(Door(Position(3,12,CHARBOURG_SHOP), Position(285,747,SOUTHCENTER)))
SOUTHCENTER.addDoor(Door(Position(303,756,SOUTHCENTER), Position(8,12,CHARBOURG_CENTREPOKEMON)))
SOUTHCENTER.addDoor(Door(Position(285,746,SOUTHCENTER), Position(3,11,CHARBOURG_SHOP)))

# Floraville
FLORAVILLE_CENTREPOKEMON = Zone("Floraville - Centre Pokémon", 428, "city/floraville-centrePokemon", False, False)
FLORAVILLE_CENTREPOKEMON.addDoor(Door(Position(8,13,FLORAVILLE_CENTREPOKEMON), Position(176,667,NORTHWEST)))
FLORAVILLE_SHOP = Zone("Floraville - Shop", 427, "city/floraville-shop", False, False)
FLORAVILLE_SHOP.addDoor(Door(Position(3,12,FLORAVILLE_SHOP), Position(184,658,NORTHWEST)))
NORTHWEST.addDoor(Door(Position(176,666,NORTHWEST), Position(8,12,FLORAVILLE_CENTREPOKEMON)))
NORTHWEST.addDoor(Door(Position(184,657,NORTHWEST), Position(3,11,FLORAVILLE_SHOP)))

# Vestigion
VESTIGION_CENTREPOKEMON = Zone("Vestigion - Centre Pokémon", 69, "city/vestigion-centrePokemon", False, False)
VESTIGION_CENTREPOKEMON.addDoor(Door(Position(8,13,VESTIGION_CENTREPOKEMON), Position(305,531,NORTHWEST)))
VESTIGION_SHOP = Zone("Vestigion - Shop", 66, "city/vestigion-shop", False, False)
VESTIGION_SHOP.addDoor(Door(Position(3,12,VESTIGION_SHOP), Position(309,549,NORTHWEST)))
NORTHWEST.addDoor(Door(Position(305,530,NORTHWEST), Position(8,12,VESTIGION_CENTREPOKEMON)))
NORTHWEST.addDoor(Door(Position(309,548,NORTHWEST), Position(3,11,VESTIGION_SHOP)))

# Unionpolis
UNIONPOLIS = Zone("Unionpolis", 86, "city/unionpolis", True, True)
UNIONPOLIS_CENTREPOKEMON = Zone("Unionpolis - Centre Pokémon", 101, "city/unionpolis-centrePokemon", False, False)
UNIONPOLIS_CENTREPOKEMON.addDoor(Door(Position(8,13,UNIONPOLIS_CENTREPOKEMON), Position(465,698,UNIONPOLIS)))
UNIONPOLIS_SHOP = Zone("Unionpolis - Shop", 87, "city/unionpolis-shop", False, False)
UNIONPOLIS_SHOP.addDoor(Door(Position(3,12,UNIONPOLIS_SHOP), Position(477,711,UNIONPOLIS)))
UNIONPOLIS.addDoor(Door(Position(465,697,UNIONPOLIS), Position(8,12,UNIONPOLIS_CENTREPOKEMON)))
UNIONPOLIS.addDoor(Door(Position(477,710,UNIONPOLIS), Position(3,11,UNIONPOLIS_SHOP)))

# Bonville
BONVILLE_CENTREPOKEMON = Zone("Bonville - Centre Pokémon", 435, "city/bonville-centrePokemon", False, False)
BONVILLE_CENTREPOKEMON.addDoor(Door(Position(8,13,BONVILLE_CENTREPOKEMON), Position(566,657,NORTHCENTER)))
BONVILLE_SHOP = Zone("Bonville - Shop", 434, "city/bonville-shop", False, False)
BONVILLE_SHOP.addDoor(Door(Position(3,12,BONVILLE_SHOP), Position(571,666,NORTHCENTER)))
NORTHCENTER.addDoor(Door(Position(566,656,NORTHCENTER), Position(8,12,BONVILLE_CENTREPOKEMON)))
NORTHCENTER.addDoor(Door(Position(571,665,NORTHCENTER), Position(3,11,BONVILLE_SHOP)))

# Voilaroc
VOILAROC = Zone("Voilaroc", 132, "city/voilaroc", True, True)
VOILAROC_CENTREPOKEMON = Zone("Voilaroc - Centre Pokémon", 134, "city/voilaroc-centrePokemon", False, False)
VOILAROC_CENTREPOKEMON.addDoor(Door(Position(8,13,VOILAROC_CENTREPOKEMON), Position(566,657,VOILAROC)))
VOILAROC_CENTRECOMMERCIAL = Zone("Voilaroc - Centre Commercial", 137, "city/centreCommercial-1", False, False)
VOILAROC_CENTRECOMMERCIALETAGE1 = Zone("Voilaroc - Centre Commercial Étage 1", 138, "city/centreCommercial-2", False, False)
VOILAROC_CENTRECOMMERCIALETAGE2 = Zone("Voilaroc - Centre Commercial Étage 2", 139, "city/centreCommercial-3", False, False)
VOILAROC_CENTRECOMMERCIALETAGE3 = Zone("Voilaroc - Centre Commercial Étage 3", 140, "city/centreCommercial-4", False, False)
VOILAROC_CENTRECOMMERCIALETAGE4 = Zone("Voilaroc - Centre Commercial Étage 4", 141, "city/centreCommercial-5", False, False)
VOILAROC_CENTRECOMMERCIALASCENSEUR = Zone("Voilaroc - Centre Commercial Ascenseur", 142, "city/centreCommercial-7", False, False)
VOILAROC_CENTRECOMMERCIALSOUSSOL1 = Zone("Voilaroc - Centre Commercial Sous-Sol 1", 566, "city/centreCommercial-6", False, False)
VOILAROC_CENTRECOMMERCIAL.addDoor(Door(Position(10,13,VOILAROC_CENTRECOMMERCIAL), Position(701,604,VOILAROC)))
VOILAROC_CENTRECOMMERCIAL.addDoor(Door(Position(7,8,VOILAROC_CENTRECOMMERCIAL), Position(12,8,VOILAROC_CENTRECOMMERCIALSOUSSOL1)))
VOILAROC_CENTRECOMMERCIAL.addDoor(Door(Position(12,8,VOILAROC_CENTRECOMMERCIAL), Position(6,8,VOILAROC_CENTRECOMMERCIALETAGE1)))
VOILAROC_CENTRECOMMERCIAL.addDoor(Door(Position(15,2,VOILAROC_CENTRECOMMERCIAL), Position(3,6,VOILAROC_CENTRECOMMERCIALASCENSEUR)))
VOILAROC_CENTRECOMMERCIALETAGE1.addDoor(Door(Position(7,8,VOILAROC_CENTRECOMMERCIALETAGE1), Position(13,8,VOILAROC_CENTRECOMMERCIAL)))
VOILAROC_CENTRECOMMERCIALETAGE1.addDoor(Door(Position(12,8,VOILAROC_CENTRECOMMERCIALETAGE1), Position(6,8,VOILAROC_CENTRECOMMERCIALETAGE2)))
VOILAROC_CENTRECOMMERCIALETAGE1.addDoor(Door(Position(15,2,VOILAROC_CENTRECOMMERCIALETAGE1), Position(3,6,VOILAROC_CENTRECOMMERCIALASCENSEUR)))
VOILAROC_CENTRECOMMERCIALETAGE2.addDoor(Door(Position(7,8,VOILAROC_CENTRECOMMERCIALETAGE2), Position(13,8,VOILAROC_CENTRECOMMERCIALETAGE1)))
VOILAROC_CENTRECOMMERCIALETAGE2.addDoor(Door(Position(12,8,VOILAROC_CENTRECOMMERCIALETAGE2), Position(6,8,VOILAROC_CENTRECOMMERCIALETAGE3)))
VOILAROC_CENTRECOMMERCIALETAGE2.addDoor(Door(Position(15,2,VOILAROC_CENTRECOMMERCIALETAGE2), Position(3,6,VOILAROC_CENTRECOMMERCIALASCENSEUR)))
VOILAROC_CENTRECOMMERCIALETAGE3.addDoor(Door(Position(7,8,VOILAROC_CENTRECOMMERCIALETAGE3), Position(13,8,VOILAROC_CENTRECOMMERCIALETAGE2)))
VOILAROC_CENTRECOMMERCIALETAGE3.addDoor(Door(Position(12,8,VOILAROC_CENTRECOMMERCIALETAGE3), Position(6,8,VOILAROC_CENTRECOMMERCIALETAGE4)))
VOILAROC_CENTRECOMMERCIALETAGE3.addDoor(Door(Position(15,2,VOILAROC_CENTRECOMMERCIALETAGE3), Position(3,6,VOILAROC_CENTRECOMMERCIALASCENSEUR)))
VOILAROC_CENTRECOMMERCIALETAGE4.addDoor(Door(Position(7,8,VOILAROC_CENTRECOMMERCIALETAGE4), Position(13,8,VOILAROC_CENTRECOMMERCIALETAGE3)))
VOILAROC_CENTRECOMMERCIALETAGE4.addDoor(Door(Position(15,2,VOILAROC_CENTRECOMMERCIALETAGE4), Position(3,6,VOILAROC_CENTRECOMMERCIALASCENSEUR)))
VOILAROC_CENTRECOMMERCIALSOUSSOL1.addDoor(Door(Position(11,8,VOILAROC_CENTRECOMMERCIALSOUSSOL1), Position(6,8,VOILAROC_CENTRECOMMERCIAL)))
VOILAROC_CENTRECOMMERCIALSOUSSOL1.addDoor(Door(Position(14,2,VOILAROC_CENTRECOMMERCIALSOUSSOL1), Position(3,6,VOILAROC_CENTRECOMMERCIALASCENSEUR)))
VOILAROC_CENTRECOMMERCIALASCENSEUR.addDoor(Door(Position(3,7,VOILAROC_CENTRECOMMERCIALASCENSEUR), Position(15,3,VOILAROC_CENTRECOMMERCIAL)))
VOILAROC.addDoor(Door(Position(566,656,VOILAROC), Position(8,12,VOILAROC_CENTREPOKEMON)))
VOILAROC.addDoor(Door(Position(701,603,VOILAROC), Position(10,12,VOILAROC_CENTRECOMMERCIAL)))

# Verchamps
VERCHAMPS_CENTREPOKEMON = Zone("Verchamps - Centre Pokémon", 123, "city/verchamps-centrePokemon", False, False)
VERCHAMPS_CENTREPOKEMON.addDoor(Door(Position(8,13,VERCHAMPS_CENTREPOKEMON), Position(600,816,SOUTH)))
VERCHAMPS_SHOP = Zone("Verchamps - Shop", 121, "city/verchamps-shop", False, False)
VERCHAMPS_SHOP.addDoor(Door(Position(3,12,VERCHAMPS_SHOP), Position(601,845,SOUTH)))
SOUTH.addDoor(Door(Position(600,815,SOUTH), Position(8,12,VERCHAMPS_CENTREPOKEMON)))
SOUTH.addDoor(Door(Position(601,844,SOUTH), Position(3,11,VERCHAMPS_SHOP)))

# Célestia
CELESTIA_CENTREPOKEMON = Zone("Célestia - Centre Pokémon", 443, "city/celestia-centrePokemon", False, False)
CELESTIA_CENTREPOKEMON.addDoor(Door(Position(8,13,CELESTIA_CENTREPOKEMON), Position(472,539,NORTHCENTER)))
CELESTIA_SHOP = Zone("Célestia - Shop", 446, "city/celestia-shop", False, False)
CELESTIA_SHOP.addDoor(Door(Position(4,9,CELESTIA_SHOP), Position(450,516,NORTHCENTER)))
NORTHCENTER.addDoor(Door(Position(472,538,NORTHCENTER), Position(8,12,CELESTIA_CENTREPOKEMON)))
NORTHCENTER.addDoor(Door(Position(450,515,NORTHCENTER), Position(4,8,CELESTIA_SHOP)))

# Joliberges
JOLIBERGES = Zone("Joliberges", 33, "city/joliberges", True, True)
JOLIBERGES_CENTREPOKEMON = Zone("Joliberges - Centre Pokémon", 36, "city/joliberges-centrePokemon", False, False)
JOLIBERGES_CENTREPOKEMON.addDoor(Door(Position(8,13,JOLIBERGES_CENTREPOKEMON), Position(58,723,JOLIBERGES)))
JOLIBERGES_SHOP = Zone("Joliberges - Shop", 34, "city/joliberges-shop", False, False)
JOLIBERGES_SHOP.addDoor(Door(Position(3,12,JOLIBERGES_SHOP), Position(53,741,JOLIBERGES)))
JOLIBERGES.addDoor(Door(Position(58,722,JOLIBERGES), Position(8,12,JOLIBERGES_CENTREPOKEMON)))
JOLIBERGES.addDoor(Door(Position(53,740,JOLIBERGES), Position(3,11,JOLIBERGES_SHOP)))

# Frimapic
FRIMAPIC_CENTREPOKEMON = Zone("Frimapic - Centre Pokémon", 168, "city/frimapic-centrePokemon", False, False)
FRIMAPIC_CENTREPOKEMON.addDoor(Door(Position(8,13,FRIMAPIC_CENTREPOKEMON), Position(379,234,NORTH)))
FRIMAPIC_SHOP = Zone("Frimapic - Shop", 166, "city/frimapic-shop", False, False)
FRIMAPIC_SHOP.addDoor(Door(Position(3,12,FRIMAPIC_SHOP), Position(353,233,NORTH)))
NORTH.addDoor(Door(Position(379,233,NORTH), Position(8,12,FRIMAPIC_CENTREPOKEMON)))
NORTH.addDoor(Door(Position(353,232,NORTH), Position(3,11,FRIMAPIC_SHOP)))

# Rivamar
RIVAMAR_CENTREPOKEMON = Zone("Rivamar - Centre Pokémon", 151, "city/rivamar-centrePokemon", False, False)
RIVAMAR_CENTREPOKEMON.addDoor(Door(Position(8,13,RIVAMAR_CENTREPOKEMON), Position(860,785,EAST)))
RIVAMAR_SHOP = Zone("Rivamar - Shop", 153, "city/rivamar-shop", False, False)
RIVAMAR_SHOP.addDoor(Door(Position(3,12,RIVAMAR_SHOP), Position(853,769,EAST)))
EAST.addDoor(Door(Position(860,784,EAST), Position(8,12,RIVAMAR_CENTREPOKEMON)))
EAST.addDoor(Door(Position(853,768,EAST), Position(3,11,RIVAMAR_SHOP)))

# Ligue Pokémon
LIGUEPOKEMON = Zone("Ligue Pokémon", 172, "city/liguePokemon-1", True, True)
LIGUEPOKEMON_CENTREPOKEMON = Zone("Route Victoire - Centre Pokémon", 173, "city/liguePokemon-centrePokemon", False, False)
LIGUEPOKEMON_INTERIEUR = Zone("Ligue Pokémon - Intérieur", 175, "city/liguePokemon-2", False, False)
LIGUEPOKEMON_CENTREPOKEMON.addDoor(Door(Position(8,13,LIGUEPOKEMON_CENTREPOKEMON), Position(842,599,EAST)))
LIGUEPOKEMON_INTERIEUR.addDoor(Door(Position(11,12,LIGUEPOKEMON_INTERIEUR), Position(847,560,LIGUEPOKEMON)))
EAST.addDoor(Door(Position(842,598,EAST), Position(8,12,LIGUEPOKEMON_CENTREPOKEMON)))
LIGUEPOKEMON.addDoor(Door(Position(847,559,LIGUEPOKEMON), Position(11,11,LIGUEPOKEMON_INTERIEUR)))

# Aire de Combat
AIREDECOMBAT_CENTREPOKEMON = Zone("Aire de Combat - Centre Pokémon", 189, "city/airedecombat-centrePokemon", False, False)
AIREDECOMBAT_CENTREPOKEMON.addDoor(Door(Position(8,13,AIREDECOMBAT_CENTREPOKEMON), Position(647,430,SECTEURCOMBAT_SOUTHEAST)))
AIREDECOMBAT_SHOP = Zone("Aire de Combat - Shop", 191, "city/airedecombat-shop", False, False)
AIREDECOMBAT_SHOP.addDoor(Door(Position(3,12,AIREDECOMBAT_SHOP), Position(660,430,SECTEURCOMBAT_SOUTHEAST)))
SECTEURCOMBAT_SOUTHEAST.addDoor(Door(Position(647,429,SECTEURCOMBAT_SOUTHEAST), Position(8,12,AIREDECOMBAT_CENTREPOKEMON)))
SECTEURCOMBAT_SOUTHEAST.addDoor(Door(Position(660,429,SECTEURCOMBAT_SOUTHEAST), Position(3,11,AIREDECOMBAT_SHOP)))

# Aire de Survie
AIREDESURVIE_CENTREPOKEMON = Zone("Aire de Survie - Centre Pokémon", 452, "city/airedesurvie-centrePokemon", False, False)
AIREDESURVIE_CENTREPOKEMON.addDoor(Door(Position(8,13,AIREDESURVIE_CENTREPOKEMON), Position(659,339,SECTEURCOMBAT_NORTHWEST)))
AIREDESURVIE_SHOP = Zone("Aire de Survie - Shop", 451, "city/airedesurvie-shop", False, False)
AIREDESURVIE_SHOP.addDoor(Door(Position(3,12,AIREDESURVIE_SHOP), Position(663,339,SECTEURCOMBAT_NORTHWEST)))
SECTEURCOMBAT_NORTHWEST.addDoor(Door(Position(659,338,SECTEURCOMBAT_NORTHWEST), Position(8,12,AIREDESURVIE_CENTREPOKEMON)))
SECTEURCOMBAT_NORTHWEST.addDoor(Door(Position(663,338,SECTEURCOMBAT_NORTHWEST), Position(3,11,AIREDESURVIE_SHOP)))

# Aire de Détente
AIREDEDETENTE_CENTREPOKEMON = Zone("Aire de Détente - Centre Pokémon", 459, "city/airededetente-centrePokemon", False, False)
AIREDEDETENTE_CENTREPOKEMON.addDoor(Door(Position(8,13,AIREDEDETENTE_CENTREPOKEMON), Position(802,473,SECTEURCOMBAT_SOUTHEAST)))
SECTEURCOMBAT_SOUTHEAST.addDoor(Door(Position(802,472,SECTEURCOMBAT_SOUTHEAST), Position(8,12,AIREDEDETENTE_CENTREPOKEMON)))

# Passage Route 206 <-> Vestigion
ROUTE206_PASSAGEVESTIGION = Zone("Route 206 - Passage Vestigion", 80, "route/route206-passageVestigion", True, False)
ROUTE206_PASSAGEVESTIGION.addDoor(Door(Position(7,2,ROUTE206_PASSAGEVESTIGION), Position(304,569,NORTHWEST)))
NORTHWEST.addDoor(Door(Position(304,570,NORTHWEST), Position(7,3,ROUTE206_PASSAGEVESTIGION)))

# Passage Route 206 <-> Charbourg
ROUTE206_PASSAGECHARBOURG = Zone("Route 206 - Passage Charbourg", 351, "route/route206-passageCharbourg", True, False)
ROUTE206_PASSAGECHARBOURG.addDoor(Door(Position(7,13,ROUTE206_PASSAGECHARBOURG), Position(302,689,SOUTHCENTER)))
SOUTHCENTER.addDoor(Door(Position(302,688,SOUTHCENTER), Position(7,12,ROUTE206_PASSAGECHARBOURG)))

# Passage Route 208 <-> Unionpolis
ROUTE208 = Zone("Route 208", 354, "route/route208", True, True)
ROUTE208_PASSAGEUNIONPOLIS = Zone("Route 208 - Passage Unionpolis", 109, "route/route208-passageUnionpolis", True, False)
ROUTE208_PASSAGEUNIONPOLIS.addDoor(Door(Position(0,7,ROUTE208_PASSAGEUNIONPOLIS), Position(447,726,ROUTE208)))
ROUTE208_PASSAGEUNIONPOLIS.addDoor(Door(Position(11,7,ROUTE208_PASSAGEUNIONPOLIS), Position(454,726,UNIONPOLIS)))
ROUTE208.addDoor(Door(Position(448,726,ROUTE208), Position(1,7,ROUTE208_PASSAGEUNIONPOLIS)))
UNIONPOLIS.addDoor(Door(Position(453,726,UNIONPOLIS), Position(10,7,ROUTE208_PASSAGEUNIONPOLIS)))

# Passage Route 209 <-> Unionpolis
ROUTE209_PASSAGEUNIONPOLIS = Zone("Route 209 - Passage Unionpolis", 110, "route/route209-passageUnionpolis", True, False)
ROUTE209_PASSAGEUNIONPOLIS.addDoor(Door(Position(0,7,ROUTE209_PASSAGEUNIONPOLIS), Position(505,726,UNIONPOLIS)))
ROUTE209_PASSAGEUNIONPOLIS.addDoor(Door(Position(11,7,ROUTE209_PASSAGEUNIONPOLIS), Position(512,726,NORTHCENTER)))
UNIONPOLIS.addDoor(Door(Position(506,726,UNIONPOLIS), Position(1,7,ROUTE209_PASSAGEUNIONPOLIS)))
NORTHCENTER.addDoor(Door(Position(511,726,NORTHCENTER), Position(10,7,ROUTE209_PASSAGEUNIONPOLIS)))

# Passage Route 212 <-> Unionpolis
ROUTE212_PASSAGEUNIONPOLIS = Zone("Route 212 - Passage Unionpolis", 111, "route/route212-passageUnionpolis", True, False)
ROUTE212_PASSAGEUNIONPOLIS.addDoor(Door(Position(5,2,ROUTE212_PASSAGEUNIONPOLIS), Position(458,729,UNIONPOLIS)))
ROUTE212_PASSAGEUNIONPOLIS.addDoor(Door(Position(5,13,ROUTE212_PASSAGEUNIONPOLIS), Position(458,737,SOUTH)))
UNIONPOLIS.addDoor(Door(Position(458,730,UNIONPOLIS), Position(5,3,ROUTE212_PASSAGEUNIONPOLIS)))
SOUTH.addDoor(Door(Position(458,736,SOUTH), Position(5,12,ROUTE212_PASSAGEUNIONPOLIS)))

# Passage Route 215 <-> Voilaroc
ROUTE215_PASSAGEVOILAROC = Zone("Route 215 - Passage Voilaroc", 149, "route/route215-passageVoilaroc", True, False)
ROUTE215_PASSAGEVOILAROC.addDoor(Door(Position(0,7,ROUTE215_PASSAGEVOILAROC), Position(671,598,NORTHCENTER)))
ROUTE215_PASSAGEVOILAROC.addDoor(Door(Position(11,7,ROUTE215_PASSAGEVOILAROC), Position(678,598,VOILAROC)))
NORTHCENTER.addDoor(Door(Position(672,598,NORTHCENTER), Position(1,7,ROUTE215_PASSAGEVOILAROC)))
VOILAROC.addDoor(Door(Position(677,598,VOILAROC), Position(10,7,ROUTE215_PASSAGEVOILAROC)))

# Passage Route 214 <-> Voilaroc
ROUTE214_PASSAGEVOILAROC = Zone("Route 214 - Passage Voilaroc", 381, "route/route214-passageVoilaroc", True, False)
ROUTE214_PASSAGEVOILAROC.addDoor(Door(Position(5,2,ROUTE214_PASSAGEVOILAROC), Position(718,638,VOILAROC)))
ROUTE214_PASSAGEVOILAROC.addDoor(Door(Position(5,13,ROUTE214_PASSAGEVOILAROC), Position(718,646,SOUTHEAST)))
VOILAROC.addDoor(Door(Position(718,639,VOILAROC), Position(5,3,ROUTE214_PASSAGEVOILAROC)))
SOUTHEAST.addDoor(Door(Position(718,645,SOUTHEAST), Position(5,12,ROUTE214_PASSAGEVOILAROC)))

# Passage Route 213 <-> Verchamps
ROUTE213 = Zone("Route 213", 373, "route/route213", True, True)
ROUTE213_PASSAGEVERCHAMPS = Zone("Route 213 - Passage Verchamps", 374, "route/route213-passageVerchamps", True, False)
ROUTE213_PASSAGEVERCHAMPS.addDoor(Door(Position(0,7,ROUTE213_PASSAGEVERCHAMPS), Position(639,812,SOUTH)))
ROUTE213_PASSAGEVERCHAMPS.addDoor(Door(Position(11,7,ROUTE213_PASSAGEVERCHAMPS), Position(646,812,ROUTE213)))
SOUTH.addDoor(Door(Position(640,812,SOUTH), Position(1,7,ROUTE213_PASSAGEVERCHAMPS)))
ROUTE213.addDoor(Door(Position(645,812,ROUTE213), Position(10,7,ROUTE213_PASSAGEVERCHAMPS)))

# Passage Route 218 <-> Féli-Cité
ROUTE218 = Zone("Route 218", 388, "route/route218", True, True)
ROUTE218_PASSAGEFELICITE = Zone("Route 218 - Passage Féli-Cité", 389, "route/route218-passageFelicite", True, False)
ROUTE218_PASSAGEFELICITE.addDoor(Door(Position(0,7,ROUTE218_PASSAGEFELICITE), Position(128,758,ROUTE218)))
ROUTE218_PASSAGEFELICITE.addDoor(Door(Position(11,7,ROUTE218_PASSAGEFELICITE), Position(121,758,SOUTHWEST)))
SOUTHWEST.addDoor(Door(Position(127,758,SOUTHWEST), Position(1,7,ROUTE218_PASSAGEFELICITE)))
ROUTE218.addDoor(Door(Position(122,758,ROUTE218), Position(10,7,ROUTE218_PASSAGEFELICITE)))

# Passage Route 218 <-> Joliberges
ROUTE218_PASSAGEJOLIBERGES = Zone("Route 218 - Passage Joliberges", 390, "route/route218-passageJoliberges", True, False)
ROUTE218_PASSAGEJOLIBERGES.addDoor(Door(Position(0,7,ROUTE218_PASSAGEJOLIBERGES), Position(63,754,JOLIBERGES)))
ROUTE218_PASSAGEJOLIBERGES.addDoor(Door(Position(11,7,ROUTE218_PASSAGEJOLIBERGES), Position(70,754,ROUTE218)))
JOLIBERGES.addDoor(Door(Position(64,754,JOLIBERGES), Position(1,7,ROUTE218_PASSAGEJOLIBERGES)))
ROUTE218.addDoor(Door(Position(69,754,ROUTE218), Position(10,7,ROUTE218_PASSAGEJOLIBERGES)))

# Passage Route 222 <-> Rivamar
ROUTE222_PASSAGERIVAMAR = Zone("Route 222 - Passage Rivamar", 398, "route/route222-passageRivamar", True, False)
ROUTE222_PASSAGERIVAMAR.addDoor(Door(Position(0,7,ROUTE222_PASSAGERIVAMAR), Position(825,790,SOUTHEAST)))
ROUTE222_PASSAGERIVAMAR.addDoor(Door(Position(11,7,ROUTE222_PASSAGERIVAMAR), Position(832,790,EAST)))
SOUTHEAST.addDoor(Door(Position(826,790,SOUTHEAST), Position(1,7,ROUTE222_PASSAGERIVAMAR)))
EAST.addDoor(Door(Position(831,790,EAST), Position(10,7,ROUTE222_PASSAGERIVAMAR)))

# Passage Route 225 <-> Aire de Combat
ROUTE225_PASSAGEAIREDECOMBAT = Zone("Route 225 - Passage Aire de Combat", 193, "route/route225-passageAiredecombat", True, False)
ROUTE225_PASSAGEAIREDECOMBAT.addDoor(Door(Position(5,2,ROUTE225_PASSAGEAIREDECOMBAT), Position(630,413,SECTEURCOMBAT_NORTHWEST)))
ROUTE225_PASSAGEAIREDECOMBAT.addDoor(Door(Position(5,13,ROUTE225_PASSAGEAIREDECOMBAT), Position(630,422,SECTEURCOMBAT_SOUTHEAST)))
SECTEURCOMBAT_NORTHWEST.addDoor(Door(Position(630,414,SECTEURCOMBAT_NORTHWEST), Position(5,3,ROUTE225_PASSAGEAIREDECOMBAT)))
SECTEURCOMBAT_SOUTHEAST.addDoor(Door(Position(630,421,SECTEURCOMBAT_SOUTHEAST), Position(5,12,ROUTE225_PASSAGEAIREDECOMBAT)))

# Passage Route 226 <-> Route 228
ROUTE226_PASSAGEROUTE228 = Zone("Route 226 - Passage Route 228", 501, "route/route226-passageRoute228", True, False)
ROUTE226_PASSAGEROUTE228.addDoor(Door(Position(0,7,ROUTE226_PASSAGEROUTE228), Position(767,330,SECTEURCOMBAT_NORTHWEST)))
ROUTE226_PASSAGEROUTE228.addDoor(Door(Position(11,7,ROUTE226_PASSAGEROUTE228), Position(774,330,SECTEURCOMBAT_SOUTHEAST)))
SECTEURCOMBAT_NORTHWEST.addDoor(Door(Position(768,330,SECTEURCOMBAT_NORTHWEST), Position(1,7,ROUTE226_PASSAGEROUTE228)))
SECTEURCOMBAT_SOUTHEAST.addDoor(Door(Position(773,330,SECTEURCOMBAT_SOUTHEAST), Position(10,7,ROUTE226_PASSAGEROUTE228)))

# Entrée Charbourg
ENTREECHARBOURG = Zone("Entrée Charbourg", 258, "dungeon/entreeCharbourg-1", True, False)
ENTREECHARBOURG_SOUSSOL1 = Zone("Entrée Charbourg - Sous-Sol 1", 259, "dungeon/entreeCharbourg-2", True, False)
ENTREECHARBOURG.addDoor(Door(Position(3,22,ENTREECHARBOURG), Position(246,749,SOUTHWEST)))
ENTREECHARBOURG.addDoor(Door(Position(28,22,ENTREECHARBOURG), Position(258,749,SOUTHCENTER)))
ENTREECHARBOURG.addDoor(Door(Position(21,5,ENTREECHARBOURG), Position(48,4,ENTREECHARBOURG_SOUSSOL1)))
ENTREECHARBOURG_SOUSSOL1.addDoor(Door(Position(47,4,ENTREECHARBOURG_SOUSSOL1), Position(20,5,ENTREECHARBOURG)))
SOUTHWEST.addDoor(Door(Position(247,749,SOUTHWEST), Position(4,22,ENTREECHARBOURG)))
SOUTHCENTER.addDoor(Door(Position(257,749,SOUTHCENTER), Position(27,22,ENTREECHARBOURG)))

# Chemin Rocheux
CHEMINROCHEUX = Zone("Chemin Rocheux", 254, "dungeon/cheminRocheux", True, False)
CHEMINROCHEUX.addDoor(Door(Position(19,51,CHEMINROCHEUX), Position(171,706,SOUTHWEST)))
CHEMINROCHEUX.addDoor(Door(Position(28,45,CHEMINROCHEUX), Position(180,699,NORTHWEST)))
SOUTHWEST.addDoor(Door(Position(171,705,SOUTHWEST), Position(19,50,CHEMINROCHEUX)))
NORTHWEST.addDoor(Door(Position(180,698,NORTHWEST), Position(28,44,CHEMINROCHEUX)))

# Forêt de Vestigion
FORETVESTIGION = Zone("Forêt de Vestigion", 203, "dungeon/foretVestigion", True, True)
FORETVESTIGION.addDoor(Door(Position(28,87,FORETVESTIGION), Position(206,582,NORTHWEST)))
FORETVESTIGION.addDoor(Door(Position(87,36,FORETVESTIGION), Position(259,524,NORTHWEST)))
NORTHWEST.addDoor(Door(Position(206,581,NORTHWEST), Position(28,86,FORETVESTIGION)))
NORTHWEST.addDoor(Door(Position(258,524,NORTHWEST), Position(86,36,FORETVESTIGION)))

# Piste Cyclable
PISTECYCLABLE = Zone("Piste Cyclable", 350, "route/pisteCyclable", True, True)
PISTECYCLABLE.addDoor(Door(Position(304,576,PISTECYCLABLE), Position(7,12,ROUTE206_PASSAGEVESTIGION)))
PISTECYCLABLE.addDoor(Door(Position(302,682,PISTECYCLABLE), Position(7,3,ROUTE206_PASSAGECHARBOURG)))
ROUTE206_PASSAGEVESTIGION.addDoor(Door(Position(7,13,ROUTE206_PASSAGEVESTIGION), Position(304,577,PISTECYCLABLE)))
ROUTE206_PASSAGECHARBOURG.addDoor(Door(Position(7,2,ROUTE206_PASSAGECHARBOURG), Position(302,681,PISTECYCLABLE)))

# Grotte Revêche
GROTTEREVECHE = Zone("Grotte Revêche", 284, "dungeon/grotteReveche-1", True, False)
GROTTEREVECHE_SOUSSOL = Zone("Grotte Revêche - Sous-Sol", 285, "dungeon/grotteReveche-2", True, False)
GROTTEREVECHE.addDoor(Door(Position(30,56,GROTTEREVECHE), Position(299,612,SOUTHCENTER)))
GROTTEREVECHE.addDoor(Door(Position(41,54,GROTTEREVECHE), Position(310,608,SOUTHCENTER)))
GROTTEREVECHE.addDoor(Door(Position(27,54,GROTTEREVECHE), Position(16,40,GROTTEREVECHE_SOUSSOL)))
GROTTEREVECHE.addDoor(Door(Position(54,54,GROTTEREVECHE), Position(43,38,GROTTEREVECHE_SOUSSOL)))
GROTTEREVECHE_SOUSSOL.addDoor(Door(Position(17,40,GROTTEREVECHE_SOUSSOL), Position(28,54,GROTTEREVECHE)))
GROTTEREVECHE_SOUSSOL.addDoor(Door(Position(44,38,GROTTEREVECHE_SOUSSOL), Position(55,54,GROTTEREVECHE)))
SOUTHCENTER.addDoor(Door(Position(299,611,SOUTHCENTER), Position(30,55,GROTTEREVECHE)))
SOUTHCENTER.addDoor(Door(Position(310,607,SOUTHCENTER), Position(41,53,GROTTEREVECHE)))

# Mont Couronné
MONTCOURONNE_PASSAGECHARBOURG = Zone("Mont Couronné - Passage Charbourg", 207, "dungeon/montCouronne-1", True, False)
MONTCOURONNE_SALLE1 = Zone("Mont Couronné - Salle 1", 208, "dungeon/montCouronne-2", True, False)
MONTCOURONNE_SALLE2 = Zone("Mont Couronné - Salle 2", 209, "dungeon/montCouronne-3", True, False)
MONTCOURONNE_EXTERIEUR1 = Zone("Mont Couronné - Extérieur 1", 211, "dungeon/montCouronne-4", False, True)
MONTCOURONNE_EXTERIEUR2 = Zone("Mont Couronné - Extérieur 2", 210, "dungeon/montCouronne-6", False, True)
MONTCOURONNE_SALLE3 = Zone("Mont Couronné - Salle 3", 212, "dungeon/montCouronne-5", True, False)
MONTCOURONNE_SALLE4 = Zone("Mont Couronné - Salle 4", 213, "dungeon/montCouronne-7", True, False)
MONTCOURONNE_SALLE5 = Zone("Mont Couronné - Salle 5", 214, "dungeon/montCouronne-8", True, False)
MONTCOURONNE_SALLE6 = Zone("Mont Couronné - Salle 6", 215, "dungeon/montCouronne-9", True, False)
MONTCOURONNE_SALLE7 = Zone("Mont Couronné - Salle 7", 216, "dungeon/montCouronne-10", True, False)
MONTCOURONNE_PASSAGEVESTIGION = Zone("Mont Couronné - Passage Vestigion", 218, "dungeon/montCouronne-11", True, False)
MONTCOURONNE_SALLE8 = Zone("Mont Couronné - Salle 8", 219, "dungeon/montCouronne-12", True, False)
MONTCOURONNE_PASSAGEFRIMAPIC = Zone("Mont Couronné - Passage Frimapic", 217, "dungeon/montCouronne-13", True, False)
MONTCOURONNE_GROTTEREGICE = Zone("Mont Couronné - Grotte Regice", 589, "dungeon/grotteRegi", True, False)
SALLEORIGINELLE = Zone("Salle Originelle", 510, "dungeon/salleOriginelle", False, False)
COLONNESLANCES = Zone("Colonnes Lances", 584, "dungeon/colonnesLances", False, False)
MONTCOURONNE_PASSAGECHARBOURG.addDoor(Door(Position(3,8,MONTCOURONNE_PASSAGECHARBOURG), Position(341,712,SOUTHCENTER)))
MONTCOURONNE_PASSAGECHARBOURG.addDoor(Door(Position(28,20,MONTCOURONNE_PASSAGECHARBOURG), Position(392,724,ROUTE208)))
MONTCOURONNE_PASSAGECHARBOURG.addDoor(Door(Position(26,3,MONTCOURONNE_PASSAGECHARBOURG), Position(27,48,MONTCOURONNE_SALLE1)))
MONTCOURONNE_SALLE1.addDoor(Door(Position(26,48,MONTCOURONNE_SALLE1), Position(25,3,MONTCOURONNE_PASSAGECHARBOURG)))
MONTCOURONNE_SALLE1.addDoor(Door(Position(1,59,MONTCOURONNE_SALLE1), Position(348,717,SOUTHCENTER)))
MONTCOURONNE_SALLE1.addDoor(Door(Position(7,23,MONTCOURONNE_SALLE1), Position(7,12,MONTCOURONNE_SALLE1)))
MONTCOURONNE_SALLE1.addDoor(Door(Position(7,13,MONTCOURONNE_SALLE1), Position(7,24,MONTCOURONNE_SALLE1)))
MONTCOURONNE_SALLE1.addDoor(Door(Position(12,4,MONTCOURONNE_SALLE1), Position(14,26,MONTCOURONNE_SALLE2)))
MONTCOURONNE_SALLE1.addDoor(Door(Position(20,4,MONTCOURONNE_SALLE1), Position(18,26,MONTCOURONNE_SALLE2)))
MONTCOURONNE_SALLE2.addDoor(Door(Position(3,30,MONTCOURONNE_SALLE2), Position(12,36,MONTCOURONNE_EXTERIEUR1)))
MONTCOURONNE_SALLE2.addDoor(Door(Position(13,26,MONTCOURONNE_SALLE2), Position(11,4,MONTCOURONNE_SALLE1)))
MONTCOURONNE_SALLE2.addDoor(Door(Position(19,26,MONTCOURONNE_SALLE2), Position(21,4,MONTCOURONNE_SALLE1)))
MONTCOURONNE_EXTERIEUR1.addDoor(Door(Position(12,35,MONTCOURONNE_EXTERIEUR1), Position(3,29,MONTCOURONNE_SALLE2)))
MONTCOURONNE_EXTERIEUR1.addDoor(Door(Position(39,18,MONTCOURONNE_EXTERIEUR1), Position(35,24,MONTCOURONNE_SALLE3)))
MONTCOURONNE_EXTERIEUR1.addDoor(Door(Position(11,17,MONTCOURONNE_EXTERIEUR1), Position(7,25,MONTCOURONNE_SALLE3)))
MONTCOURONNE_SALLE3.addDoor(Door(Position(35,25,MONTCOURONNE_SALLE3), Position(39,19,MONTCOURONNE_EXTERIEUR1)))
MONTCOURONNE_SALLE3.addDoor(Door(Position(7,26,MONTCOURONNE_SALLE3), Position(11,18,MONTCOURONNE_EXTERIEUR1)))
MONTCOURONNE_SALLE3.addDoor(Door(Position(17,6,MONTCOURONNE_SALLE3), Position(59,6,MONTCOURONNE_SALLE3)))
MONTCOURONNE_SALLE3.addDoor(Door(Position(59,7,MONTCOURONNE_SALLE3), Position(17,7,MONTCOURONNE_SALLE3)))
MONTCOURONNE_SALLE3.addDoor(Door(Position(41,10,MONTCOURONNE_SALLE3), Position(42,40,MONTCOURONNE_EXTERIEUR2)))
MONTCOURONNE_EXTERIEUR2.addDoor(Door(Position(41,40,MONTCOURONNE_EXTERIEUR2), Position(40,10,MONTCOURONNE_SALLE3)))
MONTCOURONNE_EXTERIEUR2.addDoor(Door(Position(46,28,MONTCOURONNE_EXTERIEUR2), Position(2,58,MONTCOURONNE_SALLE7)))
MONTCOURONNE_EXTERIEUR2.addDoor(Door(Position(14,19,MONTCOURONNE_EXTERIEUR2), Position(2,3,MONTCOURONNE_SALLE4)))
MONTCOURONNE_SALLE4.addDoor(Door(Position(1,3,MONTCOURONNE_SALLE4), Position(13,19,MONTCOURONNE_EXTERIEUR2)))
MONTCOURONNE_SALLE4.addDoor(Door(Position(19,8,MONTCOURONNE_SALLE4), Position(21,7,MONTCOURONNE_SALLE5)))
MONTCOURONNE_SALLE5.addDoor(Door(Position(20,7,MONTCOURONNE_SALLE5), Position(18,8,MONTCOURONNE_SALLE4)))
MONTCOURONNE_SALLE5.addDoor(Door(Position(12,24,MONTCOURONNE_SALLE5), Position(10,24,MONTCOURONNE_SALLE6)))
MONTCOURONNE_SALLE6.addDoor(Door(Position(11,24,MONTCOURONNE_SALLE6), Position(13,24,MONTCOURONNE_SALLE5)))
MONTCOURONNE_SALLE6.addDoor(Door(Position(7,5,MONTCOURONNE_SALLE6), Position(31,53,COLONNESLANCES)))
COLONNESLANCES.addDoor(Door(Position(31,54,COLONNESLANCES), Position(7,6,MONTCOURONNE_SALLE6)))
COLONNESLANCES.addDoor(Door(Position(31,52,COLONNESLANCES), Position(31,52,SALLEORIGINELLE)))
SALLEORIGINELLE.addDoor(Door(Position(31,54,SALLEORIGINELLE), Position(7,6,MONTCOURONNE_SALLE6)))
MONTCOURONNE_SALLE7.addDoor(Door(Position(1,58,MONTCOURONNE_SALLE7), Position(45,28,MONTCOURONNE_EXTERIEUR2)))
MONTCOURONNE_SALLE7.addDoor(Door(Position(16,13,MONTCOURONNE_SALLE7), Position(21,61,MONTCOURONNE_PASSAGEVESTIGION)))
MONTCOURONNE_PASSAGEVESTIGION.addDoor(Door(Position(21,62,MONTCOURONNE_PASSAGEVESTIGION), Position(16,14,MONTCOURONNE_SALLE7)))
MONTCOURONNE_PASSAGEVESTIGION.addDoor(Door(Position(1,41,MONTCOURONNE_PASSAGEVESTIGION), Position(380,532,NORTHWEST)))
MONTCOURONNE_PASSAGEVESTIGION.addDoor(Door(Position(30,35,MONTCOURONNE_PASSAGEVESTIGION), Position(419,527,NORTHCENTER)))
MONTCOURONNE_PASSAGEVESTIGION.addDoor(Door(Position(10,10,MONTCOURONNE_PASSAGEVESTIGION), Position(8,60,MONTCOURONNE_SALLE8)))
MONTCOURONNE_SALLE8.addDoor(Door(Position(9,60,MONTCOURONNE_SALLE8), Position(11,10,MONTCOURONNE_PASSAGEVESTIGION)))
MONTCOURONNE_SALLE8.addDoor(Door(Position(9,3,MONTCOURONNE_SALLE8), Position(10,27,MONTCOURONNE_PASSAGEFRIMAPIC)))
MONTCOURONNE_PASSAGEFRIMAPIC.addDoor(Door(Position(9,27,MONTCOURONNE_PASSAGEFRIMAPIC), Position(8,3,MONTCOURONNE_SALLE8)))
MONTCOURONNE_PASSAGEFRIMAPIC.addDoor(Door(Position(15,16,MONTCOURONNE_PASSAGEFRIMAPIC), Position(7,12,MONTCOURONNE_GROTTEREGICE)))
MONTCOURONNE_PASSAGEFRIMAPIC.addDoor(Door(Position(1,18,MONTCOURONNE_PASSAGEFRIMAPIC), Position(375,403,NORTH)))
MONTCOURONNE_GROTTEREGICE.addDoor(Door(Position(7,13,MONTCOURONNE_GROTTEREGICE), Position(15,17,MONTCOURONNE_PASSAGEFRIMAPIC)))
SOUTHCENTER.addDoor(Door(Position(342,712,SOUTHCENTER), Position(4,8,MONTCOURONNE_PASSAGECHARBOURG)))
ROUTE208.addDoor(Door(Position(391,724,ROUTE208), Position(27,20,MONTCOURONNE_PASSAGECHARBOURG)))
SOUTHCENTER.addDoor(Door(Position(349,717,SOUTHCENTER), Position(2,59,MONTCOURONNE_SALLE1)))
NORTHWEST.addDoor(Door(Position(381,532,NORTHWEST), Position(2,41,MONTCOURONNE_PASSAGEVESTIGION)))
NORTHCENTER.addDoor(Door(Position(418,527,NORTHCENTER), Position(29,35,MONTCOURONNE_PASSAGEVESTIGION)))
NORTH.addDoor(Door(Position(376,403,NORTH), Position(2,18,MONTCOURONNE_PASSAGEFRIMAPIC)))

# Hôtel Grand Lac
HOTELGRANDLAC = Zone("Hôtel Grand Lac", 376, "route/hotelGrandLac", False, False)
HOTELGRANDLAC.addDoor(Door(Position(8,2,HOTELGRANDLAC), Position(706,813,SOUTHEAST)))
HOTELGRANDLAC.addDoor(Door(Position(8,12,HOTELGRANDLAC), Position(706,819,ROUTE213)))
SOUTHEAST.addDoor(Door(Position(706,814,SOUTHEAST), Position(8,3,HOTELGRANDLAC)))
ROUTE213.addDoor(Door(Position(706,818,ROUTE213), Position(8,11,HOTELGRANDLAC)))

# Ile de Fer
ILEDEFER = Zone("Ile de Fer", 288, "dungeon/ileDeFer-1", True, True)
ILEDEFER_REZDECHAUSSEE = Zone("Ile de Fer - Rez-de-Chaussée", 289, "dungeon/ileDeFer-2", True, False)
ILEDEFER_SOUSSOL1OUEST = Zone("Ile de Fer - Sous-Sol 1 Ouest", 290, "dungeon/ileDeFer-3", True, False)
ILEDEFER_SOUSSOL1EST = Zone("Ile de Fer - Sous-Sol 1 Est", 291, "dungeon/ileDeFer-4", True, False)
ILEDEFER_SOUSSOL2EST = Zone("Ile de Fer - Sous-Sol 2 Est", 292, "dungeon/ileDeFer-5", True, False)
ILEDEFER_SOUSSOL2OUEST = Zone("Ile de Fer - Sous-Sol 2 Ouest", 293, "dungeon/ileDeFer-6", True, False)
ILEDEFER_GROTTEREGISTEEL = Zone("Ile de Fer - Grotte Registeel", 587, "dungeon/grotteRegi", True, False)
ILEDEFER_SORTIE = Zone("Ile de Fer - Sortie", 294, "dungeon/ileDeFer-7", True, False)
ILEDEFER_REZDECHAUSSEE.addDoor(Door(Position(6,9,ILEDEFER_REZDECHAUSSEE), Position(117,490,ILEDEFER)))
ILEDEFER_REZDECHAUSSEE.addDoor(Door(Position(3,3,ILEDEFER_REZDECHAUSSEE), Position(15,3,ILEDEFER_SOUSSOL1OUEST)))
ILEDEFER_REZDECHAUSSEE.addDoor(Door(Position(9,3,ILEDEFER_REZDECHAUSSEE), Position(2,3,ILEDEFER_SOUSSOL1EST)))
ILEDEFER_SOUSSOL1OUEST.addDoor(Door(Position(16,3,ILEDEFER_SOUSSOL1OUEST), Position(4,3,ILEDEFER_REZDECHAUSSEE)))
ILEDEFER_SOUSSOL1EST.addDoor(Door(Position(1,3,ILEDEFER_SOUSSOL1EST), Position(8,3,ILEDEFER_REZDECHAUSSEE)))
ILEDEFER_SOUSSOL1EST.addDoor(Door(Position(17,26,ILEDEFER_SOUSSOL1EST), Position(2,3,ILEDEFER_SOUSSOL2EST)))
ILEDEFER_SOUSSOL1EST.addDoor(Door(Position(5,26,ILEDEFER_SOUSSOL1EST), Position(38,3,ILEDEFER_SOUSSOL2OUEST)))
ILEDEFER_SOUSSOL2EST.addDoor(Door(Position(1,3,ILEDEFER_SOUSSOL2EST), Position(16,26,ILEDEFER_SOUSSOL1EST)))
ILEDEFER_SOUSSOL2OUEST.addDoor(Door(Position(39,3,ILEDEFER_SOUSSOL2OUEST), Position(6,26,ILEDEFER_SOUSSOL1EST)))
ILEDEFER_SOUSSOL2OUEST.addDoor(Door(Position(13,48,ILEDEFER_SOUSSOL2OUEST), Position(14,15,ILEDEFER_SORTIE)))
ILEDEFER_SORTIE.addDoor(Door(Position(15,15,ILEDEFER_SORTIE), Position(14,48,ILEDEFER_SOUSSOL2OUEST)))
ILEDEFER_SORTIE.addDoor(Door(Position(14,1,ILEDEFER_SORTIE), Position(7,12,ILEDEFER_GROTTEREGISTEEL)))
ILEDEFER_SORTIE.addDoor(Door(Position(1,5,ILEDEFER_SORTIE), Position(103,489,ILEDEFER)))
ILEDEFER_GROTTEREGISTEEL.addDoor(Door(Position(7,13,ILEDEFER_GROTTEREGISTEEL), Position(14,2,ILEDEFER_SORTIE)))
ILEDEFER.addDoor(Door(Position(117,489,ILEDEFER), Position(6,8,ILEDEFER_REZDECHAUSSEE)))
ILEDEFER.addDoor(Door(Position(104,489,ILEDEFER), Position(2,5,ILEDEFER_SORTIE)))

# Route Victoire
ROUTEVICTOIRE = Zone("Route Victoire", 244, "dungeon/routeVictoire-1", True, False)
ROUTEVICTOIRE_SALLEOUEST = Zone("Route Victoire - Salle Ouest", 245, "dungeon/routeVictoire-2", True, False)
ROUTEVICTOIRE_SALLEEST = Zone("Route Victoire - Salle Est", 246, "dungeon/routeVictoire-3", True, False)
ROUTEVICTOIRE_SALLEBRUME = Zone("Route Victoire - Salle Brume", 247, "dungeon/routeVictoire-5", True, False)
ROUTEVICTOIRE_PASSAGEEST = Zone("Route Victoire - Passage Est", 248, "dungeon/routeVictoire-4", True, False)
ROUTEVICTOIRE_PASSAGEROUTE224 = Zone("Route Victoire - Passage Route 224", 249, "dungeon/routeVictoire-6", True, False)
ROUTEVICTOIRE.addDoor(Door(Position(15,79,ROUTEVICTOIRE), Position(851,598,EAST)))
ROUTEVICTOIRE.addDoor(Door(Position(33,5,ROUTEVICTOIRE), Position(853,582,LIGUEPOKEMON)))
ROUTEVICTOIRE.addDoor(Door(Position(3,37,ROUTEVICTOIRE), Position(20,16,ROUTEVICTOIRE_SALLEOUEST)))
ROUTEVICTOIRE.addDoor(Door(Position(6,47,ROUTEVICTOIRE), Position(23,26,ROUTEVICTOIRE_SALLEOUEST)))
ROUTEVICTOIRE.addDoor(Door(Position(3,25,ROUTEVICTOIRE), Position(20,4,ROUTEVICTOIRE_SALLEOUEST)))
ROUTEVICTOIRE.addDoor(Door(Position(43,41,ROUTEVICTOIRE), Position(4,39,ROUTEVICTOIRE_SALLEEST)))
ROUTEVICTOIRE.addDoor(Door(Position(45,48,ROUTEVICTOIRE), Position(6,46,ROUTEVICTOIRE_SALLEEST)))
ROUTEVICTOIRE.addDoor(Door(Position(42,24,ROUTEVICTOIRE), Position(3,22,ROUTEVICTOIRE_SALLEEST)))
ROUTEVICTOIRE.addDoor(Door(Position(46,33,ROUTEVICTOIRE), Position(5,20,ROUTEVICTOIRE_PASSAGEEST)))
ROUTEVICTOIRE_SALLEOUEST.addDoor(Door(Position(21,16,ROUTEVICTOIRE_SALLEOUEST), Position(4,37,ROUTEVICTOIRE)))
ROUTEVICTOIRE_SALLEOUEST.addDoor(Door(Position(24,26,ROUTEVICTOIRE_SALLEOUEST), Position(7,47,ROUTEVICTOIRE)))
ROUTEVICTOIRE_SALLEOUEST.addDoor(Door(Position(21,4,ROUTEVICTOIRE_SALLEOUEST), Position(4,25,ROUTEVICTOIRE)))
ROUTEVICTOIRE_SALLEEST.addDoor(Door(Position(3,39,ROUTEVICTOIRE_SALLEEST), Position(42,41,ROUTEVICTOIRE)))
ROUTEVICTOIRE_SALLEEST.addDoor(Door(Position(5,46,ROUTEVICTOIRE_SALLEEST), Position(44,48,ROUTEVICTOIRE)))
ROUTEVICTOIRE_SALLEEST.addDoor(Door(Position(2,22,ROUTEVICTOIRE_SALLEEST), Position(41,24,ROUTEVICTOIRE)))
ROUTEVICTOIRE_PASSAGEEST.addDoor(Door(Position(4,20,ROUTEVICTOIRE_PASSAGEEST), Position(45,33,ROUTEVICTOIRE)))
ROUTEVICTOIRE_PASSAGEEST.addDoor(Door(Position(22,10,ROUTEVICTOIRE_PASSAGEEST), Position(3,58,ROUTEVICTOIRE_SALLEBRUME)))
ROUTEVICTOIRE_SALLEBRUME.addDoor(Door(Position(2,58,ROUTEVICTOIRE_SALLEBRUME), Position(21,10,ROUTEVICTOIRE_PASSAGEEST)))
ROUTEVICTOIRE_SALLEBRUME.addDoor(Door(Position(57,13,ROUTEVICTOIRE_SALLEBRUME), Position(12,16,ROUTEVICTOIRE_PASSAGEROUTE224)))
ROUTEVICTOIRE_PASSAGEROUTE224.addDoor(Door(Position(11,16,ROUTEVICTOIRE_PASSAGEROUTE224), Position(56,13,ROUTEVICTOIRE_SALLEBRUME)))
ROUTEVICTOIRE_PASSAGEROUTE224.addDoor(Door(Position(30,16,ROUTEVICTOIRE_PASSAGEROUTE224), Position(878,560,NORTHEAST)))
EAST.addDoor(Door(Position(851,597,EAST), Position(15,78,ROUTEVICTOIRE)))
NORTHEAST.addDoor(Door(Position(877,560,NORTHEAST), Position(29,16,ROUTEVICTOIRE_PASSAGEROUTE224)))
LIGUEPOKEMON.addDoor(Door(Position(854,582,LIGUEPOKEMON), Position(34,5,ROUTEVICTOIRE)))

# Grotte Retour
SOURCEADIEU = Zone("Source Adieu", 267, "dungeon/sourceAdieu", True, True)
GROTTERETOUR_ENTREE = Zone("Grotte Retour - Entrée", 268, "dungeon/grotteRetour-entree", True, False)
GROTTERETOUR_SALLEPILIER = Zone("Grotte Retour - Salle Pilier", 269, "dungeon/grotteRetour-pilier", True, False)
GROTTERETOUR_SALLEGIRATINA = Zone("Grotte Retour - Salle Giratina", 270, "dungeon/grotteRetour-giratina", True, False)
GROTTERETOUR_SALLE1 = Zone("Grotte Retour - Salle 1", 518, "dungeon/grotteRetour-1", True, False)
GROTTERETOUR_SALLE2 = Zone("Grotte Retour - Salle 2", 519, "dungeon/grotteRetour-2", True, False)
GROTTERETOUR_SALLE3 = Zone("Grotte Retour - Salle 3", 520, "dungeon/grotteRetour-3", True, False)
GROTTERETOUR_SALLE4 = Zone("Grotte Retour - Salle 4", 521, "dungeon/grotteRetour-4", True, False)
GROTTERETOUR_SALLE5 = Zone("Grotte Retour - Salle 5", 522, "dungeon/grotteRetour-5", True, False)
GROTTERETOUR_SALLE6 = Zone("Grotte Retour - Salle 6", 523, "dungeon/grotteRetour-6", True, False)
GROTTERETOUR_SALLE8 = Zone("Grotte Retour - Salle 8", 525, "dungeon/grotteRetour-8", True, False)
GROTTERETOUR_SALLE9 = Zone("Grotte Retour - Salle 9", 526, "dungeon/grotteRetour-9", True, False)
GROTTERETOUR_SALLE10 = Zone("Grotte Retour - Salle 10", 527, "dungeon/grotteRetour-10", True, False)
GROTTERETOUR_SALLE11 = Zone("Grotte Retour - Salle 11", 528, "dungeon/grotteRetour-11", True, False)
GROTTERETOUR_SALLE12 = Zone("Grotte Retour - Salle 12", 529, "dungeon/grotteRetour-12", True, False)
GROTTERETOUR_SALLE13 = Zone("Grotte Retour - Salle 13", 530, "dungeon/grotteRetour-13", True, False)
GROTTERETOUR_SALLE14 = Zone("Grotte Retour - Salle 14", 531, "dungeon/grotteRetour-14", True, False)
GROTTERETOUR_SALLE15 = Zone("Grotte Retour - Salle 15", 532, "dungeon/grotteRetour-15", True, False)
GROTTERETOUR_SALLE41 = Zone("Grotte Retour - Salle 41", 271, "dungeon/grotteRetour-41", True, False)
GROTTERETOUR_SALLE42 = Zone("Grotte Retour - Salle 42", 272, "dungeon/grotteRetour-42", True, False)
GROTTERETOUR_SALLE43 = Zone("Grotte Retour - Salle 43", 273, "dungeon/grotteRetour-43", True, False)
SOURCEADIEU.addDoor(Door(Position(12,57,SOURCEADIEU), Position(762,714,SOUTHEAST)))
SOURCEADIEU.addDoor(Door(Position(31,16,SOURCEADIEU), Position(11,16,GROTTERETOUR_ENTREE)))
GROTTERETOUR_ENTREE.addDoor(Door(Position(11,17,GROTTERETOUR_ENTREE), Position(31,17,SOURCEADIEU)))
SOUTHEAST.addDoor(Door(Position(762,713,SOUTHEAST), Position(12,56,SOURCEADIEU)))

# Mont Abrupt
MONTABRUPT_SALLE1 = Zone("Mont Abrupt - Salle 1", 263, "dungeon/montAbrupt-1", True, False)
MONTABRUPT_SALLE2 = Zone("Mont Abrupt - Salle 2", 264, "dungeon/montAbrupt-2", True, False)
MONTABRUPT_SALLEHEATRAN = Zone("Mont Abrupt - Salle Heatran", 265, "dungeon/montAbrupt-3", True, False)
MONTABRUPT_SALLE1.addDoor(Door(Position(20,30,MONTABRUPT_SALLE1), Position(750,232,SECTEURCOMBAT_NORTHWEST)))
MONTABRUPT_SALLE1.addDoor(Door(Position(17,2,MONTABRUPT_SALLE1), Position(42,86,MONTABRUPT_SALLE2)))
MONTABRUPT_SALLE2.addDoor(Door(Position(42,87,MONTABRUPT_SALLE2), Position(17,3,MONTABRUPT_SALLE1)))
MONTABRUPT_SALLE2.addDoor(Door(Position(47,2,MONTABRUPT_SALLE2), Position(7,17,MONTABRUPT_SALLEHEATRAN)))
MONTABRUPT_SALLEHEATRAN.addDoor(Door(Position(7,18,MONTABRUPT_SALLEHEATRAN), Position(47,3,MONTABRUPT_SALLE2)))
SECTEURCOMBAT_NORTHWEST.addDoor(Door(Position(750,231,SECTEURCOMBAT_NORTHWEST), Position(20,29,MONTABRUPT_SALLE1)))

# Lac Vérité
LACVERITE = Zone("Lac Vérité", 312, "dungeon/lacVérité", True, True)
LACVERITE_CAVERNEVERITE = Zone("Lac Vérité - Caverne Vérité", 313, "dungeon/grotteCre", True, False)
LACVERITE.addDoor(Door(Position(46,55,LACVERITE), Position(80,844,SOUTHWEST)))
LACVERITE.addDoor(Door(Position(32,32,LACVERITE), Position(14,29,LACVERITE_CAVERNEVERITE)))
LACVERITE_CAVERNEVERITE.addDoor(Door(Position(14,30,LACVERITE_CAVERNEVERITE), Position(32,33,LACVERITE)))
SOUTHWEST.addDoor(Door(Position(80,843,SOUTHWEST), Position(46,54,LACVERITE)))

# Lac Courage
LACCOURAGE = Zone("Lac Courage", 315, "dungeon/lacCourage", True, True)
LACCOURAGE_CAVERNECOURAGE = Zone("Lac Courage - Caverne Courage", 316, "dungeon/grotteCre", True, False)
LACCOURAGE.addDoor(Door(Position(53,10,LACCOURAGE), Position(717,760,SOUTHEAST)))
LACCOURAGE.addDoor(Door(Position(32,32,LACCOURAGE), Position(14,29,LACCOURAGE_CAVERNECOURAGE)))
LACCOURAGE_CAVERNECOURAGE.addDoor(Door(Position(14,30,LACCOURAGE_CAVERNECOURAGE), Position(32,33,LACCOURAGE)))
SOUTHEAST.addDoor(Door(Position(716,760,SOUTHEAST), Position(52,10,LACCOURAGE)))

# Lac Savoir
LACSAVOIR = Zone("Lac Savoir", 318, "dungeon/lacSavoir", False, True)
LACSAVOIR_CAVERNESAVOIR = Zone("Lac Savoir - Caverne Savoir", 319, "dungeon/grotteCre", True, False)
LACSAVOIR.addDoor(Door(Position(14,51,LACSAVOIR), Position(308,230,NORTH)))
LACSAVOIR.addDoor(Door(Position(32,32,LACSAVOIR), Position(14,29,LACSAVOIR_CAVERNESAVOIR)))
LACSAVOIR_CAVERNESAVOIR.addDoor(Door(Position(14,30,LACSAVOIR_CAVERNESAVOIR), Position(32,33,LACSAVOIR)))
NORTH.addDoor(Door(Position(308,229,NORTH), Position(14,50,LACSAVOIR)))

# Grottes Légendaires
ROUTE228_GROTTEREGIROCK = Zone("Route 228 - Grotte Regirock", 591, "dungeon/grotteRegi", True, False)
ROUTE228_GROTTEREGIROCK.addDoor(Door(Position(7,13,ROUTE228_GROTTEREGIROCK), Position(785,341,SECTEURCOMBAT_SOUTHEAST)))
SECTEURCOMBAT_SOUTHEAST.addDoor(Door(Position(785,340,SECTEURCOMBAT_SOUTHEAST), Position(7,12,ROUTE228_GROTTEREGIROCK)))

# Ile Nouvellune
ILENOUVELLUNE = Zone("Ile Nouvellune", 320, "dungeon/ileNouvellune-1", False, False)
ILENOUVELLUNE_INTERIEUR = Zone("Ile Nouvellune - Intérieur", 321, "dungeon/ileNouvellune-2", False, False)
ILENOUVELLUNE_INTERIEUR.addDoor(Door(Position(16,22,ILENOUVELLUNE_INTERIEUR), Position(53,269,ILENOUVELLUNE)))
ILENOUVELLUNE.addDoor(Door(Position(53,268,ILENOUVELLUNE), Position(16,21,ILENOUVELLUNE_INTERIEUR)))

# Ile Pleine Lune
ILEPLEINELUNE = Zone("Ile Pleine Lune", 260, "dungeon/ilePleineLune-1", False, False)
ILEPLEINELUNE_INTERIEUR = Zone("Ile Pleine Lune - Intérieur", 261, "dungeon/ilePleineLune-2", False, False)
ILEPLEINELUNE_INTERIEUR.addDoor(Door(Position(16,22,ILEPLEINELUNE_INTERIEUR), Position(137,269,ILEPLEINELUNE)))
ILEPLEINELUNE.addDoor(Door(Position(137,268,ILEPLEINELUNE), Position(16,21,ILEPLEINELUNE_INTERIEUR)))

# Cities (used for Fly)
BONAUGURE_CITY = City("bonaugure", 411, None, None, [[2,21]], None, None)
LITTORELLA_CITY = City("littorella", 418, 420, 419, [[4,20]], Position(177,842,SOUTHWEST), Position(187,842,SOUTHWEST))
FELICITE_CITY = City("felicite", 3, 6, 4, [[3,17],[4,17],[3,18],[4,18]], Position(180,776,SOUTHWEST), Position(179,766,SOUTHWEST))
CHARBOURG_CITY = City("charbourg", 45, 48, 46, [[7,17],[8,17],[8,18]], Position(303,756,SOUTHCENTER), Position(285,746,SOUTHCENTER))
FLORAVILLE_CITY = City("floraville", 426, 428, 427, [[4,13],[4,14]], Position(176,666,NORTHWEST), Position(184,657,NORTHWEST))
VESTIGION_CITY = City("vestigion", 65, 69, 66, [[8,10],[9,10],[8,11]], Position(305,530,NORTHWEST), Position(309,548,NORTHWEST))
UNIONPOLIS_CITY = City("unionpolis", 86, 101, 87, [[13,15],[14,15],[13,16],[14,16]], Position(465,697,UNIONPOLIS), Position(477,710,UNIONPOLIS))
BONVILLE_CITY = City("bonville", 433, 435, 434, [[16,14],[17,14]], Position(566,656,NORTHCENTER), Position(571,665,NORTHCENTER))
VOILAROC_CITY = City("voilaroc", 132, 134, None, [[20,12],[21,12],[20,13],[21,13]], Position(717,611,VOILAROC), None)
VERCHAMPS_CITY = City("verchamps", 120, 123, 121, [[17,19],[18,19],[17,20],[18,20]], Position(600,815,SOUTH), Position(601,844,SOUTH))
CELESTIA_CITY = City("celestia", 442, 443, 446, [[13,10]], Position(472,538,NORTHCENTER), Position(450,515,NORTHCENTER))
JOLIBERGES_CITY = City("joliberges", 33, 36, 34, [[0,16],[0,17]], Position(58,722,JOLIBERGES), Position(53,740,JOLIBERGES))
FRIMAPIC_CITY = City("frimapic", 165, 168, 166, [[10,0],[10,1]], Position(379,233,NORTH), Position(353,232,NORTH))
RIVAMAR_CITY = City("rivamar", 150, 151, 153, [[25,17],[26,17],[25,18],[26,18]], Position(860,784,EAST), Position(853,768,EAST))
ROUTEVICTOIRE_CITY = City("liguePokemon", 172, 173, None, [[25,12]], Position(842,598,EAST), None)
LIGUEPOKEMON_CITY = City("liguePokemon", 172, None, None, [[25,11]], None, None)
AIREDECOMBAT_CITY = City("airedecombat", 188, 189, 191, [[18,7],[19,7]], Position(647,429,SECTEURCOMBAT_SOUTHEAST), Position(660,429,SECTEURCOMBAT_SOUTHEAST))
AIREDESURVIE_CITY = City("airedesurvie", 450, 452, 451, [[19,4]], Position(659,338,SECTEURCOMBAT_NORTHWEST), Position(663,338,SECTEURCOMBAT_NORTHWEST))
AIREDEDETENTE_CITY = City("airededetente", 457, 459, None, [[24,8]], Position(802,472,SECTEURCOMBAT_SOUTHEAST), None)

ZONEIDLIST = [
    3,   # Féli-Cité
    33,  # Joliberges
    45,  # Charbourg
    65,  # Vestigion
    86,  # Unionpolis
    120, # Verchamps
    132, # Voilaroc
    150, # Rivamar
    165, # Frimapic
    172, # Ligue Pokémon - Extérieur
    188, # Aire de Combat
    200, # Les Eoliennes
    204, # Forge Fuego - Extérieur
    260, # Ile Pleine Lune
    262, # Mont Abrupt - Extérieur
    274, # Paradis Fleuri
    288, # Ile de Fer
    320, # Ile Nouvellune
    334, # Rive Lac Vérité
    336, # Rive Lac Courage
    340, # Rive Lac Savoir
    341, # Chemin Source
    342, # Route 201
    343, # Route 202
    344, # Route 203
    345, # Route 204 - Sud
    346, # Route 204 - Nord
    347, # Route 205 - Ouest
    349, # Route 205 - Est
    350, # Route 206
    353, # Route 207
    354, # Route 208
    356, # Route 209
    362, # Route 210 - Sud
    363, # Route 210 - Nord
    365, # Route 211 - Ouest
    366, # Route 211 - Est
    367, # Route 212 - Nord
    371, # Route 212 - Sud
    373, # Route 213
    380, # Route 214
    382, # Route 215
    383, # Route 216
    385, # Route 217
    388, # Route 218
    391, # Route 219
    392, # Route 221
    395, # Route 222
    399, # Route 224
    400, # Route 225
    403, # Route 227
    406, # Route 228
    407, # Route 229
    411, # Bonaugure
    418, # Littorella
    426, # Floraville
    433, # Bonville
    442, # Célestia
    450, # Aire de Survie
    457, # Aire de Détente
    467, # Route 220
    468, # Route 223
    469, # Route 226
    471, # Route 230
    472  # Passage Marin
]

ZONELIST = {
    3: SOUTHWEST, # Féli-Cité
    4: FELICITE_SHOP,
    6: FELICITE_CENTREPOKEMON,
    33: JOLIBERGES,
    34: JOLIBERGES_SHOP,
    36: JOLIBERGES_CENTREPOKEMON,
    45: SOUTHCENTER, # Charbourg
    46: CHARBOURG_SHOP,
    48: CHARBOURG_CENTREPOKEMON,
    65: NORTHWEST, # Vestigion
    66: VESTIGION_SHOP,
    69: VESTIGION_CENTREPOKEMON,
    80: ROUTE206_PASSAGEVESTIGION,
    86: UNIONPOLIS, # Unionpolis
    87: UNIONPOLIS_SHOP,
    101: UNIONPOLIS_CENTREPOKEMON,
    109: ROUTE208_PASSAGEUNIONPOLIS,
    110: ROUTE209_PASSAGEUNIONPOLIS,
    111: ROUTE212_PASSAGEUNIONPOLIS,
    120: SOUTH, # Verchamps
    121: VERCHAMPS_SHOP,
    123: VERCHAMPS_CENTREPOKEMON,
    132: VOILAROC, # Voilaroc
    134: VOILAROC_CENTREPOKEMON,
    137: VOILAROC_CENTRECOMMERCIAL,
    138: VOILAROC_CENTRECOMMERCIALETAGE1,
    139: VOILAROC_CENTRECOMMERCIALETAGE2,
    140: VOILAROC_CENTRECOMMERCIALETAGE3,
    141: VOILAROC_CENTRECOMMERCIALETAGE4,
    142: VOILAROC_CENTRECOMMERCIALASCENSEUR,
    149: ROUTE215_PASSAGEVOILAROC,
    150: EAST, # Rivamar
    151: RIVAMAR_CENTREPOKEMON,
    153: RIVAMAR_SHOP,
    165: NORTH, # Frimapic
    166: FRIMAPIC_SHOP,
    168: FRIMAPIC_CENTREPOKEMON,
    172: [EAST, LIGUEPOKEMON], # Ligue Pokémon - Extérieur
    173: LIGUEPOKEMON_CENTREPOKEMON,
    175: LIGUEPOKEMON_INTERIEUR,
    188: SECTEURCOMBAT_SOUTHEAST, # Aire de Combat
    189: AIREDECOMBAT_CENTREPOKEMON,
    191: AIREDECOMBAT_SHOP,
    193: ROUTE225_PASSAGEAIREDECOMBAT,
    200: NORTHWEST, # Les Eoliennes
    203: FORETVESTIGION,
    204: NORTHWEST, # Forge Fuego - Extérieur
    207: MONTCOURONNE_PASSAGECHARBOURG,
    208: MONTCOURONNE_SALLE1,
    209: MONTCOURONNE_SALLE2,
    210: MONTCOURONNE_EXTERIEUR2,
    211: MONTCOURONNE_EXTERIEUR1,
    212: MONTCOURONNE_SALLE3,
    213: MONTCOURONNE_SALLE4,
    214: MONTCOURONNE_SALLE5,
    215: MONTCOURONNE_SALLE6,
    216: MONTCOURONNE_SALLE7,
    217: MONTCOURONNE_PASSAGEFRIMAPIC,
    218: MONTCOURONNE_PASSAGEVESTIGION,
    219: MONTCOURONNE_SALLE8,
    244: ROUTEVICTOIRE,
    245: ROUTEVICTOIRE_SALLEOUEST,
    246: ROUTEVICTOIRE_SALLEEST,
    247: ROUTEVICTOIRE_SALLEBRUME,
    248: ROUTEVICTOIRE_PASSAGEEST,
    249: ROUTEVICTOIRE_PASSAGEROUTE224,
    254: CHEMINROCHEUX,
    258: ENTREECHARBOURG,
    259: ENTREECHARBOURG_SOUSSOL1,
    260: ILEPLEINELUNE,
    261: ILEPLEINELUNE_INTERIEUR,
    262: SECTEURCOMBAT_NORTHWEST, # Mont Abrupt - Extérieur
    263: MONTABRUPT_SALLE1,
    264: MONTABRUPT_SALLE2,
    265: MONTABRUPT_SALLEHEATRAN,
    267: SOURCEADIEU,
    268: GROTTERETOUR_ENTREE,
    269: GROTTERETOUR_SALLEPILIER,
    270: GROTTERETOUR_SALLEGIRATINA,
    271: GROTTERETOUR_SALLE41,
    272: GROTTERETOUR_SALLE42,
    273: GROTTERETOUR_SALLE43,
    274: NORTHEAST, # Paradis Fleuri
    284: GROTTEREVECHE,
    285: GROTTEREVECHE_SOUSSOL,
    288: ILEDEFER, # Ile de Fer
    289: ILEDEFER_REZDECHAUSSEE,
    290: ILEDEFER_SOUSSOL1OUEST,
    291: ILEDEFER_SOUSSOL1EST,
    292: ILEDEFER_SOUSSOL2EST,
    293: ILEDEFER_SOUSSOL2OUEST,
    294: ILEDEFER_SORTIE,
    312: LACVERITE,
    313: LACVERITE_CAVERNEVERITE,
    315: LACCOURAGE,
    316: LACCOURAGE_CAVERNECOURAGE,
    318: LACSAVOIR,
    319: LACSAVOIR_CAVERNESAVOIR,
    320: ILENOUVELLUNE,
    321: ILENOUVELLUNE_INTERIEUR,
    334: SOUTHWEST, # Rive Lac Vérité
    336: SOUTHEAST, # Rive Lac Courage
    340: NORTH, # Rive Lac Savoir
    341: SOUTHEAST, # Chemin Source
    342: SOUTHWEST, # Route 201
    343: SOUTHWEST, # Route 202
    344: SOUTHWEST, # Route 203
    345: SOUTHWEST, # Route 204 - Sud
    346: NORTHWEST, # Route 204 - Nord
    347: NORTHWEST, # Route 205 - Ouest
    349: NORTHWEST, # Route 205 - Est
    350: [SOUTHCENTER, PISTECYCLABLE], # Route 206 / Piste Cyclable
    351: ROUTE206_PASSAGECHARBOURG,
    353: SOUTHCENTER, # Route 207
    354: ROUTE208, # Route 208
    356: NORTHCENTER, # Route 209
    362: NORTHCENTER, # Route 210 - Sud
    363: NORTHCENTER, # Route 210 - Nord
    365: NORTHWEST, # Route 211 - Ouest
    366: NORTHCENTER, # Route 211 - Est
    367: SOUTH, # Route 212 - Nord
    371: SOUTH, # Route 212 - Sud
    373: [ROUTE213, SOUTHEAST], # Route 213
    374: ROUTE213_PASSAGEVERCHAMPS,
    376: HOTELGRANDLAC,
    380: SOUTHEAST, # Route 214
    381: ROUTE214_PASSAGEVOILAROC,
    382: NORTHCENTER, # Route 215
    383: NORTH, # Route 216
    385: NORTH, # Route 217
    388: ROUTE218, # Route 218
    389: ROUTE218_PASSAGEFELICITE,
    390: ROUTE218_PASSAGEJOLIBERGES,
    391: SOUTHWEST, # Route 219
    392: SOUTHWEST, # Route 221
    395: SOUTHEAST, # Route 222
    398: ROUTE222_PASSAGERIVAMAR,
    399: NORTHEAST, # Route 224
    400: SECTEURCOMBAT_NORTHWEST, # Route 225
    403: SECTEURCOMBAT_NORTHWEST, # Route 227
    406: SECTEURCOMBAT_SOUTHEAST, # Route 228
    407: SECTEURCOMBAT_SOUTHEAST, # Route 229
    411: SOUTHWEST, # Bonaugure
    419: LITTORELLA_SHOP,
    420: LITTORELLA_CENTREPOKEMON,
    418: SOUTHWEST, # Littorella
    426: NORTHWEST, # Floraville
    427: FLORAVILLE_SHOP,
    428: FLORAVILLE_CENTREPOKEMON,
    433: NORTHCENTER, # Bonville
    434: BONVILLE_SHOP,
    435: BONVILLE_CENTREPOKEMON,
    442: NORTHCENTER, # Célestia
    443: CELESTIA_CENTREPOKEMON,
    446: CELESTIA_SHOP,
    450: SECTEURCOMBAT_NORTHWEST, # Aire de Survie
    451: AIREDESURVIE_SHOP,
    452: AIREDESURVIE_CENTREPOKEMON,
    457: SECTEURCOMBAT_SOUTHEAST, # Aire de Détente
    459: AIREDEDETENTE_CENTREPOKEMON,
    467: SOUTHWEST, # Route 220
    468: EAST, # Route 223
    469: SECTEURCOMBAT_NORTHWEST, # Route 226
    471: SECTEURCOMBAT_SOUTHEAST, # Route 230
    472: NORTHEAST, # Passage Marin
    501: ROUTE226_PASSAGEROUTE228,
    510: SALLEORIGINELLE,
    518: GROTTERETOUR_SALLE1,
    519: GROTTERETOUR_SALLE2,
    520: GROTTERETOUR_SALLE3,
    521: GROTTERETOUR_SALLE4,
    522: GROTTERETOUR_SALLE5,
    523: GROTTERETOUR_SALLE6,
    525: GROTTERETOUR_SALLE8,
    526: GROTTERETOUR_SALLE9,
    527: GROTTERETOUR_SALLE10,
    528: GROTTERETOUR_SALLE11,
    529: GROTTERETOUR_SALLE12,
    530: GROTTERETOUR_SALLE13,
    531: GROTTERETOUR_SALLE14,
    532: GROTTERETOUR_SALLE15,
    566: VOILAROC_CENTRECOMMERCIALSOUSSOL1,
    584: COLONNESLANCES,
    587: ILEDEFER_GROTTEREGISTEEL,
    589: MONTCOURONNE_GROTTEREGICE,
    591: ROUTE228_GROTTEREGIROCK
}

# Obsolete doors (prefer using left-most, up-most or center door)
OBSOLETEDOORS = [
    Door(Position(6,2,ROUTE206_PASSAGEVESTIGION), Position(304,569,NORTHWEST)),
    Door(Position(8,2,ROUTE206_PASSAGEVESTIGION), Position(304,569,NORTHWEST)),
    Door(Position(305,570,NORTHWEST), Position(7,3,ROUTE206_PASSAGEVESTIGION)),
    Door(Position(305,576,PISTECYCLABLE), Position(7,12,ROUTE206_PASSAGEVESTIGION)),
    Door(Position(6,13,ROUTE206_PASSAGEVESTIGION), Position(304,577,PISTECYCLABLE)),
    Door(Position(8,13,ROUTE206_PASSAGEVESTIGION), Position(304,577,PISTECYCLABLE)),
    Door(Position(300,682,PISTECYCLABLE), Position(6,3,ROUTE206_PASSAGECHARBOURG)),
    Door(Position(301,682,PISTECYCLABLE), Position(7,3,ROUTE206_PASSAGECHARBOURG)),
    Door(Position(303,682,PISTECYCLABLE), Position(7,3,ROUTE206_PASSAGECHARBOURG)),
    Door(Position(304,682,PISTECYCLABLE), Position(7,3,ROUTE206_PASSAGECHARBOURG)),
    Door(Position(305,682,PISTECYCLABLE), Position(8,3,ROUTE206_PASSAGECHARBOURG)),
    Door(Position(6,2,ROUTE206_PASSAGECHARBOURG), Position(301,681,PISTECYCLABLE)),
    Door(Position(8,2,ROUTE206_PASSAGECHARBOURG), Position(304,681,PISTECYCLABLE)),
    Door(Position(6,13,ROUTE206_PASSAGECHARBOURG), Position(301,689,SOUTHCENTER)),
    Door(Position(8,13,ROUTE206_PASSAGECHARBOURG), Position(304,689,SOUTHCENTER)),
    Door(Position(301,688,SOUTHCENTER), Position(6,12,ROUTE206_PASSAGECHARBOURG)),
    Door(Position(303,688,SOUTHCENTER), Position(7,12,ROUTE206_PASSAGECHARBOURG)),
    Door(Position(304,688,SOUTHCENTER), Position(8,12,ROUTE206_PASSAGECHARBOURG)),
    Door(Position(453,727,UNIONPOLIS), Position(10,7,ROUTE208_PASSAGEUNIONPOLIS)),
    Door(Position(506,727,UNIONPOLIS), Position(1,7,ROUTE209_PASSAGEUNIONPOLIS)),
    Door(Position(459,730,UNIONPOLIS), Position(5,3,ROUTE212_PASSAGEUNIONPOLIS)),
    Door(Position(448,727,ROUTE208), Position(1,7,ROUTE208_PASSAGEUNIONPOLIS)),
    Door(Position(511,727,NORTHCENTER), Position(10,7,ROUTE209_PASSAGEUNIONPOLIS)),
    Door(Position(459,736,SOUTH), Position(5,12,ROUTE212_PASSAGEUNIONPOLIS)),
    Door(Position(719,639,VOILAROC), Position(5,3,ROUTE214_PASSAGEVOILAROC)),
    Door(Position(677,599,VOILAROC), Position(10,7,ROUTE215_PASSAGEVOILAROC)),
    Door(Position(672,599,NORTHCENTER), Position(1,7,ROUTE215_PASSAGEVOILAROC)),
    Door(Position(719,645,SOUTHEAST), Position(5,12,ROUTE214_PASSAGEVOILAROC)),
    Door(Position(645,813,ROUTE213), Position(10,7,ROUTE213_PASSAGEVERCHAMPS)),
    Door(Position(640,813,SOUTH), Position(1,7,ROUTE213_PASSAGEVERCHAMPS)),
    Door(Position(127,759,SOUTHWEST), Position(1,7,ROUTE218_PASSAGEFELICITE)),
    Door(Position(122,759,ROUTE218), Position(10,7,ROUTE218_PASSAGEFELICITE)),
    Door(Position(69,755,ROUTE218), Position(10,7,ROUTE218_PASSAGEJOLIBERGES)),
    Door(Position(64,755,JOLIBERGES), Position(1,7,ROUTE218_PASSAGEJOLIBERGES)),
    Door(Position(826,791,SOUTHEAST), Position(1,7,ROUTE222_PASSAGERIVAMAR)),
    Door(Position(831,791,EAST), Position(10,7,ROUTE222_PASSAGERIVAMAR)),
    Door(Position(631,421,SECTEURCOMBAT_SOUTHEAST), Position(5,12,ROUTE225_PASSAGEAIREDECOMBAT)),
    Door(Position(631,414,SECTEURCOMBAT_NORTHWEST), Position(5,3,ROUTE225_PASSAGEAIREDECOMBAT)),
    Door(Position(768,331,SECTEURCOMBAT_NORTHWEST), Position(1,7,ROUTE226_PASSAGEROUTE228)),
    Door(Position(773,331,SECTEURCOMBAT_SOUTHEAST), Position(10,7,ROUTE226_PASSAGEROUTE228)),
    Door(Position(29,87,FORETVESTIGION), Position(207,582,NORTHWEST)),
    Door(Position(87,37,FORETVESTIGION), Position(259,525,NORTHWEST)),
    Door(Position(207,581,NORTHWEST), Position(29,86,FORETVESTIGION)),
    Door(Position(258,525,NORTHWEST), Position(86,37,FORETVESTIGION)),
    Door(Position(850,597,EAST), Position(15,78,ROUTEVICTOIRE)),
    Door(Position(852,597,EAST), Position(15,78,ROUTEVICTOIRE)),
    Door(Position(14,79,ROUTEVICTOIRE), Position(851,598,EAST)),
    Door(Position(16,79,ROUTEVICTOIRE), Position(851,598,EAST)),
    Door(Position(33,4,ROUTEVICTOIRE), Position(853,582,LIGUEPOKEMON)),
    Door(Position(33,6,ROUTEVICTOIRE), Position(853,582,LIGUEPOKEMON)),
    Door(Position(854,581,LIGUEPOKEMON), Position(34,5,ROUTEVICTOIRE)),
    Door(Position(854,583,LIGUEPOKEMON), Position(34,5,ROUTEVICTOIRE)),
    Door(Position(13,57,SOURCEADIEU), Position(763,714,SOUTHEAST)),
    Door(Position(763,713,SOUTHEAST), Position(13,56,SOURCEADIEU)),
    Door(Position(47,55,LACVERITE), Position(81,844,SOUTHWEST)),
    Door(Position(81,843,SOUTHWEST), Position(47,54,LACVERITE)),
    Door(Position(53,11,LACCOURAGE), Position(717,761,SOUTHEAST)),
    Door(Position(716,761,SOUTHEAST), Position(52,11,LACCOURAGE)),
    Door(Position(15,51,LACSAVOIR), Position(309,230,NORTH)),
    Door(Position(309,229,NORTH), Position(15,50,LACSAVOIR)),
    Door(Position(17,22,ILENOUVELLUNE_INTERIEUR), Position(54,269,ILENOUVELLUNE)),
    Door(Position(54,268,ILENOUVELLUNE), Position(17,21,ILENOUVELLUNE_INTERIEUR)),
    Door(Position(17,22,ILEPLEINELUNE_INTERIEUR), Position(138,269,ILEPLEINELUNE)),
    Door(Position(138,268,ILEPLEINELUNE), Position(17,21,ILEPLEINELUNE_INTERIEUR))
]