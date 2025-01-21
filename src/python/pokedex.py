import copy

from data import EVOLUTIONS, POKEMON_NAMES, GBAGAME_NAMES, DANGEROUS_MOVES, MOVE_NAMES
from encounter import ENCOUNTERTABLES_DICT, BASEENCOUNTER_RATES, SPECIALENCOUNTERS, SPECIALGRASSENCOUNTERS, Encounter

ENCOUNTER_SLOTS = {
    "swarm" : {0:0, 1:1},
    "garden": {0:6, 1:7},
    "marsh": {0:6, 1:7},
    "gba": {0:8, 1:9},
}

class PokedexEntry():
    def __init__(self, pokedexId):
        self.pokedexId = pokedexId
        self.name = POKEMON_NAMES[pokedexId]
        self.caught = False

        self.evolvesFrom = None
        self.evolvesInto = []
        self.encounterTables = {}

        self.totalRate = 0
        self.rarity = 0

        self.maxScore = 0
        self.bestRoute = None
        self.bestVersionMethods = ""
        self.bestVersion = None

        self.dangerousMoves = []

    # Link evolution to base Pokémon
    def setEvolvesInto(self, evolutionList):
        self.evolvesInto = []

        for evolution in evolutionList:
            self.evolvesInto.append(POKEDEX[evolution])
            POKEDEX[evolution].evolvesFrom = self

    # Check if the Pokémon knows any dangerous move at provided level
    def getCurrentDangerousMoves(self, currentLevel):

        # Get the four last moves learned by the Pokémon
        for i in range(len(self.levelsLearnset)):
            if (self.levelsLearnset[i] > currentLevel):
                moveLevels = self.levelsLearnset[max(0, i - 4) : max(1, i)]
                break

            # Particular case : currentLevel is higher than the max learn level ; get last 4 moves
            if (i == len(self.levelsLearnset) - 1):
                moveLevels = self.levelsLearnset[max(0, i - 3) : max(1, i + 1)]

        # Return every dangerous move in the current level moveset
        return [dangerousMove.moveId for dangerousMove in self.dangerousMoves if dangerousMove.level in moveLevels]

    def setDangerousMove(self, levelsLearnset, movesList):
        self.levelsLearnset = levelsLearnset
        self.dangerousMoves = [DangerousMove(move[0], move[1]) for move in movesList]

    def __str__(self):
        return self.name + " " + str(self.encounterTables)

class DangerousMove():
    def __init__(self, moveId, level):
        self.moveId = moveId
        self.level = level

    def __str__(self):
        return f"{MOVE_NAMES[self.moveId]} : {self.level}"

    def __repr__(self):
        return str(self)

POKEDEX = {pokedexId : PokedexEntry(pokedexId) for pokedexId in range(1, 494)}

def populatePokedex():

    # Setup evolutions for each Pokémon
    for pokedexId, evolution in EVOLUTIONS.items():
        POKEDEX[pokedexId].setEvolvesInto(evolution)

    # Search in each zone if a Pokémon can be found in water or grass
    for zone in ENCOUNTERTABLES_DICT.values():
        
        # Grass encounters
        if (zone.baseEncounters):

            for i in range(12):
                encounter = zone.baseEncounters[i]

                # Base encounter slots for all three periods of the day
                if i not in (2,3):
                    addPokedexEncounter(encounter.pokedexId, zone.name, "morning", encounter)
                    addPokedexEncounter(encounter.pokedexId, zone.name, "day", encounter)
                    addPokedexEncounter(encounter.pokedexId, zone.name, "night", encounter)

                # Period-specific encounter slots
                else:
                    addPokedexEncounter(encounter.pokedexId, zone.name, "morning", encounter)
                    addPokedexEncounter(zone.dayEncounters[i - 2], zone.name, "day", encounter)
                    addPokedexEncounter(zone.nightEncounters[i - 2], zone.name, "night", encounter)

            # Pokéradar
            for pokeradarId, encounterSlot in {0:4, 1:5, 2:10, 3:11}.items():
                if (zone.pokeradarEncounters[pokeradarId] != zone.baseEncounters[encounterSlot].pokedexId):             
                    addPokedexEncounter(zone.pokeradarEncounters[pokeradarId], zone.name, "pokeradar", zone.baseEncounters[encounterSlot])

            # Swarm
            for swarmId, encounterSlot in {0:0, 1:1}.items():
                if (zone.swarmEncounters[swarmId] != zone.baseEncounters[encounterSlot].pokedexId):
                    addPokedexEncounter(zone.swarmEncounters[swarmId], zone.name, "swarm", zone.baseEncounters[encounterSlot])

            # GBA
            for gbaGame in range(1,6):
                for gbaId, encounterSlot in {0:8, 1:9}.items():
                    if (zone.gbaEncounters[gbaGame][gbaId] != zone.baseEncounters[encounterSlot].pokedexId):
                        addPokedexEncounter(zone.gbaEncounters[gbaGame][gbaId], zone.name + " (" + GBAGAME_NAMES[gbaGame] + ")", "gba", zone.baseEncounters[encounterSlot])

        # Water encounters
        if (zone.surfEncounters):
            for environment, encounterTable in {"surf": zone.surfEncounters, "oldrod": zone.oldRodEncounters, "goodrod": zone.goodRodEncounters, "superrod": zone.superRodEncounters}.items():

                # Surf - Old/Good/Super rod
                for encounter in encounterTable:
                    addPokedexEncounter(encounter.pokedexId, zone.name, environment, encounter)

    # Add special encounters (static, roaming, fossils, etc)
    for environment, encounterTable in SPECIALENCOUNTERS.items():
        for encounter in encounterTable:
            addPokedexEncounter(encounter.pokedexId, environment, environment, encounter)

    # Add Garden/Marsh encounters
    for environment, zoneName in {"garden": "Jardin Trophée", "marsh": "Grand Marais"}.items():
        for pokedexId in list(set(SPECIALGRASSENCOUNTERS[environment])):
            addPokedexEncounter(pokedexId, zoneName, environment, zone.baseEncounters[6])
            addPokedexEncounter(pokedexId, zoneName, environment, zone.baseEncounters[7])

    # Setup dangerous moves for each Pokémon
    for pokedexId, dangerousMoveData in DANGEROUS_MOVES.items():
        POKEDEX[pokedexId].setDangerousMove(dangerousMoveData["levelsLearnset"], dangerousMoveData["movesList"])

        # Check each encounter zone and method type
        for method, encounterTable in POKEDEX[pokedexId].encounterTables.items():
            for zone, encounterData in encounterTable.items():
                totalDangerousMovesId = []
                learnLevels = sorted(list(set(range(encounterData["minLevel"], encounterData["maxLevel"] + 1)).intersection(POKEDEX[pokedexId].levelsLearnset)))

                if (encounterData["minLevel"] not in learnLevels):
                    learnLevels = [encounterData["minLevel"]] + learnLevels

                # Check each possible level to see if dangeroux moves can be present in the moveset
                for level in learnLevels:
                    dangerousMovesList = POKEDEX[pokedexId].getCurrentDangerousMoves(level)

                    for move in dangerousMovesList:
                        if (move not in totalDangerousMovesId):
                            totalDangerousMovesId.append(move)

                totalDangerousMoves = [MOVE_NAMES[moveId] for moveId in totalDangerousMovesId]
                POKEDEX[pokedexId].encounterTables[method][zone]["dangerousMoves"] = " - ".join(totalDangerousMoves)

    # If a Pokémon cannot be found in the wild, check if its pre-evolution or evolution can
    for pokedexId, pokemon in POKEDEX.items():

        if (not pokemon.encounterTables):

            # Check pre-evolutions encounters, we might be able to evolve one of them
            preEvolution = pokemon.evolvesFrom
            if (preEvolution):

                # PreEvolution can be found in the wild : add encounter
                if (canBeFoundInGame(preEvolution.encounterTables)):
                    addPokedexEncounter(pokedexId, preEvolution.pokedexId, "evolution", None)

                # PreEvolution's pre-evolution can be found in the wild : add encounter
                if (preEvolution.evolvesFrom and canBeFoundInGame(preEvolution.evolvesFrom.encounterTables)):
                    addPokedexEncounter(pokedexId, preEvolution.evolvesFrom.pokedexId, "evolution", None)

            # Check evolutions encounters, we might be able to hatch an egg from one of them
            if (pokemon.evolvesInto):
                for evolution in pokemon.evolvesInto:

                    # Evolution can be found in the wild : add encounter
                    if (canBeFoundInGame(evolution.encounterTables)):
                        addPokedexEncounter(pokedexId, evolution.pokedexId, "hatch", None)

                    for secondEvolution in evolution.evolvesInto:

                        # 2nd Evolution can be found in the wild : add encounter
                        if (canBeFoundInGame(secondEvolution.encounterTables)):
                            addPokedexEncounter(pokedexId, secondEvolution.pokedexId, "hatch", None)

def canBeFoundInGame(encounterTable):
    return (encounterTable
            and not (len(encounterTable) == 1
                     and ("evolution" in encounterTable or "hatch" in encounterTable)))

def addPokedexEncounter(pokedexId, zoneName, environment, encounter):
    if (environment not in POKEDEX[pokedexId].encounterTables):
        POKEDEX[pokedexId].encounterTables[environment] = {}

    if (encounter):
        if (zoneName not in POKEDEX[pokedexId].encounterTables[environment]):
            POKEDEX[pokedexId].encounterTables[environment][zoneName] = {
                "rate": 0, "minLevel": 100, "maxLevel": 1, "dangerousMoves": ""
            }

        POKEDEX[pokedexId].encounterTables[environment][zoneName]["rate"] += encounter.rate

        if (encounter.minLevel < POKEDEX[pokedexId].encounterTables[environment][zoneName]["minLevel"]):
            POKEDEX[pokedexId].encounterTables[environment][zoneName]["minLevel"] = encounter.minLevel
            
        if (encounter.maxLevel > POKEDEX[pokedexId].encounterTables[environment][zoneName]["maxLevel"]):
            POKEDEX[pokedexId].encounterTables[environment][zoneName]["maxLevel"] = encounter.maxLevel

    # Particular case : hatch/evolve
    else:
        POKEDEX[pokedexId].encounterTables[environment][zoneName] = {"evolve/hatch": True}


class ZoneVersion():
    def __init__(self, zone):
        self.zone = zone
        self.maxRouteScore = 0

        self.selectedMethod = {
            "garden": "",
            "marsh": "",
            "swarm": "",
            "gba": ""
        }

        self.bestVersion = {
            "garden": None,
            "marsh": None,
            "swarm": None,
            "gba": None
        }

    # Calculate special Pokemon rarity score and check if their addition is beneficial
    def calculateSpecialMethodScore(self, method, specialEncounters, currentVersion, targetPokemon, methodParameter = None):

        # Enable special encounters on current best version
        for specialEncounterSlot, baseEncounterSlot in ENCOUNTER_SLOTS[method].items():
            currentVersion[self.zone.baseEncounters[baseEncounterSlot].pokedexId] -= BASEENCOUNTER_RATES[baseEncounterSlot]
            currentVersion[specialEncounters[specialEncounterSlot]] = currentVersion.get(specialEncounters[specialEncounterSlot], 0) + BASEENCOUNTER_RATES[baseEncounterSlot]

        # Calculate updated zone rarity score
        specialEncounterScore = calculateZoneScore(currentVersion, targetPokemon)

        # Check if enabling special encounter is more optimal
        if (specialEncounterScore > self.maxRouteScore):
            self.maxRouteScore = specialEncounterScore
            self.selectedMethod[method] = " " + method + (f" ({methodParameter})" if methodParameter else "")
            self.bestVersion[method] = currentVersion


def populatePokedexEncounters():
    for pokedexEntry in POKEDEX.values():
        for method, encounterTable in pokedexEntry.encounterTables.items():

            # Base grass/cave encounters
            if method in ["morning", "day", "night"]:
                for zone, encounterData in encounterTable.items():

                    # Garden/Marsh : add encounter rate once for each uncaught special Pokemon
                    if (zone == "Jardin Trophée"):
                        uncaughtGardenPokemon = sum(1 for pokedexId in list(set(SPECIALGRASSENCOUNTERS["garden"])) if not POKEDEX[pokedexId].caught)
                        pokedexEntry.totalRate += encounterData["rate"] * uncaughtGardenPokemon
                    elif ("Grand Marais" in zone):
                        uncaughtMarshPokemon = sum(1 for pokedexId in list(set(SPECIALGRASSENCOUNTERS["marsh"])) if not POKEDEX[pokedexId].caught)
                        pokedexEntry.totalRate += encounterData["rate"] * uncaughtMarshPokemon

                    # Default encounter : add encounter rate
                    else:
                        pokedexEntry.totalRate += encounterData["rate"]

            # Special grass/cave + water encounters
            elif method in ["gba", "swarm", "garden", "marsh", "surf", "oldrod", "goodrod", "superrod"]:
                for encounterData in encounterTable.values():
                    pokedexEntry.totalRate += encounterData["rate"] * 3 # x3 since you can find them during morning/day/night

        # Calculate rarity score from encounter total rate
        if (pokedexEntry.totalRate > 0):
            pokedexEntry.rarity = round(100 / pokedexEntry.totalRate, 2)

    # Find most optimal zone for each Pokemon
    for pokedexEntry in POKEDEX.values():
        if (pokedexEntry.totalRate > 0):
            findMostOptimalZone(pokedexEntry.pokedexId)

def calculateZoneScore(zoneEncounters, targetPokemon):
    if (targetPokemon not in zoneEncounters):
        return 0

    # Calculate non-caught encounters rarity score
    rarityScore = round(sum(zoneEncounters[pokedexId] * POKEDEX[pokedexId].rarity 
                            for pokedexId in zoneEncounters if pokedexId != targetPokemon and not POKEDEX[pokedexId].caught), 2)

    # Sum with target Pokemon encounter rate to have the global zone score
    zoneScore = zoneEncounters[targetPokemon] + rarityScore

    return zoneScore

def findMostOptimalZone(targetPokemon):
    targetMaxScore = 0
    bestRoute = None
    bestVersion = None
    bestVersionMethods = ""

    # Calculate rarity score for each zone to find the most optimal one
    for zone in ENCOUNTERTABLES_DICT.values():
        zoneVersion = ZoneVersion(zone)

        # Grass/Cave encounters
        if (zone.baseEncounters):
            zoneEncounters = {
                "morning": {},
                "day": {},
                "night": {},
                "garden": {},
                "marsh": {},
            }

            # Generate encounter table for morning/day/night
            for i in range(12):
                encounter = zone.baseEncounters[i]

                # Base encounter slots for all three periods of the day
                if i not in (2,3):
                    zoneEncounters["morning"][encounter.pokedexId] = zoneEncounters["morning"].get(encounter.pokedexId, 0) + encounter.rate
                    zoneEncounters["day"][encounter.pokedexId] = zoneEncounters["day"].get(encounter.pokedexId, 0) + encounter.rate
                    zoneEncounters["night"][encounter.pokedexId] = zoneEncounters["night"].get(encounter.pokedexId, 0) + encounter.rate

                # Period-specific encounter slots
                else:
                    zoneEncounters["morning"][encounter.pokedexId] = zoneEncounters["morning"].get(encounter.pokedexId, 0) + encounter.rate
                    zoneEncounters["day"][zone.dayEncounters[i - 2]] = zoneEncounters["day"].get(zone.dayEncounters[i - 2], 0) + BASEENCOUNTER_RATES[i]
                    zoneEncounters["night"][zone.nightEncounters[i - 2]] = zoneEncounters["night"].get(zone.nightEncounters[i - 2], 0) + BASEENCOUNTER_RATES[i]

            # Calculate zone score for each period of the day
            zoneScores = {
                "morning": calculateZoneScore(zoneEncounters["morning"], targetPokemon),
                "day": calculateZoneScore(zoneEncounters["day"], targetPokemon),
                "night" : calculateZoneScore(zoneEncounters["night"], targetPokemon)
            }

            # Find most optimal period to find the rarer Pokemon
            zoneVersion.maxRouteScore = max(zoneScores.values())
            bestPeriods = [period for period, score in zoneScores.items() if score == zoneVersion.maxRouteScore]
            selectedPeriod = "/".join(bestPeriods)

            # Set best base encounter list
            bestZoneVersion = copy.deepcopy(zoneEncounters[bestPeriods[0]])

            # Swarm encounters
            if (zone.swarmEncounters[0] != zone.baseEncounters[0].pokedexId):
                zoneEncounters["swarm"] = copy.deepcopy(bestZoneVersion)
                
                # Check if enabling swarm is more optimal
                zoneVersion.calculateSpecialMethodScore("swarm", zone.swarmEncounters, zoneEncounters["swarm"], targetPokemon)

            if (zoneVersion.bestVersion["swarm"]):
                bestZoneVersion = zoneVersion.bestVersion["swarm"]

            # GBA encounters
            for gbaGame in range(1,6):
                if (zone.gbaEncounters[gbaGame][0] != zone.baseEncounters[8].pokedexId or zone.gbaEncounters[gbaGame][1] != zone.baseEncounters[9].pokedexId):
                    zoneEncounters[GBAGAME_NAMES[gbaGame]] = copy.deepcopy(bestZoneVersion)

                    # Check if enabling GBA game is more optimal
                    zoneVersion.calculateSpecialMethodScore("gba", zone.gbaEncounters[gbaGame], zoneEncounters[GBAGAME_NAMES[gbaGame]], targetPokemon, GBAGAME_NAMES[gbaGame])

            if (zoneVersion.bestVersion["gba"]):
                bestZoneVersion = zoneVersion.bestVersion["gba"]
                
            # Garden encounters
            if (zone.name == "Jardin Trophée"):
                for gardenPokemonId in list(set(SPECIALGRASSENCOUNTERS["garden"])):
                    zoneEncounters["garden"][gardenPokemonId] = copy.deepcopy(bestZoneVersion)

                    # Check which Garden Pokémon is more optimal
                    zoneVersion.calculateSpecialMethodScore("garden", 2 * [gardenPokemonId], zoneEncounters["garden"][gardenPokemonId], targetPokemon, gardenPokemonId)

            if (zoneVersion.bestVersion["garden"]):
                bestZoneVersion = zoneVersion.bestVersion["garden"]

            # Marsh encounters
            if ("Grand Marais" in zone.name):
                for marshPokemonId in list(set(SPECIALGRASSENCOUNTERS["marsh"])):
                    zoneEncounters["marsh"][marshPokemonId] = copy.deepcopy(bestZoneVersion)

                    # Check which Marsh Pokémon is more optimal
                    zoneVersion.calculateSpecialMethodScore("marsh", 2 * [marshPokemonId], zoneEncounters["marsh"][marshPokemonId], targetPokemon, marshPokemonId)

            if (zoneVersion.bestVersion["marsh"]):
                bestZoneVersion = zoneVersion.bestVersion["marsh"]

            # Check if this route has the best overall rarity score for the target Pokemon
            if (zoneVersion.maxRouteScore > targetMaxScore):
                targetMaxScore = zoneVersion.maxRouteScore
                bestRoute = zone
                bestVersion = bestZoneVersion
                bestVersionMethods = selectedPeriod + "".join(zoneVersion.selectedMethod.values())

        # Surf/Rod encounters
        if (zone.surfEncounters):
            zoneWaterEncounters = {
                "surf": {},
                "oldrod": {},
                "goodrod": {},
                "superrod": {}
            }

            # Generate encounter table for surf and all rods
            for i in range(5):
                zoneWaterEncounters["surf"][zone.surfEncounters[i].pokedexId] = zoneWaterEncounters["surf"].get(zone.surfEncounters[i].pokedexId, 0) + zone.surfEncounters[i].rate
                zoneWaterEncounters["oldrod"][zone.oldRodEncounters[i].pokedexId] = zoneWaterEncounters["oldrod"].get(zone.oldRodEncounters[i].pokedexId, 0) + zone.oldRodEncounters[i].rate
                zoneWaterEncounters["goodrod"][zone.goodRodEncounters[i].pokedexId] = zoneWaterEncounters["goodrod"].get(zone.goodRodEncounters[i].pokedexId, 0) + zone.goodRodEncounters[i].rate
                zoneWaterEncounters["superrod"][zone.superRodEncounters[i].pokedexId] = zoneWaterEncounters["superrod"].get(zone.superRodEncounters[i].pokedexId, 0) + zone.superRodEncounters[i].rate

            # Calculate zone score for each way to fish Pokemon
            zoneScores = {
                "surf": calculateZoneScore(zoneWaterEncounters["surf"], targetPokemon),
                "oldrod": calculateZoneScore(zoneWaterEncounters["oldrod"], targetPokemon),
                "goodrod" : calculateZoneScore(zoneWaterEncounters["goodrod"], targetPokemon),
                "superrod" : calculateZoneScore(zoneWaterEncounters["superrod"], targetPokemon)
            }

            # Find most optimal method to find the rarer Pokemon
            maxWaterScore = max(zoneScores.values())
            bestMethods = [method for method, score in zoneScores.items() if score == maxWaterScore]
            selectedMethod = "/".join(bestMethods)

            # Set base water encounter list
            bestWaterVersion = copy.deepcopy(zoneWaterEncounters[bestMethods[0]])

            # Check if this route water has the best overall rarity score for the target Pokemon
            if (maxWaterScore > targetMaxScore):
                targetMaxScore = maxWaterScore
                bestRoute = zone
                bestVersion = bestWaterVersion
                bestVersionMethods = selectedMethod

    # Save most optimal zone
    POKEDEX[targetPokemon].maxScore = targetMaxScore
    POKEDEX[targetPokemon].bestRoute = bestRoute
    POKEDEX[targetPokemon].bestVersionMethods = bestVersionMethods
    POKEDEX[targetPokemon].bestVersion = bestVersion


def printPokedex():
    with open("pokedex.txt", "w", encoding="utf-8") as file:
        for pokedexId, pokemon in POKEDEX.items():
            file.write(f"{pokedexId} - {pokemon.name} - {pokemon.bestRoute.name if pokemon.bestRoute else None} ({pokemon.bestVersionMethods}) : {pokemon.maxScore}\n")

            if (pokemon.encounterTables):
                for environment, encounterTable in pokemon.encounterTables.items():
                    if (environment == "evolution"):
                        for evolution in encounterTable:
                            file.write("\tEvolves from " + POKEMON_NAMES[evolution] + "\n")

                    elif (environment == "hatch"):
                        for evolution in encounterTable:
                            file.write("\tHatches from " + POKEMON_NAMES[evolution] + "\n")

                    else:
                        file.write("\t" + environment.capitalize() + "\n")

                        for encounter, encounterData in encounterTable.items():
                            if (encounterData["rate"]):
                                file.write(f"\t\t{encounter} : {encounterData["rate"]}% (lvl {encounterData["minLevel"]}{"" if encounterData["minLevel"] == encounterData["maxLevel"] else "-" + str(encounterData["maxLevel"])}){" - " + encounterData["dangerousMoves"] if encounterData["dangerousMoves"] else ""}\n")
                            else:
                                file.write(f"\t\tlvl {encounterData["minLevel"]}{"" if encounterData["minLevel"] == encounterData["maxLevel"] else "-" + str(encounterData["maxLevel"])}{" - " + encounterData["dangerousMoves"] if encounterData["dangerousMoves"] else ""}\n")
            else:
                file.write("\tCannot be found\n")

            file.write("\n")

populatePokedex()
populatePokedexEncounters()
printPokedex()