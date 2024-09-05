import img
import encounter
from encounter import EncounterTables

ZONEDICTIONARY = {}

# Specific zones sharing multiple zoneid
LIGUEPOKEMON_ID = 172
PISTECYCLABLE_ID = 350
ROUTE213_ID = 373

# Overworld zones
CHARBOURG_ID = 45
VERCHAMPS_ID = 120
RIVAMAR_ID = 150
FRIMAPIC_ID = 165
AIREDECOMBAT_ID = 188
PARADISFLEURI_ID = 274
RIVELACCOURAGE_ID = 336
BONAUGURE_ID = 411
FLORAVILLE_ID = 426
BONVILLE_ID = 433
AIREDESURVIE_ID = 450
GRANDMARAIS_ID = 504

class Zone():
    def __init__(self, name, zoneId, mapFile, canBike, canFly, canDig):
        self.name = name
        self.zoneId = zoneId
        self.map = open('src/python/data/map/' + mapFile + '.map').readlines()
        self.doorList = []
        self.subzoneList = []
        self.encounterTables = None
        
        self.canBike = canBike
        self.canFly = canFly
        self.canDig = canDig

    def addDoor(self, door):
        if (door in self.doorList):
            print("Door already exists in " + str(self.name) + " : " + str(door))
        else:
            self.doorList.append(door)

    def setZoneId(self, zoneId):
        if (self.subzoneList):
            self.zoneId = zoneId
        else:
            print("Zones without subzones can't have their id updated")

    def setSubZones(self, *subzoneList):
        self.subzoneList = {}

        for subzone in subzoneList:
            self.subzoneList[subzone.zoneId] = subzone

    def setEncounterTables(self, encounterTables):
        self.encounterTables = encounterTables

    def getDoorByDestination(self, zone):
        for door in self.doorList:
            if (door.destination.zone == zone):
                return door
            
    def __eq__(self, other):
        if isinstance(other, Zone):
            return self.zoneId == other.zoneId
        return False
    
    def __str__(self):
        return ("Zone " + str(self.name) + " (" + str(self.zoneId) + ")"
                + " / can bike" if self.canBike else ""
                + " / can fly" if self.canFly else ""
                + " / can dig" if self.canDig else "")
    
    def __repr__(self):
        return str(self)
        
    def __hash__(self):
        return hash(self.zoneId)

class SubZone():
    def __init__(self, name, zoneId, topLeft, bottomRight):
        self.name = name
        self.zoneId = zoneId
        self.topLeft = topLeft
        self.bottomRight = bottomRight
        self.encounterTables = None

    def setEncounterTables(self, encounterTables):
        self.encounterTables = encounterTables

class Position:
    def __init__(self, positionX, positionY, zone):
        self.X = positionX
        self.Y = positionY

        # Provide actual Zone object
        if isinstance(zone, Zone):
            self.zone = zone

        # Provide Zone ID, search for the Zone object in ZONEDICTIONARY
        elif (isinstance(zone, int) and zone in ZONEDICTIONARY):

            # Check exceptions before going in ZONEDICTIONARY
            if (zone == LIGUEPOKEMON_ID):
                self.zone = checkLiguePokemon(positionY)

            elif (zone == ROUTE213_ID):
                self.zone = checkRoute213(positionX, positionY)

            elif (zone == PISTECYCLABLE_ID):
                self.zone = checkPisteCyclable(positionX, positionY)
            else:
                self.zone = getZoneById(zone)

        # Not Zone object nor known ZoneID
        else:
            self.zone = None
            print("Unknown zone : " + str(zone))

    def getCell(self):
        return self.zone.map[self.Y][self.X]
    
    def getDistanceTo(self, position):
        return abs(self.X - position.X) + abs(self.Y - position.Y)

    def setDistanceTo(self, position):
        self.distance = self.getDistanceTo(position)

    def __eq__(self, other):
        if isinstance(other, Position):
            return self.X == other.X and self.Y == other.Y and self.zone.zoneId == other.zone.zoneId
        return False
    
    def __hash__(self):
        return hash((self.X, self.Y, self.zone))

    def __str__(self):
        return "(" + str(self.X) + "," + str(self.Y) + ") à " + self.zone.name
    
    def __repr__(self):
        return str(self)

class Door():
    def __init__(self, position: Position, destination: Position):
        self.position = position
        self.destination = destination
        self.connectedDoor = None

    def setConnectedDoor(self, door):
        self.connectedDoor = door

    def createDoorKey(self):
        return DoorKey(tuple(sorted((self, self.connectedDoor), key = hash)))

    def __eq__(self, other):
        if isinstance(other, Door):
            return self.position == other.position
        return False
    
    def __lt__(self, other):
        return self.position.zone.zoneId < other.position.zone.zoneId
    
    def __hash__(self):
        return hash(self.position)
    
    def __str__(self):
        return "Door (" + str(self.position) + ") connected to (" + str(self.destination) + ")"
    
    def __repr__(self):
        return str(self)

class DoorKey(tuple):
    def __new__(cls, args):
        return super().__new__(cls, args)
    
    def __str__(self):
        return "DoorKey : " + str(self[0]) + "\n             " + str(self[1]) + "\n"
    
    def __repr__(self):
        return str(self)

class City():
    def __init__(self, name, zoneId, flyCoordinates, flyDoor: Door):
        self.name = name
        self.zoneId = zoneId
        self.flyCoordinates = flyCoordinates
        self.flyDoor = flyDoor

    def __str__(self):
        return "City " + str(self.name)

# Check if position if a valid cell (reachable + in map bounds)
def checkPositionValidity(position, zoneMap = None):
    try:
        if ((position.zone.map if zoneMap is None else zoneMap)[position.Y][position.X] in ["X","I","P"," "]):
            print("Unreachable cell : " + str(position) + " (" + (position.zone.map if zoneMap is None else zoneMap)[position.Y][position.X] + ")")
            return False
    except IndexError:
        print("Position out of map bounds : " + str(position))
        return False
    return True

# Used when adding new door
def checkDoorValidity(door):
    if (not checkPositionValidity(door.position) or not checkPositionValidity(door.destination)):
        print("Door has invalid position " + str(door))

    if (door.position.getCell() != "Z"):
        print("Door not coming through a Z cell : " + str(door))

    if (door.destination.zone.map[door.destination.Y - 1][door.destination.X] != "Z"
        and door.destination.zone.map[door.destination.Y + 1][door.destination.X] != "Z"
        and door.destination.zone.map[door.destination.Y][door.destination.X - 1] != "Z"
        and door.destination.zone.map[door.destination.Y][door.destination.X + 1] != "Z"):
        print("Door not arriving near a Z cell : " + str(door))

# Connect two doors to each other
def setConnectingDoors(door1, door2):

    # If the start and destination zones of each door don't match, they are not connected
    if (door1.position.zone != door2.destination.zone or door1.destination.zone != door2.position.zone):
        print("Not connected doors ! " + str(door1) + " /// " + str(door2))
        return

    if (door1.destination.zone.zoneId != GRANDMARAIS_ID and (door1.position.getDistanceTo(door2.destination) > 1 or door2.position.getDistanceTo(door1.destination) > 1)):
        print("Destination too far from the door position ! " + str(door1) + " /// " + str(door2))
        return

    # First add the door positions as actual doors from their corresponding zones
    door1.position.zone.addDoor(door1)
    door2.position.zone.addDoor(door2)

    # Then set those doors as connected
    door1.setConnectedDoor(door2)
    door2.setConnectedDoor(door1)

# Find the zone or subzone corresponding to the zoneId
def getZoneById(zoneId):
    zone = ZONEDICTIONARY[zoneId]

    # If the zone has subzones, set the zoneId of the corresponding subzone
    if (zone.subzoneList):
        zone.setZoneId(zoneId)

    return zone

# Separation between Pokemon League and Overword is purely based on Y position
def checkLiguePokemon(positionY):
    if (positionY < 592):
        return LIGUEPOKEMON
    else:
        EAST.setZoneId(LIGUEPOKEMON_ID)
        return EAST

# Directly check on Route 213 map if we're on it
def checkRoute213(positionX, positionY):
    if ROUTE213_EST.map[positionY][positionX] == " ":
        SOUTHEAST.setZoneId(ROUTE213_ID)
        return SOUTHEAST 
    else:
        return ROUTE213_EST

# Cycling Road shares positions with Route 206 so differentiate them is more complex
def checkPisteCyclable(positionX, positionY):

    # Too high for Route 206 or too low for Cycling Road
    if (positionY < 606):
        return PISTECYCLABLE
    elif (positionY > 681):
        SOUTHCENTER.setZoneId(PISTECYCLABLE_ID)
        return SOUTHCENTER
    
    # Overlap between Cycling Road and Route 206
    elif (299 <= positionX <= 306):
        if (PISTECYCLABLE.map[positionY][positionX] in ["X","N"]):
            SOUTHCENTER.setZoneId(PISTECYCLABLE_ID)
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
            if (spritePosition is None):
                SOUTHCENTER.setZoneId(PISTECYCLABLE_ID)
                return SOUTHCENTER
            else:
                return PISTECYCLABLE
            
    # Every Cycling Road position has been checked, we're on Overworld
    else:
        SOUTHCENTER.setZoneId(PISTECYCLABLE_ID)
        return SOUTHCENTER

# Check if a door is a City Fly location
def isFlyDoor(door):
    for city in CITY_LIST:
        if (city.flyDoor == door):
            return True
    return False

# Overworld
EAST = Zone("East", RIVAMAR_ID, "overworld/east", True, True, False)
NORTH = Zone("North", FRIMAPIC_ID, "overworld/north", False, True, False)
NORTHCENTER = Zone("Northcenter", BONVILLE_ID, "overworld/northcenter", True, True, False)
NORTHEAST = Zone("Northeast", PARADISFLEURI_ID, "overworld/northeast", True, True, False)
NORTHWEST = Zone("Northwest", FLORAVILLE_ID, "overworld/northwest", True, True, False)
SOUTH = Zone("South", VERCHAMPS_ID, "overworld/south", True, True, False)
SOUTHCENTER = Zone("Southcenter", CHARBOURG_ID, "overworld/southcenter", True, True, False)
SOUTHEAST = Zone("Southeast", RIVELACCOURAGE_ID, "overworld/southeast", True, True, False)
SOUTHWEST = Zone("Southwest", BONAUGURE_ID, "overworld/southwesh", True, True, False)
SECTEURCOMBAT_NORTHWEST = Zone("Secteur Combat - Northwest", AIREDESURVIE_ID, "overworld/secteurCombat-northwest", True, True, False)
SECTEURCOMBAT_SOUTHEAST = Zone("Secteur Combat - Southeast", AIREDECOMBAT_ID, "overworld/secteurCombat-southeast", True, True, False)

# Bonaugure
BONAUGURE = SubZone("Bonaugure", 411, (96,864), (127,895))
BONAUGURE.setEncounterTables(encounter.BONAUGURE)
BONAUGURE_MAISON = Zone("Bonaugure - Maison Maman", 414, "city/bonaugure-maisonMaman", False, False, False)
BONAUGURE_MAISON_DOOR = Door(Position(116,885,SOUTHWEST), Position(6,10,BONAUGURE_MAISON))
setConnectingDoors(BONAUGURE_MAISON_DOOR, Door(Position(6,11,BONAUGURE_MAISON), Position(116,886,SOUTHWEST)))

# Littorella
LITTORELLA = SubZone("Littorella", 418, (160,832), (191,863))
LITTORELLA_CENTREPOKEMON = Zone("Littorella - Centre Pokémon", 420, "city/littorella-centrePokemon", False, False, False)
LITTORELLA_CENTREPOKEMON_DOOR = Door(Position(177,842,SOUTHWEST), Position(8,12,LITTORELLA_CENTREPOKEMON))
LITTORELLA_SHOP = Zone("Littorella - Shop", 419, "city/littorella-shop", False, False, False)
setConnectingDoors(LITTORELLA_CENTREPOKEMON_DOOR, Door(Position(8,13,LITTORELLA_CENTREPOKEMON), Position(177,843,SOUTHWEST)))
setConnectingDoors(Door(Position(187,842,SOUTHWEST), Position(3,11,LITTORELLA_SHOP)), Door(Position(3,12,LITTORELLA_SHOP), Position(187,843,SOUTHWEST)))

# Féli-Cité
FELICITE = SubZone("Féli-Cité", 3, (128,736), (191,799))
FELICITE_CENTREPOKEMON = Zone("Féli-Cité - Centre Pokémon", 6, "city/felicite-centrePokemon", False, False, False)
FELICITE_CENTREPOKEMON_DOOR = Door(Position(180,776,SOUTHWEST), Position(8,12,FELICITE_CENTREPOKEMON))
FELICITE_SHOP = Zone("Féli-Cité - Shop", 4, "city/felicite-shop", False, False, False)
setConnectingDoors(FELICITE_CENTREPOKEMON_DOOR, Door(Position(8,13,FELICITE_CENTREPOKEMON), Position(180,777,SOUTHWEST)))
setConnectingDoors(Door(Position(179,766,SOUTHWEST), Position(3,11,FELICITE_SHOP)), Door(Position(3,12,FELICITE_SHOP), Position(179,767,SOUTHWEST)))

# Charbourg
CHARBOURG = SubZone("Charbourg", 45, (256,736), (319,799))
CHARBOURG_CENTREPOKEMON = Zone("Charbourg - Centre Pokémon", 48, "city/charbourg-centrePokemon", False, False, False)
CHARBOURG_CENTREPOKEMON_DOOR = Door(Position(303,756,SOUTHCENTER), Position(8,12,CHARBOURG_CENTREPOKEMON))
CHARBOURG_SHOP = Zone("Charbourg - Shop", 46, "city/charbourg-shop", False, False, False)
setConnectingDoors(CHARBOURG_CENTREPOKEMON_DOOR, Door(Position(8,13,CHARBOURG_CENTREPOKEMON), Position(303,757,SOUTHCENTER)))
setConnectingDoors(Door(Position(285,746,SOUTHCENTER), Position(3,11,CHARBOURG_SHOP)), Door(Position(3,12,CHARBOURG_SHOP), Position(285,747,SOUTHCENTER)))

# Floraville
FLORAVILLE = SubZone("Floraville", 426, (160,608), (191,671))
FLORAVILLE_CENTREPOKEMON = Zone("Floraville - Centre Pokémon", 428, "city/floraville-centrePokemon", False, False, False)
FLORAVILLE_CENTREPOKEMON_DOOR = Door(Position(176,666,NORTHWEST), Position(8,12,FLORAVILLE_CENTREPOKEMON))
FLORAVILLE_SHOP = Zone("Floraville - Shop", 427, "city/floraville-shop", False, False, False)
setConnectingDoors(FLORAVILLE_CENTREPOKEMON_DOOR, Door(Position(8,13,FLORAVILLE_CENTREPOKEMON), Position(176,667,NORTHWEST)))
setConnectingDoors(Door(Position(184,657,NORTHWEST), Position(3,11,FLORAVILLE_SHOP)), Door(Position(3,12,FLORAVILLE_SHOP), Position(184,658,NORTHWEST)))

# Vestigion
VESTIGION = SubZone("Vestigion", 65, (288,512), (351,575))
VESTIGION.setEncounterTables(encounter.VESTIGION)
VESTIGION_CENTREPOKEMON = Zone("Vestigion - Centre Pokémon", 69, "city/vestigion-centrePokemon", False, False, False)
VESTIGION_CENTREPOKEMON_DOOR = Door(Position(305,530,NORTHWEST), Position(8,12,VESTIGION_CENTREPOKEMON))
VESTIGION_SHOP = Zone("Vestigion - Shop", 66, "city/vestigion-shop", False, False, False)
setConnectingDoors(VESTIGION_CENTREPOKEMON_DOOR, Door(Position(8,13,VESTIGION_CENTREPOKEMON), Position(305,531,NORTHWEST)))
setConnectingDoors(Door(Position(309,548,NORTHWEST), Position(3,11,VESTIGION_SHOP)), Door(Position(3,12,VESTIGION_SHOP), Position(309,549,NORTHWEST)))

# Unionpolis
UNIONPOLIS = Zone("Unionpolis", 86, "city/unionpolis", True, True, False)
UNIONPOLIS_CENTREPOKEMON = Zone("Unionpolis - Centre Pokémon", 101, "city/unionpolis-centrePokemon", False, False, False)
UNIONPOLIS_CENTREPOKEMON_DOOR = Door(Position(465,697,UNIONPOLIS), Position(8,12,UNIONPOLIS_CENTREPOKEMON))
UNIONPOLIS_SHOP = Zone("Unionpolis - Shop", 87, "city/unionpolis-shop", False, False, False)
setConnectingDoors(UNIONPOLIS_CENTREPOKEMON_DOOR, Door(Position(8,13,UNIONPOLIS_CENTREPOKEMON), Position(465,698,UNIONPOLIS)))
setConnectingDoors(Door(Position(477,710,UNIONPOLIS), Position(3,11,UNIONPOLIS_SHOP)), Door(Position(3,12,UNIONPOLIS_SHOP), Position(477,711,UNIONPOLIS)))

# Bonville
BONVILLE = SubZone("Bonville", 433, (544,640), (607,671))
BONVILLE_CENTREPOKEMON = Zone("Bonville - Centre Pokémon", 435, "city/bonville-centrePokemon", False, False, False)
BONVILLE_CENTREPOKEMON_DOOR = Door(Position(566,656,NORTHCENTER), Position(8,12,BONVILLE_CENTREPOKEMON))
BONVILLE_SHOP = Zone("Bonville - Shop", 434, "city/bonville-shop", False, False, False)
setConnectingDoors(BONVILLE_CENTREPOKEMON_DOOR, Door(Position(8,13,BONVILLE_CENTREPOKEMON), Position(566,657,NORTHCENTER)))
setConnectingDoors(Door(Position(571,665,NORTHCENTER), Position(3,11,BONVILLE_SHOP)), Door(Position(3,12,BONVILLE_SHOP), Position(571,666,NORTHCENTER)))

# Voilaroc
VOILAROC = Zone("Voilaroc", 132, "city/voilaroc", True, True, False)
VOILAROC_CENTREPOKEMON = Zone("Voilaroc - Centre Pokémon", 134, "city/voilaroc-centrePokemon", False, False, False)
VOILAROC_CENTREPOKEMON_DOOR = Door(Position(717,611,VOILAROC), Position(8,12,VOILAROC_CENTREPOKEMON))
VOILAROC_CENTRECOMMERCIAL = Zone("Voilaroc - Centre Commercial", 137, "city/centreCommercial-1", False, False, False)
VOILAROC_CENTRECOMMERCIALETAGE1 = Zone("Voilaroc - Centre Commercial Étage 1", 138, "city/centreCommercial-2", False, False, False)
VOILAROC_CENTRECOMMERCIALETAGE2 = Zone("Voilaroc - Centre Commercial Étage 2", 139, "city/centreCommercial-3", False, False, False)
VOILAROC_CENTRECOMMERCIALETAGE3 = Zone("Voilaroc - Centre Commercial Étage 3", 140, "city/centreCommercial-4", False, False, False)
VOILAROC_CENTRECOMMERCIALETAGE4 = Zone("Voilaroc - Centre Commercial Étage 4", 141, "city/centreCommercial-5", False, False, False)
VOILAROC_CENTRECOMMERCIALASCENSEUR = Zone("Voilaroc - Centre Commercial Ascenseur", 142, "city/centreCommercial-7", False, False, False)
VOILAROC_CENTRECOMMERCIALSOUSSOL1 = Zone("Voilaroc - Centre Commercial Sous-Sol 1", 566, "city/centreCommercial-6", False, False, False)
VOILAROC_CENTRECOMMERCIAL.addDoor(Door(Position(15,2,VOILAROC_CENTRECOMMERCIAL), Position(3,6,VOILAROC_CENTRECOMMERCIALASCENSEUR)))
VOILAROC_CENTRECOMMERCIALETAGE1.addDoor(Door(Position(15,2,VOILAROC_CENTRECOMMERCIALETAGE1), Position(3,6,VOILAROC_CENTRECOMMERCIALASCENSEUR)))
VOILAROC_CENTRECOMMERCIALETAGE2.addDoor(Door(Position(15,2,VOILAROC_CENTRECOMMERCIALETAGE2), Position(3,6,VOILAROC_CENTRECOMMERCIALASCENSEUR)))
VOILAROC_CENTRECOMMERCIALETAGE3.addDoor(Door(Position(15,2,VOILAROC_CENTRECOMMERCIALETAGE3), Position(3,6,VOILAROC_CENTRECOMMERCIALASCENSEUR)))
VOILAROC_CENTRECOMMERCIALETAGE4.addDoor(Door(Position(15,2,VOILAROC_CENTRECOMMERCIALETAGE4), Position(3,6,VOILAROC_CENTRECOMMERCIALASCENSEUR)))
VOILAROC_CENTRECOMMERCIALSOUSSOL1.addDoor(Door(Position(14,2,VOILAROC_CENTRECOMMERCIALSOUSSOL1), Position(3,6,VOILAROC_CENTRECOMMERCIALASCENSEUR)))
VOILAROC_CENTRECOMMERCIALASCENSEUR.addDoor(Door(Position(3,7,VOILAROC_CENTRECOMMERCIALASCENSEUR), Position(15,3,VOILAROC_CENTRECOMMERCIAL)))
setConnectingDoors(VOILAROC_CENTREPOKEMON_DOOR, Door(Position(8,13,VOILAROC_CENTREPOKEMON), Position(717,612,VOILAROC)))
setConnectingDoors(Door(Position(701,603,VOILAROC), Position(10,12,VOILAROC_CENTRECOMMERCIAL)), Door(Position(10,13,VOILAROC_CENTRECOMMERCIAL), Position(701,604,VOILAROC)))
setConnectingDoors(Door(Position(7,8,VOILAROC_CENTRECOMMERCIAL), Position(12,8,VOILAROC_CENTRECOMMERCIALSOUSSOL1)), Door(Position(11,8,VOILAROC_CENTRECOMMERCIALSOUSSOL1), Position(6,8,VOILAROC_CENTRECOMMERCIAL)))
setConnectingDoors(Door(Position(12,8,VOILAROC_CENTRECOMMERCIAL), Position(6,8,VOILAROC_CENTRECOMMERCIALETAGE1)), Door(Position(7,8,VOILAROC_CENTRECOMMERCIALETAGE1), Position(13,8,VOILAROC_CENTRECOMMERCIAL)))
setConnectingDoors(Door(Position(12,8,VOILAROC_CENTRECOMMERCIALETAGE1), Position(6,8,VOILAROC_CENTRECOMMERCIALETAGE2)), Door(Position(7,8,VOILAROC_CENTRECOMMERCIALETAGE2), Position(13,8,VOILAROC_CENTRECOMMERCIALETAGE1)))
setConnectingDoors(Door(Position(12,8,VOILAROC_CENTRECOMMERCIALETAGE2), Position(6,8,VOILAROC_CENTRECOMMERCIALETAGE3)), Door(Position(7,8,VOILAROC_CENTRECOMMERCIALETAGE3), Position(13,8,VOILAROC_CENTRECOMMERCIALETAGE2)))
setConnectingDoors(Door(Position(12,8,VOILAROC_CENTRECOMMERCIALETAGE3), Position(6,8,VOILAROC_CENTRECOMMERCIALETAGE4)), Door(Position(7,8,VOILAROC_CENTRECOMMERCIALETAGE4), Position(13,8,VOILAROC_CENTRECOMMERCIALETAGE3)))

# Verchamps
VERCHAMPS = SubZone("Verchamps", 120, (576,800), (639,863))
VERCHAMPS.setEncounterTables(encounter.VERCHAMPS)
VERCHAMPS_CENTREPOKEMON = Zone("Verchamps - Centre Pokémon", 123, "city/verchamps-centrePokemon", False, False, False)
VERCHAMPS_CENTREPOKEMON_DOOR = Door(Position(600,815,SOUTH), Position(8,12,VERCHAMPS_CENTREPOKEMON))
VERCHAMPS_SHOP = Zone("Verchamps - Shop", 121, "city/verchamps-shop", False, False, False)
setConnectingDoors(VERCHAMPS_CENTREPOKEMON_DOOR, Door(Position(8,13,VERCHAMPS_CENTREPOKEMON), Position(600,816,SOUTH)))
setConnectingDoors(Door(Position(601,844,SOUTH), Position(3,11,VERCHAMPS_SHOP)), Door(Position(3,12,VERCHAMPS_SHOP), Position(601,845,SOUTH)))

# Célestia
CELESTIA = SubZone("Célestia", 442, (448,512), (479,543))
CELESTIA.setEncounterTables(encounter.CELESTIA)
CELESTIA_CENTREPOKEMON = Zone("Célestia - Centre Pokémon", 443, "city/celestia-centrePokemon", False, False, False)
CELESTIA_CENTREPOKEMON_DOOR = Door(Position(472,538,NORTHCENTER), Position(8,12,CELESTIA_CENTREPOKEMON))
CELESTIA_SHOP = Zone("Célestia - Shop", 446, "city/celestia-shop", False, False, False)
setConnectingDoors(CELESTIA_CENTREPOKEMON_DOOR, Door(Position(8,13,CELESTIA_CENTREPOKEMON), Position(472,539,NORTHCENTER)))
setConnectingDoors(Door(Position(450,515,NORTHCENTER), Position(4,8,CELESTIA_SHOP)), Door(Position(4,9,CELESTIA_SHOP), Position(450,516,NORTHCENTER)))

# Joliberges
JOLIBERGES = Zone("Joliberges", 33, "city/joliberges", True, True, False)
JOLIBERGES.setEncounterTables(encounter.JOLIBERGES)
JOLIBERGES_CENTREPOKEMON = Zone("Joliberges - Centre Pokémon", 36, "city/joliberges-centrePokemon", False, False, False)
JOLIBERGES_CENTREPOKEMON_DOOR = Door(Position(58,722,JOLIBERGES), Position(8,12,JOLIBERGES_CENTREPOKEMON))
JOLIBERGES_SHOP = Zone("Joliberges - Shop", 34, "city/joliberges-shop", False, False, False)
setConnectingDoors(JOLIBERGES_CENTREPOKEMON_DOOR, Door(Position(8,13,JOLIBERGES_CENTREPOKEMON), Position(58,723,JOLIBERGES)))
setConnectingDoors(Door(Position(53,740,JOLIBERGES), Position(3,11,JOLIBERGES_SHOP)), Door(Position(3,12,JOLIBERGES_SHOP), Position(53,741,JOLIBERGES)))

# Frimapic
FRIMAPIC = SubZone("Frimapic", 165, (352,192), (383,255))
FRIMAPIC_CENTREPOKEMON = Zone("Frimapic - Centre Pokémon", 168, "city/frimapic-centrePokemon", False, False, False)
FRIMAPIC_CENTREPOKEMON_DOOR = Door(Position(379,233,NORTH), Position(8,12,FRIMAPIC_CENTREPOKEMON))
FRIMAPIC_SHOP = Zone("Frimapic - Shop", 166, "city/frimapic-shop", False, False, False)
setConnectingDoors(FRIMAPIC_CENTREPOKEMON_DOOR, Door(Position(8,13,FRIMAPIC_CENTREPOKEMON), Position(379,234,NORTH)))
setConnectingDoors(Door(Position(353,232,NORTH), Position(3,11,FRIMAPIC_SHOP)), Door(Position(3,12,FRIMAPIC_SHOP), Position(353,233,NORTH)))

# Rivamar
RIVAMAR = SubZone("Rivamar", 150, (832,736), (895,799))
RIVAMAR.setEncounterTables(encounter.RIVAMAR)
RIVAMAR_CENTREPOKEMON = Zone("Rivamar - Centre Pokémon", 151, "city/rivamar-centrePokemon", False, False, False)
RIVAMAR_CENTREPOKEMON_DOOR = Door(Position(860,784,EAST), Position(8,12,RIVAMAR_CENTREPOKEMON))
RIVAMAR_SHOP = Zone("Rivamar - Shop", 153, "city/rivamar-shop", False, False, False)
setConnectingDoors(RIVAMAR_CENTREPOKEMON_DOOR, Door(Position(8,13,RIVAMAR_CENTREPOKEMON), Position(860,785,EAST)))
setConnectingDoors(Door(Position(853,768,EAST), Position(3,11,RIVAMAR_SHOP)), Door(Position(3,12,RIVAMAR_SHOP), Position(853,769,EAST)))

# Ligue Pokémon
LIGUEPOKEMON = Zone("Ligue Pokémon", 172, "city/liguePokemon-1", True, True, False)
LIGUEPOKEMON.setEncounterTables(encounter.LIGUEPOKEMON_EXTERIEUR)
LIGUEPOKEMON_EXTERIEUR = SubZone("Ligue Pokémon - Extérieur", 172, (832,544), (863,607))
LIGUEPOKEMON_EXTERIEUR.setEncounterTables(encounter.LIGUEPOKEMON_EXTERIEUR)
LIGUEPOKEMON_CENTREPOKEMON = Zone("Route Victoire - Centre Pokémon", 173, "city/liguePokemon-centrePokemon", False, False, False)
LIGUEPOKEMON_CENTREPOKEMON_DOOR = Door(Position(842,598,EAST), Position(8,12,LIGUEPOKEMON_CENTREPOKEMON))
LIGUEPOKEMON_INTERIEUR = Zone("Ligue Pokémon - Intérieur", 175, "city/liguePokemon-2", False, False, False)
LIGUEPOKEMON_INTERIEUR_DOOR = Door(Position(847,559,LIGUEPOKEMON), Position(11,11,LIGUEPOKEMON_INTERIEUR))
setConnectingDoors(LIGUEPOKEMON_CENTREPOKEMON_DOOR, Door(Position(8,13,LIGUEPOKEMON_CENTREPOKEMON), Position(842,599,EAST)))
setConnectingDoors(LIGUEPOKEMON_INTERIEUR_DOOR, Door(Position(11,12,LIGUEPOKEMON_INTERIEUR), Position(847,560,LIGUEPOKEMON)))

# Parc des Amis
PARCDESAMIS = Zone("Parc des Amis", 393, "city/parcdesamis", False, False, False)
PARCDESAMIS_DOOR = Door(Position(306,909,SOUTHWEST), Position(7,19,PARCDESAMIS))
setConnectingDoors(PARCDESAMIS_DOOR, Door(Position(7,20,PARCDESAMIS), Position(306,910,SOUTHWEST)))

# Aire de Combat
AIREDECOMBAT = SubZone("Aire de Combat", 188, (608,416), (671,447))
AIREDECOMBAT_CENTREPOKEMON = Zone("Aire de Combat - Centre Pokémon", 189, "city/airedecombat-centrePokemon", False, False, False)
AIREDECOMBAT_CENTREPOKEMON_DOOR = Door(Position(647,429,SECTEURCOMBAT_SOUTHEAST), Position(8,12,AIREDECOMBAT_CENTREPOKEMON))
AIREDECOMBAT_SHOP = Zone("Aire de Combat - Shop", 191, "city/airedecombat-shop", False, False, False)
setConnectingDoors(AIREDECOMBAT_CENTREPOKEMON_DOOR, Door(Position(8,13,AIREDECOMBAT_CENTREPOKEMON), Position(647,430,SECTEURCOMBAT_SOUTHEAST)))
setConnectingDoors(Door(Position(660,429,SECTEURCOMBAT_SOUTHEAST), Position(3,11,AIREDECOMBAT_SHOP)), Door(Position(3,12,AIREDECOMBAT_SHOP), Position(660,430,SECTEURCOMBAT_SOUTHEAST)))

# Aire de Survie
AIREDESURVIE = SubZone("Aire de Survie", 450, (640,320), (671,351))
AIREDESURVIE_CENTREPOKEMON = Zone("Aire de Survie - Centre Pokémon", 452, "city/airedesurvie-centrePokemon", False, False, False)
AIREDESURVIE_CENTREPOKEMON_DOOR = Door(Position(659,338,SECTEURCOMBAT_NORTHWEST), Position(8,12,AIREDESURVIE_CENTREPOKEMON))
AIREDESURVIE_SHOP = Zone("Aire de Survie - Shop", 451, "city/airedesurvie-shop", False, False, False)
setConnectingDoors(AIREDESURVIE_CENTREPOKEMON_DOOR, Door(Position(8,13,AIREDESURVIE_CENTREPOKEMON), Position(659,339,SECTEURCOMBAT_NORTHWEST)))
setConnectingDoors(Door(Position(663,338,SECTEURCOMBAT_NORTHWEST), Position(3,11,AIREDESURVIE_SHOP)), Door(Position(3,12,AIREDESURVIE_SHOP), Position(663,339,SECTEURCOMBAT_NORTHWEST)))

# Aire de Détente
AIREDEDETENTE = SubZone("Aire de Détente", 457, (800,448), (831,479))
AIREDEDETENTE.setEncounterTables(encounter.AIREDEDETENTE)
AIREDEDETENTE_CENTREPOKEMON = Zone("Aire de Détente - Centre Pokémon", 459, "city/airededetente-centrePokemon", False, False, False)
AIREDEDETENTE_CENTREPOKEMON_DOOR = Door(Position(802,472,SECTEURCOMBAT_SOUTHEAST), Position(8,12,AIREDEDETENTE_CENTREPOKEMON))
setConnectingDoors(AIREDEDETENTE_CENTREPOKEMON_DOOR, Door(Position(8,13,AIREDEDETENTE_CENTREPOKEMON), Position(802,473,SECTEURCOMBAT_SOUTHEAST)))

# Routes
ROUTE201 = SubZone("Route 201", 342, (96,832), (159,863))
ROUTE202 = SubZone("Route 202", 343, (160,800), (191,831))
ROUTE203 = SubZone("Route 203", 344, (192,736), (255,767))
ROUTE204_SUD = SubZone("Route 204 - Sud", 345, (160,704), (191,735))
ROUTE204_NORD = SubZone("Route 204 - Nord", 346, (160,672), (191,703))
ROUTE205_SUD = SubZone("Route 205 - Sud", 347, (192,576), (223,671))
ROUTE205_NORD = SubZone("Route 205 - Nord", 349, (256,512), (287,543))
ROUTE206 = SubZone("Route 206", 350, (288,576), (319,703))
ROUTE207 = SubZone("Route 207", 353, (288,704), (351,735))
ROUTE208 = Zone("Route 208", 354, "route/route208", True, True, False)
ROUTE209 = SubZone("Route 209", 356, (512,672), (575,735))
ROUTE210_SUD = SubZone("Route 210 - Sud", 362, (544,544), (575,639))
ROUTE210_NORD = SubZone("Route 210 - Nord", 363, (480,512), (575,543))
ROUTE211_OUEST = SubZone("Route 211 - Ouest", 365, (352,512), (383,543))
ROUTE211_EST = SubZone("Route 211 - Est", 366, (416,512), (447,543))
ROUTE212_SUD = SubZone("Route 212 - Sud", 371, (448,832), (575,863))
ROUTE212_NORD = SubZone("Route 212 - Nord", 367, (448,736), (479,831))
ROUTE213_EST = Zone("Route 213 - Est", 373, "route/route213", True, True, False)
ROUTE213_OUEST = SubZone("Route 213 - Ouest", 373, (640,800), (735,863))
ROUTE214 = SubZone("Route 214", 380, (704,640), (735,735))
ROUTE215 = SubZone("Route 215", 382, (576,576), (671,607))
ROUTE216 = SubZone("Route 216", 383, (288,384), (383,415))
ROUTE217 = SubZone("Route 217", 385, (288,256), (319,383))
ROUTE218 = Zone("Route 218", 388, "route/route218", True, True, False)
ROUTE219 = SubZone("Route 219", 391, (160,864), (191,895))
ROUTE220 = SubZone("Route 220", 467, (160,896), (223,927))
ROUTE221 = SubZone("Route 221", 392, (224,896), (319,927))
ROUTE222 = SubZone("Route 222", 395, (736,768), (831,799))
ROUTE223 = SubZone("Route 223", 468, (832,608), (863,735))
ROUTE224 = SubZone("Route 224", 399, (864,480), (927,575))
ROUTE225 = SubZone("Route 225", 400, (608,320), (639,415))
ROUTE226 = SubZone("Route 226", 469, (672,320), (767,351))
ROUTE227 = SubZone("Route 227", 403, (736,256), (767,319))
ROUTE228 = SubZone("Route 228", 406, (768,320), (799,415))
ROUTE229 = SubZone("Route 229", 407, (768,416), (831,447))
ROUTE230 = SubZone("Route 230", 471, (672,416), (767,447))

# Routes Encounters
ROUTE201.setEncounterTables(encounter.ROUTE201)
ROUTE202.setEncounterTables(encounter.ROUTE202)
ROUTE203.setEncounterTables(encounter.ROUTE203)
ROUTE204_SUD.setEncounterTables(encounter.ROUTE204_SUD)
ROUTE204_NORD.setEncounterTables(encounter.ROUTE204_NORD)
ROUTE205_SUD.setEncounterTables(encounter.ROUTE205_SUD)
ROUTE205_NORD.setEncounterTables(encounter.ROUTE205_NORD)
ROUTE206.setEncounterTables(encounter.ROUTE206)
ROUTE207.setEncounterTables(encounter.ROUTE207)
ROUTE208.setEncounterTables(encounter.ROUTE208)
ROUTE209.setEncounterTables(encounter.ROUTE209)
ROUTE210_SUD.setEncounterTables(encounter.ROUTE210_SUD)
ROUTE210_NORD.setEncounterTables(encounter.ROUTE210_NORD)
ROUTE211_OUEST.setEncounterTables(encounter.ROUTE211_OUEST)
ROUTE211_EST.setEncounterTables(encounter.ROUTE211_EST)
ROUTE212_SUD.setEncounterTables(encounter.ROUTE212_SUD)
ROUTE212_NORD.setEncounterTables(encounter.ROUTE212_NORD)
ROUTE213_OUEST.setEncounterTables(encounter.ROUTE213)
ROUTE214.setEncounterTables(encounter.ROUTE214)
ROUTE215.setEncounterTables(encounter.ROUTE215)
ROUTE216.setEncounterTables(encounter.ROUTE216)
ROUTE217.setEncounterTables(encounter.ROUTE217)
ROUTE218.setEncounterTables(encounter.ROUTE218)
ROUTE219.setEncounterTables(encounter.ROUTE219)
ROUTE220.setEncounterTables(encounter.ROUTE220)
ROUTE221.setEncounterTables(encounter.ROUTE221)
ROUTE222.setEncounterTables(encounter.ROUTE222)
ROUTE223.setEncounterTables(encounter.ROUTE223)
ROUTE224.setEncounterTables(encounter.ROUTE224)
ROUTE225.setEncounterTables(encounter.ROUTE225)
ROUTE226.setEncounterTables(encounter.ROUTE226)
ROUTE227.setEncounterTables(encounter.ROUTE227)
ROUTE228.setEncounterTables(encounter.ROUTE228)
ROUTE229.setEncounterTables(encounter.ROUTE229)
ROUTE230.setEncounterTables(encounter.ROUTE230)

# Passage Route 206 <-> Vestigion
ROUTE206_PASSAGEVESTIGION = Zone("Route 206 - Passage Vestigion", 80, "route/route206-passageVestigion", True, False, False)
setConnectingDoors(Door(Position(304,570,NORTHWEST), Position(7,3,ROUTE206_PASSAGEVESTIGION)), Door(Position(7,2,ROUTE206_PASSAGEVESTIGION), Position(304,569,NORTHWEST)))

# Passage Route 206 <-> Charbourg
ROUTE206_PASSAGECHARBOURG = Zone("Route 206 - Passage Charbourg", 351, "route/route206-passageCharbourg", True, False, False)
setConnectingDoors(Door(Position(302,688,SOUTHCENTER), Position(7,12,ROUTE206_PASSAGECHARBOURG)), Door(Position(7,13,ROUTE206_PASSAGECHARBOURG), Position(302,689,SOUTHCENTER)))

# Passage Route 208 <-> Unionpolis
ROUTE208_PASSAGEUNIONPOLIS = Zone("Route 208 - Passage Unionpolis", 109, "route/route208-passageUnionpolis", True, False, False)
setConnectingDoors(Door(Position(448,726,ROUTE208), Position(1,7,ROUTE208_PASSAGEUNIONPOLIS)), Door(Position(0,7,ROUTE208_PASSAGEUNIONPOLIS), Position(447,726,ROUTE208)))
setConnectingDoors(Door(Position(453,726,UNIONPOLIS), Position(10,7,ROUTE208_PASSAGEUNIONPOLIS)), Door(Position(11,7,ROUTE208_PASSAGEUNIONPOLIS), Position(454,726,UNIONPOLIS)))

# Passage Route 209 <-> Unionpolis
ROUTE209_PASSAGEUNIONPOLIS = Zone("Route 209 - Passage Unionpolis", 110, "route/route209-passageUnionpolis", True, False, False)
setConnectingDoors(Door(Position(511,726,NORTHCENTER), Position(10,7,ROUTE209_PASSAGEUNIONPOLIS)), Door(Position(11,7,ROUTE209_PASSAGEUNIONPOLIS), Position(512,726,NORTHCENTER)))
setConnectingDoors(Door(Position(506,726,UNIONPOLIS), Position(1,7,ROUTE209_PASSAGEUNIONPOLIS)), Door(Position(0,7,ROUTE209_PASSAGEUNIONPOLIS), Position(505,726,UNIONPOLIS)))

# Passage Route 212 <-> Unionpolis
ROUTE212_PASSAGEUNIONPOLIS = Zone("Route 212 - Passage Unionpolis", 111, "route/route212-passageUnionpolis", True, False, False)
setConnectingDoors(Door(Position(458,736,SOUTH), Position(5,12,ROUTE212_PASSAGEUNIONPOLIS)), Door(Position(5,13,ROUTE212_PASSAGEUNIONPOLIS), Position(458,737,SOUTH)))
setConnectingDoors(Door(Position(458,730,UNIONPOLIS), Position(5,3,ROUTE212_PASSAGEUNIONPOLIS)), Door(Position(5,2,ROUTE212_PASSAGEUNIONPOLIS), Position(458,729,UNIONPOLIS)))

# Passage Route 215 <-> Voilaroc
ROUTE215_PASSAGEVOILAROC = Zone("Route 215 - Passage Voilaroc", 149, "route/route215-passageVoilaroc", True, False, False)
setConnectingDoors(Door(Position(672,598,NORTHCENTER), Position(1,7,ROUTE215_PASSAGEVOILAROC)), Door(Position(0,7,ROUTE215_PASSAGEVOILAROC), Position(671,598,NORTHCENTER)))
setConnectingDoors(Door(Position(677,598,VOILAROC), Position(10,7,ROUTE215_PASSAGEVOILAROC)), Door(Position(11,7,ROUTE215_PASSAGEVOILAROC), Position(678,598,VOILAROC)))

# Passage Route 214 <-> Voilaroc
ROUTE214_PASSAGEVOILAROC = Zone("Route 214 - Passage Voilaroc", 381, "route/route214-passageVoilaroc", True, False, False)
setConnectingDoors(Door(Position(718,645,SOUTHEAST), Position(5,12,ROUTE214_PASSAGEVOILAROC)), Door(Position(5,13,ROUTE214_PASSAGEVOILAROC), Position(718,646,SOUTHEAST)))
setConnectingDoors(Door(Position(718,639,VOILAROC), Position(5,3,ROUTE214_PASSAGEVOILAROC)), Door(Position(5,2,ROUTE214_PASSAGEVOILAROC), Position(718,638,VOILAROC)))

# Passage Route 213 <-> Verchamps
ROUTE213_PASSAGEVERCHAMPS = Zone("Route 213 - Passage Verchamps", 374, "route/route213-passageVerchamps", True, False, False)
setConnectingDoors(Door(Position(640,812,SOUTH), Position(1,7,ROUTE213_PASSAGEVERCHAMPS)), Door(Position(0,7,ROUTE213_PASSAGEVERCHAMPS), Position(639,812,SOUTH)))
setConnectingDoors(Door(Position(645,812,ROUTE213_EST), Position(10,7,ROUTE213_PASSAGEVERCHAMPS)), Door(Position(11,7,ROUTE213_PASSAGEVERCHAMPS), Position(646,812,ROUTE213_EST)))

# Passage Route 218 <-> Féli-Cité
ROUTE218_PASSAGEFELICITE = Zone("Route 218 - Passage Féli-Cité", 389, "route/route218-passageFelicite", True, False, False)
setConnectingDoors(Door(Position(127,758,SOUTHWEST), Position(10,7,ROUTE218_PASSAGEFELICITE)), Door(Position(11,7,ROUTE218_PASSAGEFELICITE), Position(128,758,SOUTHWEST)))
setConnectingDoors(Door(Position(122,758,ROUTE218), Position(1,7,ROUTE218_PASSAGEFELICITE)), Door(Position(0,7,ROUTE218_PASSAGEFELICITE), Position(121,758,ROUTE218)))

# Passage Route 218 <-> Joliberges
ROUTE218_PASSAGEJOLIBERGES = Zone("Route 218 - Passage Joliberges", 390, "route/route218-passageJoliberges", True, False, False)
setConnectingDoors(Door(Position(69,754,ROUTE218), Position(10,7,ROUTE218_PASSAGEJOLIBERGES)), Door(Position(11,7,ROUTE218_PASSAGEJOLIBERGES), Position(70,754,ROUTE218)))
setConnectingDoors(Door(Position(64,754,JOLIBERGES), Position(1,7,ROUTE218_PASSAGEJOLIBERGES)), Door(Position(0,7,ROUTE218_PASSAGEJOLIBERGES), Position(63,754,JOLIBERGES)))

# Passage Route 222 <-> Rivamar
ROUTE222_PASSAGERIVAMAR = Zone("Route 222 - Passage Rivamar", 398, "route/route222-passageRivamar", True, False, False)
setConnectingDoors(Door(Position(826,790,SOUTHEAST), Position(1,7,ROUTE222_PASSAGERIVAMAR)), Door(Position(0,7,ROUTE222_PASSAGERIVAMAR), Position(825,790,SOUTHEAST)))
setConnectingDoors(Door(Position(831,790,EAST), Position(10,7,ROUTE222_PASSAGERIVAMAR)), Door(Position(11,7,ROUTE222_PASSAGERIVAMAR), Position(832,790,EAST)))

# Passage Route 225 <-> Aire de Combat
ROUTE225_PASSAGEAIREDECOMBAT = Zone("Route 225 - Passage Aire de Combat", 193, "route/route225-passageAiredecombat", True, False, False)
setConnectingDoors(Door(Position(630,414,SECTEURCOMBAT_NORTHWEST), Position(5,3,ROUTE225_PASSAGEAIREDECOMBAT)), Door(Position(5,2,ROUTE225_PASSAGEAIREDECOMBAT), Position(630,413,SECTEURCOMBAT_NORTHWEST)))
setConnectingDoors(Door(Position(630,421,SECTEURCOMBAT_SOUTHEAST), Position(5,12,ROUTE225_PASSAGEAIREDECOMBAT)), Door(Position(5,13,ROUTE225_PASSAGEAIREDECOMBAT), Position(630,422,SECTEURCOMBAT_SOUTHEAST)))

# Passage Route 226 <-> Route 228
ROUTE226_PASSAGEROUTE228 = Zone("Route 226 - Passage Route 228", 501, "route/route226-passageRoute228", True, False, False)
setConnectingDoors(Door(Position(768,330,SECTEURCOMBAT_NORTHWEST), Position(1,7,ROUTE226_PASSAGEROUTE228)), Door(Position(0,7,ROUTE226_PASSAGEROUTE228), Position(767,330,SECTEURCOMBAT_NORTHWEST)))
setConnectingDoors(Door(Position(773,330,SECTEURCOMBAT_SOUTHEAST), Position(10,7,ROUTE226_PASSAGEROUTE228)), Door(Position(11,7,ROUTE226_PASSAGEROUTE228), Position(774,330,SECTEURCOMBAT_SOUTHEAST)))

# Entrée Charbourg
ENTREECHARBOURG = Zone("Entrée Charbourg", 258, "dungeon/entreeCharbourg-1", True, False, True)
ENTREECHARBOURG.setEncounterTables(encounter.ENTREECHARBOURG)
ENTREECHARBOURG_SOUSSOL = Zone("Entrée Charbourg - Sous-Sol", 259, "dungeon/entreeCharbourg-2", True, False, True)
ENTREECHARBOURG_SOUSSOL.setEncounterTables(encounter.ENTREECHARBOURG_SOUSSOL)
setConnectingDoors(Door(Position(247,749,SOUTHWEST), Position(4,22,ENTREECHARBOURG)), Door(Position(3,22,ENTREECHARBOURG), Position(246,749,SOUTHWEST)))
setConnectingDoors(Door(Position(257,749,SOUTHCENTER), Position(27,22,ENTREECHARBOURG)), Door(Position(28,22,ENTREECHARBOURG), Position(258,749,SOUTHCENTER)))
setConnectingDoors(Door(Position(21,5,ENTREECHARBOURG), Position(48,4,ENTREECHARBOURG_SOUSSOL)), Door(Position(47,4,ENTREECHARBOURG_SOUSSOL), Position(20,5,ENTREECHARBOURG)))

# Entrée Charbourg
MINECHARBOURG_ENTREE = Zone("Mine Charbourg - Entrée", 198, "dungeon/mineCharbourg-1", True, False, True)
MINECHARBOURG_ENTREE.setEncounterTables(encounter.MINECHARBOURG_ENTREE)
MINECHARBOURG = Zone("Mine Charbourg", 199, "dungeon/mineCharbourg-2", True, False, True)
MINECHARBOURG.setEncounterTables(encounter.MINECHARBOURG)
setConnectingDoors(Door(Position(12,1,MINECHARBOURG_ENTREE), Position(302,795,SOUTHCENTER)), Door(Position(302,796,SOUTHCENTER), Position(12,2,MINECHARBOURG_ENTREE)))
setConnectingDoors(Door(Position(12,22,MINECHARBOURG_ENTREE), Position(15,2,MINECHARBOURG)), Door(Position(15,1,MINECHARBOURG), Position(12,21,MINECHARBOURG_ENTREE)))

# Chemin Rocheux
CHEMINROCHEUX = Zone("Chemin Rocheux", 254, "dungeon/cheminRocheux", True, False, True)
CHEMINROCHEUX.setEncounterTables(encounter.CHEMINROCHEUX)
setConnectingDoors(Door(Position(171,705,SOUTHWEST), Position(19,50,CHEMINROCHEUX)), Door(Position(19,51,CHEMINROCHEUX), Position(171,706,SOUTHWEST)))
setConnectingDoors(Door(Position(180,698,NORTHWEST), Position(28,44,CHEMINROCHEUX)), Door(Position(28,45,CHEMINROCHEUX), Position(180,699,NORTHWEST)))

# Forêt de Vestigion
FORETVESTIGION = Zone("Forêt de Vestigion", 203, "dungeon/foretVestigion", True, True, False)
FORETVESTIGION.setEncounterTables(encounter.FORETVESTIGION)
FORETVESTIGION_EXTERIEUR = SubZone("Forêt Vestigion - Extérieur", 202, (192,512), (255,575))
LESEOLIENNES = SubZone("Les Eoliennes", 200, (224,640), (255,671))
LESEOLIENNES.setEncounterTables(encounter.LESEOLIENNES)
FORGEFUEGO = SubZone("Forge Fuego - Extérieur", 204, (160,576), (191,607))
FORGEFUEGO.setEncounterTables(encounter.FORGEFUEGO)
setConnectingDoors(Door(Position(206,581,NORTHWEST), Position(28,86,FORETVESTIGION)), Door(Position(28,87,FORETVESTIGION), Position(206,582,NORTHWEST)))
setConnectingDoors(Door(Position(258,524,NORTHWEST), Position(86,36,FORETVESTIGION)), Door(Position(87,36,FORETVESTIGION), Position(259,524,NORTHWEST)))

# Vieux Château
VIEUXCHATEAU = Zone("Vieux Château", 295, "dungeon/vieuxChateau-1", False, False, False)
VIEUXCHATEAU.setEncounterTables(encounter.VIEUXCHATEAU)
VIEUXCHATEAU_SALLEAMANGER = Zone("Vieux Château - Salle à Manger", 296, "dungeon/vieuxChateau-2", False, False, False)
VIEUXCHATEAU_SALLEAMANGER.setEncounterTables(encounter.VIEUXCHATEAU)
VIEUXCHATEAU_AILES = Zone("Vieux Château - Ailes", 297, "dungeon/vieuxChateau-3", False, False, False)
VIEUXCHATEAU_AILES.setEncounterTables(encounter.VIEUXCHATEAU)
VIEUXCHATEAU_COULOIR = Zone("Vieux Château - Couloir", 298, "dungeon/vieuxChateau-4", False, False, False)
VIEUXCHATEAU_COULOIR.setEncounterTables(encounter.VIEUXCHATEAU)
VIEUXCHATEAU_CHAMBRE1 = Zone("Vieux Château - Chambre 1", 299, "dungeon/vieuxChateau-5", False, False, False)
VIEUXCHATEAU_CHAMBRE1.setEncounterTables(encounter.VIEUXCHATEAU)
VIEUXCHATEAU_CHAMBRE2 = Zone("Vieux Château - Chambre 2", 300, "dungeon/vieuxChateau-6", False, False, False)
VIEUXCHATEAU_CHAMBRE2.setEncounterTables(encounter.VIEUXCHATEAU)
VIEUXCHATEAU_CHAMBRE3 = Zone("Vieux Château - Chambre 3", 301, "dungeon/vieuxChateau-7", False, False, False)
VIEUXCHATEAU_CHAMBRE3.setEncounterTables(encounter.VIEUXCHATEAU)
VIEUXCHATEAU_CHAMBRE4 = Zone("Vieux Château - Chambre 4", 302, "dungeon/vieuxChateau-8", False, False, False)
VIEUXCHATEAU_CHAMBRE4.setEncounterTables(encounter.VIEUXCHATEAU_CHAMBRE4)
VIEUXCHATEAU_CHAMBRE5 = Zone("Vieux Château - Chambre 5", 303, "dungeon/vieuxChateau-9", False, False, False)
VIEUXCHATEAU_CHAMBRE5.setEncounterTables(encounter.VIEUXCHATEAU)
setConnectingDoors(Door(Position(9,16,VIEUXCHATEAU), Position(74,16,FORETVESTIGION)), Door(Position(74,15,FORETVESTIGION), Position(9,15,VIEUXCHATEAU)))
setConnectingDoors(Door(Position(9,5,VIEUXCHATEAU), Position(19,11,VIEUXCHATEAU_SALLEAMANGER)), Door(Position(19,12,VIEUXCHATEAU_SALLEAMANGER), Position(9,6,VIEUXCHATEAU)))
setConnectingDoors(Door(Position(0,6,VIEUXCHATEAU), Position(7,5,VIEUXCHATEAU_AILES)), Door(Position(8,5,VIEUXCHATEAU_AILES), Position(1,6,VIEUXCHATEAU)))
setConnectingDoors(Door(Position(18,6,VIEUXCHATEAU), Position(24,5,VIEUXCHATEAU_AILES)), Door(Position(23,5,VIEUXCHATEAU_AILES), Position(17,6,VIEUXCHATEAU)))
setConnectingDoors(Door(Position(9,2,VIEUXCHATEAU), Position(19,5,VIEUXCHATEAU_COULOIR)), Door(Position(19,6,VIEUXCHATEAU_COULOIR), Position(9,3,VIEUXCHATEAU)))
setConnectingDoors(Door(Position(4,2,VIEUXCHATEAU_COULOIR), Position(4,7,VIEUXCHATEAU_CHAMBRE1)), Door(Position(4,8,VIEUXCHATEAU_CHAMBRE1), Position(4,3,VIEUXCHATEAU_COULOIR)))
setConnectingDoors(Door(Position(11,2,VIEUXCHATEAU_COULOIR), Position(11,7,VIEUXCHATEAU_CHAMBRE2)), Door(Position(11,8,VIEUXCHATEAU_CHAMBRE2), Position(11,3,VIEUXCHATEAU_COULOIR)))
setConnectingDoors(Door(Position(19,2,VIEUXCHATEAU_COULOIR), Position(12,7,VIEUXCHATEAU_CHAMBRE3)), Door(Position(12,8,VIEUXCHATEAU_CHAMBRE3), Position(19,3,VIEUXCHATEAU_COULOIR)))
setConnectingDoors(Door(Position(27,2,VIEUXCHATEAU_COULOIR), Position(13,7,VIEUXCHATEAU_CHAMBRE4)), Door(Position(13,8,VIEUXCHATEAU_CHAMBRE4), Position(27,3,VIEUXCHATEAU_COULOIR)))
setConnectingDoors(Door(Position(34,2,VIEUXCHATEAU_COULOIR), Position(10,7,VIEUXCHATEAU_CHAMBRE5)), Door(Position(10,8,VIEUXCHATEAU_CHAMBRE5), Position(34,3,VIEUXCHATEAU_COULOIR)))

# Piste Cyclable
PISTECYCLABLE = Zone("Piste Cyclable", 350, "route/pisteCyclable", True, True, False)
setConnectingDoors(Door(Position(304,576,PISTECYCLABLE), Position(7,12,ROUTE206_PASSAGEVESTIGION)), Door(Position(7,13,ROUTE206_PASSAGEVESTIGION), Position(304,577,PISTECYCLABLE)))
setConnectingDoors(Door(Position(302,682,PISTECYCLABLE), Position(7,3,ROUTE206_PASSAGECHARBOURG)), Door(Position(7,2,ROUTE206_PASSAGECHARBOURG), Position(302,681,PISTECYCLABLE)))

# Grotte Revêche
GROTTEREVECHE = Zone("Grotte Revêche", 284, "dungeon/grotteReveche-1", True, False, True)
GROTTEREVECHE.setEncounterTables(encounter.GROTTEREVECHE)
GROTTEREVECHE_SOUSSOL = Zone("Grotte Revêche - Sous-Sol", 285, "dungeon/grotteReveche-2", True, False, True)
GROTTEREVECHE_SOUSSOL.setEncounterTables(encounter.GROTTEREVECHE_SOUSSOL)
setConnectingDoors(Door(Position(299,611,SOUTHCENTER), Position(30,55,GROTTEREVECHE)), Door(Position(30,56,GROTTEREVECHE), Position(299,612,SOUTHCENTER)))
setConnectingDoors(Door(Position(310,607,SOUTHCENTER), Position(41,53,GROTTEREVECHE)), Door(Position(41,54,GROTTEREVECHE), Position(310,608,SOUTHCENTER)))
setConnectingDoors(Door(Position(27,54,GROTTEREVECHE), Position(16,40,GROTTEREVECHE_SOUSSOL)), Door(Position(17,40,GROTTEREVECHE_SOUSSOL), Position(28,54,GROTTEREVECHE)))
setConnectingDoors(Door(Position(54,54,GROTTEREVECHE), Position(43,38,GROTTEREVECHE_SOUSSOL)), Door(Position(44,38,GROTTEREVECHE_SOUSSOL), Position(55,54,GROTTEREVECHE)))

# Tour Perdue
TOURPERDUE_REZDECHAUSSEE = Zone("Tour Perdue - Rez-de-Chaussée", 357, "dungeon/tourPerdue-1", False, False, False)
TOURPERDUE_REZDECHAUSSEE.setEncounterTables(encounter.TOURPERDUE_REZDECHAUSSEE)
TOURPERDUE_ETAGE1 = Zone("Tour Perdue - Étage 1", 358, "dungeon/tourPerdue-2", False, False, False)
TOURPERDUE_ETAGE1.setEncounterTables(encounter.TOURPERDUE_REZDECHAUSSEE)
TOURPERDUE_ETAGE2 = Zone("Tour Perdue - Étage 2", 359, "dungeon/tourPerdue-3", False, False, False)
TOURPERDUE_ETAGE2.setEncounterTables(encounter.TOURPERDUE_ETAGE2)
TOURPERDUE_ETAGE3 = Zone("Tour Perdue - Étage 3", 360, "dungeon/tourPerdue-4", False, False, False)
TOURPERDUE_ETAGE3.setEncounterTables(encounter.TOURPERDUE_ETAGE3)
TOURPERDUE_ETAGE4 = Zone("Tour Perdue - Étage 4", 361, "dungeon/tourPerdue-5", False, False, False)
TOURPERDUE_ETAGE4.setEncounterTables(encounter.TOURPERDUE_ETAGE4)
setConnectingDoors(Door(Position(7,15,TOURPERDUE_REZDECHAUSSEE), Position(568,681,NORTHCENTER)), Door(Position(568,680,NORTHCENTER), Position(7,14,TOURPERDUE_REZDECHAUSSEE)))
setConnectingDoors(Door(Position(5,3,TOURPERDUE_REZDECHAUSSEE), Position(11,3,TOURPERDUE_ETAGE1)), Door(Position(10,3,TOURPERDUE_ETAGE1), Position(4,3,TOURPERDUE_REZDECHAUSSEE)))
setConnectingDoors(Door(Position(5,3,TOURPERDUE_ETAGE1), Position(11,3,TOURPERDUE_ETAGE2)), Door(Position(10,3,TOURPERDUE_ETAGE2), Position(4,3,TOURPERDUE_ETAGE1)))
setConnectingDoors(Door(Position(5,3,TOURPERDUE_ETAGE2), Position(11,3,TOURPERDUE_ETAGE3)), Door(Position(10,3,TOURPERDUE_ETAGE3), Position(4,3,TOURPERDUE_ETAGE2)))
setConnectingDoors(Door(Position(5,3,TOURPERDUE_ETAGE3), Position(11,3,TOURPERDUE_ETAGE4)), Door(Position(10,3,TOURPERDUE_ETAGE4), Position(4,3,TOURPERDUE_ETAGE3)))

# Ruines Bonville
RUINESBONVILLE_ENTREE = Zone("Ruines Bonville - Entrée", 226, "dungeon/ruinesBonville-1", True, False, True)
RUINESBONVILLE_ENTREE_NORDOUEST = Zone("Ruines Bonville - Entrée Nord-Ouest", 228, "dungeon/ruinesBonville-2", True, False, True)
RUINESBONVILLE_ENTREE_NORDOUEST.setEncounterTables(encounter.RUINESBONVILLE)
RUINESBONVILLE_ENTREE_SUDEST = Zone("Ruines Bonville - Entrée Sud-Est", 230, "dungeon/ruinesBonville-3", True, False, True)
RUINESBONVILLE_ENTREE_SUDEST.setEncounterTables(encounter.RUINESBONVILLE)
RUINESBONVILLE_SALLE1 = Zone("Ruines Bonville - Salle 1", 229, "dungeon/ruinesBonville-4", True, False, True)
RUINESBONVILLE_SALLE1.setEncounterTables(encounter.RUINESBONVILLE)
RUINESBONVILLE_SALLE1_NORDEST = Zone("Ruines Bonville - Salle 1 Nord-Est", 227, "dungeon/ruinesBonville-5", True, False, True)
RUINESBONVILLE_SALLE1_NORDEST.setEncounterTables(encounter.RUINESBONVILLE)
RUINESBONVILLE_SALLE1_SUDEST = Zone("Ruines Bonville - Salle 1 Sud-Est", 232, "dungeon/ruinesBonville-6", True, False, True)
RUINESBONVILLE_SALLE1_SUDEST.setEncounterTables(encounter.RUINESBONVILLE)
RUINESBONVILLE_SALLE2 = Zone("Ruines Bonville - Salle 2", 231, "dungeon/ruinesBonville-7", True, False, True)
RUINESBONVILLE_SALLE2.setEncounterTables(encounter.RUINESBONVILLE)
RUINESBONVILLE_SALLE2_NORDOUEST = Zone("Ruines Bonville - Salle 2 Nord-Ouest", 235, "dungeon/ruinesBonville-8", True, False, True)
RUINESBONVILLE_SALLE2_NORDOUEST.setEncounterTables(encounter.RUINESBONVILLE)
RUINESBONVILLE_SALLE2_SUDOUEST = Zone("Ruines Bonville - Salle 2 Sud-Ouest", 236, "dungeon/ruinesBonville-9", True, False, True)
RUINESBONVILLE_SALLE2_SUDOUEST.setEncounterTables(encounter.RUINESBONVILLE)
RUINESBONVILLE_SALLE3 = Zone("Ruines Bonville - Salle 3", 237, "dungeon/ruinesBonville-10", True, False, True)
RUINESBONVILLE_SALLE3.setEncounterTables(encounter.RUINESBONVILLE)
RUINESBONVILLE_SALLE3_SUDEST = Zone("Ruines Bonville - Salle 3 Sud-Est", 241, "dungeon/ruinesBonville-11", True, False, True)
RUINESBONVILLE_SALLE3_SUDEST.setEncounterTables(encounter.RUINESBONVILLE)
RUINESBONVILLE_SALLE4 = Zone("Ruines Bonville - Salle 4", 239, "dungeon/ruinesBonville-12", True, False, True)
RUINESBONVILLE_SALLE4.setEncounterTables(encounter.RUINESBONVILLE)
RUINESBONVILLE_SALLE4_SUDOUEST = Zone("Ruines Bonville - Salle 4 Sud-Ouest", 234, "dungeon/ruinesBonville-13", True, False, True)
RUINESBONVILLE_SALLE4_SUDOUEST.setEncounterTables(encounter.RUINESBONVILLE)
RUINESBONVILLE_SALLE4_SUDEST = Zone("Ruines Bonville - Salle 4 Sud-Est", 515, "dungeon/ruinesBonville-14", True, False, True)
RUINESBONVILLE_SALLE4_SUDEST.setEncounterTables(encounter.RUINESBONVILLE)
RUINESBONVILLE_SALLE5 = Zone("Ruines Bonville - Salle 5", 238, "dungeon/ruinesBonville-15", True, False, True)
RUINESBONVILLE_SALLE5.setEncounterTables(encounter.RUINESBONVILLE)
RUINESBONVILLE_SALLE5_NORDOUEST = Zone("Ruines Bonville - Salle 5 Nord-Ouest", 242, "dungeon/ruinesBonville-16", True, False, True)
RUINESBONVILLE_SALLE5_NORDOUEST.setEncounterTables(encounter.RUINESBONVILLE)
RUINESBONVILLE_SALLE5_SUDEST = Zone("Ruines Bonville - Salle 5 Sud-Est", 233, "dungeon/ruinesBonville-17", True, False, True)
RUINESBONVILLE_SALLE5_SUDEST.setEncounterTables(encounter.RUINESBONVILLE)
RUINESBONVILLE_SALLE6 = Zone("Ruines Bonville - Salle 6", 240, "dungeon/ruinesBonville-18", True, False, True)
RUINESBONVILLE_SALLE6.setEncounterTables(encounter.RUINESBONVILLE)
setConnectingDoors(Door(Position(5,12,RUINESBONVILLE_ENTREE), Position(595,656,NORTHCENTER)), Door(Position(595,655,NORTHCENTER), Position(5,11,RUINESBONVILLE_ENTREE)))
setConnectingDoors(Door(Position(3,3,RUINESBONVILLE_ENTREE), Position(5,3,RUINESBONVILLE_ENTREE_NORDOUEST)), Door(Position(6,3,RUINESBONVILLE_ENTREE_NORDOUEST), Position(4,3,RUINESBONVILLE_ENTREE)))
setConnectingDoors(Door(Position(7,3,RUINESBONVILLE_ENTREE), Position(4,3,RUINESBONVILLE_SALLE1)), Door(Position(3,3,RUINESBONVILLE_SALLE1), Position(6,3,RUINESBONVILLE_ENTREE)))
setConnectingDoors(Door(Position(7,10,RUINESBONVILLE_ENTREE), Position(2,3,RUINESBONVILLE_ENTREE_SUDEST)), Door(Position(1,3,RUINESBONVILLE_ENTREE_SUDEST), Position(6,10,RUINESBONVILLE_ENTREE)))
setConnectingDoors(Door(Position(7,3,RUINESBONVILLE_SALLE1), Position(4,3,RUINESBONVILLE_SALLE1_NORDEST)), Door(Position(3,3,RUINESBONVILLE_SALLE1_NORDEST), Position(6,3,RUINESBONVILLE_SALLE1)))
setConnectingDoors(Door(Position(7,10,RUINESBONVILLE_SALLE1), Position(2,3,RUINESBONVILLE_SALLE1_SUDEST)), Door(Position(1,3,RUINESBONVILLE_SALLE1_SUDEST), Position(6,10,RUINESBONVILLE_SALLE1)))
setConnectingDoors(Door(Position(3,10,RUINESBONVILLE_SALLE1), Position(6,10,RUINESBONVILLE_SALLE2)), Door(Position(7,10,RUINESBONVILLE_SALLE2), Position(4,10,RUINESBONVILLE_SALLE1)))
setConnectingDoors(Door(Position(3,3,RUINESBONVILLE_SALLE2), Position(5,3,RUINESBONVILLE_SALLE2_NORDOUEST)), Door(Position(6,3,RUINESBONVILLE_SALLE2_NORDOUEST), Position(4,3,RUINESBONVILLE_SALLE2)))
setConnectingDoors(Door(Position(7,3,RUINESBONVILLE_SALLE2), Position(4,10,RUINESBONVILLE_SALLE3)), Door(Position(3,10,RUINESBONVILLE_SALLE3), Position(6,3,RUINESBONVILLE_SALLE2)))
setConnectingDoors(Door(Position(3,10,RUINESBONVILLE_SALLE2), Position(5,3,RUINESBONVILLE_SALLE2_SUDOUEST)), Door(Position(6,3,RUINESBONVILLE_SALLE2_SUDOUEST), Position(4,10,RUINESBONVILLE_SALLE2)))
setConnectingDoors(Door(Position(3,3,RUINESBONVILLE_SALLE3), Position(6,3,RUINESBONVILLE_SALLE4)), Door(Position(7,3,RUINESBONVILLE_SALLE4), Position(4,3,RUINESBONVILLE_SALLE3)))
setConnectingDoors(Door(Position(7,10,RUINESBONVILLE_SALLE3), Position(2,3,RUINESBONVILLE_SALLE3_SUDEST)), Door(Position(1,3,RUINESBONVILLE_SALLE3_SUDEST), Position(6,10,RUINESBONVILLE_SALLE3)))
setConnectingDoors(Door(Position(1,3,RUINESBONVILLE_SALLE4), Position(6,3,RUINESBONVILLE_SALLE5)), Door(Position(7,3,RUINESBONVILLE_SALLE5), Position(2,3,RUINESBONVILLE_SALLE4)))
setConnectingDoors(Door(Position(1,10,RUINESBONVILLE_SALLE4), Position(6,3,RUINESBONVILLE_SALLE4_SUDOUEST)), Door(Position(7,3,RUINESBONVILLE_SALLE4_SUDOUEST), Position(2,10,RUINESBONVILLE_SALLE4)))
setConnectingDoors(Door(Position(7,10,RUINESBONVILLE_SALLE4), Position(2,3,RUINESBONVILLE_SALLE4_SUDEST)), Door(Position(1,3,RUINESBONVILLE_SALLE4_SUDEST), Position(6,10,RUINESBONVILLE_SALLE4)))
setConnectingDoors(Door(Position(3,3,RUINESBONVILLE_SALLE5), Position(5,3,RUINESBONVILLE_SALLE5_NORDOUEST)), Door(Position(6,3,RUINESBONVILLE_SALLE5_NORDOUEST), Position(4,3,RUINESBONVILLE_SALLE5)))
setConnectingDoors(Door(Position(7,10,RUINESBONVILLE_SALLE5), Position(4,3,RUINESBONVILLE_SALLE5_SUDEST)), Door(Position(3,3,RUINESBONVILLE_SALLE5_SUDEST), Position(6,10,RUINESBONVILLE_SALLE5)))
setConnectingDoors(Door(Position(3,10,RUINESBONVILLE_SALLE5), Position(8,3,RUINESBONVILLE_SALLE6)), Door(Position(9,3,RUINESBONVILLE_SALLE6), Position(4,10,RUINESBONVILLE_SALLE5)))

# Tunnel Ruinemaniac
TUNNELRUINEMANIAC = Zone("Tunnel Ruinemaniac", 513, "dungeon/tunnelRuinemaniac", True, False, True)
TUNNELRUINEMANIAC.setEncounterTables(encounter.TUNNELRUINEMANIAC)
RUINESBONVILLE_SALLE7 = Zone("Ruines Bonville - Salle 7", 225, "dungeon/ruinesBonville-19", True, False, True)
RUINESBONVILLE_SALLE7.setEncounterTables(encounter.RUINESBONVILLE)
setConnectingDoors(Door(Position(93,7,TUNNELRUINEMANIAC), Position(713,670,SOUTHEAST)), Door(Position(712,670,SOUTHEAST), Position(92,7,TUNNELRUINEMANIAC)))
setConnectingDoors(Door(Position(1,7,TUNNELRUINEMANIAC), Position(8,3,RUINESBONVILLE_SALLE7)), Door(Position(9,3,RUINESBONVILLE_SALLE7), Position(2,7,TUNNELRUINEMANIAC)))
setConnectingDoors(Door(Position(5,12,RUINESBONVILLE_SALLE7), Position(597,653,NORTHCENTER)), Door(Position(597,652,NORTHCENTER), Position(5,11,RUINESBONVILLE_SALLE7)))

# Mont Couronné
MONTCOURONNE_PASSAGECHARBOURG = Zone("Mont Couronné - Passage Charbourg", 207, "dungeon/montCouronne-1", True, False, True)
MONTCOURONNE_PASSAGECHARBOURG.setEncounterTables(encounter.MONTCOURONNE_PASSAGECHARBOURG)
MONTCOURONNE_SALLE1 = Zone("Mont Couronné - Salle 1", 208, "dungeon/montCouronne-2", True, False, True)
MONTCOURONNE_SALLE1.setEncounterTables(encounter.MONTCOURONNE_SALLE1)
MONTCOURONNE_SALLE2 = Zone("Mont Couronné - Salle 2", 209, "dungeon/montCouronne-3", True, False, True)
MONTCOURONNE_SALLE2.setEncounterTables(encounter.MONTCOURONNE_SALLE2)
MONTCOURONNE_EXTERIEUR1 = Zone("Mont Couronné - Extérieur 1", 211, "dungeon/montCouronne-4", False, True, False)
MONTCOURONNE_EXTERIEUR1.setEncounterTables(encounter.MONTCOURONNE_EXTERIEUR)
MONTCOURONNE_EXTERIEUR2 = Zone("Mont Couronné - Extérieur 2", 210, "dungeon/montCouronne-6", False, True, False)
MONTCOURONNE_EXTERIEUR2.setEncounterTables(encounter.MONTCOURONNE_EXTERIEUR)
MONTCOURONNE_SALLE3 = Zone("Mont Couronné - Salle 3", 212, "dungeon/montCouronne-5", True, False, True)
MONTCOURONNE_SALLE3.setEncounterTables(encounter.MONTCOURONNE_SALLE3)
MONTCOURONNE_SALLE4 = Zone("Mont Couronné - Salle 4", 213, "dungeon/montCouronne-7", True, False, True)
MONTCOURONNE_SALLE4.setEncounterTables(encounter.MONTCOURONNE_SALLE4)
MONTCOURONNE_SALLE5 = Zone("Mont Couronné - Salle 5", 214, "dungeon/montCouronne-8", True, False, True)
MONTCOURONNE_SALLE5.setEncounterTables(encounter.MONTCOURONNE_SALLE5)
MONTCOURONNE_SALLE6 = Zone("Mont Couronné - Salle 6", 215, "dungeon/montCouronne-9", True, False, True)
MONTCOURONNE_SALLE6.setEncounterTables(encounter.MONTCOURONNE_SALLE6)
MONTCOURONNE_SALLE7 = Zone("Mont Couronné - Salle 7", 216, "dungeon/montCouronne-10", True, False, True)
MONTCOURONNE_SALLE7.setEncounterTables(encounter.MONTCOURONNE_SALLE7)
MONTCOURONNE_PASSAGEVESTIGION = Zone("Mont Couronné - Passage Vestigion", 218, "dungeon/montCouronne-11", True, False, True)
MONTCOURONNE_PASSAGEVESTIGION.setEncounterTables(encounter.MONTCOURONNE_PASSAGEVESTIGION)
MONTCOURONNE_SALLE8 = Zone("Mont Couronné - Salle 8", 219, "dungeon/montCouronne-12", True, False, True)
MONTCOURONNE_SALLE8.setEncounterTables(encounter.MONTCOURONNE_SALLE8)
MONTCOURONNE_PASSAGEFRIMAPIC = Zone("Mont Couronné - Passage Frimapic", 217, "dungeon/montCouronne-13", True, False, True)
MONTCOURONNE_PASSAGEFRIMAPIC.setEncounterTables(encounter.MONTCOURONNE_PASSAGEFRIMAPIC)
MONTCOURONNE_GROTTEREGICE = Zone("Mont Couronné - Grotte Regice", 589, "dungeon/grotteRegi", True, False, True)
SALLEORIGINELLE = Zone("Salle Originelle", 510, "dungeon/salleOriginelle", False, False, False)
COLONNESLANCES = Zone("Colonnes Lances", 584, "dungeon/colonnesLances", False, False, False)
COLONNESLANCES.addDoor(Door(Position(31,52,COLONNESLANCES), Position(31,52,SALLEORIGINELLE)))
SALLEORIGINELLE.addDoor(Door(Position(31,54,SALLEORIGINELLE), Position(7,6,MONTCOURONNE_SALLE6)))
setConnectingDoors(Door(Position(3,8,MONTCOURONNE_PASSAGECHARBOURG), Position(341,712,SOUTHCENTER)), Door(Position(342,712,SOUTHCENTER), Position(4,8,MONTCOURONNE_PASSAGECHARBOURG)))
setConnectingDoors(Door(Position(28,20,MONTCOURONNE_PASSAGECHARBOURG), Position(392,724,ROUTE208)), Door(Position(391,724,ROUTE208), Position(27,20,MONTCOURONNE_PASSAGECHARBOURG)))
setConnectingDoors(Door(Position(26,3,MONTCOURONNE_PASSAGECHARBOURG), Position(27,48,MONTCOURONNE_SALLE1)), Door(Position(26,48,MONTCOURONNE_SALLE1), Position(25,3,MONTCOURONNE_PASSAGECHARBOURG)))
setConnectingDoors(Door(Position(1,59,MONTCOURONNE_SALLE1), Position(348,717,SOUTHCENTER)), Door(Position(349,717,SOUTHCENTER), Position(2,59,MONTCOURONNE_SALLE1)))
setConnectingDoors(Door(Position(7,23,MONTCOURONNE_SALLE1), Position(7,12,MONTCOURONNE_SALLE1)), Door(Position(7,13,MONTCOURONNE_SALLE1), Position(7,24,MONTCOURONNE_SALLE1)))
setConnectingDoors(Door(Position(12,4,MONTCOURONNE_SALLE1), Position(14,26,MONTCOURONNE_SALLE2)), Door(Position(13,26,MONTCOURONNE_SALLE2), Position(11,4,MONTCOURONNE_SALLE1)))
setConnectingDoors(Door(Position(20,4,MONTCOURONNE_SALLE1), Position(18,26,MONTCOURONNE_SALLE2)), Door(Position(19,26,MONTCOURONNE_SALLE2), Position(21,4,MONTCOURONNE_SALLE1)))
setConnectingDoors(Door(Position(3,30,MONTCOURONNE_SALLE2), Position(12,36,MONTCOURONNE_EXTERIEUR1)), Door(Position(12,35,MONTCOURONNE_EXTERIEUR1), Position(3,29,MONTCOURONNE_SALLE2)))
setConnectingDoors(Door(Position(39,18,MONTCOURONNE_EXTERIEUR1), Position(35,24,MONTCOURONNE_SALLE3)), Door(Position(35,25,MONTCOURONNE_SALLE3), Position(39,19,MONTCOURONNE_EXTERIEUR1)))
setConnectingDoors(Door(Position(11,17,MONTCOURONNE_EXTERIEUR1), Position(7,25,MONTCOURONNE_SALLE3)), Door(Position(7,26,MONTCOURONNE_SALLE3), Position(11,18,MONTCOURONNE_EXTERIEUR1)))
setConnectingDoors(Door(Position(17,6,MONTCOURONNE_SALLE3), Position(59,6,MONTCOURONNE_SALLE3)), Door(Position(59,7,MONTCOURONNE_SALLE3), Position(17,7,MONTCOURONNE_SALLE3)))
setConnectingDoors(Door(Position(41,10,MONTCOURONNE_SALLE3), Position(42,40,MONTCOURONNE_EXTERIEUR2)), Door(Position(41,40,MONTCOURONNE_EXTERIEUR2), Position(40,10,MONTCOURONNE_SALLE3)))
setConnectingDoors(Door(Position(46,28,MONTCOURONNE_EXTERIEUR2), Position(2,58,MONTCOURONNE_SALLE7)), Door(Position(1,58,MONTCOURONNE_SALLE7), Position(45,28,MONTCOURONNE_EXTERIEUR2)))
setConnectingDoors(Door(Position(14,19,MONTCOURONNE_EXTERIEUR2), Position(2,3,MONTCOURONNE_SALLE4)), Door(Position(1,3,MONTCOURONNE_SALLE4), Position(13,19,MONTCOURONNE_EXTERIEUR2)))
setConnectingDoors(Door(Position(19,8,MONTCOURONNE_SALLE4), Position(21,7,MONTCOURONNE_SALLE5)), Door(Position(20,7,MONTCOURONNE_SALLE5), Position(18,8,MONTCOURONNE_SALLE4)))
setConnectingDoors(Door(Position(12,24,MONTCOURONNE_SALLE5), Position(10,24,MONTCOURONNE_SALLE6)), Door(Position(11,24,MONTCOURONNE_SALLE6), Position(13,24,MONTCOURONNE_SALLE5)))
setConnectingDoors(Door(Position(7,5,MONTCOURONNE_SALLE6), Position(31,53,COLONNESLANCES)), Door(Position(31,54,COLONNESLANCES), Position(7,6,MONTCOURONNE_SALLE6)))
setConnectingDoors(Door(Position(21,62,MONTCOURONNE_PASSAGEVESTIGION), Position(16,14,MONTCOURONNE_SALLE7)), Door(Position(16,13,MONTCOURONNE_SALLE7), Position(21,61,MONTCOURONNE_PASSAGEVESTIGION)))
setConnectingDoors(Door(Position(1,41,MONTCOURONNE_PASSAGEVESTIGION), Position(380,532,NORTHWEST)), Door(Position(381,532,NORTHWEST), Position(2,41,MONTCOURONNE_PASSAGEVESTIGION)))
setConnectingDoors(Door(Position(30,35,MONTCOURONNE_PASSAGEVESTIGION), Position(419,527,NORTHCENTER)), Door(Position(418,527,NORTHCENTER), Position(29,35,MONTCOURONNE_PASSAGEVESTIGION)))
setConnectingDoors(Door(Position(10,10,MONTCOURONNE_PASSAGEVESTIGION), Position(8,60,MONTCOURONNE_SALLE8)), Door(Position(9,60,MONTCOURONNE_SALLE8), Position(11,10,MONTCOURONNE_PASSAGEVESTIGION)))
setConnectingDoors(Door(Position(9,27,MONTCOURONNE_PASSAGEFRIMAPIC), Position(8,3,MONTCOURONNE_SALLE8)), Door(Position(9,3,MONTCOURONNE_SALLE8), Position(10,27,MONTCOURONNE_PASSAGEFRIMAPIC)))
setConnectingDoors(Door(Position(15,16,MONTCOURONNE_PASSAGEFRIMAPIC), Position(7,12,MONTCOURONNE_GROTTEREGICE)), Door(Position(7,13,MONTCOURONNE_GROTTEREGICE), Position(15,17,MONTCOURONNE_PASSAGEFRIMAPIC)))
setConnectingDoors(Door(Position(1,18,MONTCOURONNE_PASSAGEFRIMAPIC), Position(375,403,NORTH)), Door(Position(376,403,NORTH), Position(2,18,MONTCOURONNE_PASSAGEFRIMAPIC)))

# Hôtel Grand Lac
HOTELGRANDLAC = Zone("Hôtel Grand Lac", 376, "route/hotelGrandLac", False, False, False)
setConnectingDoors(Door(Position(706,814,SOUTHEAST), Position(8,3,HOTELGRANDLAC)), Door(Position(8,2,HOTELGRANDLAC), Position(706,813,SOUTHEAST)))
setConnectingDoors(Door(Position(706,818,ROUTE213_EST), Position(8,11,HOTELGRANDLAC)), Door(Position(8,12,HOTELGRANDLAC), Position(706,819,ROUTE213_EST)))

# Manoir Pokémon
MANOIRPOKEMON = Zone("Manoir Pokémon", 368, "route/manoirPokemon-1", False, False, False)
MANOIRPOKEMON_BUREAU = Zone("Manoir Pokémon - Bureau Décorum", 370, "route/manoirPokemon-2", False, False, False)
JARDINTROPHEE = Zone("Jardin Trophée", 287, "route/jardinTrophee", True, True, False)
JARDINTROPHEE.setEncounterTables(encounter.JARDINTROPHEE)
setConnectingDoors(Door(Position(33,17,MANOIRPOKEMON), Position(470,773,SOUTH)), Door(Position(470,772,SOUTH), Position(33,16,MANOIRPOKEMON)))
setConnectingDoors(Door(Position(48,5,MANOIRPOKEMON), Position(16,10,MANOIRPOKEMON_BUREAU)), Door(Position(16,11,MANOIRPOKEMON_BUREAU), Position(48,6,MANOIRPOKEMON)))
setConnectingDoors(Door(Position(33,2,MANOIRPOKEMON), Position(14,25,JARDINTROPHEE)), Door(Position(14,26,JARDINTROPHEE), Position(33,3,MANOIRPOKEMON)))

# Grand Marais
VERCHAMPS_OBSERVATOIRE = Zone("Observatoire", 125, "city/verchamps-observatoire-1", False, False, False)
VERCHAMPS_OBSERVATOIRE_ETAGE1 = Zone("Observatoire - Étage 1", 126, "city/verchamps-observatoire-2", False, False, False)
GRANDMARAIS = Zone("Grand Marais", GRANDMARAIS_ID, "route/grandMarais", True, False, False)
GRANDMARAIS_PARC1 = SubZone("Grand Marais - Parc 1", 504, (32,32), (63,63))
GRANDMARAIS_PARC1.setEncounterTables(encounter.GRANDMARAIS_PARC1)
GRANDMARAIS_PARC2 = SubZone("Grand Marais - Parc 2", 505, (64,32), (95,63))
GRANDMARAIS_PARC2.setEncounterTables(encounter.GRANDMARAIS_PARC2)
GRANDMARAIS_PARC3 = SubZone("Grand Marais - Parc 3", 506, (32,64), (63,95))
GRANDMARAIS_PARC3.setEncounterTables(encounter.GRANDMARAIS_PARC3)
GRANDMARAIS_PARC4 = SubZone("Grand Marais - Parc 4", 507, (64,64), (95,95))
GRANDMARAIS_PARC4.setEncounterTables(encounter.GRANDMARAIS_PARC4)
GRANDMARAIS_PARC5 = SubZone("Grand Marais - Parc 5", 508, (32,96), (63,127))
GRANDMARAIS_PARC5.setEncounterTables(encounter.GRANDMARAIS_PARC5)
GRANDMARAIS_PARC6 = SubZone("Grand Marais - Parc 6", 509, (64,96), (95,127))
GRANDMARAIS_PARC6.setEncounterTables(encounter.GRANDMARAIS_PARC6)
GRANDMARAIS.setSubZones(GRANDMARAIS_PARC1, GRANDMARAIS_PARC2, GRANDMARAIS_PARC3, GRANDMARAIS_PARC4, GRANDMARAIS_PARC5, GRANDMARAIS_PARC6)
setConnectingDoors(Door(Position(5,2,VERCHAMPS_OBSERVATOIRE), Position(68,116,GRANDMARAIS)), Door(Position(68,119,GRANDMARAIS), Position(5,3,VERCHAMPS_OBSERVATOIRE)))
setConnectingDoors(Door(Position(9,8,VERCHAMPS_OBSERVATOIRE), Position(7,8,VERCHAMPS_OBSERVATOIRE_ETAGE1)), Door(Position(8,8,VERCHAMPS_OBSERVATOIRE_ETAGE1), Position(10,8,VERCHAMPS_OBSERVATOIRE)))
setConnectingDoors(Door(Position(5,12,VERCHAMPS_OBSERVATOIRE), Position(610,810,SOUTH)), Door(Position(610,809,SOUTH), Position(5,11,VERCHAMPS_OBSERVATOIRE)))

# Ile de Fer
ILEDEFER = Zone("Ile de Fer", 288, "dungeon/ileDeFer-1", True, True, False)
ILEDEFER.setEncounterTables(encounter.ILEDEFER)
ILEDEFER_REZDECHAUSSEE = Zone("Ile de Fer - Rez-de-Chaussée", 289, "dungeon/ileDeFer-2", True, False, True)
ILEDEFER_REZDECHAUSSEE.setEncounterTables(encounter.ILEDEFER_REZDECHAUSSEE)
ILEDEFER_SOUSSOL1OUEST = Zone("Ile de Fer - Sous-Sol 1 Ouest", 290, "dungeon/ileDeFer-3", True, False, True)
ILEDEFER_SOUSSOL1OUEST.setEncounterTables(encounter.ILEDEFER_SOUSSOL1)
ILEDEFER_SOUSSOL1EST = Zone("Ile de Fer - Sous-Sol 1 Est", 291, "dungeon/ileDeFer-4", True, False, True)
ILEDEFER_SOUSSOL1EST.setEncounterTables(encounter.ILEDEFER_SOUSSOL1)
ILEDEFER_SOUSSOL2EST = Zone("Ile de Fer - Sous-Sol 2 Est", 292, "dungeon/ileDeFer-5", True, False, True)
ILEDEFER_SOUSSOL2EST.setEncounterTables(encounter.ILEDEFER_SOUSSOL2)
ILEDEFER_SOUSSOL2OUEST = Zone("Ile de Fer - Sous-Sol 2 Ouest", 293, "dungeon/ileDeFer-6", True, False, True)
ILEDEFER_SOUSSOL2OUEST.setEncounterTables(encounter.ILEDEFER_SOUSSOL2)
ILEDEFER_GROTTEREGISTEEL = Zone("Ile de Fer - Grotte Registeel", 587, "dungeon/grotteRegi", True, False, True)
ILEDEFER_SORTIE = Zone("Ile de Fer - Sortie", 294, "dungeon/ileDeFer-7", True, False, True)
ILEDEFER_SORTIE.setEncounterTables(encounter.ILEDEFER_SORTIE)
setConnectingDoors(Door(Position(117,489,ILEDEFER), Position(6,8,ILEDEFER_REZDECHAUSSEE)), Door(Position(6,9,ILEDEFER_REZDECHAUSSEE), Position(117,490,ILEDEFER)))
setConnectingDoors(Door(Position(104,489,ILEDEFER), Position(2,5,ILEDEFER_SORTIE)), Door(Position(1,5,ILEDEFER_SORTIE), Position(103,489,ILEDEFER)))
setConnectingDoors(Door(Position(3,3,ILEDEFER_REZDECHAUSSEE), Position(15,3,ILEDEFER_SOUSSOL1OUEST)), Door(Position(16,3,ILEDEFER_SOUSSOL1OUEST), Position(4,3,ILEDEFER_REZDECHAUSSEE)))
setConnectingDoors(Door(Position(9,3,ILEDEFER_REZDECHAUSSEE), Position(2,3,ILEDEFER_SOUSSOL1EST)), Door(Position(1,3,ILEDEFER_SOUSSOL1EST), Position(8,3,ILEDEFER_REZDECHAUSSEE)))
setConnectingDoors(Door(Position(17,26,ILEDEFER_SOUSSOL1EST), Position(2,3,ILEDEFER_SOUSSOL2EST)), Door(Position(1,3,ILEDEFER_SOUSSOL2EST), Position(16,26,ILEDEFER_SOUSSOL1EST)))
setConnectingDoors(Door(Position(5,26,ILEDEFER_SOUSSOL1EST), Position(38,3,ILEDEFER_SOUSSOL2OUEST)), Door(Position(39,3,ILEDEFER_SOUSSOL2OUEST), Position(6,26,ILEDEFER_SOUSSOL1EST)))
setConnectingDoors(Door(Position(13,48,ILEDEFER_SOUSSOL2OUEST), Position(14,15,ILEDEFER_SORTIE)), Door(Position(15,15,ILEDEFER_SORTIE), Position(14,48,ILEDEFER_SOUSSOL2OUEST)))
setConnectingDoors(Door(Position(14,1,ILEDEFER_SORTIE), Position(7,12,ILEDEFER_GROTTEREGISTEEL)), Door(Position(7,13,ILEDEFER_GROTTEREGISTEEL), Position(14,2,ILEDEFER_SORTIE)))

# Temple Frimapic
TEMPLEFRIMAPIC_ENTREE = Zone("Temple Frimapic - Entrée", 278, "dungeon/templeFrimapic-1", True, False, True)
TEMPLEFRIMAPIC_ENTREE.setEncounterTables(encounter.TEMPLEFRIMAPIC_ENTREE)
TEMPLEFRIMAPIC_SOUSSOL1 = Zone("Temple Frimapic - Sous-Sol 1", 279, "dungeon/templeFrimapic-2", True, False, True)
TEMPLEFRIMAPIC_SOUSSOL1.setEncounterTables(encounter.TEMPLEFRIMAPIC_SOUSSOL1)
TEMPLEFRIMAPIC_SOUSSOL2 = Zone("Temple Frimapic - Sous-Sol 2", 280, "dungeon/templeFrimapic-3", True, False, True)
TEMPLEFRIMAPIC_SOUSSOL2.setEncounterTables(encounter.TEMPLEFRIMAPIC_SOUSSOL23)
TEMPLEFRIMAPIC_SOUSSOL3 = Zone("Temple Frimapic - Sous-Sol 3", 281, "dungeon/templeFrimapic-4", True, False, True)
TEMPLEFRIMAPIC_SOUSSOL3.setEncounterTables(encounter.TEMPLEFRIMAPIC_SOUSSOL23)
TEMPLEFRIMAPIC_SOUSSOL4 = Zone("Temple Frimapic - Sous-Sol 4", 282, "dungeon/templeFrimapic-5", True, False, True)
TEMPLEFRIMAPIC_SOUSSOL4.setEncounterTables(encounter.TEMPLEFRIMAPIC_SOUSSOL45)
TEMPLEFRIMAPIC_SALLEREGIGIGAS = Zone("Temple Frimapic - Salle Regigias", 283, "dungeon/templeFrimapic-6", True, False, True)
TEMPLEFRIMAPIC_SALLEREGIGIGAS.setEncounterTables(encounter.TEMPLEFRIMAPIC_SOUSSOL45)
setConnectingDoors(Door(Position(8,14,TEMPLEFRIMAPIC_ENTREE), Position(366,198,NORTH)), Door(Position(366,197,NORTH), Position(8,13,TEMPLEFRIMAPIC_ENTREE)))
setConnectingDoors(Door(Position(13,3,TEMPLEFRIMAPIC_ENTREE), Position(4,3,TEMPLEFRIMAPIC_SOUSSOL1)), Door(Position(5,3,TEMPLEFRIMAPIC_SOUSSOL1), Position(14,3,TEMPLEFRIMAPIC_ENTREE)))
setConnectingDoors(Door(Position(13,3,TEMPLEFRIMAPIC_SOUSSOL1), Position(6,3,TEMPLEFRIMAPIC_SOUSSOL2)), Door(Position(7,3,TEMPLEFRIMAPIC_SOUSSOL2), Position(14,3,TEMPLEFRIMAPIC_SOUSSOL1)))
setConnectingDoors(Door(Position(13,3,TEMPLEFRIMAPIC_SOUSSOL2), Position(6,3,TEMPLEFRIMAPIC_SOUSSOL3)), Door(Position(7,3,TEMPLEFRIMAPIC_SOUSSOL3), Position(14,3,TEMPLEFRIMAPIC_SOUSSOL2)))
setConnectingDoors(Door(Position(13,3,TEMPLEFRIMAPIC_SOUSSOL3), Position(6,3,TEMPLEFRIMAPIC_SOUSSOL4)), Door(Position(7,3,TEMPLEFRIMAPIC_SOUSSOL4), Position(14,3,TEMPLEFRIMAPIC_SOUSSOL3)))
setConnectingDoors(Door(Position(13,3,TEMPLEFRIMAPIC_SOUSSOL4), Position(8,3,TEMPLEFRIMAPIC_SALLEREGIGIGAS)), Door(Position(9,3,TEMPLEFRIMAPIC_SALLEREGIGIGAS), Position(14,3,TEMPLEFRIMAPIC_SOUSSOL4)))

# Route Victoire
ROUTEVICTOIRE = Zone("Route Victoire", 244, "dungeon/routeVictoire-1", True, False, True)
ROUTEVICTOIRE.setEncounterTables(encounter.ROUTEVICTOIRE)
ROUTEVICTOIRE_SALLEOUEST = Zone("Route Victoire - Salle Ouest", 245, "dungeon/routeVictoire-2", True, False, True)
ROUTEVICTOIRE_SALLEOUEST.setEncounterTables(encounter.ROUTEVICTOIRE_SALLEOUEST)
ROUTEVICTOIRE_SALLEEST = Zone("Route Victoire - Salle Est", 246, "dungeon/routeVictoire-3", True, False, True)
ROUTEVICTOIRE_SALLEEST.setEncounterTables(encounter.ROUTEVICTOIRE_SALLEEST)
ROUTEVICTOIRE_SALLEBRUME = Zone("Route Victoire - Salle Brume", 247, "dungeon/routeVictoire-5", True, False, True)
ROUTEVICTOIRE_SALLEBRUME.setEncounterTables(encounter.ROUTEVICTOIRE_SALLEBRUME)
ROUTEVICTOIRE_PASSAGEEST = Zone("Route Victoire - Passage Est", 248, "dungeon/routeVictoire-4", True, False, True)
ROUTEVICTOIRE_PASSAGEEST.setEncounterTables(encounter.ROUTEVICTOIRE_PASSAGEEST)
ROUTEVICTOIRE_PASSAGEROUTE224 = Zone("Route Victoire - Passage Route 224", 249, "dungeon/routeVictoire-6", True, False, True)
ROUTEVICTOIRE_PASSAGEROUTE224.setEncounterTables(encounter.ROUTEVICTOIRE_PASSAGEROUTE224)
PASSAGEMARIN = SubZone("Passage Marin", 472, (896,224), (927,479))
PARADISFLEURI = SubZone("Paradis Fleuri", 274, (896,192), (927,223))
setConnectingDoors(Door(Position(15,79,ROUTEVICTOIRE), Position(851,598,EAST)), Door(Position(851,597,EAST), Position(15,78,ROUTEVICTOIRE)))
setConnectingDoors(Door(Position(33,5,ROUTEVICTOIRE), Position(853,582,LIGUEPOKEMON)), Door(Position(854,582,LIGUEPOKEMON), Position(34,5,ROUTEVICTOIRE)))
setConnectingDoors(Door(Position(3,37,ROUTEVICTOIRE), Position(20,16,ROUTEVICTOIRE_SALLEOUEST)), Door(Position(21,16,ROUTEVICTOIRE_SALLEOUEST), Position(4,37,ROUTEVICTOIRE)))
setConnectingDoors(Door(Position(6,47,ROUTEVICTOIRE), Position(23,26,ROUTEVICTOIRE_SALLEOUEST)), Door(Position(24,26,ROUTEVICTOIRE_SALLEOUEST), Position(7,47,ROUTEVICTOIRE)))
setConnectingDoors(Door(Position(3,25,ROUTEVICTOIRE), Position(20,4,ROUTEVICTOIRE_SALLEOUEST)), Door(Position(21,4,ROUTEVICTOIRE_SALLEOUEST), Position(4,25,ROUTEVICTOIRE)))
setConnectingDoors(Door(Position(43,41,ROUTEVICTOIRE), Position(4,39,ROUTEVICTOIRE_SALLEEST)), Door(Position(3,39,ROUTEVICTOIRE_SALLEEST), Position(42,41,ROUTEVICTOIRE)))
setConnectingDoors(Door(Position(45,48,ROUTEVICTOIRE), Position(6,46,ROUTEVICTOIRE_SALLEEST)), Door(Position(5,46,ROUTEVICTOIRE_SALLEEST), Position(44,48,ROUTEVICTOIRE)))
setConnectingDoors(Door(Position(42,24,ROUTEVICTOIRE), Position(3,22,ROUTEVICTOIRE_SALLEEST)), Door(Position(2,22,ROUTEVICTOIRE_SALLEEST), Position(41,24,ROUTEVICTOIRE)))
setConnectingDoors(Door(Position(46,33,ROUTEVICTOIRE), Position(5,20,ROUTEVICTOIRE_PASSAGEEST)), Door(Position(4,20,ROUTEVICTOIRE_PASSAGEEST), Position(45,33,ROUTEVICTOIRE)))
setConnectingDoors(Door(Position(2,58,ROUTEVICTOIRE_SALLEBRUME), Position(21,10,ROUTEVICTOIRE_PASSAGEEST)), Door(Position(22,10,ROUTEVICTOIRE_PASSAGEEST), Position(3,58,ROUTEVICTOIRE_SALLEBRUME)))
setConnectingDoors(Door(Position(57,13,ROUTEVICTOIRE_SALLEBRUME), Position(12,16,ROUTEVICTOIRE_PASSAGEROUTE224)), Door(Position(11,16,ROUTEVICTOIRE_PASSAGEROUTE224), Position(56,13,ROUTEVICTOIRE_SALLEBRUME)))
setConnectingDoors(Door(Position(877,560,NORTHEAST), Position(29,16,ROUTEVICTOIRE_PASSAGEROUTE224)), Door(Position(30,16,ROUTEVICTOIRE_PASSAGEROUTE224), Position(878,560,NORTHEAST)))

# Grotte Retour
CHEMINSOURCE = SubZone("Chemin Source", 341, (736,672), (799,735))
SOURCEADIEU = Zone("Source Adieu", 267, "dungeon/sourceAdieu", True, True, False)
SOURCEADIEU.setEncounterTables(encounter.SOURCEADIEU)
GROTTERETOUR_ENTREE = Zone("Grotte Retour - Entrée", 268, "dungeon/grotteRetour-entree", True, False, False)
GROTTERETOUR_SALLEPILIER = Zone("Grotte Retour - Salle Pilier", 269, "dungeon/grotteRetour-pilier", True, False, False)
GROTTERETOUR_SALLEGIRATINA = Zone("Grotte Retour - Salle Giratina", 270, "dungeon/grotteRetour-giratina", True, False, False)
GROTTERETOUR_SALLE1 = Zone("Grotte Retour - Salle 1", 518, "dungeon/grotteRetour-1", True, False, False)
GROTTERETOUR_SALLE2 = Zone("Grotte Retour - Salle 2", 519, "dungeon/grotteRetour-2", True, False, False)
GROTTERETOUR_SALLE3 = Zone("Grotte Retour - Salle 3", 520, "dungeon/grotteRetour-3", True, False, False)
GROTTERETOUR_SALLE4 = Zone("Grotte Retour - Salle 4", 521, "dungeon/grotteRetour-4", True, False, False)
GROTTERETOUR_SALLE5 = Zone("Grotte Retour - Salle 5", 522, "dungeon/grotteRetour-5", True, False, False)
GROTTERETOUR_SALLE6 = Zone("Grotte Retour - Salle 6", 523, "dungeon/grotteRetour-6", True, False, False)
GROTTERETOUR_SALLE6 = Zone("Grotte Retour - Salle 7", 524, "dungeon/grotteRetour-7", True, False, False)
GROTTERETOUR_SALLE8 = Zone("Grotte Retour - Salle 8", 525, "dungeon/grotteRetour-8", True, False, False)
GROTTERETOUR_SALLE9 = Zone("Grotte Retour - Salle 9", 526, "dungeon/grotteRetour-9", True, False, False)
GROTTERETOUR_SALLE10 = Zone("Grotte Retour - Salle 10", 527, "dungeon/grotteRetour-10", True, False, False)
GROTTERETOUR_SALLE11 = Zone("Grotte Retour - Salle 11", 528, "dungeon/grotteRetour-11", True, False, False)
GROTTERETOUR_SALLE12 = Zone("Grotte Retour - Salle 12", 529, "dungeon/grotteRetour-12", True, False, False)
GROTTERETOUR_SALLE13 = Zone("Grotte Retour - Salle 13", 530, "dungeon/grotteRetour-13", True, False, False)
GROTTERETOUR_SALLE14 = Zone("Grotte Retour - Salle 14", 531, "dungeon/grotteRetour-14", True, False, False)
GROTTERETOUR_SALLE15 = Zone("Grotte Retour - Salle 15", 532, "dungeon/grotteRetour-15", True, False, False)
GROTTERETOUR_SALLE41 = Zone("Grotte Retour - Salle 41", 271, "dungeon/grotteRetour-41", True, False, False)
GROTTERETOUR_SALLE42 = Zone("Grotte Retour - Salle 42", 272, "dungeon/grotteRetour-42", True, False, False)
GROTTERETOUR_SALLE43 = Zone("Grotte Retour - Salle 43", 273, "dungeon/grotteRetour-43", True, False, False)
setConnectingDoors(Door(Position(12,57,SOURCEADIEU), Position(762,714,SOUTHEAST)), Door(Position(762,713,SOUTHEAST), Position(12,56,SOURCEADIEU)))
setConnectingDoors(Door(Position(31,16,SOURCEADIEU), Position(11,16,GROTTERETOUR_ENTREE)), Door(Position(11,17,GROTTERETOUR_ENTREE), Position(31,17,SOURCEADIEU)))

# Mont Abrupt
MONTABRUPT_EXTERIEUR = SubZone("Mont Abrupt - Extérieur", 262, (736,224), (767,255))
MONTABRUPT_EXTERIEUR.setEncounterTables(encounter.MONTABRUPT_EXTERIEUR)
MONTABRUPT_SALLE1 = Zone("Mont Abrupt - Salle 1", 263, "dungeon/montAbrupt-1", True, False, True)
MONTABRUPT_SALLE1.setEncounterTables(encounter.MONTABRUPT_SALLE1)
MONTABRUPT_SALLE2 = Zone("Mont Abrupt - Salle 2", 264, "dungeon/montAbrupt-2", True, False, True)
MONTABRUPT_SALLE2.setEncounterTables(encounter.MONTABRUPT_SALLE2)
MONTABRUPT_SALLEHEATRAN = Zone("Mont Abrupt - Salle Heatran", 265, "dungeon/montAbrupt-3", True, False, False)
setConnectingDoors(Door(Position(20,30,MONTABRUPT_SALLE1), Position(750,232,SECTEURCOMBAT_NORTHWEST)), Door(Position(750,231,SECTEURCOMBAT_NORTHWEST), Position(20,29,MONTABRUPT_SALLE1)))
setConnectingDoors(Door(Position(17,2,MONTABRUPT_SALLE1), Position(42,86,MONTABRUPT_SALLE2)), Door(Position(42,87,MONTABRUPT_SALLE2), Position(17,3,MONTABRUPT_SALLE1)))
setConnectingDoors(Door(Position(47,2,MONTABRUPT_SALLE2), Position(7,17,MONTABRUPT_SALLEHEATRAN)), Door(Position(7,18,MONTABRUPT_SALLEHEATRAN), Position(47,3,MONTABRUPT_SALLE2)))

# Lac Vérité
LACVERITE = Zone("Lac Vérité", 312, "dungeon/lacVérité", True, True, False)
LACVERITE.setEncounterTables(encounter.LACVERITE)
LACVERITE_CAVERNEVERITE = Zone("Lac Vérité - Caverne Vérité", 313, "dungeon/caverneVerite", True, False, False)
RIVELACVERITE = SubZone("Rive Lac Vérité", 334, (32,800), (95,863))
setConnectingDoors(Door(Position(46,55,LACVERITE), Position(80,844,SOUTHWEST)), Door(Position(80,843,SOUTHWEST), Position(46,54,LACVERITE)))
setConnectingDoors(Door(Position(32,32,LACVERITE), Position(14,29,LACVERITE_CAVERNEVERITE)), Door(Position(14,30,LACVERITE_CAVERNEVERITE), Position(32,33,LACVERITE)))

# Lac Courage
LACCOURAGE = Zone("Lac Courage", 315, "dungeon/lacCourage", True, True, False)
LACCOURAGE.setEncounterTables(encounter.LACCOURAGE)
LACCOURAGE_CAVERNECOURAGE = Zone("Lac Courage - Caverne Courage", 316, "dungeon/caverneCourage", True, False, False)
RIVELACCOURAGE = SubZone("Rive Lac Courage", 336, (672,736), (735,799))
RIVELACCOURAGE.setEncounterTables(encounter.RIVELACCOURAGE)
setConnectingDoors(Door(Position(53,10,LACCOURAGE), Position(717,760,SOUTHEAST)), Door(Position(716,760,SOUTHEAST), Position(52,10,LACCOURAGE)))
setConnectingDoors(Door(Position(32,32,LACCOURAGE), Position(14,29,LACCOURAGE_CAVERNECOURAGE)), Door(Position(14,30,LACCOURAGE_CAVERNECOURAGE), Position(32,33,LACCOURAGE)))

# Lac Savoir
LACSAVOIR = Zone("Lac Savoir", 318, "dungeon/lacSavoir", False, True, False)
LACSAVOIR.setEncounterTables(encounter.LACSAVOIR)
LACSAVOIR_CAVERNESAVOIR = Zone("Lac Savoir - Caverne Savoir", 319, "dungeon/caverneSavoir", True, False, False)
RIVELACSAVOIR = SubZone("Rive Lac Savoir", 340, (288,192), (351,255))
RIVELACSAVOIR.setEncounterTables(encounter.RIVELACSAVOIR)
setConnectingDoors(Door(Position(14,51,LACSAVOIR), Position(308,230,NORTH)), Door(Position(308,229,NORTH), Position(14,50,LACSAVOIR)))
setConnectingDoors(Door(Position(32,32,LACSAVOIR), Position(14,29,LACSAVOIR_CAVERNESAVOIR)), Door(Position(14,30,LACSAVOIR_CAVERNESAVOIR), Position(32,33,LACSAVOIR)))

# Grottes Légendaires
ROUTE228_GROTTEREGIROCK = Zone("Route 228 - Grotte Regirock", 591, "dungeon/grotteRegi", True, False, True)
setConnectingDoors(Door(Position(785,340,SECTEURCOMBAT_SOUTHEAST), Position(7,12,ROUTE228_GROTTEREGIROCK)), Door(Position(7,13,ROUTE228_GROTTEREGIROCK), Position(785,341,SECTEURCOMBAT_SOUTHEAST)))

# Ile Nouvellune
ILENOUVELLUNE = Zone("Ile Nouvellune", 320, "dungeon/ileNouvellune-1", False, False, False)
ILENOUVELLUNE_INTERIEUR = Zone("Ile Nouvellune - Intérieur", 321, "dungeon/ileNouvellune-2", False, False, False)
setConnectingDoors(Door(Position(137,268,ILENOUVELLUNE), Position(16,21,ILENOUVELLUNE_INTERIEUR)), Door(Position(16,22,ILENOUVELLUNE_INTERIEUR), Position(137,269,ILENOUVELLUNE)))

# Ile Pleine Lune
ILEPLEINELUNE = Zone("Ile Pleine Lune", 260, "dungeon/ilePleineLune-1", False, False, False)
ILEPLEINELUNE_INTERIEUR = Zone("Ile Pleine Lune - Intérieur", 261, "dungeon/ilePleineLune-2", False, False, False)
setConnectingDoors(Door(Position(53,268,ILEPLEINELUNE), Position(16,21,ILEPLEINELUNE_INTERIEUR)), Door(Position(16,22,ILEPLEINELUNE_INTERIEUR), Position(53,269,ILEPLEINELUNE)))

# Houses (just for anchor zones)
RESTAURANTSEPTETOILES = Zone("Restaurant 7 Étoiles", 337, "route/restaurantSeptEtoiles", False, False, False)
CAFECABANE = Zone("Café Cabane", 492, "route/cafeCabane", False, False, False)
ROUTE210_MAISON = Zone("Route 210 - Maison", 364, "route/route210-maison", False, False, False)
ROUTE212_MAISON = Zone("Route 212 - Maison", 372, "route/route212-maison", False, False, False)
ROUTE216_MAISON = Zone("Route 216 - Maison", 384, "route/route216-maison", False, False, False)
ROUTE217_MAISON = Zone("Route 217 - Maison", 386, "route/route217-maison", False, False, False)
ROUTE225_MAISON = Zone("Route 225 - Maison", 498, "route/route226-maison", False, False, False)
ROUTE226_MAISON = Zone("Route 226 - Maison", 499, "route/route226-maison", False, False, False)
ROUTE227_MAISON = Zone("Route 227 - Maison", 500, "route/route227-maison", False, False, False)
ROUTE228_MAISON1 = Zone("Route 227 - Maison 1", 502, "route/route228-maison2", False, False, False)
ROUTE228_MAISON2 = Zone("Route 227 - Maison 2", 503, "route/route228-maison2", False, False, False)
setConnectingDoors(Door(Position(706,790,SOUTHEAST), Position(9,12,RESTAURANTSEPTETOILES)), Door(Position(9,13,RESTAURANTSEPTETOILES), Position(706,791,SOUTHEAST)))
setConnectingDoors(Door(Position(566,591,NORTHCENTER), Position(5,8,CAFECABANE)), Door(Position(5,9,CAFECABANE), Position(566,592,NORTHCENTER)))
setConnectingDoors(Door(Position(564,516,NORTHCENTER), Position(4,8,ROUTE210_MAISON)), Door(Position(4,9,ROUTE210_MAISON), Position(564,517,NORTHCENTER)))
setConnectingDoors(Door(Position(517,846,SOUTH), Position(4,8,ROUTE212_MAISON)), Door(Position(4,9,ROUTE212_MAISON), Position(517,847,SOUTH)))
setConnectingDoors(Door(Position(303,398,NORTH), Position(4,8,ROUTE216_MAISON)), Door(Position(4,9,ROUTE216_MAISON), Position(303,399,NORTH)))
setConnectingDoors(Door(Position(293,311,NORTH), Position(4,8,ROUTE217_MAISON)), Door(Position(4,9,ROUTE217_MAISON), Position(293,312,NORTH)))
setConnectingDoors(Door(Position(617,368,SECTEURCOMBAT_NORTHWEST), Position(4,8,ROUTE225_MAISON)), Door(Position(4,9,ROUTE225_MAISON), Position(617,369,SECTEURCOMBAT_NORTHWEST)))
setConnectingDoors(Door(Position(739,339,SECTEURCOMBAT_NORTHWEST), Position(4,8,ROUTE226_MAISON)), Door(Position(4,9,ROUTE226_MAISON), Position(739,340,SECTEURCOMBAT_NORTHWEST)))
setConnectingDoors(Door(Position(740,302,SECTEURCOMBAT_NORTHWEST), Position(4,8,ROUTE227_MAISON)), Door(Position(4,9,ROUTE227_MAISON), Position(740,303,SECTEURCOMBAT_NORTHWEST)))
setConnectingDoors(Door(Position(789,356,SECTEURCOMBAT_SOUTHEAST), Position(4,8,ROUTE228_MAISON1)), Door(Position(4,9,ROUTE228_MAISON1), Position(789,357,SECTEURCOMBAT_SOUTHEAST)))
setConnectingDoors(Door(Position(775,386,SECTEURCOMBAT_SOUTHEAST), Position(4,8,ROUTE228_MAISON2)), Door(Position(4,9,ROUTE228_MAISON2), Position(775,387,SECTEURCOMBAT_SOUTHEAST)))

# Sub-Zones belonging on Overworld map
EAST.setSubZones(RIVAMAR, LIGUEPOKEMON_EXTERIEUR, ROUTE223)
NORTH.setSubZones(FRIMAPIC, ROUTE216, ROUTE217, RIVELACSAVOIR)
NORTHCENTER.setSubZones(BONVILLE, CELESTIA, ROUTE209, ROUTE210_SUD, ROUTE210_NORD, ROUTE211_EST, ROUTE215)
NORTHEAST.setSubZones(ROUTE224, PASSAGEMARIN, PARADISFLEURI)
NORTHWEST.setSubZones(FLORAVILLE, VESTIGION, ROUTE204_NORD, ROUTE205_SUD, ROUTE205_NORD, ROUTE211_OUEST, LESEOLIENNES, FORETVESTIGION_EXTERIEUR, FORGEFUEGO)
SOUTH.setSubZones(VERCHAMPS, ROUTE212_NORD, ROUTE212_SUD)
SOUTHCENTER.setSubZones(CHARBOURG, ROUTE206, ROUTE207)
SOUTHEAST.setSubZones(ROUTE213_OUEST, ROUTE214, ROUTE222, RIVELACCOURAGE, CHEMINSOURCE)
SOUTHWEST.setSubZones(BONAUGURE, LITTORELLA, FELICITE, ROUTE201, ROUTE202, ROUTE203, ROUTE204_SUD, ROUTE219, ROUTE220, ROUTE221, RIVELACVERITE)
SECTEURCOMBAT_NORTHWEST.setSubZones(AIREDESURVIE, ROUTE228, ROUTE229, ROUTE230, MONTABRUPT_EXTERIEUR)
SECTEURCOMBAT_SOUTHEAST.setSubZones(AIREDECOMBAT, AIREDEDETENTE, ROUTE225, ROUTE226, ROUTE227)

# Cities (used for Fly)
BONAUGURE_CITY = City("Bonaugure", 411,[[2,21]], BONAUGURE_MAISON_DOOR)
LITTORELLA_CITY = City("Littorella", 418, [[4,20]], LITTORELLA_CENTREPOKEMON_DOOR)
FELICITE_CITY = City("Féli-Cité", 3, [[3,17],[4,17],[3,18],[4,18]], FELICITE_CENTREPOKEMON_DOOR)
CHARBOURG_CITY = City("Charbourg", 45, [[7,17],[8,17],[8,18]], CHARBOURG_CENTREPOKEMON_DOOR)
FLORAVILLE_CITY = City("Floraville", 426, [[4,13],[4,14]], FLORAVILLE_CENTREPOKEMON_DOOR)
VESTIGION_CITY = City("Vestigion", 65, [[8,10],[9,10],[8,11]], VESTIGION_CENTREPOKEMON_DOOR)
UNIONPOLIS_CITY = City("Unionpolis", 86, [[13,15],[14,15],[13,16],[14,16]], UNIONPOLIS_CENTREPOKEMON_DOOR)
BONVILLE_CITY = City("Bonville", 433, [[16,14],[17,14]], BONVILLE_CENTREPOKEMON_DOOR)
VOILAROC_CITY = City("Voilaroc", 132, [[20,12],[21,12],[20,13],[21,13]], VOILAROC_CENTREPOKEMON_DOOR)
VERCHAMPS_CITY = City("Verchamps", 120, [[17,19],[18,19],[17,20],[18,20]], VERCHAMPS_CENTREPOKEMON_DOOR)
CELESTIA_CITY = City("Célestia", 442, [[13,10]], CELESTIA_CENTREPOKEMON_DOOR)
JOLIBERGES_CITY = City("Joliberges", 33, [[0,16],[0,17]], JOLIBERGES_CENTREPOKEMON_DOOR)
FRIMAPIC_CITY = City("Frimapic", 165, [[10,0],[10,1]], FRIMAPIC_CENTREPOKEMON_DOOR)
RIVAMAR_CITY = City("Rivamar", 150, [[25,17],[26,17],[25,18],[26,18]], RIVAMAR_CENTREPOKEMON_DOOR)
ROUTEVICTOIRE_CITY = City("Route Victoire", 172, [[25,12]], LIGUEPOKEMON_CENTREPOKEMON_DOOR)
LIGUEPOKEMON_CITY = City("Ligue Pokémon", 172, [[25,11]], LIGUEPOKEMON_INTERIEUR_DOOR)
PARCDESAMIS_CITY = City("Parc des Amis", 392, [[8,22]], PARCDESAMIS_DOOR)
AIREDECOMBAT_CITY = City("Aire de Combat", 188, [[18,7],[19,7]], AIREDECOMBAT_CENTREPOKEMON_DOOR)
AIREDESURVIE_CITY = City("Aire de Survie", 450, [[19,4]], AIREDESURVIE_CENTREPOKEMON_DOOR)
AIREDEDETENTE_CITY = City("Aire de Détente", 457, [[24,8]], AIREDEDETENTE_CENTREPOKEMON_DOOR)

CITY_LIST = [
    BONAUGURE_CITY, LITTORELLA_CITY, FELICITE_CITY, CHARBOURG_CITY, FLORAVILLE_CITY, VESTIGION_CITY,
    UNIONPOLIS_CITY, BONVILLE_CITY, VOILAROC_CITY, VERCHAMPS_CITY, CELESTIA_CITY, JOLIBERGES_CITY,
    FRIMAPIC_CITY, RIVAMAR_CITY, ROUTEVICTOIRE_CITY, LIGUEPOKEMON_CITY, PARCDESAMIS_CITY,
    AIREDECOMBAT_CITY, AIREDESURVIE_CITY, AIREDEDETENTE_CITY
]

ZONEIDLIST = {
    3:   "Féli-Cité",
    33:  "Joliberges",
    45:  "Charbourg",
    65:  "Vestigion",
    86:  "Unionpolis",
    120: "Verchamps",
    132: "Voilaroc",
    150: "Rivamar",
    165: "Frimapic",
    172: "Ligue Pokémon - Extérieur",
    188: "Aire de Combat",
    200: "Les Eoliennes",
    202: "Forêt Vestigion - Extérieur",
    204: "Forge Fuego - Extérieur",
    260: "Ile Pleine Lune",
    262: "Mont Abrupt - Extérieur",
    274: "Paradis Fleuri",
    288: "Ile de Fer",
    320: "Ile Nouvellune",
    334: "Rive Lac Vérité",
    336: "Rive Lac Courage",
    340: "Rive Lac Savoir",
    341: "Chemin Source",
    342: "Route 201",
    343: "Route 202",
    344: "Route 203",
    345: "Route 204 - Sud",
    346: "Route 204 - Nord",
    347: "Route 205 - Sud",
    349: "Route 205 - Nord",
    350: "Route 206",
    353: "Route 207",
    354: "Route 208",
    356: "Route 209",
    362: "Route 210 - Sud",
    363: "Route 210 - Nord",
    365: "Route 211 - Ouest",
    366: "Route 211 - Est",
    367: "Route 212 - Nord",
    371: "Route 212 - Sud",
    373: "Route 213",
    380: "Route 214",
    382: "Route 215",
    383: "Route 216",
    385: "Route 217",
    388: "Route 218",
    391: "Route 219",
    392: "Route 221",
    395: "Route 222",
    399: "Route 224",
    400: "Route 225",
    403: "Route 227",
    406: "Route 228",
    407: "Route 229",
    411: "Bonaugure",
    418: "Littorella",
    426: "Floraville",
    433: "Bonville",
    442: "Célestia",
    450: "Aire de Survie",
    457: "Aire de Détente",
    467: "Route 220",
    468: "Route 223",
    469: "Route 226",
    471: "Route 230",
    472: "Passage Marin",
    504: "Grand Marais - Parc 1",
    505: "Grand Marais - Parc 2",
    506: "Grand Marais - Parc 3",
    507: "Grand Marais - Parc 4",
    508: "Grand Marais - Parc 5",
    509: "Grand Marais - Parc 6",
}

ZONELIST = [
    # Overworld
	SOUTH, SOUTHWEST, SOUTHCENTER, SOUTHEAST, NORTH, NORTHWEST, NORTHCENTER, NORTHEAST, EAST, SECTEURCOMBAT_SOUTHEAST, SECTEURCOMBAT_NORTHWEST,
    
    # Cities
    BONAUGURE_MAISON, FELICITE_CENTREPOKEMON, JOLIBERGES_CENTREPOKEMON, CHARBOURG_CENTREPOKEMON, VESTIGION_CENTREPOKEMON, UNIONPOLIS_CENTREPOKEMON, VERCHAMPS_CENTREPOKEMON, VOILAROC_CENTREPOKEMON, RIVAMAR_CENTREPOKEMON, FRIMAPIC_CENTREPOKEMON, LIGUEPOKEMON_CENTREPOKEMON, AIREDECOMBAT_CENTREPOKEMON, LITTORELLA_CENTREPOKEMON, FLORAVILLE_CENTREPOKEMON, BONVILLE_CENTREPOKEMON, CELESTIA_CENTREPOKEMON, AIREDESURVIE_CENTREPOKEMON, AIREDEDETENTE_CENTREPOKEMON, 
	FELICITE_SHOP, JOLIBERGES_SHOP, CHARBOURG_SHOP, VESTIGION_SHOP, UNIONPOLIS_SHOP, VERCHAMPS_SHOP, RIVAMAR_SHOP, FRIMAPIC_SHOP, AIREDECOMBAT_SHOP, LITTORELLA_SHOP, FLORAVILLE_SHOP, BONVILLE_SHOP, CELESTIA_SHOP, AIREDESURVIE_SHOP,
	JOLIBERGES, UNIONPOLIS, VOILAROC, LIGUEPOKEMON, LIGUEPOKEMON_INTERIEUR, PARCDESAMIS,
    VOILAROC_CENTRECOMMERCIAL, VOILAROC_CENTRECOMMERCIALETAGE1, VOILAROC_CENTRECOMMERCIALETAGE2, VOILAROC_CENTRECOMMERCIALETAGE3, VOILAROC_CENTRECOMMERCIALETAGE4, VOILAROC_CENTRECOMMERCIALASCENSEUR, VOILAROC_CENTRECOMMERCIALSOUSSOL1,
    VERCHAMPS_OBSERVATOIRE, VERCHAMPS_OBSERVATOIRE_ETAGE1,

    # Routes
    ROUTE208, ROUTE213_EST, ROUTE218,
	ROUTE206_PASSAGEVESTIGION, ROUTE206_PASSAGECHARBOURG, ROUTE208_PASSAGEUNIONPOLIS, ROUTE209_PASSAGEUNIONPOLIS, ROUTE212_PASSAGEUNIONPOLIS, ROUTE215_PASSAGEVOILAROC, ROUTE225_PASSAGEAIREDECOMBAT, ROUTE214_PASSAGEVOILAROC, ROUTE218_PASSAGEFELICITE, ROUTE213_PASSAGEVERCHAMPS, ROUTE218_PASSAGEJOLIBERGES, ROUTE222_PASSAGERIVAMAR, ROUTE226_PASSAGEROUTE228,
    GRANDMARAIS, HOTELGRANDLAC, PISTECYCLABLE, MANOIRPOKEMON, MANOIRPOKEMON_BUREAU, JARDINTROPHEE, RESTAURANTSEPTETOILES, CAFECABANE,
    ROUTE210_MAISON, ROUTE212_MAISON, ROUTE216_MAISON, ROUTE217_MAISON, ROUTE225_MAISON, ROUTE226_MAISON, ROUTE227_MAISON, ROUTE228_MAISON1, ROUTE228_MAISON2,

    # Dungeons
    ENTREECHARBOURG, ENTREECHARBOURG_SOUSSOL, CHEMINROCHEUX, MINECHARBOURG_ENTREE, MINECHARBOURG,
    FORETVESTIGION, VIEUXCHATEAU, VIEUXCHATEAU_SALLEAMANGER, VIEUXCHATEAU_AILES, VIEUXCHATEAU_COULOIR, VIEUXCHATEAU_CHAMBRE1, VIEUXCHATEAU_CHAMBRE2, VIEUXCHATEAU_CHAMBRE3, VIEUXCHATEAU_CHAMBRE4, VIEUXCHATEAU_CHAMBRE5,
    GROTTEREVECHE, GROTTEREVECHE_SOUSSOL,
    TOURPERDUE_REZDECHAUSSEE, TOURPERDUE_ETAGE1, TOURPERDUE_ETAGE2, TOURPERDUE_ETAGE3, TOURPERDUE_ETAGE4,
    TUNNELRUINEMANIAC, RUINESBONVILLE_ENTREE, RUINESBONVILLE_ENTREE_NORDOUEST, RUINESBONVILLE_ENTREE_SUDEST, RUINESBONVILLE_SALLE1, RUINESBONVILLE_SALLE1_NORDEST, RUINESBONVILLE_SALLE1_SUDEST, RUINESBONVILLE_SALLE2, RUINESBONVILLE_SALLE2_NORDOUEST, RUINESBONVILLE_SALLE2_SUDOUEST, RUINESBONVILLE_SALLE3, RUINESBONVILLE_SALLE3_SUDEST, RUINESBONVILLE_SALLE4, RUINESBONVILLE_SALLE4_SUDOUEST, RUINESBONVILLE_SALLE4_SUDEST, RUINESBONVILLE_SALLE5, RUINESBONVILLE_SALLE5_NORDOUEST, RUINESBONVILLE_SALLE5_SUDEST, RUINESBONVILLE_SALLE6, RUINESBONVILLE_SALLE7,
	MONTCOURONNE_PASSAGECHARBOURG, MONTCOURONNE_SALLE1, MONTCOURONNE_SALLE2, MONTCOURONNE_EXTERIEUR2, MONTCOURONNE_EXTERIEUR1, MONTCOURONNE_SALLE3, MONTCOURONNE_SALLE4, MONTCOURONNE_SALLE5, MONTCOURONNE_SALLE6, MONTCOURONNE_SALLE7, MONTCOURONNE_PASSAGEFRIMAPIC, MONTCOURONNE_PASSAGEVESTIGION, MONTCOURONNE_SALLE8,
	ILEDEFER, ILEDEFER_REZDECHAUSSEE, ILEDEFER_SOUSSOL1OUEST, ILEDEFER_SOUSSOL1EST, ILEDEFER_SOUSSOL2EST, ILEDEFER_SOUSSOL2OUEST, ILEDEFER_SORTIE,
    TEMPLEFRIMAPIC_ENTREE, TEMPLEFRIMAPIC_SOUSSOL1, TEMPLEFRIMAPIC_SOUSSOL2, TEMPLEFRIMAPIC_SOUSSOL3, TEMPLEFRIMAPIC_SOUSSOL4, TEMPLEFRIMAPIC_SALLEREGIGIGAS,
    ROUTEVICTOIRE, ROUTEVICTOIRE_SALLEOUEST, ROUTEVICTOIRE_SALLEEST, ROUTEVICTOIRE_SALLEBRUME, ROUTEVICTOIRE_PASSAGEEST, ROUTEVICTOIRE_PASSAGEROUTE224,
    SOURCEADIEU, GROTTERETOUR_ENTREE, GROTTERETOUR_SALLEPILIER, GROTTERETOUR_SALLEGIRATINA, GROTTERETOUR_SALLE1, GROTTERETOUR_SALLE2, GROTTERETOUR_SALLE3, GROTTERETOUR_SALLE4, GROTTERETOUR_SALLE5, GROTTERETOUR_SALLE6, GROTTERETOUR_SALLE8, GROTTERETOUR_SALLE9, GROTTERETOUR_SALLE10, GROTTERETOUR_SALLE11, GROTTERETOUR_SALLE12, GROTTERETOUR_SALLE13, GROTTERETOUR_SALLE14, GROTTERETOUR_SALLE15, GROTTERETOUR_SALLE41, GROTTERETOUR_SALLE42, GROTTERETOUR_SALLE43,
    MONTABRUPT_SALLE1, MONTABRUPT_SALLE2, MONTABRUPT_SALLEHEATRAN,
	
    # Legendaries
	LACVERITE, LACVERITE_CAVERNEVERITE, LACCOURAGE, LACCOURAGE_CAVERNECOURAGE, LACSAVOIR, LACSAVOIR_CAVERNESAVOIR,
	ILEPLEINELUNE, ILEPLEINELUNE_INTERIEUR, ILENOUVELLUNE, ILENOUVELLUNE_INTERIEUR, ILEDEFER_GROTTEREGISTEEL, MONTCOURONNE_GROTTEREGICE, ROUTE228_GROTTEREGIROCK,
	COLONNESLANCES, SALLEORIGINELLE,
]

ZONEDICTIONARY = {
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
    125: VERCHAMPS_OBSERVATOIRE,
    126: VERCHAMPS_OBSERVATOIRE_ETAGE1,
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
    198: MINECHARBOURG_ENTREE,
    199: MINECHARBOURG,
    200: NORTHWEST, # Les Eoliennes
    202: NORTHWEST, # Forêt Vestigion - Extérieur
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
    225: RUINESBONVILLE_SALLE7,
    226: RUINESBONVILLE_ENTREE,
	227: RUINESBONVILLE_SALLE1_NORDEST,
	228: RUINESBONVILLE_ENTREE_NORDOUEST,
	229: RUINESBONVILLE_SALLE1,
	230: RUINESBONVILLE_ENTREE_SUDEST,
	231: RUINESBONVILLE_SALLE2,
	232: RUINESBONVILLE_SALLE1_SUDEST,
	233: RUINESBONVILLE_SALLE5_SUDEST,
	234: RUINESBONVILLE_SALLE4_SUDOUEST,
	235: RUINESBONVILLE_SALLE2_NORDOUEST,
	236: RUINESBONVILLE_SALLE2_SUDOUEST,
	237: RUINESBONVILLE_SALLE3,
	238: RUINESBONVILLE_SALLE5,
	239: RUINESBONVILLE_SALLE4,
	240: RUINESBONVILLE_SALLE6,
	241: RUINESBONVILLE_SALLE3_SUDEST,
	242: RUINESBONVILLE_SALLE5_NORDOUEST,
    244: ROUTEVICTOIRE,
    245: ROUTEVICTOIRE_SALLEOUEST,
    246: ROUTEVICTOIRE_SALLEEST,
    247: ROUTEVICTOIRE_SALLEBRUME,
    248: ROUTEVICTOIRE_PASSAGEEST,
    249: ROUTEVICTOIRE_PASSAGEROUTE224,
    254: CHEMINROCHEUX,
    258: ENTREECHARBOURG,
    259: ENTREECHARBOURG_SOUSSOL,
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
    278: TEMPLEFRIMAPIC_ENTREE,
    279: TEMPLEFRIMAPIC_SOUSSOL1,
    280: TEMPLEFRIMAPIC_SOUSSOL2,
    281: TEMPLEFRIMAPIC_SOUSSOL3,
    282: TEMPLEFRIMAPIC_SOUSSOL4,
    283: TEMPLEFRIMAPIC_SALLEREGIGIGAS,
    284: GROTTEREVECHE,
    285: GROTTEREVECHE_SOUSSOL,
    287: JARDINTROPHEE,
    288: ILEDEFER, # Ile de Fer
    289: ILEDEFER_REZDECHAUSSEE,
    290: ILEDEFER_SOUSSOL1OUEST,
    291: ILEDEFER_SOUSSOL1EST,
    292: ILEDEFER_SOUSSOL2EST,
    293: ILEDEFER_SOUSSOL2OUEST,
    294: ILEDEFER_SORTIE,
    295: VIEUXCHATEAU,
    296: VIEUXCHATEAU_SALLEAMANGER,
    297: VIEUXCHATEAU_AILES,
    298: VIEUXCHATEAU_COULOIR,
    299: VIEUXCHATEAU_CHAMBRE1,
    300: VIEUXCHATEAU_CHAMBRE2,
    301: VIEUXCHATEAU_CHAMBRE3,
    302: VIEUXCHATEAU_CHAMBRE4,
    303: VIEUXCHATEAU_CHAMBRE5,
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
    337: RESTAURANTSEPTETOILES,
    340: NORTH, # Rive Lac Savoir
    341: SOUTHEAST, # Chemin Source
    342: SOUTHWEST, # Route 201
    343: SOUTHWEST, # Route 202
    344: SOUTHWEST, # Route 203
    345: SOUTHWEST, # Route 204 - Sud
    346: NORTHWEST, # Route 204 - Nord
    347: NORTHWEST, # Route 205 - Sud
    349: NORTHWEST, # Route 205 - Nord
    350: [SOUTHCENTER, PISTECYCLABLE], # Route 206 / Piste Cyclable
    351: ROUTE206_PASSAGECHARBOURG,
    353: SOUTHCENTER, # Route 207
    354: ROUTE208, # Route 208
    356: NORTHCENTER, # Route 209
    357: TOURPERDUE_REZDECHAUSSEE,
    358: TOURPERDUE_ETAGE1,
    359: TOURPERDUE_ETAGE2,
    360: TOURPERDUE_ETAGE3,
    361: TOURPERDUE_ETAGE4,
    362: NORTHCENTER, # Route 210 - Sud
    363: NORTHCENTER, # Route 210 - Nord
    364: ROUTE210_MAISON,
    365: NORTHWEST, # Route 211 - Ouest
    366: NORTHCENTER, # Route 211 - Est
    367: SOUTH, # Route 212 - Nord
    368: MANOIRPOKEMON,
    370: MANOIRPOKEMON_BUREAU,
    371: SOUTH, # Route 212 - Sud
    372: ROUTE212_MAISON,
    373: [ROUTE213_EST, SOUTHEAST], # Route 213
    374: ROUTE213_PASSAGEVERCHAMPS,
    376: HOTELGRANDLAC,
    380: SOUTHEAST, # Route 214
    381: ROUTE214_PASSAGEVOILAROC,
    382: NORTHCENTER, # Route 215
    383: NORTH, # Route 216
    384: ROUTE216_MAISON,
    385: NORTH, # Route 217
    386: ROUTE217_MAISON,
    388: ROUTE218, # Route 218
    389: ROUTE218_PASSAGEFELICITE,
    390: ROUTE218_PASSAGEJOLIBERGES,
    391: SOUTHWEST, # Route 219
    392: SOUTHWEST, # Route 221
    393: PARCDESAMIS,
    395: SOUTHEAST, # Route 222
    398: ROUTE222_PASSAGERIVAMAR,
    399: NORTHEAST, # Route 224
    400: SECTEURCOMBAT_NORTHWEST, # Route 225
    403: SECTEURCOMBAT_NORTHWEST, # Route 227
    406: SECTEURCOMBAT_SOUTHEAST, # Route 228
    407: SECTEURCOMBAT_SOUTHEAST, # Route 229
    411: SOUTHWEST, # Bonaugure
    414: BONAUGURE_MAISON,
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
    492: CAFECABANE,
    498: ROUTE225_MAISON,
    499: ROUTE226_MAISON,
    500: ROUTE227_MAISON,
    501: ROUTE226_PASSAGEROUTE228,
    502: ROUTE228_MAISON1,
    503: ROUTE228_MAISON2,
    504: GRANDMARAIS,
    505: GRANDMARAIS,
    506: GRANDMARAIS,
    507: GRANDMARAIS,
    508: GRANDMARAIS,
    509: GRANDMARAIS,
    510: SALLEORIGINELLE,
    513: TUNNELRUINEMANIAC,
	515: RUINESBONVILLE_SALLE4_SUDEST,
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
    Door(Position(645,813,ROUTE213_EST), Position(10,7,ROUTE213_PASSAGEVERCHAMPS)),
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
    Door(Position(300,796,SOUTHCENTER), Position(11,2,MINECHARBOURG_ENTREE)),
    Door(Position(301,796,SOUTHCENTER), Position(11,2,MINECHARBOURG_ENTREE)),
    Door(Position(303,796,SOUTHCENTER), Position(13,2,MINECHARBOURG_ENTREE)),
    Door(Position(304,796,SOUTHCENTER), Position(13,2,MINECHARBOURG_ENTREE)),
    Door(Position(11,1,MINECHARBOURG_ENTREE), Position(301,795,SOUTHCENTER)),
    Door(Position(13,1,MINECHARBOURG_ENTREE), Position(303,795,SOUTHCENTER)),
    Door(Position(11,22,MINECHARBOURG_ENTREE), Position(15,2,MINECHARBOURG)),
    Door(Position(13,22,MINECHARBOURG_ENTREE), Position(15,2,MINECHARBOURG)),
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
    Door(Position(611,809,SOUTH), Position(5,11,VERCHAMPS_OBSERVATOIRE)),
    Door(Position(69,119,GRANDMARAIS), Position(5,3,VERCHAMPS_OBSERVATOIRE)),
    Door(Position(47,55,LACVERITE), Position(81,844,SOUTHWEST)),
    Door(Position(81,843,SOUTHWEST), Position(47,54,LACVERITE)),
    Door(Position(53,11,LACCOURAGE), Position(717,761,SOUTHEAST)),
    Door(Position(716,761,SOUTHEAST), Position(52,11,LACCOURAGE)),
    Door(Position(15,51,LACSAVOIR), Position(309,230,NORTH)),
    Door(Position(309,229,NORTH), Position(15,50,LACSAVOIR)),
    Door(Position(307,909,SOUTHWEST), Position(7,19,PARCDESAMIS)),
    Door(Position(17,22,ILEPLEINELUNE_INTERIEUR), Position(54,269,ILEPLEINELUNE)),
    Door(Position(54,268,ILEPLEINELUNE), Position(17,21,ILENOUVELLUNE_INTERIEUR)),
    Door(Position(17,22,ILEPLEINELUNE_INTERIEUR), Position(138,269,ILENOUVELLUNE)),
    Door(Position(138,268,ILENOUVELLUNE), Position(17,21,ILENOUVELLUNE_INTERIEUR)),
]