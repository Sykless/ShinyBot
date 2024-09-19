from data import POKEMON_NAMES
import copy

SAPPHIRE = 1
RUBY = 2
EMERALD = 3
FIRERED = 4
LEAFGREEN = 5

JARDINTROPHEE_ID = 287
GRANDMARAIS_PARC1_ID = 504
GRANDMARAIS_PARC6_ID = 509

# Pokemon encountered in grass under special conditions
SPECIALGRASSENCOUNTERS = {
    "garden": [133, 438, 440, 52, 173, 35, 174, 311, 39, 132, 351, 312, 439, 183, 113, 298],
    "swarm": [84, 263, 104, 246, 231, 206, 209, 325, 96, 225, 100, 83, 300, 177, 296, 98, 327, 374, 127, 222, 309, 287],
    "marsh": [454, 352, 352, 455, 451, 453, 195, 452, 451, 453, 195, 115, 46, 452, 102, 102, 451, 453, 451, 455, 193, 285, 46, 115, 316, 357, 316, 285, 451, 455, 453, 114],
}

# Pokémon not encountered in grass or water
SPECIALENCOUNTERS = {
    "static": [377, 378, 379, 425, 442, 479, 480, 482, 483, 484, 485, 486, 487, 491, 492, 493],
    "fossil": [138, 140, 142, 345, 347, 408, 410],
    "honey": [190, 214, 412, 415, 420, 446],
    "roaming": [144, 145, 146, 481, 488],
    "starter": [387, 390, 393],
    "given": [137, 447],
    "manaphy": [490],
    "feebas": [349]
}

# There are respectively 12, 5 and 5 different possible encounters while walking or surfing/fishing, each has a fixed encounter rate
BASEENCOUNTER_RATES = [20,20,10,10,10,10,5,5,4,4,1,1]
SURFENCOUNTER_RATES = [60,30,5,4,1]
RODENCOUNTER_RATES = [40,40,15,4,1]

class Encounter():
    def __init__(self, pokedexId, rate, minLevel, maxLevel):
        self.pokedexId = pokedexId
        self.rate = rate
        self.minLevel = minLevel
        self.maxLevel = maxLevel

    def __str__(self):
        return "Encounter(" + str(self.pokedexId) + "," + str(self.rate) + "," + str(self.minLevel) + "," + str(self.maxLevel) + ")"
    
    def __repr__(self):
        return POKEMON_NAMES[self.pokedexId] + " level " + str(self.minLevel) + ("-" + str(self.maxLevel) if self.minLevel != self.maxLevel else "") + " at " + str(self.rate) + "%\n" 

class EncounterTables():
    def __init__(self, name, topLeftPosition = None, bottomRightBottom = None):
        self.name = name
        self.baseEncounters = []
        self.dayEncounters = []
        self.nightEncounters = []
        self.pokeradarEncounters = []
        self.swarmEncounters = []
        self.gbaEncounters = []
        self.surfEncounters = []
        self.oldRodEncounters = []
        self.goodRodEncounters = []
        self.superRodEncounters = []

        if (topLeftPosition):
            self.topLeftPosition = topLeftPosition
            self.bottomRightBottom = bottomRightBottom

    def setBaseEncounters(self, *baseEncounters):
        self.baseEncounters = baseEncounters

    def setDayEncounters(self, *dayEncounters):
        self.dayEncounters = dayEncounters

    def setNightEncounters(self, *nightEncounters):
        self.nightEncounters = nightEncounters

    def setSwarmEncounters(self, *swarmEncounters):
        self.swarmEncounters = swarmEncounters

    def setPokeradarEncounters(self, *pokeradarEncounters):
        self.pokeradarEncounters = pokeradarEncounters

    def setGbaEncounters(self, *gbaEncounters):
        self.gbaEncounters = gbaEncounters

    def setSurfEncounters(self, *surfEncounters):
        self.surfEncounters = surfEncounters

    def setOldRodEncounters(self, *oldRodEncounters):
        self.oldRodEncounters = oldRodEncounters

    def setGoodRodEncounters(self, *goodRodEncounters):
        self.goodRodEncounters = goodRodEncounters

    def setSuperRodEncounters(self, *superRodEncounters):
        self.superRodEncounters = superRodEncounters
    
    def initTable(self, tableDict, objectName = None):
        self.baseEncounters = []
        self.surfEncounters = []
        self.oldRodEncounters = []
        self.goodRodEncounters = []
        self.superRodEncounters = []

        with open('encounterData.py', 'a') as file:
            if (tableDict["walkEncounterTable"]):
                self.dayEncounters = tableDict["walkEncounterTable"]["dayEncounters"]
                self.nightEncounters = tableDict["walkEncounterTable"]["nightEncounters"]
                self.pokeradarEncounters = tableDict["walkEncounterTable"]["pokeradarEncounters"]
                self.swarmEncounters = tableDict["walkEncounterTable"]["swarmEncounters"]
                self.gbaEncounters = [[None]] + tableDict["walkEncounterTable"]["gbaEncounters"]

                for i in range(12):
                    self.baseEncounters.append(Encounter(tableDict["walkEncounterTable"]["morningEncounters"][i]["pokedexId"],
                                                        BASEENCOUNTER_RATES[i],
                                                        tableDict["walkEncounterTable"]["morningEncounters"][i]["level"],
                                                        tableDict["walkEncounterTable"]["morningEncounters"][i]["level"]))
                    
                # Generate instructions to create the final object
                if (objectName):
                    instructions = (str(objectName) + ".setBaseEncounters(" + ", ".join(str(encounter) for encounter in self.baseEncounters) + ")\n"
                                    + str(objectName) + ".setDayEncounters(" + ",".join(str(encounter) for encounter in self.dayEncounters) + ")\n"
                                    + str(objectName) + ".setNightEncounters(" + ",".join(str(encounter) for encounter in self.nightEncounters) + ")\n"
                                    + str(objectName) + ".setSwarmEncounters(" + ",".join(str(encounter) for encounter in self.swarmEncounters) + ")\n"
                                    + str(objectName) + ".setPokeradarEncounters(" + ",".join(str(encounter) for encounter in self.pokeradarEncounters) + ")\n"
                                    + str(objectName) + ".setGbaEncounters([" + "], [".join(",".join(str(encounter) for encounter in gbaEncounterList) for gbaEncounterList in self.gbaEncounters) + "])\n")
                    file.write(instructions)
                    print(instructions)

            if (tableDict["waterEncounterTable"]):
                for i in range(5):
                    self.surfEncounters.append(Encounter(tableDict["waterEncounterTable"]["surfEncounters"][i]["pokedexId"],
                                                        SURFENCOUNTER_RATES[i],
                                                        tableDict["waterEncounterTable"]["surfEncounters"][i]["minLevel"],
                                                        tableDict["waterEncounterTable"]["surfEncounters"][i]["maxLevel"]))
                    
                for i in range(5):
                    self.oldRodEncounters.append(Encounter(tableDict["waterEncounterTable"]["oldRodEncounters"][i]["pokedexId"],
                                                        RODENCOUNTER_RATES[i],
                                                        tableDict["waterEncounterTable"]["oldRodEncounters"][i]["minLevel"],
                                                        tableDict["waterEncounterTable"]["oldRodEncounters"][i]["maxLevel"]))
                
                for i in range(5):
                    self.goodRodEncounters.append(Encounter(tableDict["waterEncounterTable"]["goodRodEncounters"][i]["pokedexId"],
                                                            RODENCOUNTER_RATES[i],
                                                            tableDict["waterEncounterTable"]["goodRodEncounters"][i]["minLevel"],
                                                            tableDict["waterEncounterTable"]["goodRodEncounters"][i]["maxLevel"]))
                    
                for i in range(5):
                    self.superRodEncounters.append(Encounter(tableDict["waterEncounterTable"]["superRodEncounters"][i]["pokedexId"],
                                                            RODENCOUNTER_RATES[i],
                                                            tableDict["waterEncounterTable"]["superRodEncounters"][i]["minLevel"],
                                                            tableDict["waterEncounterTable"]["superRodEncounters"][i]["maxLevel"]))
                    
                # Generate instructions to create the final object
                if (objectName):
                    instructions = (str(objectName) + ".setSurfEncounters(" + ", ".join(str(encounter) for encounter in self.surfEncounters) + ")\n"
                                    + str(objectName) + ".setOldRodEncounters(" + ", ".join(str(encounter) for encounter in self.oldRodEncounters) + ")\n"
                                    + str(objectName) + ".setGoodRodEncounters(" + ", ".join(str(encounter) for encounter in self.goodRodEncounters) + ")\n"
                                    + str(objectName) + ".setSuperRodEncounters(" + ", ".join(str(encounter) for encounter in self.superRodEncounters) + ")\n")
                    file.write(instructions)
                    print(instructions)

            if (objectName):
                file.write("\n")
 

    def generateCurrentTables(self, gameData, zoneId, pokeradar = False):

        encounterTables = {
            "walkEncounters": {"table": {}, "baseEncounters": copy.deepcopy(self.baseEncounters)},
            "surfEncounters": {"table": {}, "baseEncounters": copy.deepcopy(self.surfEncounters)},
            "oldRodEncounter": {"table": {}, "baseEncounters": copy.deepcopy(self.oldRodEncounters)},
            "goodRodEncounter": {"table": {}, "baseEncounters": copy.deepcopy(self.goodRodEncounters)},
            "superRodEncounter": {"table": {}, "baseEncounters": copy.deepcopy(self.superRodEncounters)}
        }

        # Generate walking encounters
        if (self.baseEncounters):

            # During the day : replace encounters 3 and 4 (10% encounters) by Day encounters
            if (10 <= gameData.hourOfDay < 18):
                encounterTables["walkEncounters"]["baseEncounters"][2].pokedexId = self.dayEncounters[0]
                encounterTables["walkEncounters"]["baseEncounters"][3].pokedexId = self.dayEncounters[1]

            # During the dight : replace encounters 3 and 4 (10% encounters) by Night encounters
            elif (0 <= gameData.hourOfDay < 4 or 18 <= gameData.hourOfDay < 24 ):
                encounterTables["walkEncounters"]["baseEncounters"][2].pokedexId = self.nightEncounters[0]
                encounterTables["walkEncounters"]["baseEncounters"][3].pokedexId = self.nightEncounters[1]

            # During a swarm : replace encounters 1 and 2 (20% encounters) by Swarm encounters 
            if (SPECIALGRASSENCOUNTERS["swarm"][gameData.swarmPokemon] == self.swarmEncounters[0]):
                encounterTables["walkEncounters"]["baseEncounters"][0].pokedexId = self.swarmEncounters[0]
                encounterTables["walkEncounters"]["baseEncounters"][1].pokedexId = self.swarmEncounters[1]

            # In Jardin Trophée : replace encounters 7 and 8 (5% encounters) by Garden encounters
            if (zoneId == JARDINTROPHEE_ID):
                encounterTables["walkEncounters"]["baseEncounters"][6].pokedexId = SPECIALGRASSENCOUNTERS["garden"][gameData.gardenPokemonToday]
                encounterTables["walkEncounters"]["baseEncounters"][7].pokedexId = SPECIALGRASSENCOUNTERS["garden"][gameData.gardenPokemonYesterday if gameData.gardenPokemonYesterday else gameData.gardenPokemonToday]

            # In Grand Marais : replace encounters 7 and 8 (5% encounters) by Marsh encounters
            if (GRANDMARAIS_PARC1_ID <= zoneId <= GRANDMARAIS_PARC6_ID):
                encounterTables["walkEncounters"]["baseEncounters"][6].pokedexId = SPECIALGRASSENCOUNTERS["marsh"][gameData.marshPokemonList[zoneId - GRANDMARAIS_PARC1_ID]]
                encounterTables["walkEncounters"]["baseEncounters"][7].pokedexId = SPECIALGRASSENCOUNTERS["marsh"][gameData.marshPokemonList[zoneId - GRANDMARAIS_PARC1_ID]]

            # GBA game inserted : replace encounters 9 and 10 (4% encounters) by GBA game encounters
            if (gameData.gbaGame > 0):
                encounterTables["walkEncounters"]["baseEncounters"][8].pokedexId = self.gbaEncounters[gameData.gbaGame][0]
                encounterTables["walkEncounters"]["baseEncounters"][9].pokedexId = self.gbaEncounters[gameData.gbaGame][1]

            # Rare grass patches using Pokéradar : replace encounters 5, 6 (10% encounters), 11 and 12 (1% encounters) by Pokéradar encounters
            if (pokeradar):
                encounterTables["walkEncounters"]["baseEncounters"][4].pokedexId = self.pokeradarEncounters[0]
                encounterTables["walkEncounters"]["baseEncounters"][5].pokedexId = self.pokeradarEncounters[1]
                encounterTables["walkEncounters"]["baseEncounters"][10].pokedexId = self.pokeradarEncounters[2]
                encounterTables["walkEncounters"]["baseEncounters"][11].pokedexId = self.pokeradarEncounters[3]

        # Setup encounter table to get total rate and min/max level of each Pokémon
        for _, encounterTable in encounterTables.items():
            for encounter in encounterTable["baseEncounters"]:
            
                # Pokémon not already in table : add it
                if (not encounter.pokedexId in encounterTable["table"]):
                    encounterTable["table"][encounter.pokedexId] = encounter

                # Pokémon already in table : update total rate, min and max levels
                else:
                    encounterTable["table"][encounter.pokedexId].rate += encounter.rate

                    if (encounterTable["table"][encounter.pokedexId].minLevel > encounter.minLevel):
                        encounterTable["table"][encounter.pokedexId].minLevel = encounter.minLevel

                    if (encounterTable["table"][encounter.pokedexId].maxLevel < encounter.maxLevel):
                        encounterTable["table"][encounter.pokedexId].maxLevel = encounter.maxLevel

        # Return all tables
        return (encounterTables["walkEncounters"]["table"],
                encounterTables["surfEncounters"]["table"],
                encounterTables["oldRodEncounter"]["table"],
                encounterTables["goodRodEncounter"]["table"],
                encounterTables["superRodEncounter"]["table"])

BONAUGURE = EncounterTables("Bonaugure")
BONAUGURE.setSurfEncounters(Encounter(54,60,20,30), Encounter(54,30,20,30), Encounter(55,5,20,40), Encounter(55,4,20,40), Encounter(55,1,20,40))
BONAUGURE.setOldRodEncounters(Encounter(129,40,4,6), Encounter(129,40,3,7), Encounter(129,15,5,10), Encounter(129,4,5,10), Encounter(129,1,5,15))
BONAUGURE.setGoodRodEncounters(Encounter(129,40,15,20), Encounter(118,40,15,20), Encounter(129,15,10,25), Encounter(118,4,25,35), Encounter(118,1,25,35))
BONAUGURE.setSuperRodEncounters(Encounter(130,40,30,40), Encounter(119,40,30,40), Encounter(130,15,40,55), Encounter(119,4,40,55), Encounter(119,1,40,55))

VESTIGION = EncounterTables("Vestigion")
VESTIGION.setSurfEncounters(Encounter(54,60,20,30), Encounter(54,30,20,30), Encounter(55,5,20,40), Encounter(55,4,20,40), Encounter(55,1,20,40))
VESTIGION.setOldRodEncounters(Encounter(129,40,4,6), Encounter(129,40,3,7), Encounter(129,15,5,10), Encounter(129,4,5,10), Encounter(129,1,5,15))
VESTIGION.setGoodRodEncounters(Encounter(129,40,15,20), Encounter(339,40,15,20), Encounter(129,15,10,25), Encounter(339,4,10,25), Encounter(339,1,10,25))
VESTIGION.setSuperRodEncounters(Encounter(130,40,30,40), Encounter(340,40,30,40), Encounter(130,15,40,55), Encounter(340,4,40,55), Encounter(340,1,40,55))

CELESTIA = EncounterTables("Célestia")
CELESTIA.setSurfEncounters(Encounter(54,60,20,30), Encounter(54,30,20,30), Encounter(55,5,20,40), Encounter(55,4,20,40), Encounter(55,1,20,40))
CELESTIA.setOldRodEncounters(Encounter(129,40,4,6), Encounter(129,40,3,7), Encounter(129,15,5,10), Encounter(129,4,5,10), Encounter(129,1,5,15))
CELESTIA.setGoodRodEncounters(Encounter(129,40,15,20), Encounter(118,40,15,20), Encounter(129,15,10,25), Encounter(118,4,25,35), Encounter(118,1,25,35))
CELESTIA.setSuperRodEncounters(Encounter(130,40,30,55), Encounter(341,40,30,40), Encounter(342,15,40,55), Encounter(119,4,40,55), Encounter(119,1,40,55))

VERCHAMPS = EncounterTables("Verchamps")
VERCHAMPS.setSurfEncounters(Encounter(72,60,20,30), Encounter(422,30,20,30), Encounter(73,5,20,40), Encounter(278,4,20,30), Encounter(423,1,20,40))
VERCHAMPS.setOldRodEncounters(Encounter(129,40,4,6), Encounter(129,40,3,7), Encounter(129,15,5,10), Encounter(129,4,5,10), Encounter(129,1,5,15))
VERCHAMPS.setGoodRodEncounters(Encounter(129,40,15,20), Encounter(223,40,15,20), Encounter(129,15,10,25), Encounter(223,4,10,25), Encounter(223,1,10,25))
VERCHAMPS.setSuperRodEncounters(Encounter(130,40,30,40), Encounter(224,40,30,40), Encounter(130,15,40,55), Encounter(224,4,40,55), Encounter(224,1,40,55))

JOLIBERGES = EncounterTables("Joliberges")
JOLIBERGES.setSurfEncounters(Encounter(72,60,20,30), Encounter(422,30,20,30), Encounter(73,5,20,40), Encounter(73,4,20,40), Encounter(423,1,20,40))
JOLIBERGES.setOldRodEncounters(Encounter(129,40,4,6), Encounter(129,40,3,7), Encounter(129,15,5,10), Encounter(129,4,5,10), Encounter(129,1,5,15))
JOLIBERGES.setGoodRodEncounters(Encounter(129,40,15,20), Encounter(456,40,15,20), Encounter(129,15,10,25), Encounter(456,4,10,25), Encounter(456,1,10,25))
JOLIBERGES.setSuperRodEncounters(Encounter(130,40,30,55), Encounter(457,40,30,40), Encounter(120,15,20,50), Encounter(457,4,40,55), Encounter(457,1,40,55))

RIVAMAR = EncounterTables("Rivamar")
RIVAMAR.setSurfEncounters(Encounter(72,60,30,40), Encounter(278,30,30,40), Encounter(73,5,30,50), Encounter(73,4,30,50), Encounter(279,1,30,50))
RIVAMAR.setOldRodEncounters(Encounter(129,40,4,6), Encounter(129,40,3,7), Encounter(129,15,5,10), Encounter(129,4,5,10), Encounter(129,1,5,15))
RIVAMAR.setGoodRodEncounters(Encounter(129,40,15,20), Encounter(223,40,15,20), Encounter(129,15,10,25), Encounter(223,4,10,25), Encounter(223,1,10,25))
RIVAMAR.setSuperRodEncounters(Encounter(130,40,30,55), Encounter(224,40,30,40), Encounter(120,15,20,50), Encounter(224,4,40,55), Encounter(224,1,40,55))

AIREDEDETENTE = EncounterTables("Aire de Détente")
AIREDEDETENTE.setSurfEncounters(Encounter(55,60,35,55), Encounter(55,30,35,55), Encounter(54,5,35,45), Encounter(54,4,35,45), Encounter(54,1,35,45))
AIREDEDETENTE.setOldRodEncounters(Encounter(129,40,4,6), Encounter(129,40,3,7), Encounter(129,15,5,10), Encounter(129,4,5,10), Encounter(129,1,5,15))
AIREDEDETENTE.setGoodRodEncounters(Encounter(129,40,15,20), Encounter(129,40,15,20), Encounter(129,15,10,25), Encounter(129,4,25,35), Encounter(129,1,25,35))
AIREDEDETENTE.setSuperRodEncounters(Encounter(129,40,40,60), Encounter(129,40,30,70), Encounter(129,15,20,80), Encounter(129,4,10,90), Encounter(129,1,1,100))

ROUTE201 = EncounterTables("Route 201")
ROUTE201.setBaseEncounters(Encounter(396,20,2,2), Encounter(399,20,2,2), Encounter(396,10,3,3), Encounter(401,10,3,3), Encounter(396,10,3,3), Encounter(399,10,3,3), Encounter(396,5,3,3), Encounter(399,5,3,3), Encounter(396,4,2,2), Encounter(399,4,2,2), Encounter(396,1,2,2), Encounter(399,1,2,2))
ROUTE201.setDayEncounters(396,399)
ROUTE201.setNightEncounters(401,399)
ROUTE201.setSwarmEncounters(84,84)
ROUTE201.setPokeradarEncounters(32,29,32,29)
ROUTE201.setGbaEncounters([None], [396,399], [396,399], [396,399], [58,58], [396,399])

ROUTE202 = EncounterTables("Route 202")
ROUTE202.setBaseEncounters(Encounter(403,20,3,3), Encounter(399,20,3,3), Encounter(396,10,4,4), Encounter(401,10,3,3), Encounter(403,10,4,4), Encounter(399,10,3,3), Encounter(396,5,4,4), Encounter(399,5,4,4), Encounter(396,4,2,2), Encounter(399,4,2,2), Encounter(396,1,2,2), Encounter(399,1,2,2))
ROUTE202.setDayEncounters(396,399)
ROUTE202.setNightEncounters(401,399)
ROUTE202.setSwarmEncounters(263,263)
ROUTE202.setPokeradarEncounters(161,161,161,161)
ROUTE202.setGbaEncounters([None], [396,399], [396,399], [396,399], [58,58], [396,399])

ROUTE203 = EncounterTables("Route 203")
ROUTE203.setBaseEncounters(Encounter(396,20,4,4), Encounter(403,20,4,4), Encounter(396,10,5,5), Encounter(401,10,4,4), Encounter(399,10,5,5), Encounter(63,10,4,4), Encounter(63,5,5,5), Encounter(403,5,5,5), Encounter(396,4,6,6), Encounter(399,4,6,6), Encounter(396,1,7,7), Encounter(399,1,7,7))
ROUTE203.setDayEncounters(396,399)
ROUTE203.setNightEncounters(401,41)
ROUTE203.setSwarmEncounters(104,104)
ROUTE203.setPokeradarEncounters(399,63,396,399)
ROUTE203.setGbaEncounters([None], [270,270], [273,273], [204,204], [396,399], [396,399])
ROUTE203.setSurfEncounters(Encounter(54,60,20,30), Encounter(54,30,20,30), Encounter(55,5,20,40), Encounter(55,4,20,40), Encounter(55,1,20,40))
ROUTE203.setOldRodEncounters(Encounter(129,40,4,6), Encounter(129,40,3,7), Encounter(129,15,5,10), Encounter(129,4,5,10), Encounter(129,1,5,15))
ROUTE203.setGoodRodEncounters(Encounter(129,40,15,20), Encounter(118,40,15,20), Encounter(129,15,10,25), Encounter(118,4,10,25), Encounter(118,1,10,25))
ROUTE203.setSuperRodEncounters(Encounter(130,40,30,40), Encounter(119,40,30,40), Encounter(130,15,40,55), Encounter(119,4,40,55), Encounter(119,1,40,55))

ROUTE204_SUD = EncounterTables("Route 204 - Sud")
ROUTE204_SUD.setBaseEncounters(Encounter(396,20,4,4), Encounter(399,20,4,4), Encounter(265,10,4,4), Encounter(401,10,3,3), Encounter(406,10,4,4), Encounter(403,10,4,4), Encounter(406,5,5,5), Encounter(403,5,5,5), Encounter(396,4,5,5), Encounter(399,4,5,5), Encounter(396,1,6,6), Encounter(399,1,6,6))
ROUTE204_SUD.setDayEncounters(265,406)
ROUTE204_SUD.setNightEncounters(401,41)
ROUTE204_SUD.setSwarmEncounters(396,399)
ROUTE204_SUD.setPokeradarEncounters(406,403,396,399)
ROUTE204_SUD.setGbaEncounters([None], [270,270], [273,273], [204,204], [10,10], [13,13])
ROUTE204_SUD.setSurfEncounters(Encounter(54,60,20,30), Encounter(54,30,20,30), Encounter(55,5,20,40), Encounter(55,4,20,40), Encounter(55,1,20,40))
ROUTE204_SUD.setOldRodEncounters(Encounter(129,40,4,6), Encounter(129,40,3,7), Encounter(129,15,5,10), Encounter(129,4,5,10), Encounter(129,1,5,15))
ROUTE204_SUD.setGoodRodEncounters(Encounter(129,40,15,20), Encounter(118,40,15,20), Encounter(129,15,10,25), Encounter(118,4,10,25), Encounter(118,1,10,25))
ROUTE204_SUD.setSuperRodEncounters(Encounter(130,40,30,40), Encounter(119,40,30,40), Encounter(130,15,40,55), Encounter(119,4,40,55), Encounter(119,1,40,55))

ROUTE204_NORD = EncounterTables("Route 204 - Nord")
ROUTE204_NORD.setBaseEncounters(Encounter(396,20,9,9), Encounter(399,20,9,9), Encounter(265,10,9,9), Encounter(401,10,8,8), Encounter(406,10,9,9), Encounter(403,10,9,9), Encounter(406,5,10,10), Encounter(403,5,10,10), Encounter(396,4,10,10), Encounter(399,4,10,10), Encounter(396,1,11,11), Encounter(399,1,11,11))
ROUTE204_NORD.setDayEncounters(265,406)
ROUTE204_NORD.setNightEncounters(401,41)
ROUTE204_NORD.setSwarmEncounters(396,399)
ROUTE204_NORD.setPokeradarEncounters(191,191,191,191)
ROUTE204_NORD.setGbaEncounters([None], [270,270], [273,273], [204,204], [10,10], [13,13])
ROUTE204_NORD.setSurfEncounters(Encounter(54,60,20,30), Encounter(54,30,20,30), Encounter(55,5,20,40), Encounter(55,4,20,40), Encounter(55,1,20,40))
ROUTE204_NORD.setOldRodEncounters(Encounter(129,40,4,6), Encounter(129,40,3,7), Encounter(129,15,5,10), Encounter(129,4,5,10), Encounter(129,1,5,15))
ROUTE204_NORD.setGoodRodEncounters(Encounter(129,40,15,20), Encounter(118,40,15,20), Encounter(129,15,10,25), Encounter(118,4,10,25), Encounter(118,1,10,25))
ROUTE204_NORD.setSuperRodEncounters(Encounter(130,40,30,40), Encounter(119,40,30,40), Encounter(130,15,40,55), Encounter(119,4,40,55), Encounter(119,1,40,55))

ROUTE205_SUD = EncounterTables("Route 205 - Sud")
ROUTE205_SUD.setBaseEncounters(Encounter(422,20,10,10), Encounter(422,20,11,11), Encounter(418,10,10,10), Encounter(422,10,9,9), Encounter(399,10,10,10), Encounter(422,10,11,11), Encounter(417,5,9,9), Encounter(417,5,11,11), Encounter(418,4,11,11), Encounter(422,4,12,12), Encounter(418,1,11,11), Encounter(422,1,12,12))
ROUTE205_SUD.setDayEncounters(418,422)
ROUTE205_SUD.setNightEncounters(418,422)
ROUTE205_SUD.setSwarmEncounters(422,422)
ROUTE205_SUD.setPokeradarEncounters(187,187,187,187)
ROUTE205_SUD.setGbaEncounters([None], [418,422], [418,422], [418,422], [418,422], [418,422])
ROUTE205_SUD.setSurfEncounters(Encounter(422,60,20,30), Encounter(72,30,20,30), Encounter(423,5,20,40), Encounter(423,4,20,40), Encounter(73,1,20,40))
ROUTE205_SUD.setOldRodEncounters(Encounter(129,40,4,6), Encounter(129,40,3,7), Encounter(129,15,5,10), Encounter(129,4,5,10), Encounter(129,1,5,15))
ROUTE205_SUD.setGoodRodEncounters(Encounter(129,40,15,20), Encounter(456,40,15,20), Encounter(129,15,10,25), Encounter(456,4,10,25), Encounter(456,1,10,25))
ROUTE205_SUD.setSuperRodEncounters(Encounter(130,40,30,55), Encounter(457,40,30,40), Encounter(90,15,20,50), Encounter(457,4,40,55), Encounter(457,1,40,55))

ROUTE205_NORD = EncounterTables("Route 205 - Nord")
ROUTE205_NORD.setBaseEncounters(Encounter(399,20,12,12), Encounter(406,20,12,12), Encounter(265,10,13,13), Encounter(401,10,12,12), Encounter(266,10,14,14), Encounter(268,10,14,14), Encounter(399,5,13,13), Encounter(399,5,14,14), Encounter(406,4,13,13), Encounter(406,4,14,14), Encounter(267,1,15,15), Encounter(269,1,15,15))
ROUTE205_NORD.setDayEncounters(265,406)
ROUTE205_NORD.setNightEncounters(401,163)
ROUTE205_NORD.setSwarmEncounters(399,406)
ROUTE205_NORD.setPokeradarEncounters(79,79,79,79)
ROUTE205_NORD.setGbaEncounters([None], [270,270], [406,406], [406,406], [406,406], [406,406])
ROUTE205_NORD.setSurfEncounters(Encounter(54,60,20,30), Encounter(54,30,20,30), Encounter(55,5,20,40), Encounter(55,4,20,40), Encounter(55,1,20,40))
ROUTE205_NORD.setOldRodEncounters(Encounter(129,40,4,6), Encounter(129,40,3,7), Encounter(129,15,5,10), Encounter(129,4,5,10), Encounter(129,1,5,15))
ROUTE205_NORD.setGoodRodEncounters(Encounter(129,40,15,20), Encounter(339,40,15,20), Encounter(129,15,10,25), Encounter(339,4,10,25), Encounter(339,1,10,25))
ROUTE205_NORD.setSuperRodEncounters(Encounter(130,40,30,40), Encounter(340,40,30,40), Encounter(130,15,40,55), Encounter(340,4,40,55), Encounter(340,1,40,55))

ROUTE206 = EncounterTables("Route 206")
ROUTE206.setBaseEncounters(Encounter(77,20,16,16), Encounter(74,20,16,16), Encounter(207,10,18,18), Encounter(402,10,17,17), Encounter(207,10,16,16), Encounter(66,10,17,17), Encounter(66,5,18,18), Encounter(74,5,18,18), Encounter(66,4,19,19), Encounter(74,4,18,18), Encounter(66,1,19,19), Encounter(74,1,18,18))
ROUTE206.setDayEncounters(207,77)
ROUTE206.setNightEncounters(402,41)
ROUTE206.setSwarmEncounters(246,246)
ROUTE206.setPokeradarEncounters(343,343,343,343)
ROUTE206.setGbaEncounters([None], [66,74], [66,74], [66,74], [66,74], [66,74])

ROUTE207 = EncounterTables("Route 207")
ROUTE207.setBaseEncounters(Encounter(66,20,7,7), Encounter(74,20,5,5), Encounter(77,10,6,6), Encounter(401,10,5,5), Encounter(77,10,5,5), Encounter(66,10,6,6), Encounter(66,5,8,8), Encounter(74,5,6,6), Encounter(77,4,7,7), Encounter(74,4,7,7), Encounter(77,1,7,7), Encounter(74,1,7,7))
ROUTE207.setDayEncounters(77,66)
ROUTE207.setNightEncounters(401,41)
ROUTE207.setSwarmEncounters(231,231)
ROUTE207.setPokeradarEncounters(234,234,234,234)
ROUTE207.setGbaEncounters([None], [77,74], [77,74], [77,74], [77,74], [77,74])

ROUTE208 = EncounterTables("Route 208")
ROUTE208.setBaseEncounters(Encounter(406,20,18,18), Encounter(399,20,18,18), Encounter(406,10,19,19), Encounter(280,10,17,17), Encounter(315,10,19,19), Encounter(400,10,18,18), Encounter(280,5,18,18), Encounter(400,5,19,19), Encounter(315,4,20,20), Encounter(400,4,20,20), Encounter(315,1,20,20), Encounter(400,1,20,20))
ROUTE208.setDayEncounters(406,280)
ROUTE208.setNightEncounters(41,280)
ROUTE208.setSwarmEncounters(206,206)
ROUTE208.setPokeradarEncounters(235,235,235,235)
ROUTE208.setGbaEncounters([None], [336,336], [335,335], [315,400], [315,400], [315,400])
ROUTE208.setSurfEncounters(Encounter(54,60,20,20), Encounter(54,30,20,20), Encounter(55,5,20,40), Encounter(55,4,20,40), Encounter(55,1,20,40))
ROUTE208.setOldRodEncounters(Encounter(129,40,4,6), Encounter(129,40,3,7), Encounter(129,15,5,10), Encounter(129,4,5,10), Encounter(129,1,5,15))
ROUTE208.setGoodRodEncounters(Encounter(129,40,15,20), Encounter(118,40,15,20), Encounter(129,15,10,25), Encounter(118,4,10,25), Encounter(118,1,10,25))
ROUTE208.setSuperRodEncounters(Encounter(130,40,30,40), Encounter(119,40,30,40), Encounter(130,15,40,55), Encounter(119,4,40,55), Encounter(119,1,40,55))

ROUTE209 = EncounterTables("Route 209")
ROUTE209.setBaseEncounters(Encounter(315,20,19,19), Encounter(400,20,18,18), Encounter(397,10,19,19), Encounter(280,10,17,17), Encounter(397,10,18,18), Encounter(400,10,19,19), Encounter(280,5,18,18), Encounter(315,5,20,20), Encounter(280,4,19,19), Encounter(113,4,17,17), Encounter(280,1,19,19), Encounter(113,1,19,19))
ROUTE209.setDayEncounters(397,280)
ROUTE209.setNightEncounters(41,355)
ROUTE209.setSwarmEncounters(209,209)
ROUTE209.setPokeradarEncounters(281,281,281,281)
ROUTE209.setGbaEncounters([None], [280,113], [280,113], [280,113], [280,113], [37,37])
ROUTE209.setSurfEncounters(Encounter(54,60,20,30), Encounter(54,30,20,30), Encounter(55,5,20,40), Encounter(55,4,20,40), Encounter(55,1,20,40))
ROUTE209.setOldRodEncounters(Encounter(129,40,4,6), Encounter(129,40,3,7), Encounter(129,15,5,10), Encounter(129,4,5,10), Encounter(129,1,5,15))
ROUTE209.setGoodRodEncounters(Encounter(129,40,15,20), Encounter(118,40,15,20), Encounter(129,15,10,25), Encounter(118,4,10,25), Encounter(118,1,10,25))
ROUTE209.setSuperRodEncounters(Encounter(130,40,30,40), Encounter(119,40,30,40), Encounter(130,15,40,55), Encounter(119,4,40,55), Encounter(119,1,40,55))

ROUTE210_SUD = EncounterTables("Route 210 - Sud")
ROUTE210_SUD.setBaseEncounters(Encounter(397,20,19,19), Encounter(74,20,18,18), Encounter(123,10,21,21), Encounter(77,10,20,20), Encounter(315,10,20,20), Encounter(77,10,19,19), Encounter(123,5,19,19), Encounter(315,5,21,21), Encounter(77,4,21,21), Encounter(113,4,19,19), Encounter(77,1,21,21), Encounter(113,1,21,21))
ROUTE210_SUD.setDayEncounters(77,77)
ROUTE210_SUD.setNightEncounters(164,163)
ROUTE210_SUD.setSwarmEncounters(397,74)
ROUTE210_SUD.setPokeradarEncounters(241,128,241,128)
ROUTE210_SUD.setGbaEncounters([None], [77,113], [273,274], [204,204], [77,113], [77,113])

ROUTE210_NORD = EncounterTables("Route 210 - Nord")
ROUTE210_NORD.setBaseEncounters(Encounter(333,20,27,27), Encounter(400,20,28,28), Encounter(123,10,27,27), Encounter(307,10,27,27), Encounter(307,10,29,29), Encounter(66,10,28,28), Encounter(123,5,29,29), Encounter(67,5,29,29), Encounter(66,4,29,29), Encounter(67,4,30,30), Encounter(66,1,29,29), Encounter(67,1,30,30))
ROUTE210_NORD.setDayEncounters(333,307)
ROUTE210_NORD.setNightEncounters(164,163)
ROUTE210_NORD.setSwarmEncounters(333,400)
ROUTE210_NORD.setPokeradarEncounters(371,371,371,371)
ROUTE210_NORD.setGbaEncounters([None], [336,336], [335,335], [66,67], [66,67], [66,67])
ROUTE210_NORD.setSurfEncounters(Encounter(54,60,20,30), Encounter(54,30,20,30), Encounter(55,5,20,40), Encounter(55,4,20,40), Encounter(55,1,20,40))
ROUTE210_NORD.setOldRodEncounters(Encounter(129,40,4,6), Encounter(129,40,3,7), Encounter(129,15,5,10), Encounter(129,4,5,10), Encounter(129,1,5,15))
ROUTE210_NORD.setGoodRodEncounters(Encounter(129,40,15,20), Encounter(339,40,15,20), Encounter(129,15,10,25), Encounter(340,4,25,35), Encounter(340,1,25,35))
ROUTE210_NORD.setSuperRodEncounters(Encounter(130,40,30,40), Encounter(340,40,30,40), Encounter(130,15,40,55), Encounter(340,4,40,55), Encounter(340,1,40,55))

ROUTE211_OUEST = EncounterTables("Route 211 - Ouest")
ROUTE211_OUEST.setBaseEncounters(Encounter(307,20,13,13), Encounter(399,20,14,14), Encounter(307,10,14,14), Encounter(307,10,15,15), Encounter(433,10,14,14), Encounter(66,10,14,14), Encounter(433,5,16,16), Encounter(436,5,14,14), Encounter(66,4,15,15), Encounter(436,4,16,16), Encounter(66,1,15,15), Encounter(436,1,16,16))
ROUTE211_OUEST.setDayEncounters(307,307)
ROUTE211_OUEST.setNightEncounters(41,163)
ROUTE211_OUEST.setSwarmEncounters(307,399)
ROUTE211_OUEST.setPokeradarEncounters(236,236,236,236)
ROUTE211_OUEST.setGbaEncounters([None], [66,436], [66,436], [216,216], [66,436], [66,436])

ROUTE211_EST = EncounterTables("Route 211 - Est")
ROUTE211_EST.setBaseEncounters(Encounter(307,20,27,27), Encounter(75,20,28,28), Encounter(307,10,28,28), Encounter(307,10,29,29), Encounter(433,10,28,28), Encounter(67,10,29,29), Encounter(433,5,30,30), Encounter(436,5,29,29), Encounter(67,4,30,30), Encounter(436,4,29,29), Encounter(67,1,30,30), Encounter(436,1,29,29))
ROUTE211_EST.setDayEncounters(307,307)
ROUTE211_EST.setNightEncounters(41,164)
ROUTE211_EST.setSwarmEncounters(307,75)
ROUTE211_EST.setPokeradarEncounters(433,67,67,436)
ROUTE211_EST.setGbaEncounters([None], [67,436], [67,436], [67,436], [67,436], [67,436])

ROUTE212_SUD = EncounterTables("Route 212 - Sud")
ROUTE212_SUD.setBaseEncounters(Encounter(422,20,23,23), Encounter(195,20,24,24), Encounter(418,10,25,25), Encounter(422,10,24,24), Encounter(195,10,26,26), Encounter(422,10,25,25), Encounter(453,5,24,24), Encounter(453,5,25,25), Encounter(418,4,23,23), Encounter(422,4,26,26), Encounter(418,1,23,23), Encounter(422,1,26,26))
ROUTE212_SUD.setDayEncounters(418,422)
ROUTE212_SUD.setNightEncounters(418,422)
ROUTE212_SUD.setSwarmEncounters(422,195)
ROUTE212_SUD.setPokeradarEncounters(88,88,88,88)
ROUTE212_SUD.setGbaEncounters([None], [271,270], [418,422], [418,422], [23,23], [418,422])
ROUTE212_SUD.setSurfEncounters(Encounter(422,60,20,30), Encounter(72,30,20,30), Encounter(423,5,20,40), Encounter(423,4,20,40), Encounter(73,1,20,40))
ROUTE212_SUD.setOldRodEncounters(Encounter(129,40,4,6), Encounter(129,40,3,7), Encounter(129,15,5,10), Encounter(129,4,5,10), Encounter(129,1,5,15))
ROUTE212_SUD.setGoodRodEncounters(Encounter(129,40,15,20), Encounter(223,40,15,20), Encounter(129,15,10,25), Encounter(223,4,10,25), Encounter(223,1,10,25))
ROUTE212_SUD.setSuperRodEncounters(Encounter(130,40,30,40), Encounter(224,40,30,40), Encounter(130,15,40,55), Encounter(224,4,40,55), Encounter(224,1,40,55))

ROUTE212_NORD = EncounterTables("Route 212 - Nord")
ROUTE212_NORD.setBaseEncounters(Encounter(315,20,23,23), Encounter(183,20,21,21), Encounter(397,10,23,23), Encounter(281,10,22,22), Encounter(315,10,22,22), Encounter(397,10,21,21), Encounter(281,5,24,24), Encounter(281,5,24,24), Encounter(315,4,24,24), Encounter(183,4,23,23), Encounter(315,1,24,24), Encounter(183,1,23,23))
ROUTE212_NORD.setDayEncounters(397,280)
ROUTE212_NORD.setNightEncounters(183,183)
ROUTE212_NORD.setSwarmEncounters(315,183)
ROUTE212_NORD.setPokeradarEncounters(235,235,235,235)
ROUTE212_NORD.setGbaEncounters([None], [315,183], [315,183], [315,183], [315,183], [315,183])
ROUTE212_NORD.setSurfEncounters(Encounter(54,60,20,30), Encounter(54,30,20,30), Encounter(55,5,20,40), Encounter(55,4,20,40), Encounter(55,1,20,40))
ROUTE212_NORD.setOldRodEncounters(Encounter(129,40,4,6), Encounter(129,40,3,7), Encounter(129,15,5,10), Encounter(129,4,5,10), Encounter(129,1,5,15))
ROUTE212_NORD.setGoodRodEncounters(Encounter(129,40,15,20), Encounter(118,40,15,20), Encounter(129,15,10,25), Encounter(118,4,10,25), Encounter(118,1,10,25))
ROUTE212_NORD.setSuperRodEncounters(Encounter(130,40,30,40), Encounter(119,40,30,40), Encounter(130,15,40,55), Encounter(119,4,40,55), Encounter(119,1,40,55))

ROUTE213 = EncounterTables("Route 213")
ROUTE213.setBaseEncounters(Encounter(422,20,24,24), Encounter(418,20,23,23), Encounter(441,10,23,23), Encounter(441,10,25,25), Encounter(278,10,25,25), Encounter(422,10,25,25), Encounter(278,5,24,24), Encounter(278,5,26,26), Encounter(418,4,25,25), Encounter(422,4,26,26), Encounter(418,1,25,25), Encounter(422,1,26,26))
ROUTE213.setDayEncounters(441,441)
ROUTE213.setNightEncounters(422,418)
ROUTE213.setSwarmEncounters(422,418)
ROUTE213.setPokeradarEncounters(277,277,277,277)
ROUTE213.setGbaEncounters([None], [418,422], [418,422], [418,422], [418,422], [418,422])
ROUTE213.setSurfEncounters(Encounter(72,60,20,30), Encounter(278,30,20,30), Encounter(73,5,20,40), Encounter(422,4,20,30), Encounter(423,1,20,40))
ROUTE213.setOldRodEncounters(Encounter(129,40,4,6), Encounter(129,40,3,7), Encounter(129,15,5,10), Encounter(129,4,5,10), Encounter(129,1,5,15))
ROUTE213.setGoodRodEncounters(Encounter(129,40,15,20), Encounter(223,40,15,20), Encounter(129,15,10,25), Encounter(223,4,10,25), Encounter(223,1,10,25))
ROUTE213.setSuperRodEncounters(Encounter(130,40,30,40), Encounter(224,40,30,40), Encounter(130,15,40,55), Encounter(224,4,40,55), Encounter(224,1,40,55))

ROUTE214 = EncounterTables("Route 214")
ROUTE214.setBaseEncounters(Encounter(75,20,23,23), Encounter(74,20,21,21), Encounter(75,10,22,22), Encounter(111,10,22,22), Encounter(228,10,23,23), Encounter(111,10,23,23), Encounter(75,5,24,24), Encounter(111,5,21,21), Encounter(228,4,24,24), Encounter(111,4,24,24), Encounter(228,1,24,24), Encounter(111,1,24,24))
ROUTE214.setDayEncounters(75,111)
ROUTE214.setNightEncounters(228,41)
ROUTE214.setSwarmEncounters(325,325)
ROUTE214.setPokeradarEncounters(261,261,261,261)
ROUTE214.setGbaEncounters([None], [228,111], [228,111], [228,111], [228,111], [37,37])
ROUTE214.setSurfEncounters(Encounter(54,60,20,30), Encounter(54,30,20,30), Encounter(55,5,20,40), Encounter(55,4,20,40), Encounter(55,1,20,40))
ROUTE214.setOldRodEncounters(Encounter(129,40,4,6), Encounter(129,40,3,7), Encounter(129,15,5,10), Encounter(129,4,5,10), Encounter(129,1,5,15))
ROUTE214.setGoodRodEncounters(Encounter(129,40,15,20), Encounter(118,40,15,20), Encounter(129,15,10,25), Encounter(118,4,10,25), Encounter(118,1,10,25))
ROUTE214.setSuperRodEncounters(Encounter(130,40,30,40), Encounter(119,40,30,40), Encounter(130,15,40,55), Encounter(119,4,40,55), Encounter(119,1,40,55))

ROUTE215 = EncounterTables("Route 215")
ROUTE215.setBaseEncounters(Encounter(397,20,19,19), Encounter(183,20,20,20), Encounter(123,10,22,22), Encounter(397,10,21,21), Encounter(108,10,20,20), Encounter(63,10,19,19), Encounter(123,5,20,20), Encounter(64,5,21,21), Encounter(183,4,22,22), Encounter(64,4,22,22), Encounter(183,1,22,22), Encounter(64,1,22,22))
ROUTE215.setDayEncounters(397,397)
ROUTE215.setNightEncounters(183,183)
ROUTE215.setSwarmEncounters(96,96)
ROUTE215.setPokeradarEncounters(108,63,183,64)
ROUTE215.setGbaEncounters([None], [183,64], [183,64], [183,64], [183,64], [183,64])

ROUTE216 = EncounterTables("Route 216")
ROUTE216.setBaseEncounters(Encounter(459,20,32,32), Encounter(215,20,33,33), Encounter(307,10,32,32), Encounter(459,10,33,33), Encounter(307,10,33,33), Encounter(215,10,34,34), Encounter(459,5,34,34), Encounter(215,5,35,35), Encounter(75,4,35,35), Encounter(459,4,35,35), Encounter(75,1,35,35), Encounter(459,1,35,35))
ROUTE216.setDayEncounters(307,459)
ROUTE216.setNightEncounters(41,361)
ROUTE216.setSwarmEncounters(459,215)
ROUTE216.setPokeradarEncounters(307,215,75,459)
ROUTE216.setGbaEncounters([None], [75,459], [75,459], [217,217], [75,459], [75,459])

ROUTE217 = EncounterTables("Route 217")
ROUTE217.setBaseEncounters(Encounter(459,20,32,32), Encounter(220,20,33,33), Encounter(215,10,33,33), Encounter(459,10,33,33), Encounter(215,10,34,34), Encounter(220,10,34,34), Encounter(459,5,34,34), Encounter(220,5,32,32), Encounter(215,4,35,35), Encounter(459,4,35,35), Encounter(215,1,35,35), Encounter(459,1,35,35))
ROUTE217.setDayEncounters(215,459)
ROUTE217.setNightEncounters(361,361)
ROUTE217.setSwarmEncounters(225,225)
ROUTE217.setPokeradarEncounters(221,221,221,221)
ROUTE217.setGbaEncounters([None], [215,459], [215,459], [217,217], [215,459], [215,459])

ROUTE218 = EncounterTables("Route 218")
ROUTE218.setBaseEncounters(Encounter(423,20,28,28), Encounter(419,20,29,29), Encounter(441,10,28,28), Encounter(441,10,30,30), Encounter(122,10,29,29), Encounter(122,10,30,30), Encounter(419,5,30,30), Encounter(122,5,31,31), Encounter(419,4,31,31), Encounter(423,4,30,30), Encounter(419,1,31,31), Encounter(423,1,30,30))
ROUTE218.setDayEncounters(441,441)
ROUTE218.setNightEncounters(423,419)
ROUTE218.setSwarmEncounters(100,100)
ROUTE218.setPokeradarEncounters(122,122,419,423)
ROUTE218.setGbaEncounters([None], [419,423], [419,423], [419,423], [419,423], [419,423])
ROUTE218.setSurfEncounters(Encounter(72,60,20,30), Encounter(422,30,20,30), Encounter(73,5,20,40), Encounter(73,4,20,40), Encounter(423,1,20,40))
ROUTE218.setOldRodEncounters(Encounter(129,40,4,6), Encounter(129,40,3,7), Encounter(129,15,5,10), Encounter(129,4,5,10), Encounter(129,1,5,15))
ROUTE218.setGoodRodEncounters(Encounter(129,40,15,20), Encounter(456,40,15,20), Encounter(129,15,10,25), Encounter(456,4,10,25), Encounter(456,1,10,25))
ROUTE218.setSuperRodEncounters(Encounter(130,40,30,40), Encounter(457,40,30,40), Encounter(130,15,40,55), Encounter(457,4,40,55), Encounter(457,1,40,55))

ROUTE219 = EncounterTables("Route 219")
ROUTE219.setSurfEncounters(Encounter(72,60,20,30), Encounter(278,30,20,30), Encounter(73,5,20,40), Encounter(73,4,20,40), Encounter(279,1,20,40))
ROUTE219.setOldRodEncounters(Encounter(129,40,4,6), Encounter(129,40,3,7), Encounter(129,15,5,10), Encounter(129,4,5,10), Encounter(129,1,5,15))
ROUTE219.setGoodRodEncounters(Encounter(129,40,15,20), Encounter(456,40,15,20), Encounter(129,15,10,25), Encounter(457,4,25,35), Encounter(457,1,25,35))
ROUTE219.setSuperRodEncounters(Encounter(130,40,30,40), Encounter(457,40,30,40), Encounter(130,15,40,55), Encounter(457,4,40,55), Encounter(457,1,40,55))

ROUTE220 = EncounterTables("Route 220")
ROUTE220.setSurfEncounters(Encounter(72,60,20,30), Encounter(278,30,20,30), Encounter(73,5,20,40), Encounter(73,4,20,40), Encounter(279,1,20,40))
ROUTE220.setOldRodEncounters(Encounter(129,40,4,6), Encounter(129,40,3,7), Encounter(129,15,5,10), Encounter(129,4,5,10), Encounter(129,1,5,15))
ROUTE220.setGoodRodEncounters(Encounter(129,40,15,20), Encounter(456,40,15,20), Encounter(129,15,10,25), Encounter(457,4,25,35), Encounter(457,1,25,35))
ROUTE220.setSuperRodEncounters(Encounter(130,40,30,55), Encounter(457,40,30,40), Encounter(170,15,20,50), Encounter(457,4,40,55), Encounter(457,1,40,55))

ROUTE221 = EncounterTables("Route 221")
ROUTE221.setBaseEncounters(Encounter(419,20,29,29), Encounter(203,20,28,28), Encounter(315,10,28,28), Encounter(315,10,29,29), Encounter(185,10,31,31), Encounter(185,10,30,30), Encounter(203,5,30,30), Encounter(185,5,29,29), Encounter(419,4,31,31), Encounter(315,4,30,30), Encounter(419,1,31,31), Encounter(315,1,30,30))
ROUTE221.setDayEncounters(315,315)
ROUTE221.setNightEncounters(419,315)
ROUTE221.setSwarmEncounters(83,83)
ROUTE221.setPokeradarEncounters(33,30,33,30)
ROUTE221.setGbaEncounters([None], [419,315], [419,315], [419,315], [419,315], [419,315])
ROUTE221.setSurfEncounters(Encounter(72,60,20,30), Encounter(278,30,20,30), Encounter(73,5,20,40), Encounter(73,4,20,40), Encounter(279,1,20,40))
ROUTE221.setOldRodEncounters(Encounter(129,40,4,6), Encounter(129,40,3,7), Encounter(129,15,5,10), Encounter(129,4,5,10), Encounter(129,1,5,15))
ROUTE221.setGoodRodEncounters(Encounter(129,40,15,20), Encounter(456,40,15,20), Encounter(129,15,10,25), Encounter(457,4,25,35), Encounter(457,1,25,35))
ROUTE221.setSuperRodEncounters(Encounter(130,40,30,40), Encounter(457,40,30,40), Encounter(130,15,40,55), Encounter(457,4,40,55), Encounter(457,1,40,55))

ROUTE222 = EncounterTables("Route 222")
ROUTE222.setBaseEncounters(Encounter(125,20,39,39), Encounter(419,20,40,40), Encounter(125,10,41,41), Encounter(441,10,38,38), Encounter(278,10,38,38), Encounter(81,10,39,39), Encounter(404,5,38,38), Encounter(404,5,40,40), Encounter(279,4,40,40), Encounter(82,4,41,41), Encounter(279,1,40,40), Encounter(82,1,41,41))
ROUTE222.setDayEncounters(125,441)
ROUTE222.setNightEncounters(419,419)
ROUTE222.setSwarmEncounters(300,300)
ROUTE222.setPokeradarEncounters(180,180,180,180)
ROUTE222.setGbaEncounters([None], [279,82], [279,82], [279,82], [279,82], [279,82])
ROUTE222.setSurfEncounters(Encounter(72,60,30,40), Encounter(278,30,30,40), Encounter(73,5,30,50), Encounter(73,4,30,50), Encounter(279,1,30,50))
ROUTE222.setOldRodEncounters(Encounter(129,40,4,6), Encounter(129,40,3,7), Encounter(129,15,5,10), Encounter(129,4,5,10), Encounter(129,1,5,15))
ROUTE222.setGoodRodEncounters(Encounter(129,40,15,20), Encounter(223,40,15,20), Encounter(129,15,10,25), Encounter(223,4,10,25), Encounter(223,1,10,25))
ROUTE222.setSuperRodEncounters(Encounter(130,40,30,40), Encounter(224,40,30,40), Encounter(130,15,40,55), Encounter(224,4,40,55), Encounter(224,1,40,55))

ROUTE223 = EncounterTables("Route 223")
ROUTE223.setSurfEncounters(Encounter(73,60,30,50), Encounter(279,30,30,50), Encounter(458,5,30,40), Encounter(458,4,30,40), Encounter(458,1,30,40))
ROUTE223.setOldRodEncounters(Encounter(129,40,4,6), Encounter(129,40,3,7), Encounter(129,15,5,10), Encounter(129,4,5,10), Encounter(129,1,5,15))
ROUTE223.setGoodRodEncounters(Encounter(129,40,15,20), Encounter(223,40,15,25), Encounter(129,15,10,25), Encounter(224,4,25,35), Encounter(224,1,25,35))
ROUTE223.setSuperRodEncounters(Encounter(130,40,30,55), Encounter(320,40,30,40), Encounter(224,15,20,50), Encounter(321,4,40,55), Encounter(321,1,40,55))

ROUTE224 = EncounterTables("Route 224")
ROUTE224.setBaseEncounters(Encounter(419,20,50,50), Encounter(315,20,50,50), Encounter(69,10,49,49), Encounter(69,10,49,49), Encounter(279,10,51,51), Encounter(423,10,49,49), Encounter(44,5,51,51), Encounter(70,5,51,51), Encounter(267,4,52,52), Encounter(269,4,52,52), Encounter(267,1,52,52), Encounter(269,1,52,52))
ROUTE224.setDayEncounters(69,69)
ROUTE224.setNightEncounters(43,43)
ROUTE224.setSwarmEncounters(177,177)
ROUTE224.setPokeradarEncounters(279,423,267,269)
ROUTE224.setGbaEncounters([None], [267,269], [267,269], [213,213], [267,269], [267,269])
ROUTE224.setSurfEncounters(Encounter(279,60,35,55), Encounter(73,30,35,55), Encounter(423,5,35,55), Encounter(423,4,35,55), Encounter(423,1,35,55))
ROUTE224.setOldRodEncounters(Encounter(129,40,4,6), Encounter(129,40,3,7), Encounter(129,15,5,10), Encounter(129,4,5,10), Encounter(129,1,5,15))
ROUTE224.setGoodRodEncounters(Encounter(129,40,15,20), Encounter(223,40,15,25), Encounter(129,15,10,25), Encounter(223,4,10,25), Encounter(223,1,10,25))
ROUTE224.setSuperRodEncounters(Encounter(130,40,30,55), Encounter(224,40,30,40), Encounter(370,15,20,30), Encounter(224,4,40,55), Encounter(224,1,40,55))

ROUTE225 = EncounterTables("Route 225")
ROUTE225.setBaseEncounters(Encounter(67,20,48,48), Encounter(75,20,49,49), Encounter(22,10,48,48), Encounter(22,10,50,50), Encounter(22,10,49,49), Encounter(20,10,50,50), Encounter(67,5,50,50), Encounter(20,5,49,49), Encounter(21,4,47,47), Encounter(19,4,47,47), Encounter(21,1,47,47), Encounter(19,1,47,47))
ROUTE225.setDayEncounters(22,22)
ROUTE225.setNightEncounters(354,354)
ROUTE225.setSwarmEncounters(296,296)
ROUTE225.setPokeradarEncounters(57,57,56,56)
ROUTE225.setGbaEncounters([None], [21,19], [21,19], [21,19], [21,19], [21,19])
ROUTE225.setSurfEncounters(Encounter(55,60,35,55), Encounter(55,30,35,55), Encounter(54,5,35,45), Encounter(54,4,35,45), Encounter(54,1,35,45))
ROUTE225.setOldRodEncounters(Encounter(129,40,4,6), Encounter(129,40,3,7), Encounter(129,15,5,10), Encounter(129,4,5,10), Encounter(129,1,5,15))
ROUTE225.setGoodRodEncounters(Encounter(129,40,15,20), Encounter(339,40,15,20), Encounter(129,15,10,25), Encounter(339,4,10,25), Encounter(339,1,10,25))
ROUTE225.setSuperRodEncounters(Encounter(130,40,30,40), Encounter(340,40,30,40), Encounter(130,15,40,55), Encounter(340,4,40,55), Encounter(340,1,40,55))

ROUTE226 = EncounterTables("Route 226")
ROUTE226.setBaseEncounters(Encounter(67,20,48,48), Encounter(75,20,49,49), Encounter(22,10,48,48), Encounter(22,10,50,50), Encounter(278,10,49,49), Encounter(20,10,50,50), Encounter(67,5,50,50), Encounter(20,5,49,49), Encounter(278,4,47,47), Encounter(19,4,47,47), Encounter(278,1,47,47), Encounter(19,1,47,47))
ROUTE226.setDayEncounters(22,22)
ROUTE226.setNightEncounters(354,354)
ROUTE226.setSwarmEncounters(98,98)
ROUTE226.setPokeradarEncounters(57,57,56,56)
ROUTE226.setGbaEncounters([None], [278,19], [278,19], [278,19], [278,19], [278,19])
ROUTE226.setSurfEncounters(Encounter(278,60,35,45), Encounter(279,30,35,55), Encounter(73,5,35,55), Encounter(73,4,35,55), Encounter(73,1,35,55))
ROUTE226.setOldRodEncounters(Encounter(129,40,4,6), Encounter(129,40,3,7), Encounter(129,15,5,10), Encounter(129,4,5,10), Encounter(129,1,5,15))
ROUTE226.setGoodRodEncounters(Encounter(129,40,15,20), Encounter(116,40,15,20), Encounter(129,15,10,25), Encounter(116,4,10,25), Encounter(116,1,10,25))
ROUTE226.setSuperRodEncounters(Encounter(130,40,30,55), Encounter(117,40,30,40), Encounter(369,15,20,50), Encounter(117,4,40,55), Encounter(117,1,40,55))

ROUTE227 = EncounterTables("Route 227")
ROUTE227.setBaseEncounters(Encounter(323,20,53,53), Encounter(112,20,54,54), Encounter(22,10,51,51), Encounter(75,10,51,51), Encounter(22,10,53,53), Encounter(110,10,52,52), Encounter(227,5,53,53), Encounter(75,5,53,53), Encounter(322,4,51,51), Encounter(111,4,52,52), Encounter(322,1,51,51), Encounter(111,1,52,52))
ROUTE227.setDayEncounters(22,75)
ROUTE227.setNightEncounters(42,75)
ROUTE227.setSwarmEncounters(327,327)
ROUTE227.setPokeradarEncounters(324,324,324,324)
ROUTE227.setGbaEncounters([None], [322,111], [322,111], [322,111], [322,111], [322,111])
ROUTE227.setSurfEncounters(Encounter(61,60,35,55), Encounter(60,30,35,45), Encounter(61,5,35,55), Encounter(61,4,35,55), Encounter(61,1,35,55))
ROUTE227.setOldRodEncounters(Encounter(129,40,4,6), Encounter(129,40,3,7), Encounter(129,15,5,10), Encounter(129,4,5,10), Encounter(129,1,5,15))
ROUTE227.setGoodRodEncounters(Encounter(129,40,15,20), Encounter(339,40,15,20), Encounter(129,15,10,25), Encounter(339,4,10,25), Encounter(339,1,10,25))
ROUTE227.setSuperRodEncounters(Encounter(130,40,30,40), Encounter(340,40,30,40), Encounter(130,15,40,55), Encounter(340,4,40,55), Encounter(340,1,40,55))

ROUTE228 = EncounterTables("Route 228")
ROUTE228.setBaseEncounters(Encounter(51,20,51,51), Encounter(332,20,52,52), Encounter(450,10,50,50), Encounter(112,10,50,50), Encounter(112,10,52,52), Encounter(450,10,51,51), Encounter(51,5,52,52), Encounter(51,5,50,50), Encounter(50,4,49,49), Encounter(331,4,50,50), Encounter(50,1,49,49), Encounter(331,1,50,50))
ROUTE228.setDayEncounters(450,112)
ROUTE228.setNightEncounters(332,332)
ROUTE228.setSwarmEncounters(374,374)
ROUTE228.setPokeradarEncounters(112,450,50,331)
ROUTE228.setGbaEncounters([None], [50,331], [50,331], [50,331], [50,331], [28,28])
ROUTE228.setSurfEncounters(Encounter(61,60,35,55), Encounter(60,30,35,45), Encounter(61,5,35,55), Encounter(61,4,35,55), Encounter(61,1,35,55))
ROUTE228.setOldRodEncounters(Encounter(129,40,4,6), Encounter(129,40,3,7), Encounter(129,15,5,10), Encounter(129,4,5,10), Encounter(129,1,5,15))
ROUTE228.setGoodRodEncounters(Encounter(129,40,15,20), Encounter(339,40,15,20), Encounter(129,15,10,25), Encounter(340,4,25,35), Encounter(340,1,25,35))
ROUTE228.setSuperRodEncounters(Encounter(130,40,30,40), Encounter(340,40,30,40), Encounter(130,15,40,55), Encounter(340,4,40,55), Encounter(340,1,40,55))

ROUTE229 = EncounterTables("Route 229")
ROUTE229.setBaseEncounters(Encounter(315,20,48,48), Encounter(315,20,49,49), Encounter(166,10,50,50), Encounter(166,10,50,50), Encounter(313,10,49,49), Encounter(314,10,49,49), Encounter(16,5,47,47), Encounter(315,5,50,50), Encounter(267,4,48,48), Encounter(269,4,48,48), Encounter(267,1,48,48), Encounter(269,1,48,48))
ROUTE229.setDayEncounters(16,16)
ROUTE229.setNightEncounters(168,168)
ROUTE229.setSwarmEncounters(127,127)
ROUTE229.setPokeradarEncounters(49,49,48,48)
ROUTE229.setGbaEncounters([None], [271,271], [274,274], [204,204], [267,269], [267,269])
ROUTE229.setSurfEncounters(Encounter(283,60,35,45), Encounter(283,30,35,45), Encounter(283,5,35,45), Encounter(284,4,35,55), Encounter(284,1,35,55))
ROUTE229.setOldRodEncounters(Encounter(129,40,4,6), Encounter(129,40,3,7), Encounter(129,15,5,10), Encounter(129,4,5,10), Encounter(129,1,5,15))
ROUTE229.setGoodRodEncounters(Encounter(129,40,15,20), Encounter(118,40,15,20), Encounter(129,15,10,25), Encounter(118,4,10,25), Encounter(118,1,10,25))
ROUTE229.setSuperRodEncounters(Encounter(130,40,30,40), Encounter(119,40,30,40), Encounter(130,15,40,55), Encounter(119,4,40,55), Encounter(119,1,40,55))

ROUTE230 = EncounterTables("Route 230")
ROUTE230.setBaseEncounters(Encounter(279,20,48,48), Encounter(419,20,48,48), Encounter(69,10,47,47), Encounter(69,10,47,47), Encounter(315,10,49,49), Encounter(279,10,50,50), Encounter(44,5,49,49), Encounter(70,5,49,49), Encounter(278,4,48,48), Encounter(419,4,50,50), Encounter(278,1,48,48), Encounter(419,1,50,50))
ROUTE230.setDayEncounters(69,69)
ROUTE230.setNightEncounters(43,43)
ROUTE230.setSwarmEncounters(222,222)
ROUTE230.setPokeradarEncounters(175,175,175,175)
ROUTE230.setGbaEncounters([None], [279,419], [279,419], [279,419], [279,419], [279,419])
ROUTE230.setSurfEncounters(Encounter(364,60,35,55), Encounter(279,30,35,55), Encounter(73,5,35,55), Encounter(73,4,35,55), Encounter(73,1,35,55))
ROUTE230.setOldRodEncounters(Encounter(129,40,4,6), Encounter(129,40,3,7), Encounter(129,15,5,10), Encounter(129,4,5,10), Encounter(129,1,5,15))
ROUTE230.setGoodRodEncounters(Encounter(129,40,15,20), Encounter(223,40,15,20), Encounter(129,15,10,25), Encounter(223,4,10,25), Encounter(223,1,10,25))
ROUTE230.setSuperRodEncounters(Encounter(130,40,30,55), Encounter(320,40,30,40), Encounter(224,15,20,50), Encounter(321,4,40,55), Encounter(321,1,40,55))


LESEOLIENNES = EncounterTables("Les Éoliennes")
LESEOLIENNES.setBaseEncounters(Encounter(422,20,9,9), Encounter(403,20,10,10), Encounter(418,10,9,9), Encounter(422,10,10,10), Encounter(418,10,10,10), Encounter(422,10,11,11), Encounter(417,5,9,9), Encounter(417,5,11,11), Encounter(418,4,11,11), Encounter(422,4,12,12), Encounter(418,1,11,11), Encounter(422,1,12,12))
LESEOLIENNES.setDayEncounters(418,422)
LESEOLIENNES.setNightEncounters(418,422)
LESEOLIENNES.setSwarmEncounters(309,309)
LESEOLIENNES.setPokeradarEncounters(179,179,179,179)
LESEOLIENNES.setGbaEncounters([None], [418,422], [418,422], [418,422], [418,422], [418,422])
LESEOLIENNES.setSurfEncounters(Encounter(422,60,20,30), Encounter(72,30,20,30), Encounter(423,5,20,40), Encounter(423,4,20,40), Encounter(73,1,20,40))
LESEOLIENNES.setOldRodEncounters(Encounter(129,40,4,6), Encounter(129,40,3,7), Encounter(129,15,5,10), Encounter(129,4,5,10), Encounter(129,1,5,15))
LESEOLIENNES.setGoodRodEncounters(Encounter(129,40,15,20), Encounter(456,40,15,20), Encounter(129,15,10,25), Encounter(456,4,10,25), Encounter(456,1,10,25))
LESEOLIENNES.setSuperRodEncounters(Encounter(130,40,30,55), Encounter(457,40,30,40), Encounter(90,15,20,50), Encounter(457,4,40,55), Encounter(457,1,40,55))

FORGEFUEGO = EncounterTables("Forge Fuego - Extérieur")
FORGEFUEGO.setBaseEncounters(Encounter(126,20,28,28), Encounter(81,20,29,29), Encounter(126,10,29,29), Encounter(419,10,29,29), Encounter(419,10,30,30), Encounter(423,10,30,30), Encounter(81,5,28,28), Encounter(81,5,30,30), Encounter(419,4,31,31), Encounter(423,4,31,31), Encounter(419,1,31,31), Encounter(423,1,31,31))
FORGEFUEGO.setDayEncounters(126,419)
FORGEFUEGO.setNightEncounters(423,419)
FORGEFUEGO.setSwarmEncounters(126,81)
FORGEFUEGO.setPokeradarEncounters(304,304,304,304)
FORGEFUEGO.setGbaEncounters([None], [419,423], [419,423], [419,423], [419,423], [419,423])
FORGEFUEGO.setSurfEncounters(Encounter(72,60,20,30), Encounter(422,30,20,30), Encounter(73,5,20,40), Encounter(73,4,20,40), Encounter(423,1,20,40))
FORGEFUEGO.setOldRodEncounters(Encounter(129,40,4,6), Encounter(129,40,3,7), Encounter(129,15,5,10), Encounter(129,4,5,10), Encounter(129,1,5,15))
FORGEFUEGO.setGoodRodEncounters(Encounter(129,40,15,20), Encounter(456,40,15,20), Encounter(129,15,10,25), Encounter(456,4,10,25), Encounter(456,1,10,25))
FORGEFUEGO.setSuperRodEncounters(Encounter(130,40,30,55), Encounter(457,40,30,40), Encounter(90,15,20,50), Encounter(457,4,40,55), Encounter(457,1,40,55))

FORETVESTIGION = EncounterTables("Forêt Vestigion")
FORETVESTIGION.setBaseEncounters(Encounter(427,20,11,11), Encounter(406,20,10,10), Encounter(265,10,10,10), Encounter(401,10,12,12), Encounter(406,10,11,11), Encounter(399,10,12,12), Encounter(266,5,12,12), Encounter(268,5,12,12), Encounter(427,4,13,13), Encounter(92,4,13,13), Encounter(267,1,14,14), Encounter(269,1,14,14))
FORETVESTIGION.setDayEncounters(265,406)
FORETVESTIGION.setNightEncounters(401,163)
FORETVESTIGION.setSwarmEncounters(287,287)
FORETVESTIGION.setPokeradarEncounters(290,290,290,290)
FORETVESTIGION.setGbaEncounters([None], [427,92], [273,273], [204,204], [10,11], [13,14])

VIEUXCHATEAU = EncounterTables("Vieux Château")
VIEUXCHATEAU.setBaseEncounters(Encounter(92,20,14,14), Encounter(92,20,15,15), Encounter(92,10,14,14), Encounter(92,10,15,15), Encounter(92,10,16,16), Encounter(92,10,17,17), Encounter(92,5,16,16), Encounter(92,5,17,17), Encounter(92,4,17,17), Encounter(92,4,17,17), Encounter(92,1,17,17), Encounter(92,1,17,17))
VIEUXCHATEAU.setDayEncounters(92,92)
VIEUXCHATEAU.setNightEncounters(92,92)
VIEUXCHATEAU.setSwarmEncounters(92,92)
VIEUXCHATEAU.setPokeradarEncounters(92,92,92,92)
VIEUXCHATEAU.setGbaEncounters([None], [92,92], [92,92], [92,92], [92,92], [92,92])

VIEUXCHATEAU_CHAMBRE4 = EncounterTables("Vieux Château - Chambre 4")
VIEUXCHATEAU_CHAMBRE4.setBaseEncounters(Encounter(92,20,14,14), Encounter(92,20,15,15), Encounter(92,10,14,14), Encounter(92,10,15,15), Encounter(92,10,16,16), Encounter(92,10,17,17), Encounter(92,5,16,16), Encounter(92,5,17,17), Encounter(92,4,17,17), Encounter(92,4,17,17), Encounter(92,1,17,17), Encounter(92,1,17,17))
VIEUXCHATEAU_CHAMBRE4.setDayEncounters(92,92)
VIEUXCHATEAU_CHAMBRE4.setNightEncounters(92,92)
VIEUXCHATEAU_CHAMBRE4.setSwarmEncounters(92,92)
VIEUXCHATEAU_CHAMBRE4.setPokeradarEncounters(92,92,92,92)
VIEUXCHATEAU_CHAMBRE4.setGbaEncounters([None], [94,92], [94,92], [94,92], [94,92], [94,92])

TOURPERDUE_REZDECHAUSSEE = EncounterTables("Tour Perdue - Rez-de-Chaussée")
TOURPERDUE_REZDECHAUSSEE.setBaseEncounters(Encounter(92,20,18,18), Encounter(41,20,17,17), Encounter(92,10,19,19), Encounter(92,10,17,17), Encounter(41,10,18,18), Encounter(92,10,17,17), Encounter(41,5,19,19), Encounter(92,5,20,20), Encounter(92,4,20,20), Encounter(92,4,20,20), Encounter(92,1,20,20), Encounter(92,1,20,20))
TOURPERDUE_REZDECHAUSSEE.setDayEncounters(92,92)
TOURPERDUE_REZDECHAUSSEE.setNightEncounters(355,355)
TOURPERDUE_REZDECHAUSSEE.setSwarmEncounters(92,41)
TOURPERDUE_REZDECHAUSSEE.setPokeradarEncounters(41,92,92,92)
TOURPERDUE_REZDECHAUSSEE.setGbaEncounters([None], [92,92], [92,92], [92,92], [92,92], [92,92])

TOURPERDUE_ETAGE2 = EncounterTables("Tour Perdue - Étage 2")
TOURPERDUE_ETAGE2.setBaseEncounters(Encounter(92,20,19,19), Encounter(41,20,18,18), Encounter(92,10,20,20), Encounter(92,10,18,18), Encounter(41,10,19,19), Encounter(92,10,18,18), Encounter(41,5,20,20), Encounter(92,5,21,21), Encounter(92,4,21,21), Encounter(92,4,21,21), Encounter(92,1,21,21), Encounter(42,1,21,21))
TOURPERDUE_ETAGE2.setDayEncounters(92,92)
TOURPERDUE_ETAGE2.setNightEncounters(355,355)
TOURPERDUE_ETAGE2.setSwarmEncounters(92,41)
TOURPERDUE_ETAGE2.setPokeradarEncounters(41,92,92,92)
TOURPERDUE_ETAGE2.setGbaEncounters([None], [92,92], [92,92], [92,92], [92,92], [92,92])

TOURPERDUE_ETAGE3 = EncounterTables("Tour Perdue - Étage 3")
TOURPERDUE_ETAGE3.setBaseEncounters(Encounter(92,20,19,19), Encounter(41,20,18,18), Encounter(92,10,20,20), Encounter(92,10,18,18), Encounter(41,10,19,19), Encounter(92,10,18,18), Encounter(41,5,20,20), Encounter(92,5,21,21), Encounter(92,4,21,21), Encounter(42,4,21,21), Encounter(92,1,21,21), Encounter(42,1,21,21))
TOURPERDUE_ETAGE3.setDayEncounters(92,92)
TOURPERDUE_ETAGE3.setNightEncounters(355,355)
TOURPERDUE_ETAGE3.setSwarmEncounters(92,41)
TOURPERDUE_ETAGE3.setPokeradarEncounters(41,92,92,92)
TOURPERDUE_ETAGE3.setGbaEncounters([None], [92,92], [92,92], [92,92], [92,92], [92,92])

TOURPERDUE_ETAGE4 = EncounterTables("Tour Perdue - Étage 4")
TOURPERDUE_ETAGE4.setBaseEncounters(Encounter(92,20,20,20), Encounter(41,20,19,19), Encounter(92,10,21,21), Encounter(92,10,19,19), Encounter(41,10,20,20), Encounter(92,10,19,19), Encounter(41,5,21,21), Encounter(42,5,22,22), Encounter(92,4,22,22), Encounter(42,4,22,22), Encounter(92,1,22,22), Encounter(42,1,22,22))
TOURPERDUE_ETAGE4.setDayEncounters(92,92)
TOURPERDUE_ETAGE4.setNightEncounters(355,355)
TOURPERDUE_ETAGE4.setSwarmEncounters(92,41)
TOURPERDUE_ETAGE4.setPokeradarEncounters(41,92,92,92)
TOURPERDUE_ETAGE4.setGbaEncounters([None], [92,92], [92,92], [92,92], [92,92], [92,92])

RUINESBONVILLE = EncounterTables("Ruines Bonville")
RUINESBONVILLE.setBaseEncounters(Encounter(201,20,20,20), Encounter(201,20,21,21), Encounter(201,10,22,22), Encounter(201,10,23,23), Encounter(201,10,24,24), Encounter(201,10,25,25), Encounter(201,5,26,26), Encounter(201,5,27,27), Encounter(201,4,28,28), Encounter(201,4,29,29), Encounter(201,1,30,30), Encounter(201,1,30,30))
RUINESBONVILLE.setDayEncounters(201,201)
RUINESBONVILLE.setNightEncounters(201,201)
RUINESBONVILLE.setSwarmEncounters(201,201)
RUINESBONVILLE.setPokeradarEncounters(201,201,201,201)
RUINESBONVILLE.setGbaEncounters([None], [201,201], [201,201], [201,201], [201,201], [201,201])

GRANDMARAIS_PARC1 = EncounterTables("Grand Marais - Parc 1")
GRANDMARAIS_PARC1.setBaseEncounters(Encounter(194,20,28,28), Encounter(400,20,28,28), Encounter(357,10,28,28), Encounter(357,10,30,30), Encounter(194,10,29,29), Encounter(195,10,30,30), Encounter(194,5,28,28), Encounter(194,5,30,30), Encounter(193,4,30,30), Encounter(114,4,30,30), Encounter(193,1,31,31), Encounter(114,1,31,31))
GRANDMARAIS_PARC1.setDayEncounters(357,357)
GRANDMARAIS_PARC1.setNightEncounters(164,164)
GRANDMARAIS_PARC1.setSwarmEncounters(194,400)
GRANDMARAIS_PARC1.setPokeradarEncounters(194,195,193,114)
GRANDMARAIS_PARC1.setGbaEncounters([None], [193,114], [193,114], [193,114], [24,24], [193,114])
GRANDMARAIS_PARC1.setSurfEncounters(Encounter(194,60,20,30), Encounter(194,30,20,30), Encounter(195,5,20,40), Encounter(195,4,20,40), Encounter(195,1,20,40))
GRANDMARAIS_PARC1.setOldRodEncounters(Encounter(129,40,3,6), Encounter(129,40,4,7), Encounter(129,15,5,10), Encounter(129,4,5,10), Encounter(129,1,5,15))
GRANDMARAIS_PARC1.setGoodRodEncounters(Encounter(129,40,15,20), Encounter(339,40,15,20), Encounter(129,15,10,25), Encounter(339,4,10,25), Encounter(339,1,10,25))
GRANDMARAIS_PARC1.setSuperRodEncounters(Encounter(130,40,30,55), Encounter(318,40,30,40), Encounter(340,15,20,50), Encounter(318,4,40,55), Encounter(318,1,40,55))

GRANDMARAIS_PARC2 = EncounterTables("Grand Marais - Parc 2")
GRANDMARAIS_PARC2.setBaseEncounters(Encounter(194,20,28,28), Encounter(400,20,28,28), Encounter(357,10,28,28), Encounter(357,10,30,30), Encounter(194,10,29,29), Encounter(195,10,30,30), Encounter(194,5,28,28), Encounter(194,5,30,30), Encounter(193,4,30,30), Encounter(114,4,30,30), Encounter(193,1,31,31), Encounter(114,1,31,31))
GRANDMARAIS_PARC2.setDayEncounters(357,357)
GRANDMARAIS_PARC2.setNightEncounters(164,164)
GRANDMARAIS_PARC2.setSwarmEncounters(194,400)
GRANDMARAIS_PARC2.setPokeradarEncounters(194,195,193,114)
GRANDMARAIS_PARC2.setGbaEncounters([None], [193,114], [193,114], [193,114], [24,24], [193,114])
GRANDMARAIS_PARC2.setSurfEncounters(Encounter(194,60,20,30), Encounter(194,30,20,30), Encounter(195,5,20,40), Encounter(195,4,20,40), Encounter(195,1,20,40))
GRANDMARAIS_PARC2.setOldRodEncounters(Encounter(129,40,3,6), Encounter(129,40,4,7), Encounter(129,15,5,10), Encounter(129,4,5,10), Encounter(129,1,5,15))
GRANDMARAIS_PARC2.setGoodRodEncounters(Encounter(129,40,15,20), Encounter(339,40,15,20), Encounter(129,15,10,25), Encounter(339,4,10,25), Encounter(339,1,10,25))
GRANDMARAIS_PARC2.setSuperRodEncounters(Encounter(130,40,30,55), Encounter(318,40,30,40), Encounter(340,15,20,50), Encounter(318,4,40,55), Encounter(318,1,40,55))

GRANDMARAIS_PARC3 = EncounterTables("Grand Marais - Parc 3")
GRANDMARAIS_PARC3.setBaseEncounters(Encounter(194,20,27,27), Encounter(400,20,27,27), Encounter(400,10,28,28), Encounter(114,10,27,27), Encounter(114,10,28,28), Encounter(195,10,29,29), Encounter(194,5,28,28), Encounter(194,5,29,29), Encounter(193,4,29,29), Encounter(114,4,29,29), Encounter(193,1,30,30), Encounter(114,1,30,30))
GRANDMARAIS_PARC3.setDayEncounters(400,114)
GRANDMARAIS_PARC3.setNightEncounters(164,163)
GRANDMARAIS_PARC3.setSwarmEncounters(194,400)
GRANDMARAIS_PARC3.setPokeradarEncounters(114,195,193,114)
GRANDMARAIS_PARC3.setGbaEncounters([None], [193,114], [193,114], [193,114], [24,24], [193,114])
GRANDMARAIS_PARC3.setSurfEncounters(Encounter(194,60,20,30), Encounter(194,30,20,30), Encounter(195,5,20,40), Encounter(195,4,20,40), Encounter(195,1,20,40))
GRANDMARAIS_PARC3.setOldRodEncounters(Encounter(129,40,3,6), Encounter(129,40,4,7), Encounter(129,15,5,10), Encounter(129,4,5,10), Encounter(129,1,5,15))
GRANDMARAIS_PARC3.setGoodRodEncounters(Encounter(129,40,15,20), Encounter(339,40,15,20), Encounter(129,15,10,25), Encounter(339,4,10,25), Encounter(339,1,10,25))
GRANDMARAIS_PARC3.setSuperRodEncounters(Encounter(130,40,30,55), Encounter(318,40,30,40), Encounter(340,15,20,50), Encounter(318,4,40,55), Encounter(318,1,40,55))

GRANDMARAIS_PARC4 = EncounterTables("Grand Marais - Parc 4")
GRANDMARAIS_PARC4.setBaseEncounters(Encounter(194,20,27,27), Encounter(400,20,27,27), Encounter(400,10,28,28), Encounter(114,10,27,27), Encounter(114,10,28,28), Encounter(195,10,29,29), Encounter(194,5,28,28), Encounter(194,5,29,29), Encounter(193,4,29,29), Encounter(114,4,29,29), Encounter(193,1,30,30), Encounter(114,1,30,30))
GRANDMARAIS_PARC4.setDayEncounters(400,114)
GRANDMARAIS_PARC4.setNightEncounters(164,163)
GRANDMARAIS_PARC4.setSwarmEncounters(194,400)
GRANDMARAIS_PARC4.setPokeradarEncounters(114,195,193,114)
GRANDMARAIS_PARC4.setGbaEncounters([None], [193,114], [193,114], [193,114], [24,24], [193,114])
GRANDMARAIS_PARC4.setSurfEncounters(Encounter(194,60,20,30), Encounter(194,30,20,30), Encounter(195,5,20,40), Encounter(195,4,20,40), Encounter(195,1,20,40))
GRANDMARAIS_PARC4.setOldRodEncounters(Encounter(129,40,3,6), Encounter(129,40,4,7), Encounter(129,15,5,10), Encounter(129,4,5,10), Encounter(129,1,5,15))
GRANDMARAIS_PARC4.setGoodRodEncounters(Encounter(129,40,15,20), Encounter(339,40,15,20), Encounter(129,15,10,25), Encounter(339,4,10,25), Encounter(339,1,10,25))
GRANDMARAIS_PARC4.setSuperRodEncounters(Encounter(130,40,30,55), Encounter(318,40,30,40), Encounter(340,15,20,50), Encounter(318,4,40,55), Encounter(318,1,40,55))

GRANDMARAIS_PARC5 = EncounterTables("Grand Marais - Parc 5")
GRANDMARAIS_PARC5.setBaseEncounters(Encounter(194,20,26,26), Encounter(400,20,26,26), Encounter(400,10,27,27), Encounter(193,10,26,26), Encounter(193,10,27,27), Encounter(195,10,28,28), Encounter(194,5,27,27), Encounter(194,5,28,28), Encounter(193,4,28,28), Encounter(114,4,28,28), Encounter(193,1,29,29), Encounter(114,1,29,29))
GRANDMARAIS_PARC5.setDayEncounters(400,193)
GRANDMARAIS_PARC5.setNightEncounters(163,163)
GRANDMARAIS_PARC5.setSwarmEncounters(194,400)
GRANDMARAIS_PARC5.setPokeradarEncounters(193,195,193,114)
GRANDMARAIS_PARC5.setGbaEncounters([None], [193,114], [193,114], [193,114], [24,24], [193,114])
GRANDMARAIS_PARC5.setSurfEncounters(Encounter(194,60,20,30), Encounter(194,30,20,30), Encounter(195,5,20,40), Encounter(195,4,20,40), Encounter(195,1,20,40))
GRANDMARAIS_PARC5.setOldRodEncounters(Encounter(129,40,3,6), Encounter(129,40,4,7), Encounter(129,15,5,10), Encounter(129,4,5,10), Encounter(129,1,5,15))
GRANDMARAIS_PARC5.setGoodRodEncounters(Encounter(129,40,15,20), Encounter(339,40,15,20), Encounter(129,15,10,25), Encounter(339,4,10,25), Encounter(339,1,10,25))
GRANDMARAIS_PARC5.setSuperRodEncounters(Encounter(130,40,30,55), Encounter(318,40,30,40), Encounter(340,15,20,50), Encounter(318,4,40,55), Encounter(318,1,40,55))

GRANDMARAIS_PARC6 = EncounterTables("Grand Marais - Parc 6")
GRANDMARAIS_PARC6.setBaseEncounters(Encounter(194,20,26,26), Encounter(400,20,26,26), Encounter(400,10,27,27), Encounter(193,10,26,26), Encounter(193,10,27,27), Encounter(195,10,28,28), Encounter(194,5,27,27), Encounter(194,5,28,28), Encounter(193,4,28,28), Encounter(114,4,28,28), Encounter(193,1,29,29), Encounter(114,1,29,29))
GRANDMARAIS_PARC6.setDayEncounters(400,193)
GRANDMARAIS_PARC6.setNightEncounters(163,163)
GRANDMARAIS_PARC6.setSwarmEncounters(194,400)
GRANDMARAIS_PARC6.setPokeradarEncounters(193,195,193,114)
GRANDMARAIS_PARC6.setGbaEncounters([None], [193,114], [193,114], [193,114], [24,24], [193,114])
GRANDMARAIS_PARC6.setSurfEncounters(Encounter(194,60,20,30), Encounter(194,30,20,30), Encounter(195,5,20,40), Encounter(195,4,20,40), Encounter(195,1,20,40))
GRANDMARAIS_PARC6.setOldRodEncounters(Encounter(129,40,3,6), Encounter(129,40,4,7), Encounter(129,15,5,10), Encounter(129,4,5,10), Encounter(129,1,5,15))
GRANDMARAIS_PARC6.setGoodRodEncounters(Encounter(129,40,15,20), Encounter(339,40,15,20), Encounter(129,15,10,25), Encounter(339,4,10,25), Encounter(339,1,10,25))
GRANDMARAIS_PARC6.setSuperRodEncounters(Encounter(130,40,30,55), Encounter(318,40,30,40), Encounter(340,15,20,50), Encounter(318,4,40,55), Encounter(318,1,40,55))

JARDINTROPHEE = EncounterTables("Jardin Trophée")
JARDINTROPHEE.setBaseEncounters(Encounter(172,20,21,21), Encounter(315,20,22,22), Encounter(397,10,22,22), Encounter(402,10,23,23), Encounter(315,10,23,23), Encounter(397,10,24,24), Encounter(25,5,22,22), Encounter(172,5,22,22), Encounter(25,4,24,24), Encounter(172,4,22,22), Encounter(25,1,24,24), Encounter(172,1,22,22))
JARDINTROPHEE.setDayEncounters(397,397)
JARDINTROPHEE.setNightEncounters(402,402)
JARDINTROPHEE.setSwarmEncounters(172,315)
JARDINTROPHEE.setPokeradarEncounters(315,397,25,172)
JARDINTROPHEE.setGbaEncounters([None], [25,172], [25,172], [25,172], [25,172], [25,172])


LIGUEPOKEMON_EXTERIEUR = EncounterTables("Ligue Pokémon - Extérieur")
LIGUEPOKEMON_EXTERIEUR.setSurfEncounters(Encounter(278,60,30,40), Encounter(279,30,30,50), Encounter(279,5,30,50), Encounter(73,4,30,50), Encounter(73,1,30,50))
LIGUEPOKEMON_EXTERIEUR.setOldRodEncounters(Encounter(129,40,4,6), Encounter(129,40,3,7), Encounter(129,15,5,10), Encounter(129,4,5,10), Encounter(129,1,5,15))
LIGUEPOKEMON_EXTERIEUR.setGoodRodEncounters(Encounter(129,40,15,20), Encounter(223,40,15,20), Encounter(129,15,10,25), Encounter(223,4,10,25), Encounter(223,1,10,25))
LIGUEPOKEMON_EXTERIEUR.setSuperRodEncounters(Encounter(130,40,30,55), Encounter(224,40,30,40), Encounter(370,15,20,30), Encounter(224,4,40,55), Encounter(224,1,40,55))

SOURCEADIEU = EncounterTables("Source Adieu")
SOURCEADIEU.setBaseEncounters(Encounter(75,20,38,38), Encounter(400,20,37,37), Encounter(75,10,39,39), Encounter(397,10,38,38), Encounter(400,10,38,38), Encounter(397,10,40,40), Encounter(75,5,37,37), Encounter(433,5,37,37), Encounter(356,4,40,40), Encounter(433,4,39,39), Encounter(356,1,40,40), Encounter(433,1,39,39))
SOURCEADIEU.setDayEncounters(75,397)
SOURCEADIEU.setNightEncounters(356,42)
SOURCEADIEU.setSwarmEncounters(75,400)
SOURCEADIEU.setPokeradarEncounters(400,397,356,433)
SOURCEADIEU.setGbaEncounters([None], [337,337], [338,338], [356,433], [356,433], [356,433])
SOURCEADIEU.setSurfEncounters(Encounter(55,60,20,40), Encounter(55,30,20,40), Encounter(55,5,20,40), Encounter(55,4,20,40), Encounter(55,1,20,40))
SOURCEADIEU.setOldRodEncounters(Encounter(129,40,4,6), Encounter(129,40,3,7), Encounter(129,15,5,10), Encounter(129,4,5,10), Encounter(129,1,5,15))
SOURCEADIEU.setGoodRodEncounters(Encounter(129,40,15,20), Encounter(118,40,15,20), Encounter(129,15,10,25), Encounter(118,4,10,25), Encounter(118,1,10,25))
SOURCEADIEU.setSuperRodEncounters(Encounter(130,40,30,40), Encounter(119,40,30,40), Encounter(130,15,40,55), Encounter(119,4,40,55), Encounter(119,1,40,55))

ENTREECHARBOURG = EncounterTables("Entrée Charbourg")
ENTREECHARBOURG.setBaseEncounters(Encounter(41,20,5,5), Encounter(54,20,5,5), Encounter(41,10,6,6), Encounter(54,10,6,6), Encounter(74,10,5,5), Encounter(41,10,5,5), Encounter(54,5,7,7), Encounter(74,5,7,7), Encounter(41,4,7,7), Encounter(41,4,8,8), Encounter(41,1,7,7), Encounter(41,1,8,8))
ENTREECHARBOURG.setDayEncounters(41,54)
ENTREECHARBOURG.setNightEncounters(41,54)
ENTREECHARBOURG.setSwarmEncounters(41,54)
ENTREECHARBOURG.setPokeradarEncounters(74,41,41,41)
ENTREECHARBOURG.setGbaEncounters([None], [41,41], [41,41], [41,41], [41,41], [41,41])

ENTREECHARBOURG_SOUSSOL = EncounterTables("Entrée Charbourg - Sous-Sol")
ENTREECHARBOURG_SOUSSOL.setBaseEncounters(Encounter(41,20,6,6), Encounter(54,20,8,8), Encounter(41,10,7,7), Encounter(54,10,9,9), Encounter(74,10,6,6), Encounter(41,10,8,8), Encounter(54,5,10,10), Encounter(74,5,8,8), Encounter(41,4,9,9), Encounter(42,4,10,10), Encounter(41,1,9,9), Encounter(42,1,10,10))
ENTREECHARBOURG_SOUSSOL.setDayEncounters(41,54)
ENTREECHARBOURG_SOUSSOL.setNightEncounters(41,54)
ENTREECHARBOURG_SOUSSOL.setSwarmEncounters(41,54)
ENTREECHARBOURG_SOUSSOL.setPokeradarEncounters(74,41,41,42)
ENTREECHARBOURG_SOUSSOL.setGbaEncounters([None], [41,42], [41,42], [41,42], [41,42], [41,42])
ENTREECHARBOURG_SOUSSOL.setSurfEncounters(Encounter(54,60,20,30), Encounter(41,30,20,30), Encounter(55,5,20,40), Encounter(42,4,20,40), Encounter(42,1,20,40))
ENTREECHARBOURG_SOUSSOL.setOldRodEncounters(Encounter(129,40,4,6), Encounter(129,40,3,7), Encounter(129,15,5,10), Encounter(129,4,5,10), Encounter(129,1,5,15))
ENTREECHARBOURG_SOUSSOL.setGoodRodEncounters(Encounter(129,40,15,20), Encounter(339,40,15,20), Encounter(129,15,10,25), Encounter(339,4,10,25), Encounter(339,1,10,25))
ENTREECHARBOURG_SOUSSOL.setSuperRodEncounters(Encounter(130,40,30,55), Encounter(340,40,30,40), Encounter(130,15,40,55), Encounter(340,4,40,55), Encounter(340,1,40,55))

MINECHARBOURG_ENTREE = EncounterTables("Mine Charbourg - Entrée")
MINECHARBOURG_ENTREE.setBaseEncounters(Encounter(74,20,5,5), Encounter(74,20,6,6), Encounter(41,10,5,5), Encounter(41,10,6,6), Encounter(74,10,4,4), Encounter(74,10,7,7), Encounter(95,5,6,6), Encounter(95,5,8,8), Encounter(74,4,8,8), Encounter(41,4,7,7), Encounter(74,1,8,8), Encounter(41,1,7,7))
MINECHARBOURG_ENTREE.setDayEncounters(41,41)
MINECHARBOURG_ENTREE.setNightEncounters(41,41)
MINECHARBOURG_ENTREE.setSwarmEncounters(74,74)
MINECHARBOURG_ENTREE.setPokeradarEncounters(74,74,74,74)
MINECHARBOURG_ENTREE.setGbaEncounters([None], [74,74], [74,74], [74,74], [74,74], [74,74])

MINECHARBOURG = EncounterTables("Mine Charbourg")
MINECHARBOURG.setBaseEncounters(Encounter(74,20,6,6), Encounter(74,20,7,7), Encounter(41,10,6,6), Encounter(41,10,7,7), Encounter(74,10,5,5), Encounter(74,10,8,8), Encounter(95,5,7,7), Encounter(95,5,9,9), Encounter(74,4,9,9), Encounter(41,4,8,8), Encounter(74,1,9,9), Encounter(41,1,8,8))
MINECHARBOURG.setDayEncounters(41,41)
MINECHARBOURG.setNightEncounters(41,41)
MINECHARBOURG.setSwarmEncounters(74,74)
MINECHARBOURG.setPokeradarEncounters(74,74,74,74)
MINECHARBOURG.setGbaEncounters([None], [74,74], [74,74], [74,74], [74,74], [74,74])

CHEMINROCHEUX = EncounterTables("Chemin Rocheux")
CHEMINROCHEUX.setBaseEncounters(Encounter(41,20,4,4), Encounter(54,20,4,4), Encounter(41,10,5,5), Encounter(54,10,5,5), Encounter(41,10,3,3), Encounter(41,10,3,3), Encounter(54,5,6,6), Encounter(41,5,6,6), Encounter(41,4,6,6), Encounter(41,4,6,6), Encounter(41,1,6,6), Encounter(41,1,6,6))
CHEMINROCHEUX.setDayEncounters(41,54)
CHEMINROCHEUX.setNightEncounters(41,54)
CHEMINROCHEUX.setSwarmEncounters(41,54)
CHEMINROCHEUX.setPokeradarEncounters(41,41,41,41)
CHEMINROCHEUX.setGbaEncounters([None], [41,41], [41,41], [41,41], [41,41], [41,41])
CHEMINROCHEUX.setSurfEncounters(Encounter(54,60,20,30), Encounter(41,30,20,30), Encounter(55,5,20,40), Encounter(42,4,20,40), Encounter(42,1,20,40))
CHEMINROCHEUX.setOldRodEncounters(Encounter(129,40,4,6), Encounter(129,40,3,7), Encounter(129,15,5,10), Encounter(129,4,5,10), Encounter(129,1,5,15))
CHEMINROCHEUX.setGoodRodEncounters(Encounter(129,40,15,20), Encounter(339,40,15,20), Encounter(129,15,10,25), Encounter(339,4,10,25), Encounter(339,1,10,25))
CHEMINROCHEUX.setSuperRodEncounters(Encounter(130,40,30,55), Encounter(340,40,30,40), Encounter(130,15,40,55), Encounter(340,4,40,55), Encounter(340,1,40,55))

GROTTEREVECHE = EncounterTables("Grotte Revêche")
GROTTEREVECHE.setBaseEncounters(Encounter(436,20,18,18), Encounter(74,20,18,18), Encounter(74,10,17,17), Encounter(41,10,19,19), Encounter(436,10,20,20), Encounter(95,10,20,20), Encounter(74,5,19,19), Encounter(74,5,20,20), Encounter(41,4,17,17), Encounter(95,4,18,18), Encounter(41,1,17,17), Encounter(95,1,18,18))
GROTTEREVECHE.setDayEncounters(74,41)
GROTTEREVECHE.setNightEncounters(74,41)
GROTTEREVECHE.setSwarmEncounters(436,74)
GROTTEREVECHE.setPokeradarEncounters(436,95,74,95)
GROTTEREVECHE.setGbaEncounters([None], [74,95], [74,95], [74,95], [74,95], [27,27])

GROTTEREVECHE_SOUSSOL = EncounterTables("Grotte Revêche - Sous-Sol")
GROTTEREVECHE_SOUSSOL.setBaseEncounters(Encounter(436,20,18,18), Encounter(74,20,18,18), Encounter(443,10,17,17), Encounter(41,10,19,19), Encounter(436,10,20,20), Encounter(95,10,20,20), Encounter(443,5,19,19), Encounter(74,5,20,20), Encounter(443,4,20,20), Encounter(95,4,18,18), Encounter(443,1,20,20), Encounter(95,1,18,18))
GROTTEREVECHE_SOUSSOL.setDayEncounters(443,41)
GROTTEREVECHE_SOUSSOL.setNightEncounters(443,41)
GROTTEREVECHE_SOUSSOL.setSwarmEncounters(436,74)
GROTTEREVECHE_SOUSSOL.setPokeradarEncounters(436,95,443,95)
GROTTEREVECHE_SOUSSOL.setGbaEncounters([None], [443,95], [443,95], [443,95], [443,95], [27,27])

TUNNELRUINEMANIAC = EncounterTables("Tunnel Ruinemaniac")
TUNNELRUINEMANIAC.setBaseEncounters(Encounter(74,20,25,25), Encounter(74,20,24,24), Encounter(74,10,23,23), Encounter(74,10,25,25), Encounter(74,10,25,25), Encounter(449,10,25,25), Encounter(74,5,25,25), Encounter(449,5,25,25), Encounter(74,4,25,25), Encounter(449,4,24,24), Encounter(74,1,25,25), Encounter(449,1,26,26))
TUNNELRUINEMANIAC.setDayEncounters(74,74)
TUNNELRUINEMANIAC.setNightEncounters(74,74)
TUNNELRUINEMANIAC.setSwarmEncounters(74,74)
TUNNELRUINEMANIAC.setPokeradarEncounters(74,449,74,449)
TUNNELRUINEMANIAC.setGbaEncounters([None], [74,449], [74,449], [74,449], [74,449], [74,449])

MONTCOURONNE_PASSAGECHARBOURG = EncounterTables("Mont Couronné - Passage Charbourg")
MONTCOURONNE_PASSAGECHARBOURG.setBaseEncounters(Encounter(436,20,18,18), Encounter(74,20,19,19), Encounter(307,10,18,18), Encounter(35,10,17,17), Encounter(66,10,20,20), Encounter(307,10,20,20), Encounter(433,5,17,17), Encounter(299,5,18,18), Encounter(41,4,19,19), Encounter(433,4,19,19), Encounter(41,1,19,19), Encounter(433,1,19,19))
MONTCOURONNE_PASSAGECHARBOURG.setDayEncounters(307,74)
MONTCOURONNE_PASSAGECHARBOURG.setNightEncounters(41,35)
MONTCOURONNE_PASSAGECHARBOURG.setSwarmEncounters(436,74)
MONTCOURONNE_PASSAGECHARBOURG.setPokeradarEncounters(66,307,41,433)
MONTCOURONNE_PASSAGECHARBOURG.setGbaEncounters([None], [41,433], [41,433], [41,433], [41,433], [41,433])
MONTCOURONNE_PASSAGECHARBOURG.setSurfEncounters(Encounter(41,60,20,30), Encounter(41,30,20,30), Encounter(42,5,20,40), Encounter(42,4,20,40), Encounter(42,1,20,40))
MONTCOURONNE_PASSAGECHARBOURG.setOldRodEncounters(Encounter(129,40,4,6), Encounter(129,40,3,7), Encounter(129,15,5,10), Encounter(129,4,5,10), Encounter(129,1,5,15))
MONTCOURONNE_PASSAGECHARBOURG.setGoodRodEncounters(Encounter(129,40,15,20), Encounter(339,40,15,20), Encounter(129,15,10,25), Encounter(339,4,10,25), Encounter(339,1,10,25))
MONTCOURONNE_PASSAGECHARBOURG.setSuperRodEncounters(Encounter(130,40,30,55), Encounter(340,40,30,40), Encounter(130,15,20,55), Encounter(340,4,40,55), Encounter(340,1,40,55))

MONTCOURONNE_SALLE1 = EncounterTables("Mont Couronné - Salle 1")
MONTCOURONNE_SALLE1.setBaseEncounters(Encounter(437,20,37,37), Encounter(75,20,38,38), Encounter(308,10,37,37), Encounter(35,10,36,36), Encounter(67,10,39,39), Encounter(308,10,39,39), Encounter(433,5,36,36), Encounter(299,5,37,37), Encounter(42,4,38,38), Encounter(433,4,38,38), Encounter(42,1,38,38), Encounter(433,1,38,38))
MONTCOURONNE_SALLE1.setDayEncounters(308,75)
MONTCOURONNE_SALLE1.setNightEncounters(42,35)
MONTCOURONNE_SALLE1.setSwarmEncounters(437,75)
MONTCOURONNE_SALLE1.setPokeradarEncounters(67,308,42,433)
MONTCOURONNE_SALLE1.setGbaEncounters([None], [337,337], [338,338], [42,433], [42,433], [42,433])

MONTCOURONNE_SALLE2 = EncounterTables("Mont Couronné - Salle 2")
MONTCOURONNE_SALLE2.setBaseEncounters(Encounter(437,20,37,37), Encounter(75,20,38,38), Encounter(308,10,37,37), Encounter(35,10,36,36), Encounter(67,10,39,39), Encounter(308,10,39,39), Encounter(433,5,36,36), Encounter(299,5,37,37), Encounter(42,4,38,38), Encounter(433,4,38,38), Encounter(308,1,38,38), Encounter(433,1,38,38))
MONTCOURONNE_SALLE2.setDayEncounters(308,75)
MONTCOURONNE_SALLE2.setNightEncounters(42,35)
MONTCOURONNE_SALLE2.setSwarmEncounters(437,75)
MONTCOURONNE_SALLE2.setPokeradarEncounters(67,308,308,433)
MONTCOURONNE_SALLE2.setGbaEncounters([None], [337,337], [338,338], [42,433], [42,433], [42,433])

MONTCOURONNE_EXTERIEUR = EncounterTables("Mont Couronné - Extérieur")
MONTCOURONNE_EXTERIEUR.setBaseEncounters(Encounter(459,20,36,36), Encounter(460,20,38,38), Encounter(308,10,38,38), Encounter(460,10,39,39), Encounter(67,10,40,40), Encounter(308,10,40,40), Encounter(433,5,37,37), Encounter(299,5,38,38), Encounter(359,4,38,38), Encounter(433,4,39,39), Encounter(359,1,40,40), Encounter(433,1,39,39))
MONTCOURONNE_EXTERIEUR.setDayEncounters(308,460)
MONTCOURONNE_EXTERIEUR.setNightEncounters(42,164)
MONTCOURONNE_EXTERIEUR.setSwarmEncounters(459,460)
MONTCOURONNE_EXTERIEUR.setPokeradarEncounters(294,294,294,294)
MONTCOURONNE_EXTERIEUR.setGbaEncounters([None], [337,337], [338,338], [359,433], [359,433], [359,433])

MONTCOURONNE_SALLE3 = EncounterTables("Mont Couronné - Salle 3")
MONTCOURONNE_SALLE3.setBaseEncounters(Encounter(437,20,37,37), Encounter(75,20,38,38), Encounter(308,10,37,37), Encounter(35,10,36,36), Encounter(67,10,39,39), Encounter(308,10,39,39), Encounter(433,5,36,36), Encounter(299,5,37,37), Encounter(42,4,38,38), Encounter(433,4,38,38), Encounter(42,1,38,38), Encounter(433,1,38,38))
MONTCOURONNE_SALLE3.setDayEncounters(308,75)
MONTCOURONNE_SALLE3.setNightEncounters(42,35)
MONTCOURONNE_SALLE3.setSwarmEncounters(437,75)
MONTCOURONNE_SALLE3.setPokeradarEncounters(67,308,42,433)
MONTCOURONNE_SALLE3.setGbaEncounters([None], [337,337], [338,338], [42,433], [42,433], [42,433])
MONTCOURONNE_SALLE3.setSurfEncounters(Encounter(41,60,20,30), Encounter(41,30,20,30), Encounter(42,5,20,40), Encounter(42,4,20,40), Encounter(42,1,20,40))
MONTCOURONNE_SALLE3.setOldRodEncounters(Encounter(129,40,4,6), Encounter(129,40,3,7), Encounter(129,15,5,10), Encounter(129,4,5,10), Encounter(129,1,5,15))
MONTCOURONNE_SALLE3.setGoodRodEncounters(Encounter(129,40,15,20), Encounter(339,40,15,20), Encounter(129,15,10,25), Encounter(339,4,10,25), Encounter(339,1,10,25))
MONTCOURONNE_SALLE3.setSuperRodEncounters(Encounter(130,40,30,55), Encounter(147,40,15,25), Encounter(340,15,20,50), Encounter(148,4,20,40), Encounter(148,1,35,55))

MONTCOURONNE_SALLE4 = EncounterTables("Mont Couronné - Salle 4")
MONTCOURONNE_SALLE4.setBaseEncounters(Encounter(437,20,37,37), Encounter(75,20,38,38), Encounter(308,10,37,37), Encounter(35,10,36,36), Encounter(67,10,39,39), Encounter(308,10,39,39), Encounter(433,5,36,36), Encounter(299,5,37,37), Encounter(42,4,38,38), Encounter(433,4,38,38), Encounter(42,1,38,38), Encounter(358,1,39,39))
MONTCOURONNE_SALLE4.setDayEncounters(308,75)
MONTCOURONNE_SALLE4.setNightEncounters(42,35)
MONTCOURONNE_SALLE4.setSwarmEncounters(437,75)
MONTCOURONNE_SALLE4.setPokeradarEncounters(67,308,42,358)
MONTCOURONNE_SALLE4.setGbaEncounters([None], [337,337], [338,338], [42,433], [42,433], [42,433])

MONTCOURONNE_SALLE5 = EncounterTables("Mont Couronné - Salle 5")
MONTCOURONNE_SALLE5.setBaseEncounters(Encounter(437,20,37,37), Encounter(75,20,38,38), Encounter(308,10,37,37), Encounter(35,10,36,36), Encounter(67,10,39,39), Encounter(308,10,39,39), Encounter(433,5,36,36), Encounter(299,5,37,37), Encounter(42,4,38,38), Encounter(358,4,39,39), Encounter(42,1,38,38), Encounter(358,1,40,40))
MONTCOURONNE_SALLE5.setDayEncounters(308,75)
MONTCOURONNE_SALLE5.setNightEncounters(42,35)
MONTCOURONNE_SALLE5.setSwarmEncounters(437,75)
MONTCOURONNE_SALLE5.setPokeradarEncounters(67,308,42,358)
MONTCOURONNE_SALLE5.setGbaEncounters([None], [337,337], [338,338], [42,358], [42,358], [42,358])

MONTCOURONNE_SALLE6 = EncounterTables("Mont Couronné - Salle 6")
MONTCOURONNE_SALLE6.setBaseEncounters(Encounter(437,20,37,37), Encounter(75,20,38,38), Encounter(308,10,37,37), Encounter(35,10,36,36), Encounter(67,10,39,39), Encounter(308,10,39,39), Encounter(358,5,39,39), Encounter(299,5,37,37), Encounter(42,4,38,38), Encounter(358,4,40,40), Encounter(42,1,38,38), Encounter(358,1,41,41))
MONTCOURONNE_SALLE6.setDayEncounters(308,75)
MONTCOURONNE_SALLE6.setNightEncounters(42,35)
MONTCOURONNE_SALLE6.setSwarmEncounters(437,75)
MONTCOURONNE_SALLE6.setPokeradarEncounters(67,308,42,358)
MONTCOURONNE_SALLE6.setGbaEncounters([None], [337,337], [338,338], [42,358], [42,358], [42,358])

MONTCOURONNE_SALLE7 = EncounterTables("Mont Couronné - Salle 7")
MONTCOURONNE_SALLE7.setBaseEncounters(Encounter(75,20,37,37), Encounter(75,20,38,38), Encounter(308,10,37,37), Encounter(35,10,36,36), Encounter(67,10,39,39), Encounter(308,10,39,39), Encounter(433,5,36,36), Encounter(299,5,37,37), Encounter(42,4,38,38), Encounter(433,4,38,38), Encounter(42,1,38,38), Encounter(433,1,38,38))
MONTCOURONNE_SALLE7.setDayEncounters(308,75)
MONTCOURONNE_SALLE7.setNightEncounters(42,35)
MONTCOURONNE_SALLE7.setSwarmEncounters(75,75)
MONTCOURONNE_SALLE7.setPokeradarEncounters(67,308,42,433)
MONTCOURONNE_SALLE7.setGbaEncounters([None], [337,337], [338,338], [42,433], [42,433], [42,433])

MONTCOURONNE_PASSAGEVESTIGION = EncounterTables("Mont Couronné - Passage Vestigion")
MONTCOURONNE_PASSAGEVESTIGION.setBaseEncounters(Encounter(436,20,14,14), Encounter(74,20,15,15), Encounter(307,10,14,14), Encounter(173,10,13,13), Encounter(66,10,16,16), Encounter(307,10,16,16), Encounter(433,5,13,13), Encounter(299,5,14,14), Encounter(41,4,15,15), Encounter(433,4,15,15), Encounter(41,1,15,15), Encounter(433,1,15,15))
MONTCOURONNE_PASSAGEVESTIGION.setDayEncounters(307,74)
MONTCOURONNE_PASSAGEVESTIGION.setNightEncounters(41,173)
MONTCOURONNE_PASSAGEVESTIGION.setSwarmEncounters(436,74)
MONTCOURONNE_PASSAGEVESTIGION.setPokeradarEncounters(66,307,41,433)
MONTCOURONNE_PASSAGEVESTIGION.setGbaEncounters([None], [41,433], [41,433], [41,433], [41,433], [41,433])

MONTCOURONNE_SALLE8 = EncounterTables("Mont Couronné - Salle 8")
MONTCOURONNE_SALLE8.setBaseEncounters(Encounter(436,20,33,33), Encounter(75,20,34,34), Encounter(307,10,33,33), Encounter(35,10,32,32), Encounter(67,10,35,35), Encounter(307,10,35,35), Encounter(433,5,32,32), Encounter(299,5,33,33), Encounter(42,4,34,34), Encounter(433,4,34,34), Encounter(42,1,34,34), Encounter(433,1,34,34))
MONTCOURONNE_SALLE8.setDayEncounters(307,75)
MONTCOURONNE_SALLE8.setNightEncounters(42,35)
MONTCOURONNE_SALLE8.setSwarmEncounters(436,75)
MONTCOURONNE_SALLE8.setPokeradarEncounters(67,307,42,433)
MONTCOURONNE_SALLE8.setGbaEncounters([None], [42,433], [42,433], [42,433], [42,433], [42,433])
MONTCOURONNE_SALLE8.setSurfEncounters(Encounter(41,60,20,30), Encounter(41,30,20,30), Encounter(42,5,20,40), Encounter(42,4,20,40), Encounter(42,1,20,40))
MONTCOURONNE_SALLE8.setOldRodEncounters(Encounter(129,40,3,6), Encounter(129,40,4,7), Encounter(129,15,5,10), Encounter(129,4,5,10), Encounter(129,1,5,15))
MONTCOURONNE_SALLE8.setGoodRodEncounters(Encounter(129,40,15,20), Encounter(339,40,15,20), Encounter(129,15,10,25), Encounter(339,4,10,25), Encounter(339,1,10,25))
MONTCOURONNE_SALLE8.setSuperRodEncounters(Encounter(130,40,30,40), Encounter(340,40,30,40), Encounter(130,15,40,55), Encounter(340,4,40,55), Encounter(340,1,40,55))

MONTCOURONNE_PASSAGEFRIMAPIC = EncounterTables("Mont Couronné - Passage Frimapic")
MONTCOURONNE_PASSAGEFRIMAPIC.setBaseEncounters(Encounter(436,20,33,33), Encounter(75,20,34,34), Encounter(307,10,33,33), Encounter(35,10,32,32), Encounter(67,10,35,35), Encounter(307,10,35,35), Encounter(433,5,32,32), Encounter(299,5,33,33), Encounter(42,4,34,34), Encounter(433,4,34,34), Encounter(42,1,34,34), Encounter(433,1,34,34))
MONTCOURONNE_PASSAGEFRIMAPIC.setDayEncounters(307,75)
MONTCOURONNE_PASSAGEFRIMAPIC.setNightEncounters(42,35)
MONTCOURONNE_PASSAGEFRIMAPIC.setSwarmEncounters(436,75)
MONTCOURONNE_PASSAGEFRIMAPIC.setPokeradarEncounters(67,307,42,433)
MONTCOURONNE_PASSAGEFRIMAPIC.setGbaEncounters([None], [42,433], [42,433], [42,433], [42,433], [42,433])

ILEDEFER = EncounterTables("Ile de Fer")
ILEDEFER.setSurfEncounters(Encounter(278,60,20,30), Encounter(72,30,20,30), Encounter(279,5,20,40), Encounter(279,4,20,40), Encounter(73,1,20,40))
ILEDEFER.setOldRodEncounters(Encounter(129,40,4,6), Encounter(129,40,3,7), Encounter(129,15,5,10), Encounter(129,4,5,10), Encounter(129,1,5,15))
ILEDEFER.setGoodRodEncounters(Encounter(129,40,15,20), Encounter(456,40,15,20), Encounter(129,15,10,25), Encounter(456,4,10,25), Encounter(456,1,10,25))
ILEDEFER.setSuperRodEncounters(Encounter(130,40,30,55), Encounter(457,40,30,40), Encounter(211,15,20,50), Encounter(457,4,40,55), Encounter(457,1,40,55))

ILEDEFER_REZDECHAUSSEE = EncounterTables("Ile de Fer - Rez-de-Chaussée")
ILEDEFER_REZDECHAUSSEE.setBaseEncounters(Encounter(74,20,31,31), Encounter(75,20,32,32), Encounter(41,10,30,30), Encounter(42,10,32,32), Encounter(74,10,32,32), Encounter(75,10,33,33), Encounter(95,5,31,31), Encounter(95,5,33,33), Encounter(74,4,30,30), Encounter(75,4,31,31), Encounter(74,1,30,30), Encounter(75,1,31,31))
ILEDEFER_REZDECHAUSSEE.setDayEncounters(41,42)
ILEDEFER_REZDECHAUSSEE.setNightEncounters(41,42)
ILEDEFER_REZDECHAUSSEE.setSwarmEncounters(74,75)
ILEDEFER_REZDECHAUSSEE.setPokeradarEncounters(74,75,74,75)
ILEDEFER_REZDECHAUSSEE.setGbaEncounters([None], [74,75], [74,75], [74,75], [74,75], [74,75])

ILEDEFER_SOUSSOL1 = EncounterTables("Ile de Fer - Sous-Sol 1")
ILEDEFER_SOUSSOL1.setBaseEncounters(Encounter(75,20,31,31), Encounter(75,20,32,32), Encounter(42,10,30,30), Encounter(42,10,32,32), Encounter(75,10,32,32), Encounter(75,10,33,33), Encounter(95,5,31,31), Encounter(95,5,33,33), Encounter(75,4,30,30), Encounter(75,4,31,31), Encounter(75,1,30,30), Encounter(75,1,31,31))
ILEDEFER_SOUSSOL1.setDayEncounters(42,42)
ILEDEFER_SOUSSOL1.setNightEncounters(42,42)
ILEDEFER_SOUSSOL1.setSwarmEncounters(75,75)
ILEDEFER_SOUSSOL1.setPokeradarEncounters(75,75,75,75)
ILEDEFER_SOUSSOL1.setGbaEncounters([None], [302,302], [303,303], [75,75], [75,75], [75,75])

ILEDEFER_SOUSSOL2 = EncounterTables("Ile de Fer - Sous-Sol 2")
ILEDEFER_SOUSSOL2.setBaseEncounters(Encounter(95,20,32,32), Encounter(75,20,33,33), Encounter(42,10,31,31), Encounter(42,10,33,33), Encounter(75,10,33,33), Encounter(75,10,34,34), Encounter(208,5,33,33), Encounter(208,5,35,35), Encounter(75,4,31,31), Encounter(75,4,32,32), Encounter(75,1,31,31), Encounter(75,1,32,32))
ILEDEFER_SOUSSOL2.setDayEncounters(42,42)
ILEDEFER_SOUSSOL2.setNightEncounters(42,42)
ILEDEFER_SOUSSOL2.setSwarmEncounters(95,75)
ILEDEFER_SOUSSOL2.setPokeradarEncounters(75,75,75,75)
ILEDEFER_SOUSSOL2.setGbaEncounters([None], [302,302], [303,303], [75,75], [75,75], [75,75])

ILEDEFER_SORTIE = EncounterTables("Ile de Fer - Sortie")
ILEDEFER_SORTIE.setBaseEncounters(Encounter(208,20,32,32), Encounter(75,20,33,33), Encounter(42,10,31,31), Encounter(42,10,33,33), Encounter(75,10,33,33), Encounter(75,10,34,34), Encounter(208,5,33,33), Encounter(208,5,35,35), Encounter(75,4,31,31), Encounter(75,4,32,32), Encounter(75,1,31,31), Encounter(75,1,32,32))
ILEDEFER_SORTIE.setDayEncounters(42,42)
ILEDEFER_SORTIE.setNightEncounters(42,42)
ILEDEFER_SORTIE.setSwarmEncounters(95,75)
ILEDEFER_SORTIE.setPokeradarEncounters(75,75,75,75)
ILEDEFER_SORTIE.setGbaEncounters([None], [302,302], [303,303], [75,75], [75,75], [75,75])

TEMPLEFRIMAPIC_ENTREE = EncounterTables("Temple Frimapic - Entrée")
TEMPLEFRIMAPIC_ENTREE.setBaseEncounters(Encounter(42,20,47,47), Encounter(42,20,48,48), Encounter(42,10,49,49), Encounter(42,10,50,50), Encounter(42,10,48,48), Encounter(215,10,49,49), Encounter(238,5,47,47), Encounter(42,5,49,49), Encounter(238,4,49,49), Encounter(42,4,47,47), Encounter(238,1,49,49), Encounter(42,1,47,47))
TEMPLEFRIMAPIC_ENTREE.setDayEncounters(42,42)
TEMPLEFRIMAPIC_ENTREE.setNightEncounters(42,42)
TEMPLEFRIMAPIC_ENTREE.setSwarmEncounters(42,42)
TEMPLEFRIMAPIC_ENTREE.setPokeradarEncounters(42,215,238,42)
TEMPLEFRIMAPIC_ENTREE.setGbaEncounters([None], [238,42], [238,42], [238,42], [238,42], [238,42])

TEMPLEFRIMAPIC_SOUSSOL1 = EncounterTables("Temple Frimapic - Sous-Sol 1")
TEMPLEFRIMAPIC_SOUSSOL1.setBaseEncounters(Encounter(42,20,47,47), Encounter(42,20,48,48), Encounter(42,10,49,49), Encounter(42,10,50,50), Encounter(42,10,48,48), Encounter(215,10,49,49), Encounter(124,5,47,47), Encounter(42,5,49,49), Encounter(124,4,49,49), Encounter(42,4,47,47), Encounter(124,1,49,49), Encounter(42,1,47,47))
TEMPLEFRIMAPIC_SOUSSOL1.setDayEncounters(42,42)
TEMPLEFRIMAPIC_SOUSSOL1.setNightEncounters(42,42)
TEMPLEFRIMAPIC_SOUSSOL1.setSwarmEncounters(42,42)
TEMPLEFRIMAPIC_SOUSSOL1.setPokeradarEncounters(42,215,124,42)
TEMPLEFRIMAPIC_SOUSSOL1.setGbaEncounters([None], [124,42], [124,42], [124,42], [124,42], [124,42])

TEMPLEFRIMAPIC_SOUSSOL23 = EncounterTables("Temple Frimapic - Sous-Sol 2-3")
TEMPLEFRIMAPIC_SOUSSOL23.setBaseEncounters(Encounter(42,20,47,47), Encounter(42,20,48,48), Encounter(42,10,49,49), Encounter(42,10,50,50), Encounter(42,10,48,48), Encounter(215,10,50,50), Encounter(124,5,48,48), Encounter(42,5,49,49), Encounter(124,4,50,50), Encounter(42,4,47,47), Encounter(124,1,50,50), Encounter(42,1,47,47))
TEMPLEFRIMAPIC_SOUSSOL23.setDayEncounters(42,42)
TEMPLEFRIMAPIC_SOUSSOL23.setNightEncounters(42,42)
TEMPLEFRIMAPIC_SOUSSOL23.setSwarmEncounters(42,42)
TEMPLEFRIMAPIC_SOUSSOL23.setPokeradarEncounters(42,215,124,42)
TEMPLEFRIMAPIC_SOUSSOL23.setGbaEncounters([None], [124,42], [124,42], [124,42], [124,42], [124,42])

TEMPLEFRIMAPIC_SOUSSOL45 = EncounterTables("Temple Frimapic - Sous-Sol 4-5")
TEMPLEFRIMAPIC_SOUSSOL45.setBaseEncounters(Encounter(42,20,47,47), Encounter(42,20,48,48), Encounter(42,10,49,49), Encounter(42,10,50,50), Encounter(42,10,48,48), Encounter(215,10,51,51), Encounter(124,5,49,49), Encounter(42,5,49,49), Encounter(124,4,51,51), Encounter(42,4,47,47), Encounter(124,1,51,51), Encounter(42,1,47,47))
TEMPLEFRIMAPIC_SOUSSOL45.setDayEncounters(42,42)
TEMPLEFRIMAPIC_SOUSSOL45.setNightEncounters(42,42)
TEMPLEFRIMAPIC_SOUSSOL45.setSwarmEncounters(42,42)
TEMPLEFRIMAPIC_SOUSSOL45.setPokeradarEncounters(42,215,124,42)
TEMPLEFRIMAPIC_SOUSSOL45.setGbaEncounters([None], [124,42], [124,42], [124,42], [124,42], [124,42])

ROUTEVICTOIRE = EncounterTables("Route Victoire")
ROUTEVICTOIRE.setBaseEncounters(Encounter(75,20,40,40), Encounter(111,20,41,41), Encounter(75,10,42,42), Encounter(95,10,41,41), Encounter(95,10,42,42), Encounter(112,10,41,41), Encounter(42,5,43,43), Encounter(112,5,43,43), Encounter(208,4,42,42), Encounter(444,4,41,41), Encounter(208,1,42,42), Encounter(444,1,41,41))
ROUTEVICTOIRE.setDayEncounters(75,95)
ROUTEVICTOIRE.setNightEncounters(42,95)
ROUTEVICTOIRE.setSwarmEncounters(75,111)
ROUTEVICTOIRE.setPokeradarEncounters(95,112,208,444)
ROUTEVICTOIRE.setGbaEncounters([None], [208,444], [208,444], [208,444], [208,444], [208,444])

ROUTEVICTOIRE_SALLEOUEST = EncounterTables("Route Victoire - Salle Ouest")
ROUTEVICTOIRE_SALLEOUEST.setBaseEncounters(Encounter(82,20,41,41), Encounter(208,20,42,42), Encounter(75,10,41,41), Encounter(208,10,42,42), Encounter(208,10,44,44), Encounter(82,10,43,43), Encounter(42,5,44,44), Encounter(75,5,43,43), Encounter(95,4,42,42), Encounter(444,4,43,43), Encounter(95,1,42,42), Encounter(444,1,43,43))
ROUTEVICTOIRE_SALLEOUEST.setDayEncounters(75,208)
ROUTEVICTOIRE_SALLEOUEST.setNightEncounters(42,208)
ROUTEVICTOIRE_SALLEOUEST.setSwarmEncounters(82,208)
ROUTEVICTOIRE_SALLEOUEST.setPokeradarEncounters(208,82,95,444)
ROUTEVICTOIRE_SALLEOUEST.setGbaEncounters([None], [95,444], [95,444], [95,444], [95,444], [95,444])

ROUTEVICTOIRE_SALLEEST = EncounterTables("Route Victoire - Salle Est")
ROUTEVICTOIRE_SALLEEST.setBaseEncounters(Encounter(419,20,42,42), Encounter(184,20,41,41), Encounter(75,10,41,41), Encounter(184,10,43,43), Encounter(95,10,42,42), Encounter(419,10,44,44), Encounter(42,5,44,44), Encounter(75,5,43,43), Encounter(208,4,44,44), Encounter(444,4,43,43), Encounter(208,1,44,44), Encounter(444,1,43,43))
ROUTEVICTOIRE_SALLEEST.setDayEncounters(75,184)
ROUTEVICTOIRE_SALLEEST.setNightEncounters(42,184)
ROUTEVICTOIRE_SALLEEST.setSwarmEncounters(419,184)
ROUTEVICTOIRE_SALLEEST.setPokeradarEncounters(95,419,208,444)
ROUTEVICTOIRE_SALLEEST.setGbaEncounters([None], [208,444], [208,444], [208,444], [208,444], [208,444])
ROUTEVICTOIRE_SALLEEST.setSurfEncounters(Encounter(419,60,30,50), Encounter(419,30,30,50), Encounter(42,5,30,50), Encounter(42,4,30,50), Encounter(42,1,30,50))
ROUTEVICTOIRE_SALLEEST.setOldRodEncounters(Encounter(129,40,4,6), Encounter(129,40,3,7), Encounter(129,15,5,10), Encounter(129,4,5,10), Encounter(129,1,5,15))
ROUTEVICTOIRE_SALLEEST.setGoodRodEncounters(Encounter(129,40,15,20), Encounter(129,40,15,20), Encounter(129,15,10,25), Encounter(129,4,10,25), Encounter(129,1,10,25))
ROUTEVICTOIRE_SALLEEST.setSuperRodEncounters(Encounter(130,40,30,40), Encounter(130,40,30,40), Encounter(130,15,40,55), Encounter(130,4,40,55), Encounter(130,1,40,55))

ROUTEVICTOIRE_PASSAGEEST = EncounterTables("Route Victoire - Passage Est")
ROUTEVICTOIRE_PASSAGEEST.setBaseEncounters(Encounter(75,20,47,47), Encounter(419,20,47,47), Encounter(75,10,49,49), Encounter(95,10,48,48), Encounter(95,10,50,50), Encounter(419,10,48,48), Encounter(42,5,50,50), Encounter(419,5,49,49), Encounter(208,4,50,50), Encounter(444,4,50,50), Encounter(208,1,50,50), Encounter(444,1,50,50))
ROUTEVICTOIRE_PASSAGEEST.setDayEncounters(75,95)
ROUTEVICTOIRE_PASSAGEEST.setNightEncounters(42,95)
ROUTEVICTOIRE_PASSAGEEST.setSwarmEncounters(75,419)
ROUTEVICTOIRE_PASSAGEEST.setPokeradarEncounters(95,419,208,444)
ROUTEVICTOIRE_PASSAGEEST.setGbaEncounters([None], [208,444], [208,444], [208,444], [208,444], [208,444])

ROUTEVICTOIRE_SALLEBRUME = EncounterTables("Route Victoire - Salle Brume")
ROUTEVICTOIRE_SALLEBRUME.setBaseEncounters(Encounter(419,20,48,48), Encounter(184,20,47,47), Encounter(75,10,47,47), Encounter(184,10,49,49), Encounter(87,10,48,48), Encounter(419,10,50,50), Encounter(42,5,50,50), Encounter(75,5,49,49), Encounter(87,4,50,50), Encounter(444,4,49,49), Encounter(87,1,50,50), Encounter(444,1,49,49))
ROUTEVICTOIRE_SALLEBRUME.setDayEncounters(75,184)
ROUTEVICTOIRE_SALLEBRUME.setNightEncounters(42,184)
ROUTEVICTOIRE_SALLEBRUME.setSwarmEncounters(419,184)
ROUTEVICTOIRE_SALLEBRUME.setPokeradarEncounters(87,419,87,444)
ROUTEVICTOIRE_SALLEBRUME.setGbaEncounters([None], [87,444], [87,444], [87,444], [87,444], [87,444])
ROUTEVICTOIRE_SALLEBRUME.setSurfEncounters(Encounter(419,60,35,55), Encounter(87,30,35,55), Encounter(131,5,35,55), Encounter(131,4,35,55), Encounter(131,1,35,55))
ROUTEVICTOIRE_SALLEBRUME.setOldRodEncounters(Encounter(129,40,4,6), Encounter(129,40,3,7), Encounter(129,15,5,10), Encounter(129,4,5,10), Encounter(129,1,5,15))
ROUTEVICTOIRE_SALLEBRUME.setGoodRodEncounters(Encounter(129,40,15,20), Encounter(129,40,15,20), Encounter(129,15,10,25), Encounter(129,4,10,25), Encounter(129,1,10,25))
ROUTEVICTOIRE_SALLEBRUME.setSuperRodEncounters(Encounter(130,40,30,40), Encounter(130,40,30,40), Encounter(130,15,40,55), Encounter(130,4,40,55), Encounter(130,1,40,55))

ROUTEVICTOIRE_PASSAGEROUTE224 = EncounterTables("Route Victoire - Passage Route 224")
ROUTEVICTOIRE_PASSAGEROUTE224.setBaseEncounters(Encounter(75,20,47,47), Encounter(419,20,47,47), Encounter(75,10,49,49), Encounter(95,10,48,48), Encounter(95,10,50,50), Encounter(419,10,48,48), Encounter(42,5,49,49), Encounter(419,5,49,49), Encounter(208,4,50,50), Encounter(444,4,50,50), Encounter(208,1,50,50), Encounter(444,1,50,50))
ROUTEVICTOIRE_PASSAGEROUTE224.setDayEncounters(75,95)
ROUTEVICTOIRE_PASSAGEROUTE224.setNightEncounters(42,95)
ROUTEVICTOIRE_PASSAGEROUTE224.setSwarmEncounters(75,419)
ROUTEVICTOIRE_PASSAGEROUTE224.setPokeradarEncounters(95,419,208,444)
ROUTEVICTOIRE_PASSAGEROUTE224.setGbaEncounters([None], [208,444], [208,444], [208,444], [208,444], [208,444])

GROTTERETOUR_ENTREE = EncounterTables("Grotte Retour - Entrée")
GROTTERETOUR_ENTREE.setBaseEncounters(Encounter(92,20,15,15), Encounter(436,20,15,15), Encounter(92,10,16,16), Encounter(42,10,17,17), Encounter(92,10,17,17), Encounter(42,10,17,17), Encounter(42,5,18,18), Encounter(433,5,16,16), Encounter(355,4,18,18), Encounter(433,4,18,18), Encounter(355,1,18,18), Encounter(433,1,18,18))
GROTTERETOUR_ENTREE.setDayEncounters(92,42)
GROTTERETOUR_ENTREE.setNightEncounters(356,42)
GROTTERETOUR_ENTREE.setSwarmEncounters(92,436)
GROTTERETOUR_ENTREE.setPokeradarEncounters(92,42,356,433)
GROTTERETOUR_ENTREE.setGbaEncounters([None], [337,337], [338,338], [356,433], [356,433], [356,433])

GROTTERETOUR_AFTERFIRST = EncounterTables("Grotte Retour - Après Premier Pilier")
GROTTERETOUR_AFTERFIRST.setBaseEncounters(Encounter(93,20,25,25), Encounter(436,20,25,25), Encounter(93,10,26,26), Encounter(42,10,27,27), Encounter(93,10,27,27), Encounter(42,10,27,27), Encounter(42,5,28,28), Encounter(433,5,26,26), Encounter(355,4,28,28), Encounter(433,4,28,28), Encounter(356,1,28,28), Encounter(358,1,28,28))
GROTTERETOUR_AFTERFIRST.setDayEncounters(93,42)
GROTTERETOUR_AFTERFIRST.setNightEncounters(356,42)
GROTTERETOUR_AFTERFIRST.setSwarmEncounters(93,436)
GROTTERETOUR_AFTERFIRST.setPokeradarEncounters(93,42,356,433)
GROTTERETOUR_AFTERFIRST.setGbaEncounters([None], [337,337], [338,338], [356,433], [356,433], [356,433])

GROTTERETOUR_AFTERSECOND = EncounterTables("Grotte Retour - Après Second Pilier")
GROTTERETOUR_AFTERSECOND.setBaseEncounters(Encounter(93,20,35,35), Encounter(437,20,35,35), Encounter(93,10,36,36), Encounter(42,10,37,37), Encounter(93,10,37,37), Encounter(42,10,37,37), Encounter(42,5,38,38), Encounter(358,5,36,36), Encounter(356,4,38,38), Encounter(358,4,38,38), Encounter(356,1,38,38), Encounter(358,1,38,38))
GROTTERETOUR_AFTERSECOND.setDayEncounters(93,42)
GROTTERETOUR_AFTERSECOND.setNightEncounters(356,42)
GROTTERETOUR_AFTERSECOND.setSwarmEncounters(93,437)
GROTTERETOUR_AFTERSECOND.setPokeradarEncounters(93,42,356,358)
GROTTERETOUR_AFTERSECOND.setGbaEncounters([None], [337,337], [338,338], [356,358], [356,358], [356,358])

MONTABRUPT_EXTERIEUR = EncounterTables("Mont Abrupt - Extérieur")
MONTABRUPT_EXTERIEUR.setBaseEncounters(Encounter(323,20,53,53), Encounter(112,20,54,54), Encounter(22,10,51,51), Encounter(75,10,51,51), Encounter(22,10,53,53), Encounter(110,10,52,52), Encounter(227,5,53,53), Encounter(75,5,53,53), Encounter(322,4,51,51), Encounter(111,4,52,52), Encounter(322,1,51,51), Encounter(111,1,52,52))
MONTABRUPT_EXTERIEUR.setDayEncounters(22,75)
MONTABRUPT_EXTERIEUR.setNightEncounters(42,75)
MONTABRUPT_EXTERIEUR.setSwarmEncounters(323,112)
MONTABRUPT_EXTERIEUR.setPokeradarEncounters(324,324,324,324)
MONTABRUPT_EXTERIEUR.setGbaEncounters([None], [322,111], [322,111], [322,111], [322,111], [322,111])

MONTABRUPT_SALLE1 = EncounterTables("Mont Abrupt - Salle 1")
MONTABRUPT_SALLE1.setBaseEncounters(Encounter(219,20,54,54), Encounter(112,20,54,54), Encounter(42,10,52,52), Encounter(75,10,51,51), Encounter(42,10,52,52), Encounter(110,10,53,53), Encounter(110,5,51,51), Encounter(75,5,53,53), Encounter(218,4,52,52), Encounter(111,4,52,52), Encounter(218,1,52,52), Encounter(111,1,52,52))
MONTABRUPT_SALLE1.setDayEncounters(42,75)
MONTABRUPT_SALLE1.setNightEncounters(42,75)
MONTABRUPT_SALLE1.setSwarmEncounters(219,112)
MONTABRUPT_SALLE1.setPokeradarEncounters(42,110,218,111)
MONTABRUPT_SALLE1.setGbaEncounters([None], [218,111], [218,111], [218,111], [218,111], [218,111])

MONTABRUPT_SALLE2 = EncounterTables("Mont Abrupt - Salle 2")
MONTABRUPT_SALLE2.setBaseEncounters(Encounter(219,20,53,53), Encounter(219,20,55,55), Encounter(42,10,53,53), Encounter(75,10,52,52), Encounter(112,10,55,55), Encounter(110,10,54,54), Encounter(110,5,52,52), Encounter(75,5,54,54), Encounter(218,4,53,53), Encounter(109,4,53,53), Encounter(218,1,53,53), Encounter(109,1,53,53))
MONTABRUPT_SALLE2.setDayEncounters(42,75)
MONTABRUPT_SALLE2.setNightEncounters(42,75)
MONTABRUPT_SALLE2.setSwarmEncounters(219,219)
MONTABRUPT_SALLE2.setPokeradarEncounters(112,110,218,109)
MONTABRUPT_SALLE2.setGbaEncounters([None], [218,109], [218,109], [218,109], [218,109], [218,109])

RIVELACCOURAGE = EncounterTables("Rive Lac Courage")
RIVELACCOURAGE.setBaseEncounters(Encounter(203,20,26,26), Encounter(400,20,25,25), Encounter(397,10,26,26), Encounter(402,10,27,27), Encounter(397,10,27,27), Encounter(228,10,28,28), Encounter(397,5,28,28), Encounter(400,5,26,26), Encounter(203,4,28,28), Encounter(400,4,27,27), Encounter(203,1,28,28), Encounter(400,1,27,27))
RIVELACCOURAGE.setDayEncounters(397,397)
RIVELACCOURAGE.setNightEncounters(402,228)
RIVELACCOURAGE.setSwarmEncounters(203,400)
RIVELACCOURAGE.setPokeradarEncounters(33,30,33,30)
RIVELACCOURAGE.setGbaEncounters([None], [203,400], [203,400], [203,400], [203,400], [203,400])

RIVELACSAVOIR = EncounterTables("Rive Lac Savoir")
RIVELACSAVOIR.setBaseEncounters(Encounter(459,20,33,33), Encounter(220,20,32,32), Encounter(215,10,33,33), Encounter(459,10,32,32), Encounter(215,10,35,35), Encounter(220,10,34,34), Encounter(459,5,34,34), Encounter(220,5,32,32), Encounter(215,4,35,35), Encounter(459,4,35,35), Encounter(215,1,35,35), Encounter(459,1,35,35))
RIVELACSAVOIR.setDayEncounters(215,459)
RIVELACSAVOIR.setNightEncounters(361,361)
RIVELACSAVOIR.setSwarmEncounters(459,220)
RIVELACSAVOIR.setPokeradarEncounters(215,220,215,459)
RIVELACSAVOIR.setGbaEncounters([None], [215,459], [215,459], [217,217], [215,459], [215,459])

LACVERITE = EncounterTables("Lac Vérité")
LACVERITE.setBaseEncounters(Encounter(396,20,2,2), Encounter(399,20,2,2), Encounter(396,10,3,3), Encounter(399,10,3,3), Encounter(396,10,3,3), Encounter(399,10,3,3), Encounter(396,5,4,4), Encounter(399,5,4,4), Encounter(396,4,4,4), Encounter(399,4,4,4), Encounter(396,1,4,4), Encounter(399,1,4,4))
LACVERITE.setDayEncounters(396,399)
LACVERITE.setNightEncounters(396,399)
LACVERITE.setSwarmEncounters(396,399)
LACVERITE.setPokeradarEncounters(202,202,202,202)
LACVERITE.setGbaEncounters([None], [337,337], [338,338], [396,399], [396,399], [396,399])
LACVERITE.setSurfEncounters(Encounter(54,60,20,30), Encounter(54,30,20,30), Encounter(55,5,20,40), Encounter(55,4,20,40), Encounter(55,1,20,40))
LACVERITE.setOldRodEncounters(Encounter(129,40,4,6), Encounter(129,40,3,7), Encounter(129,15,5,10), Encounter(129,4,5,10), Encounter(129,1,5,15))
LACVERITE.setGoodRodEncounters(Encounter(129,40,15,20), Encounter(118,40,15,20), Encounter(129,15,10,25), Encounter(119,4,25,35), Encounter(119,1,25,35))
LACVERITE.setSuperRodEncounters(Encounter(130,40,30,40), Encounter(119,40,30,40), Encounter(130,15,40,55), Encounter(119,4,40,55), Encounter(119,1,40,55))

LACCOURAGE = EncounterTables("Lac Courage")
LACCOURAGE.setBaseEncounters(Encounter(397,20,38,38), Encounter(400,20,39,39), Encounter(397,10,40,40), Encounter(400,10,41,41), Encounter(55,10,40,40), Encounter(54,10,38,38), Encounter(55,5,41,41), Encounter(54,5,39,39), Encounter(397,4,40,40), Encounter(400,4,41,41), Encounter(397,1,40,40), Encounter(400,1,41,41))
LACCOURAGE.setDayEncounters(397,400)
LACCOURAGE.setNightEncounters(397,400)
LACCOURAGE.setSwarmEncounters(397,400)
LACCOURAGE.setPokeradarEncounters(202,202,202,202)
LACCOURAGE.setGbaEncounters([None], [337,337], [338,338], [397,400], [397,400], [397,400])
LACCOURAGE.setSurfEncounters(Encounter(54,60,20,30), Encounter(54,30,20,30), Encounter(55,5,20,40), Encounter(55,4,20,40), Encounter(55,1,20,40))
LACCOURAGE.setOldRodEncounters(Encounter(129,40,4,6), Encounter(129,40,3,7), Encounter(129,15,5,10), Encounter(129,4,5,10), Encounter(129,1,5,15))
LACCOURAGE.setGoodRodEncounters(Encounter(129,40,15,20), Encounter(118,40,15,20), Encounter(129,15,10,25), Encounter(119,4,25,35), Encounter(119,1,25,35))
LACCOURAGE.setSuperRodEncounters(Encounter(130,40,30,40), Encounter(119,40,30,40), Encounter(130,15,40,55), Encounter(119,4,40,55), Encounter(119,1,40,55))

LACSAVOIR = EncounterTables("Lac Savoir")
LACSAVOIR.setBaseEncounters(Encounter(459,20,38,38), Encounter(400,20,39,39), Encounter(459,10,39,39), Encounter(459,10,40,40), Encounter(55,10,40,40), Encounter(215,10,41,41), Encounter(55,5,39,39), Encounter(54,5,38,38), Encounter(459,4,41,41), Encounter(400,4,40,40), Encounter(459,1,41,41), Encounter(400,1,40,40))
LACSAVOIR.setDayEncounters(459,459)
LACSAVOIR.setNightEncounters(361,361)
LACSAVOIR.setSwarmEncounters(459,400)
LACSAVOIR.setPokeradarEncounters(55,215,459,400)
LACSAVOIR.setGbaEncounters([None], [337,337], [338,338], [216,216], [459,400], [459,400])
LACSAVOIR.setSurfEncounters(Encounter(54,60,20,30), Encounter(54,30,20,30), Encounter(55,5,20,40), Encounter(55,4,20,40), Encounter(55,1,20,40))
LACSAVOIR.setOldRodEncounters(Encounter(129,40,4,6), Encounter(129,40,3,7), Encounter(129,15,5,10), Encounter(129,4,5,10), Encounter(129,1,5,15))
LACSAVOIR.setGoodRodEncounters(Encounter(129,40,15,20), Encounter(118,40,15,20), Encounter(129,15,10,25), Encounter(119,4,25,35), Encounter(119,1,25,35))
LACSAVOIR.setSuperRodEncounters(Encounter(130,40,30,40), Encounter(119,40,30,40), Encounter(130,15,40,55), Encounter(119,4,40,55), Encounter(119,1,40,55))

ENCOUNTERTABLES_LIST = [
    # Cities
    BONAUGURE, VESTIGION, CELESTIA, VERCHAMPS, JOLIBERGES, RIVAMAR, AIREDEDETENTE,

    # Routes
    ROUTE201, ROUTE202, ROUTE203, ROUTE204_SUD, ROUTE204_NORD, ROUTE205_SUD, ROUTE205_NORD, ROUTE206,
    ROUTE207, ROUTE208, ROUTE209, ROUTE210_SUD, ROUTE210_NORD, ROUTE211_OUEST, ROUTE211_EST, ROUTE212_SUD,
    ROUTE212_NORD, ROUTE213, ROUTE214, ROUTE215, ROUTE216, ROUTE217, ROUTE218, ROUTE219, ROUTE220, ROUTE221,
    ROUTE222, ROUTE223, ROUTE224, ROUTE225, ROUTE226, ROUTE227, ROUTE228, ROUTE229, ROUTE230, 

    # Key Locations
    LESEOLIENNES, FORGEFUEGO, FORETVESTIGION, VIEUXCHATEAU, VIEUXCHATEAU_CHAMBRE4, TOURPERDUE_REZDECHAUSSEE,
    TOURPERDUE_ETAGE2, TOURPERDUE_ETAGE3, TOURPERDUE_ETAGE4, RUINESBONVILLE, GRANDMARAIS_PARC1, GRANDMARAIS_PARC2,
    GRANDMARAIS_PARC3, GRANDMARAIS_PARC4, GRANDMARAIS_PARC5, GRANDMARAIS_PARC6, JARDINTROPHEE, LIGUEPOKEMON_EXTERIEUR,
    SOURCEADIEU, RIVELACCOURAGE, RIVELACSAVOIR, LACVERITE, LACCOURAGE, LACSAVOIR,
    
    # Caves
    ENTREECHARBOURG, ENTREECHARBOURG_SOUSSOL, MINECHARBOURG_ENTREE, MINECHARBOURG, CHEMINROCHEUX, GROTTEREVECHE,
    GROTTEREVECHE_SOUSSOL, TUNNELRUINEMANIAC, MONTCOURONNE_PASSAGECHARBOURG, MONTCOURONNE_SALLE1, MONTCOURONNE_SALLE2,
    MONTCOURONNE_EXTERIEUR, MONTCOURONNE_SALLE3, MONTCOURONNE_SALLE4, MONTCOURONNE_SALLE5, MONTCOURONNE_SALLE6,
    MONTCOURONNE_SALLE7, MONTCOURONNE_PASSAGEVESTIGION, MONTCOURONNE_SALLE8, MONTCOURONNE_PASSAGEFRIMAPIC, ILEDEFER,
    ILEDEFER_REZDECHAUSSEE, ILEDEFER_SOUSSOL1, ILEDEFER_SOUSSOL2, ILEDEFER_SORTIE, TEMPLEFRIMAPIC_ENTREE,
    TEMPLEFRIMAPIC_SOUSSOL1, TEMPLEFRIMAPIC_SOUSSOL23, TEMPLEFRIMAPIC_SOUSSOL45, ROUTEVICTOIRE, ROUTEVICTOIRE_SALLEOUEST,
    ROUTEVICTOIRE_SALLEEST, ROUTEVICTOIRE_PASSAGEEST, ROUTEVICTOIRE_SALLEBRUME, ROUTEVICTOIRE_PASSAGEROUTE224,
    GROTTERETOUR_ENTREE, GROTTERETOUR_AFTERFIRST, GROTTERETOUR_AFTERSECOND, MONTABRUPT_EXTERIEUR, MONTABRUPT_SALLE1, MONTABRUPT_SALLE2
]