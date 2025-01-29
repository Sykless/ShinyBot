
import re

from data import EVOLUTIONS, POKEMON_NAMES, GBAGAME_NAMES, DANGEROUS_MOVES, MOVE_NAMES
from encounter import ENCOUNTERTABLES_DICT, SPECIALENCOUNTERS, SPECIALGRASSENCOUNTERS
from encounter import SAPPHIRE, RUBY, EMERALD, FIRERED, LEAFGREEN

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


########################################################################################
# Class used to calculate the best way to encounter a Pokémon across all zone versions #
########################################################################################
class ZoneVersion():
    def __init__(self, zone):
        self.zone = zone
        self.maxRouteScore = 0

        self.selectedMethod = {
            "period": "",
            "garden": "",
            "marsh": "",
            "swarm": "",
            "gba": ""
        }


    # Calculate special Pokemon rarity score and check if their addition is beneficial
    def calculateSpecialMethodScore(self, method, specialEncounters, targetPokemon, methodParameter = None):

        # Enable special encounters on current best version
        currentVersion = self.reconstructBestEncounterTable(method, specialEncounters)

        # Calculate updated zone rarity score
        specialEncounterScore = calculateZoneScore(currentVersion, targetPokemon)

        # Check if enabling special encounter is more optimal
        if (specialEncounterScore > self.maxRouteScore):
            self.maxRouteScore = specialEncounterScore
            self.selectedMethod[method] = method + (f" ({methodParameter})" if methodParameter else "")


    # Reconstruct the zone encounter table from every method stored (period, swarm, gba, etc)
    def reconstructBestEncounterTable(self, newMethod, specialEncounters):
        bestEncounterTable = {}

        # Retrieve method parameters if saved
        gardenPokemonId = int(re.search(r"\((\d+)\)", self.selectedMethod["garden"]).group(1)) if self.selectedMethod["garden"] else None
        marshPokemonId = int(re.search(r"\((\d+)\)", self.selectedMethod["marsh"]).group(1)) if self.selectedMethod["marsh"] else None
        gbaGame = int(re.search(r"\((\d+)\)", self.selectedMethod["gba"]).group(1)) if self.selectedMethod["gba"] else None

        # Generate encounter table for morning/day/night
        for i in range(12):
            encounter = self.zone.baseEncounters[i]

            # Period-specific encounters
            if i in (0,1) and (self.selectedMethod["swarm"] or newMethod == "swarm"):
                addZoneEncounter(bestEncounterTable, self.zone.swarmEncounters[i], encounter)

            elif i in (2,3) and ("morning" in self.selectedMethod["period"] and newMethod not in ["day","night"] or newMethod == "morning"):
                addZoneEncounter(bestEncounterTable, encounter.pokedexId, encounter)

            elif i in (2,3) and ("day" in self.selectedMethod["period"] and newMethod not in ["morning","night"] or newMethod == "day"):
                addZoneEncounter(bestEncounterTable, self.zone.dayEncounters[i - 2], encounter)

            elif i in (2,3) and ("night" in self.selectedMethod["period"] and newMethod not in ["morning","day"] or newMethod == "night"):
                addZoneEncounter(bestEncounterTable, self.zone.nightEncounters[i - 2], encounter)

            elif i in (6,7) and (self.selectedMethod["garden"] or newMethod == "garden"):
                if newMethod == "garden":
                    addZoneEncounter(bestEncounterTable, specialEncounters[i - 6], encounter)
                else:
                    addZoneEncounter(bestEncounterTable, gardenPokemonId, encounter)

            elif i in (6,7) and (self.selectedMethod["marsh"] or newMethod == "marsh"):
                if newMethod == "marsh":
                    addZoneEncounter(bestEncounterTable, specialEncounters[i - 6], encounter)
                else:
                    addZoneEncounter(bestEncounterTable, marshPokemonId, encounter)

            elif i in (8,9) and (self.selectedMethod["gba"] or newMethod == "gba"):
                if newMethod == "gba":
                    addZoneEncounter(bestEncounterTable, specialEncounters[i - 8], encounter)
                else:
                    addZoneEncounter(bestEncounterTable, self.zone.gbaEncounters[gbaGame][i - 8], encounter)

            # Default : morning encounters
            else:
                addZoneEncounter(bestEncounterTable, encounter.pokedexId, encounter)

        return bestEncounterTable


# Initialize empty Pokedex entries for all 493 Pokémon
POKEDEX = {pokedexId : PokedexEntry(pokedexId) for pokedexId in range(1, 494)}


#####################################################
# Fills all Pokédex entries with all encounter data #
#####################################################
def initPokedex():

    # Step 1 : associate each Pokémon to every possible way to encounter them
    populatePokedex()

    # Step 2 : Calculate rarity score for each Pokémon
    calculatePokedexRarityScores()

    # Step 3 : find most optimized zone to encounter each Pokémon
    findMostOptimalZone()

    # Step 4 : print all Pokédex data in a txt file
    printPokedex()


############################################################################
# Fills each Pokédex entry with all possible ways to encounter the Pokémon #
############################################################################
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
            for gbaGame in [SAPPHIRE, RUBY, EMERALD, FIRERED, LEAFGREEN]:
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


####################################################################################################
# Check if a Pokémon can be found in the game by cheking its encounter table and their evolution's #
####################################################################################################
def canBeFoundInGame(encounterTable):
    return (encounterTable
            and not (len(encounterTable) == 1
                     and ("evolution" in encounterTable or "hatch" in encounterTable)))


#################################################################################
# Update encounter rate and min/max level of a Pokémon on provided zone version #
#################################################################################
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


##########################################################################
# Calculate total encounter rate and rarity score for each Pokédex entry #
##########################################################################
def calculatePokedexRarityScores():
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
            pokedexEntry.rarity = 100 / pokedexEntry.totalRate


####################################################################################################
# Calculate zone score from current zone encounters rarity score and target pokemon encounter rate #
####################################################################################################
def calculateZoneScore(zoneEncounters, targetPokemon):
    if (targetPokemon not in zoneEncounters):
        return 0

    # Calculate non-caught encounters rarity score
    rarityScore = sum(
        zoneEncounters[pokedexId]["rate"] * POKEDEX[pokedexId].rarity 
        for pokedexId in zoneEncounters if not POKEDEX[pokedexId].caught
    )

    # Sum with target Pokemon encounter rate to have the global zone score
    return round(zoneEncounters[targetPokemon]["rate"] + rarityScore, 2)


#####################################################################
# Add encounter data to current zone when testing multiple versions #
#####################################################################
def addZoneEncounter(currentZoneEncounters, pokedexId, encounter):
    if (pokedexId not in currentZoneEncounters):
        currentZoneEncounters[pokedexId] = {
            "rate": 0, "minLevel": 100, "maxLevel": 1, "dangerousMoves": ""
        }

    currentZoneEncounters[pokedexId]["rate"] += encounter.rate

    if (encounter.minLevel < currentZoneEncounters[pokedexId]["minLevel"]):
        currentZoneEncounters[pokedexId]["minLevel"] = encounter.minLevel
        
    if (encounter.maxLevel > currentZoneEncounters[pokedexId]["maxLevel"]):
        currentZoneEncounters[pokedexId]["maxLevel"] = encounter.maxLevel


#######################################################################################
# Check which period (morning/day/night) has the best zone score for provided Pokémon #
#######################################################################################
def getBestPeriodScore(zoneVersion, targetPokemon):

    # Generate encounter table for morning/day/night
    zoneEncounters = {
        "morning": zoneVersion.reconstructBestEncounterTable("morning", None),
        "day": zoneVersion.reconstructBestEncounterTable("day", None),
        "night": zoneVersion.reconstructBestEncounterTable("night", None),
    }

    # Calculate zone score for each period of the day
    zoneScores = {
        "morning": calculateZoneScore(zoneEncounters["morning"], targetPokemon),
        "day": calculateZoneScore(zoneEncounters["day"], targetPokemon),
        "night" : calculateZoneScore(zoneEncounters["night"], targetPokemon)
    }

    # Find most optimal period to find the rarer Pokemon
    maxScore = max(zoneScores.values())
    bestPeriods = [period for period, score in zoneScores.items() if score == maxScore]

    return maxScore, bestPeriods


#######################################################################################################
# Generate all possible zone versions to check which is the most optimized to search for each Pokémon #
#######################################################################################################
def findMostOptimalZone():

    # Find most optimal zone for each Pokemon
    for pokedexEntry in POKEDEX.values():

        # Don't search for mose optimized zone if we can't find the Pokémon in the wild
        if (pokedexEntry.totalRate == 0):
            continue

        targetMaxScore = 0
        bestRoute = None
        bestVersionMethods = ""

        # Calculate rarity score for each zone to find the most optimal one
        for zone in ENCOUNTERTABLES_DICT.values():
            zoneVersion = ZoneVersion(zone)

            # Grass/Cave encounters
            if (zone.baseEncounters):

                # Find most optimal period (morning/day/night) to find the rarer Pokemon
                maxPeriodScore, bestPeriods = getBestPeriodScore(zoneVersion, pokedexEntry.pokedexId)
                zoneVersion.maxRouteScore = maxPeriodScore
                zoneVersion.selectedMethod["period"] = "/".join(bestPeriods)

                # Check if enabling swarm is more optimal
                if (zone.swarmEncounters[0] != zone.baseEncounters[0].pokedexId):
                    zoneVersion.calculateSpecialMethodScore("swarm", zone.swarmEncounters, pokedexEntry.pokedexId)

                # Check if enabling GBA game is more optimal
                for gbaGame in [SAPPHIRE, RUBY, EMERALD, FIRERED, LEAFGREEN]:
                    if (zone.gbaEncounters[gbaGame][0] != zone.baseEncounters[8].pokedexId or zone.gbaEncounters[gbaGame][1] != zone.baseEncounters[9].pokedexId):
                        zoneVersion.calculateSpecialMethodScore("gba", zone.gbaEncounters[gbaGame], pokedexEntry.pokedexId, gbaGame)

                # Check which Garden Pokémon is more optimal
                if (zone.name == "Jardin Trophée"):
                    for gardenPokemonId in list(set(SPECIALGRASSENCOUNTERS["garden"])):
                        zoneVersion.calculateSpecialMethodScore("garden", 2 * [gardenPokemonId], pokedexEntry.pokedexId, gardenPokemonId)

                # Check which Marsh Pokémon is more optimal
                if ("Grand Marais" in zone.name):
                    for marshPokemonId in list(set(SPECIALGRASSENCOUNTERS["marsh"])):
                        zoneVersion.calculateSpecialMethodScore("marsh", 2 * [marshPokemonId], pokedexEntry.pokedexId, marshPokemonId)

                # If the Pokémon doesn't normally appear, check which period is best after special encounters have been added
                if (maxPeriodScore == 0 and zoneVersion.maxRouteScore > 0):
                    maxPeriodScore, bestPeriods = getBestPeriodScore(zoneVersion, pokedexEntry.pokedexId)

                    # Check if we found a better period than default (morning)
                    if (maxPeriodScore > zoneVersion.maxRouteScore):
                        zoneVersion.maxRouteScore = maxPeriodScore
                        zoneVersion.selectedMethod["period"] = "/".join(bestPeriods)

                # Check if this route has the best overall rarity score for the target Pokemon
                if (zoneVersion.maxRouteScore > targetMaxScore):
                    targetMaxScore = zoneVersion.maxRouteScore
                    bestRoute = zone
                    bestVersionMethods = " / ".join([method for method in zoneVersion.selectedMethod.values() if method != ""])

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
                    addZoneEncounter(zoneWaterEncounters["surf"], zone.surfEncounters[i].pokedexId, zone.surfEncounters[i])
                    addZoneEncounter(zoneWaterEncounters["oldrod"], zone.oldRodEncounters[i].pokedexId, zone.oldRodEncounters[i])
                    addZoneEncounter(zoneWaterEncounters["goodrod"], zone.goodRodEncounters[i].pokedexId, zone.goodRodEncounters[i])
                    addZoneEncounter(zoneWaterEncounters["superrod"], zone.superRodEncounters[i].pokedexId, zone.superRodEncounters[i])

                # Calculate zone score for each way to fish Pokemon
                zoneScores = {
                    "surf": calculateZoneScore(zoneWaterEncounters["surf"], pokedexEntry.pokedexId),
                    "oldrod": calculateZoneScore(zoneWaterEncounters["oldrod"], pokedexEntry.pokedexId),
                    "goodrod" : calculateZoneScore(zoneWaterEncounters["goodrod"], pokedexEntry.pokedexId),
                    "superrod" : calculateZoneScore(zoneWaterEncounters["superrod"], pokedexEntry.pokedexId)
                }

                # Find most optimal method to find the rarer Pokemon
                maxWaterScore = max(zoneScores.values())
                bestMethods = [method for method, score in zoneScores.items() if score == maxWaterScore]
                selectedMethod = "/".join(bestMethods)

                # Check if this route water has the best overall rarity score for the target Pokemon
                if (maxWaterScore > targetMaxScore):
                    targetMaxScore = maxWaterScore
                    bestRoute = zone
                    bestVersionMethods = selectedMethod

        # Save most optimal zone
        POKEDEX[pokedexEntry.pokedexId].maxScore = targetMaxScore
        POKEDEX[pokedexEntry.pokedexId].bestRoute = bestRoute
        POKEDEX[pokedexEntry.pokedexId].bestVersionMethods = bestVersionMethods


#####################################################################################################
# Display all encounter data (most optimized zone, encounter rate for each zone, etc) in a txt file #
#####################################################################################################
def printPokedex():
    with open("backup/txt/pokedex.txt", "w", encoding="utf-8") as file:
        for pokedexId, pokemon in POKEDEX.items():
            file.write(f"{pokedexId} - {pokemon.name}")

            # Replace GBA gameId by actual GBA game name
            if ("gba (" in pokemon.bestVersionMethods):
                gbaGameId = int(re.findall(r"gba \((\d)", pokemon.bestVersionMethods)[0])
                pokemon.bestVersionMethods = pokemon.bestVersionMethods.replace(f"gba ({gbaGameId}", f"gba ({GBAGAME_NAMES[gbaGameId]}")

            if (pokemon.rarity):
                file.write(f" - Rarity Score : {round(pokemon.rarity,3)}")
            if (pokemon.bestRoute):
                file.write(f" - Best Route : {pokemon.bestRoute.name} ({pokemon.bestVersionMethods}) : {pokemon.maxScore}")
            file.write("\n")

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
                            file.write("\t\t")

                            if (encounterData["rate"]):
                                file.write(f"{encounter} : {encounterData["rate"]}% - ")

                            file.write(f"lvl {encounterData["minLevel"]}")

                            if (encounterData["minLevel"] != encounterData["maxLevel"]):
                                file.write(f"-{encounterData["maxLevel"]}")

                            if (encounterData["dangerousMoves"]):
                                file.write(f" / {encounterData["dangerousMoves"]}")

                            file.write("\n")

            else:
                file.write("\tCannot be found\n")

            file.write("\n")

initPokedex()