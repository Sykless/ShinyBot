import encounter
from data import POKEMON_NAMES

class PokedexEntry():
    def __init__(self, pokedexId):
        self.pokedexId = pokedexId
        self.name = POKEMON_NAMES[pokedexId]
        self.evolvesFrom = None
        self.evolvesInto = []

    # Link evolution to base Pokémon
    def setEvolvesInto(self, evolutionList):
        for evolution in evolutionList:
            self.evolvesInto = POKEDEX[evolution]
            POKEDEX[evolution].evolvesFrom = self


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

for pokedexId, evolution in EVOLUTIONS.items():
    POKEDEX[pokedexId].setEvolvesInto(evolution)