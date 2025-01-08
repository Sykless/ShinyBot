import copy
from data import POKEMON_NAMES
from data import GBAGAME_NAMES

from encounter import ENCOUNTERTABLES_DICT
from encounter import BASEENCOUNTER_RATES
from encounter import SPECIALENCOUNTERS
from encounter import SPECIALGRASSENCOUNTERS

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

    # Link evolution to base Pokémon
    def setEvolvesInto(self, evolutionList):
        self.evolvesInto = []

        for evolution in evolutionList:
            self.evolvesInto.append(POKEDEX[evolution])
            POKEDEX[evolution].evolvesFrom = self

    def __str__(self):
        return self.name + " " + str(self.encounterTables)

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

POKEDEX = {pokedexId : PokedexEntry(pokedexId) for pokedexId in range(1, 494)}
EVOLUTIONS = {
    # Gen I
    1: [2], 2: [3],  # Bulbizarre - Herbizarre - Florizarre
    4: [5], 5: [6],  # Salamèche - Reptincel - Dracaufeu
    7: [8], 8: [9],  # Carapuce - Carabaffe - Tortank
    10: [11], 11: [12],  # Chenipan - Chrysacier - Papilusion
    13: [14], 14: [15],  # Aspicot - Coconfort - Dardargnan
    16: [17], 17: [18],  # Roucool - Roucoups - Roucarnage
    19: [20],  # Rattata - Rattatac
    21: [22],  # Piafabec - Rapasdepic
    23: [24],  # Abo - Arbok
    25: [26],  # Pikachu - Raichu
    27: [28],  # Sabelette - Sablaireau
    29: [30], 30: [31],  # Nidoran-F - Nidorina - Nidoqueen
    32: [33], 33: [34],  # Nidoran-M - Nidorino - Nidoking
    35: [36],  # Mélofée - Mélodelfe
    37: [38],  # Goupix - Feunard
    39: [40],  # Rondoudou - Grodoudou
    41: [42], 42: [169],  # Nosferapti - Nosferalto - Nostenfer
    43: [44], 44: [45, 182],  # Mystherbe - Ortide - Rafflesia / Joliflor
    46: [47],  # Paras - Parasect
    48: [49],  # Mimitoss - Aéromite
    50: [51],  # Taupiqueur - Triopikeur
    52: [53],  # Miaouss - Persian
    54: [55],  # Psykokwak - Akwakwak
    56: [57],  # Férosinge - Colossinge
    58: [59],  # Caninos - Arcanin
    60: [61], 61: [62, 186],  # Ptitard - Têtarte - Tartard / Tarpaud
    63: [64], 64: [65],  # Abra - Kadabra - Alakazam
    66: [67], 67: [68],  # Machoc - Machopeur - Mackogneur
    69: [70], 70: [71],  # Chétiflor - Boustiflor - Empiflor
    72: [73],  # Tentacool - Tentacruel
    74: [75], 75: [76],  # Racaillou - Gravalanch - Grolem
    77: [78],  # Ponyta - Galopa
    79: [80, 199],  # Ramoloss - Flagadoss / Roigada
    81: [82], 82: [462],  # Magnéti - Magnéton - Magnézone
    84: [85],  # Doduo - Dodrio
    86: [87],  # Otaria - Lamantine
    88: [89],  # Tadmorv - Grotadmorv
    90: [91],  # Kokiyas - Crustabri
    92: [93], 93: [94],  # Fantominus - Spectrum - Ectoplasma
    95: [208],  # Onix - Steelix
    96: [97],  # Soporifik - Hypnomade
    98: [99],  # Krabby - Krabboss
    100: [101],  # Voltorbe - Électrode
    102: [103],  # Noeunoeuf - Noadkoko
    104: [105],  # Osselait - Ossatueur
    108: [463],  # Excelangue - Coudlangue
    109: [110],  # Smogo - Smogogo
    111: [112], 112: [464],  # Rhinocorne - Rhinoféros - Rhinastoc
    113: [242],  # Leveinard - Leuphorie
    114: [465],  # Saquedeneu - Bouldeneu
    116: [117], 117: [230],  # Hypotrempe - Hypocéan - Hyporoi
    118: [119],  # Poissirène - Poissoroy
    120: [121],  # Stari - Staross
    123: [212],  # Insécateur - Cizayox
    125: [466],  # Élektek - Élekable
    126: [467],  # Magmar - Maganon
    129: [130],  # Magicarpe - Léviator
    133: [134, 135, 136, 196, 197, 470, 471],  # Évoli - Aquali / Voltali / Pyroli / Mentali / Noctali / Phyllali / Givrali
    137: [233],  # Porygon - Porygon2
    138: [139],  # Amonita - Amonistar
    140: [141],  # Kabuto - Kabutops
    147: [148], 148: [149],  # Minidraco - Draco - Dracolosse

    # Gen II
    152: [153], 153: [154],  # Germignon - Macronium - Méganium
    155: [156], 156: [157],  # Héricendre - Feurisson - Typhlosion
    158: [159], 159: [160],  # Kaiminus - Crocrodil - Aligatueur
    161: [162],  # Fouinette - Fouinar
    163: [164],  # Hoothoot - Noarfang
    165: [166],  # Coxy - Coxyclaque
    167: [168],  # Mimigal - Migalos
    170: [171],  # Loupio - Lanturn
    172: [25],  # Pichu - Pikachu
    173: [35],  # Mélo - Mélofée
    174: [39],  # Toudoudou - Rondoudou
    175: [176], 176: [468],  # Togepi - Togetic - Togekiss
    177: [178],  # Natu - Xatu
    179: [180], 180: [181],  # Wattouat - Lainergie - Pharamp
    183: [184],  # Marill - Azumarill
    187: [188], 188: [189],  # Granivol - Floravol - Cotovol
    190: [424],  # Capumain - Capidextre
    191: [192],  # Tournegrin - Héliatronc
    193: [469],  # Yanma - Yanméga
    194: [195],  # Axoloto - Maraiste
    198: [430],  # Cornèbre - Corboss
    200: [429],  # Feuforêve - Magirêve
    204: [205],  # Pomdepik - Foretress
    207: [472],  # Scorplane - Scorvol
    209: [210],  # Snubbull - Granbull
    215: [461],  # Farfuret - Dimoret
    216: [217],  # Teddiursa - Ursaring
    218: [219],  # Limagma - Volcaropod
    220: [221], 221: [473],  # Marcacrin - Cochignon - Mammochon
    223: [224],  # Rémoraid - Octillery
    228: [229],  # Malosse - Démolosse
    231: [232],  # Phanpy - Donphan
    233: [474],  # Porygon2 - Porygon-Z
    236: [106, 107, 237],  # Debugant - Kicklee / Tygnon / Kapoera
    238: [124],  # Lippouti - Lippoutou
    239: [125],  # Élekid - Élektek
    240: [126],  # Magby - Magmar
    246: [247], 247: [248],  # Embrylex - Ymphect - Tyranocif

    # Gen III
    252: [253], 253: [254],  # Arcko - Massko - Jungko
    255: [256], 256: [257],  # Poussifeu - Galifeu - Braségali
    258: [259], 259: [260],  # Gobou - Flobio - Laggron
    261: [262],  # Medhyèna - Grahyèna
    263: [264],  # Zigzaton - Linéon
    265: [266, 268],  # Chenipotte - Armulys / Blindalys
    266: [267],  # Armulys - Charmillon
    268: [269],  # Blindalys - Papinox
    270: [271], 271: [272],  # Nénupiot - Lombre - Ludicolo
    273: [274], 274: [275],  # Grainipiot - Pifeuil - Tengalice
    276: [277],  # Nirondelle - Hélédelle
    278: [279],  # Goélise - Bekipan
    280: [281], 281: [282, 475],  # Tarsal - Kirlia - Gardevoir / Gallame
    283: [284],  # Arakdo - Maskadra
    285: [286],  # Balignon - Chapignon
    287: [288], 288: [289],  # Parecool - Vigoroth - Monaflèmit
    290: [291, 292],  # Ningale - Ninjask / Munja
    293: [294], 294: [295],  # Chuchmur - Ramboum - Brouhabam
    296: [297],  # Makuhita - Hariyama
    298: [183],  # Azurill - Marill
    299: [476],  # Tarinor - Tarinorme
    300: [301],  # Skitty - Delcatty
    304: [305], 305: [306],  # Galekid - Galegon - Galeking
    307: [308],  # Méditikka - Charmina
    309: [310],  # Dynavolt - Élecsprint
    315: [407],  # Rosélia - Roserade
    316: [317],  # Gloupti - Avaltout
    318: [319],  # Carvanha - Sharpedo
    320: [321],  # Wailmer - Wailord
    322: [323],  # Chamallot - Camérupt
    325: [326],  # Spoink - Groret
    328: [329], 329: [330],  # Kraknoix - Vibraninf - Libégon
    331: [332],  # Cacnea - Cacturne
    333: [334],  # Tylton - Altaria
    339: [340],  # Barloche - Barbicha
    341: [342],  # Écrapince - Colhomard
    343: [344],  # Balbuto - Kaorine
    345: [346],  # Lilia - Vacilys
    347: [348],  # Anorith - Armaldo
    349: [350],  # Barpau - Milobellus
    353: [354],  # Polichombr - Branette
    355: [356], 356: [477],  # Skelénox - Téraclope - Noctunoir
    360: [202],  # Okéoké - Qulbutoké
    361: [362, 478],  # Stalgamin - Oniglali / Momartik
    363: [364], 364: [365],  # Obalie - Phogleur - Kaimorse
    366: [367, 368],  # Coquiperl - Serpang / Rosabyss
    371: [372], 372: [373],  # Draby - Drackhaus - Drattak
    374: [375], 375: [376],  # Terhal - Métang - Métalosse

    # Gen IV
    387: [388], 388: [389],  # Tortipouss - Boskara - Torterra
    390: [391], 391: [392],  # Ouisticram - Chimpenfeu - Simiabraz
    393: [394], 394: [395],  # Tiplouf - Prinplouf - Pingoléon
    396: [397], 397: [398],  # Étourmi - Étourvol - Étouraptor
    399: [400],  # Keunotor - Castorno
    401: [402],  # Crikzik - Mélokrik
    403: [404], 404: [405],  # Lixy - Luxio - Luxray
    406: [315],  # Rozbouton - Rosélia
    408: [409],  # Kranidos - Charkos
    410: [411],  # Dinoclier - Bastiodon
    412: [413, 414],  # Cheniti - Cheniselle / Papilord
    415: [416],  # Apitrini - Apireine
    418: [419],  # Mustébouée - Mustéflott
    420: [421],  # Ceribou - Ceriflor
    422: [423],  # Sancoki - Tritosor
    425: [426],  # Baudrive - Grodrive
    427: [428],  # Laporeille - Lockpin
    431: [432],  # Chaglam - Chaffreux
    433: [358],  # Korillon - Éoko
    434: [435],  # Moufouette - Moufflair
    436: [437],  # Archéomire - Archéodong
    438: [185],  # Manzaï - Simularbre
    439: [122],  # Mime Jr. - M. Mime
    440: [113],  # Ptiravi - Leveinard
    443: [444], 444: [445],  # Griknot - Carmache - Carchacrok
    446: [143],  # Goinfrex - Ronflex
    447: [448],  # Riolu - Lucario
    449: [450],  # Hippopotas - Hippodocus
    451: [452],  # Rapion - Drascore
    453: [454],  # Cradopaud - Coatox
    456: [457],  # Écayon - Luminéon
    458: [226],  # Babimanta - Démanta
    459: [460],  # Blizzi - Blizzaroi
    489: [490]   # Phione - Manaphy (not really an evolution but used to mark it as an egg)
}
    
def populatePokedex():

    # Setup evolutions for each Pokémon
    for pokedexId, evolution in EVOLUTIONS.items():
        POKEDEX[pokedexId].setEvolvesInto(evolution)

    # Search in each zone if a Pokémon can be found in water or grass
    for zone in ENCOUNTERTABLES_DICT.values():
        
        # Grass encounters
        if (zone.baseEncounters):

            # Morning
            for encounter in zone.baseEncounters:
                addPokedexEncounter(encounter.pokedexId, zone.name, "morning", encounter.rate)
                addPokedexEncounter(encounter.pokedexId, zone.name, "day", encounter.rate)
                addPokedexEncounter(encounter.pokedexId, zone.name, "night", encounter.rate)

            # Day
            for dayId, encounterSlot in {0:2, 1:3}.items():
                addPokedexEncounter(zone.dayEncounters[dayId], zone.name, "day", BASEENCOUNTER_RATES[encounterSlot])
                removePokedexEncounter(zone, "day", encounterSlot)

            # Night
            for nightId, encounterSlot in {0:2, 1:3}.items():
                addPokedexEncounter(zone.nightEncounters[nightId], zone.name, "night", BASEENCOUNTER_RATES[encounterSlot])
                removePokedexEncounter(zone, "night", encounterSlot)

            # Pokéradar
            for pokeradarId, encounterSlot in {0:4, 1:5, 2:10, 3:11}.items():
                if (zone.pokeradarEncounters[pokeradarId] != zone.baseEncounters[encounterSlot].pokedexId):             
                    addPokedexEncounter(zone.pokeradarEncounters[pokeradarId], zone.name, "pokeradar", BASEENCOUNTER_RATES[encounterSlot])

            # Swarm
            for swarmId, encounterSlot in {0:0, 1:1}.items():
                if (zone.swarmEncounters[swarmId] != zone.baseEncounters[encounterSlot].pokedexId):
                    addPokedexEncounter(zone.swarmEncounters[swarmId], zone.name, "swarm", BASEENCOUNTER_RATES[encounterSlot])

            # GBA
            for gbaGame in range(1,6):
                for gbaId, encounterSlot in {0:8, 1:9}.items():
                    if (zone.gbaEncounters[gbaGame][gbaId] != zone.baseEncounters[encounterSlot].pokedexId):
                        addPokedexEncounter(zone.gbaEncounters[gbaGame][gbaId], zone.name + " (" + GBAGAME_NAMES[gbaGame] + ")", "gba", BASEENCOUNTER_RATES[encounterSlot])

        # Water encounters
        if (zone.surfEncounters):
            for environment, encounterTable in {"surf": zone.surfEncounters, "oldrod": zone.oldRodEncounters, "goodrod": zone.goodRodEncounters, "superrod": zone.superRodEncounters}.items():

                # Surf - Old/Good/Super rod
                for encounter in encounterTable:
                    addPokedexEncounter(encounter.pokedexId, zone.name, environment, encounter.rate)


    # Add special encounters (static, roaming, fossils, etc)
    for environment, encounterTable in SPECIALENCOUNTERS.items():
        for pokedexId in encounterTable:
            addPokedexEncounter(pokedexId, environment, environment, True)

    # Add Garden/Marsh encounters
    for environment, zoneName in {"garden": "Jardin Trophée", "marsh": "Grand Marais"}.items():
        for pokedexId in list(set(SPECIALGRASSENCOUNTERS[environment])):
            addPokedexEncounter(pokedexId, zoneName, environment, BASEENCOUNTER_RATES[6] + BASEENCOUNTER_RATES[7])

    # If a Pokémon cannot be found in the wild, check if its pre-evolution or evolution can
    for pokedexId, pokemon in POKEDEX.items():

        if (not pokemon.encounterTables):

            # Check pre-evolutions encounters, we might be able to evolve one of them
            preEvolution = pokemon.evolvesFrom
            if (preEvolution):

                # PreEvolution can be found in the wild : add encounter
                if (canBeFoundInGame(preEvolution.encounterTables)):
                    addPokedexEncounter(pokedexId, preEvolution.pokedexId, "evolution", True)

                # PreEvolution's pre-evolution can be found in the wild : add encounter
                if (preEvolution.evolvesFrom and canBeFoundInGame(preEvolution.evolvesFrom.encounterTables)):
                    addPokedexEncounter(pokedexId, preEvolution.evolvesFrom.pokedexId, "evolution", True)

            # Check evolutions encounters, we might be able to hatch an egg from one of them
            if (pokemon.evolvesInto):
                for evolution in pokemon.evolvesInto:

                    # Evolution can be found in the wild : add encounter
                    if (canBeFoundInGame(evolution.encounterTables)):
                        addPokedexEncounter(pokedexId, evolution.pokedexId, "hatch", True)

                    for secondEvolution in evolution.evolvesInto:

                        # 2nd Evolution can be found in the wild : add encounter
                        if (canBeFoundInGame(secondEvolution.encounterTables)):
                            addPokedexEncounter(pokedexId, secondEvolution.pokedexId, "hatch", True)

def canBeFoundInGame(encounterTable):
    return (encounterTable
            and not (len(encounterTable) == 1
                     and ("evolution" in encounterTable or "hatch" in encounterTable)))

def addPokedexEncounter(pokedexId, zoneName, environment, rate):
    if (environment not in POKEDEX[pokedexId].encounterTables):
        POKEDEX[pokedexId].encounterTables[environment] = {}

    if (zoneName not in POKEDEX[pokedexId].encounterTables[environment]):
        POKEDEX[pokedexId].encounterTables[environment][zoneName] = 0

    POKEDEX[pokedexId].encounterTables[environment][zoneName] += rate

def removePokedexEncounter(zone, environment, encounterSlot):
    POKEDEX[zone.baseEncounters[encounterSlot].pokedexId].encounterTables[environment][zone.name] -= BASEENCOUNTER_RATES[encounterSlot]

    if (POKEDEX[zone.baseEncounters[encounterSlot].pokedexId].encounterTables[environment][zone.name] == 0):
        del POKEDEX[zone.baseEncounters[encounterSlot].pokedexId].encounterTables[environment][zone.name]

    if (not POKEDEX[zone.baseEncounters[encounterSlot].pokedexId].encounterTables[environment]):
        del POKEDEX[zone.baseEncounters[encounterSlot].pokedexId].encounterTables[environment]

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

                        if (environment not in SPECIALENCOUNTERS):
                            for encounter, rate in encounterTable.items():
                                file.write("\t\t" + str(encounter) + " : " + str(rate) + "%\n")

            else:
                file.write("\tCannot be found\n")

            file.write("\n")

def populatePokedexEncounters():
    for pokedexEntry in POKEDEX.values():
        for method, encounterTable in pokedexEntry.encounterTables.items():
            # Base grass/cave encounters
            if method in ["morning", "day", "night"]:
                for zone, rate in encounterTable.items():

                    if (zone == "Jardin Trophée"):
                        uncaughtGardenPokemon = sum(1 for pokedexId in SPECIALGRASSENCOUNTERS["garden"] if not POKEDEX[pokedexId].caught)
                        pokedexEntry.totalRate += rate * uncaughtGardenPokemon

                    elif ("Grand Marais" in zone):
                        uncaughtMarshPokemon = sum(1 for pokedexId in SPECIALGRASSENCOUNTERS["marsh"] if not POKEDEX[pokedexId].caught)
                        pokedexEntry.totalRate += rate * uncaughtMarshPokemon

                    else:
                        pokedexEntry.totalRate += rate

            # Special grass/cave encounters
            elif method in ["gba", "swarm", "garden", "marsh"]:
                for rate in encounterTable.values():
                    pokedexEntry.totalRate += rate * 3 # x3 since you can find them during morning/day/night

            # Surf encounters
            elif method in ["surf"]:
                for rate in encounterTable.values():
                    pass # Do something with surf rates

            # Rods encounters
            elif method in ["oldrod", "goodrod", "superrod"]:
                for rate in encounterTable.values():
                    pass # Do something with rod rates

        # Calculate rarity score from encounter total rate
        if (pokedexEntry.totalRate > 0):
            pokedexEntry.rarity = round(100 / pokedexEntry.totalRate, 2)

    # Find most optimal zone
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

    # for pokedexId in zoneEncounters:
    #     print(f"{POKEMON_NAMES[pokedexId]} : {zoneEncounters[pokedexId]} * {POKEDEX[pokedexId].rarity} = {zoneEncounters[pokedexId] * POKEDEX[pokedexId].rarity}")
    # print(zoneEncounters)
    # print(f"{zoneEncounters[targetPokemon]} + {rarityScore} = {zoneScore}", end = "\n\n")

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
            bestZoneVersion = copy.deepcopy(zoneEncounters[bestPeriods[0]])
            selectedPeriod = "/".join(bestPeriods)

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

            if (zoneVersion.selectedMethod["gba"]):
                bestZoneVersion = zoneVersion.selectedMethod["gba"]
                
            # Garden encounters
            if (zone.name == "Jardin Trophée"):
                for gardenPokemonId in list(set(SPECIALGRASSENCOUNTERS["garden"])):
                    zoneEncounters["garden"][gardenPokemonId] = copy.deepcopy(bestZoneVersion)

                    # Check which Garden Pokémon is more optimal
                    zoneVersion.calculateSpecialMethodScore("garden", 2 * [gardenPokemonId], zoneEncounters["garden"][gardenPokemonId], targetPokemon, gardenPokemonId)

            if (zoneVersion.selectedMethod["garden"]):
                bestZoneVersion = zoneVersion.selectedMethod["garden"]

            # Check if this route has the best overall rarity score for the target Pokemon
            if (zoneVersion.maxRouteScore > targetMaxScore):
                targetMaxScore = zoneVersion.maxRouteScore
                bestRoute = zone
                bestVersion = bestZoneVersion
                bestVersionMethods = selectedPeriod + "".join(zoneVersion.selectedMethod.values())

    # Save most optimal zone
    POKEDEX[targetPokemon].maxScore = targetMaxScore
    POKEDEX[targetPokemon].bestRoute = bestRoute
    POKEDEX[targetPokemon].bestVersionMethods = bestVersionMethods
    POKEDEX[targetPokemon].bestVersion = bestVersion

populatePokedex()
populatePokedexEncounters()
printPokedex()