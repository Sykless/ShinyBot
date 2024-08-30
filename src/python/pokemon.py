from utils import formatNumber
from utils import getShinyValue
from bag import Item

import memory

FLY_ID = 19
DIG_ID = 91

class Move:
    def __init__(self, id, PP, PPUp):
        self.id = id
        self.name = MOVE_NAMES[id]
        self.PP = PP
        self.PPUp = PPUp
    
    def isHM(self):
            return self.id in HM_LIST

class Ability:
    def __init__(self, id):
        self.id = id
        self.name = ABILITY_LIST[id]

class Nature:
    def __init__(self, id):
        self.id = id
        self.name = NATURE_LIST[id]

class Contest:
    def __init__(self, cool, beauty, cute, smart, tough, sheen):
        self.cool = cool
        self.cool = beauty
        self.cool = cute
        self.cool = smart
        self.cool = tough
        self.cool = sheen

class Met:
    def __init__(self, level, date, location, dateEggReceived, locationEggReceived):
        self.level = level
        self.date = date
        self.location = location
        self.dateEggReceived = dateEggReceived
        self.locationEggReceived = locationEggReceived

class Trainer:
    def __init__(self, ID, secretID, name, female):
        self.ID = ID
        self.secretID = secretID
        self.name = name
        self.female = female

class Ribbons:
    def __init__(self, sinnohRibbon1, sinnohRibbon2, sinnohRibbon3, sinnohRibbon4, hoennRibbon1, hoennRibbon2):
        self.sinnohRibbon1 = sinnohRibbon1
        self.sinnohRibbon2 = sinnohRibbon2
        self.sinnohRibbon3 = sinnohRibbon3
        self.sinnohRibbon4 = sinnohRibbon4
        self.hoennRibbon1 = hoennRibbon1
        self.hoennRibbon2 = hoennRibbon2

class Stats:
    def __init__(self, HP, attack, defense, speed, specialAttack, specialDefense):
        self.HP = HP
        self.attack = attack
        self.defense = defense
        self.speed = speed
        self.specialAttack = specialAttack
        self.specialDefense = specialDefense

    def __str__(self):
        statsString = ("HP : " + str(self.HP)
                + " - ATQ : " + str(self.attack)
                + " - DEF : " + str(self.defense)
                + " - SPA : " + str(self.specialAttack)
                + " - SPD : " + str(self.specialDefense)
                + " - SPE : " + str(self.speed))
        return statsString

class Status:
    def __init__(self, poisoned, paralyzed, toxic, asleep, frozen, burned):
        self.poisoned = poisoned
        self.paralyzed = paralyzed
        self.toxic = toxic
        self.asleep = asleep
        self.frozen = frozen
        self.burned = burned 

class Pokemon:
    def __init__(self, experience = None, ribbons = None, stats = None, sealCoordinates = None, currentHP = None, moves = None, met = None,
                 alternateForms = None, pokedexId = None, IV = None, OT = None, status = None, level = None, EV = None, pokeballId = None,
                 contest = None, female = None, pokerus = None, originalLanguage = None, markings = None, nickname = None, capsule = None,
                 genderless = None, originGame = None, nicknamed = None, item = None, pid = None, friendship = None, abilityId = None,
                 isEgg = None):

        try:
            self.pid = pid
            self.pokedexId = pokedexId
            self.name = POKEMON_NAMES[pokedexId]
            self.level = level
            self.moves = [Move(**jsonMove) for jsonMove in moves]
            self.ability = Ability(abilityId)
            self.nature = Nature(pid % 25)
            self.item = item
            self.currentHP = currentHP
            self.stats = Stats(**stats)
            self.IV = Stats(**IV)
            self.EV = Stats(**EV)
            self.experience = experience
            self.status = Status(**status)

            self.OT = Trainer(**OT)
            self.met = Met(**met)
            self.nicknamed = nicknamed
            self.nickname = nickname
            self.isEgg = isEgg
            self.pokeball = Item(pokeballId,1)
            self.female = female
            self.genderless = genderless
            self.friendship = friendship
            self.pokerus = pokerus
            self.alternateForms = alternateForms
            self.originalLanguage = originalLanguage
            self.originGame = originGame

            self.ribbons = Ribbons(**ribbons)
            self.contest = Contest(**contest)
            self.markings = markings
            self.capsule = capsule
            self.sealCoordinates = sealCoordinates

            self.shinyValue = getShinyValue(pid, self.OT.ID, self.OT.secretID)
            self.isShiny = self.shinyValue < 255

            self.isValid = True

        # We might receive invalid data since team memory address is shared with other parameters when you're not in battle/menu
        except IndexError:
            self.isValid = False
        
    def __str__(self):
        return (str(self.name) + " " + ("♀" if self.female else "♂")
                + " level " + str(self.level) + " (" + self.ability.name + " - " + self.nature.name + ")" + " - PID = " + str(hex(self.pid)) + " - Shiny value : " + str(self.shinyValue)  + "\n"
                + " - " + self.moves[0].name + " (" + str(self.moves[0].PP) + ")\n"
                + (" - " + self.moves[1].name + " (" + str(self.moves[1].PP) + ")\n" if len(self.moves) >= 2 else "")
                + (" - " + self.moves[2].name + " (" + str(self.moves[2].PP) + ")\n" if len(self.moves) >= 3 else "")
                + (" - " + self.moves[3].name + " (" + str(self.moves[3].PP) + ")\n" if len(self.moves) >= 4 else "")
                + "\n"
                + " =============================================\n"
                + " =       =  HP = ATQ = DEF = SPA = SPD = SPE =\n"
                + " =============================================\n"
                + " = STATS = " + formatNumber(self.stats.HP) + " = " + formatNumber(self.stats.attack) + " = " + formatNumber(self.stats.defense) + " = " + formatNumber(self.stats.specialAttack) + " = " + formatNumber(self.stats.specialDefense) + " = " + formatNumber(self.stats.speed) + " =\n"
                + " =============================================\n"
                + " = IV    = " + formatNumber(self.IV.HP) + " = " + formatNumber(self.IV.attack) + " = " + formatNumber(self.IV.defense) + " = " + formatNumber(self.IV.specialAttack) + " = " + formatNumber(self.IV.specialDefense) + " = " + formatNumber(self.IV.speed) + " =\n"
                + " =============================================\n"
                + " = EV    = " + formatNumber(self.EV.HP) + " = " + formatNumber(self.EV.attack) + " = " + formatNumber(self.EV.defense) + " = " + formatNumber(self.EV.specialAttack) + " = " + formatNumber(self.EV.specialDefense) + " = " + formatNumber(self.EV.speed) + " =\n"
                + " =============================================\n") if hasattr(self, 'name') else ("Unknown Pokémon : " + str(self.pokedexId))
    
def isHMAvailable(hmId):
    jsonTeamData = memory.readPokemonTeamData()

    for pokemonPosition in range(len(jsonTeamData)):
        movePosition = 0
        pokemon = Pokemon(**jsonTeamData[pokemonPosition])

        if (pokemon.isValid):
            for move in pokemon.moves:
                if (move.isHM()):
                    movePosition += 1

                    # Return first pokemon with Fly available
                    if (move.id == hmId):
                        return [pokemonPosition, movePosition]
    
    # No Pokemon with Fly
    print("No Pokemon with HM " + MOVE_NAMES[hmId] + " !")
    return [None, None]

POKEMON_NAMES =  [
    # Gen 1
     "MissingNo", "Bulbizarre", "Herbizarre", "Florizarre", "Salamèche", "Reptincel", "Dracaufeu", "Carapuce", "Carabaffe","Tortank", "Chenipan", "Chrysacier",
     "Papilusion", "Aspicot", "Coconfort", "Dardargnan", "Roucool", "Roucoups", "Roucarnage", "Rattata", "Rattatac", "Piafabec", "Rapasdepic", "Abo", "Arbok",
     "Pikachu", "Raichu", "Sabelette", "Sablaireau", "Nidoran-F", "Nidorina", "Nidoqueen", "Nidoran-M", "Nidorino", "Nidoking", "Mélofée", "Mélodelfe", "Goupix",
     "Feunard", "Rondoudou", "Grodoudou", "Nosferapti", "Nosferalto", "Mystherbe", "Ortide", "Rafflesia", "Paras", "Parasect", "Mimitoss", "Aéromite", "Taupiqueur",
     "Triopikeur", "Miaouss", "Persian", "Psykokwak", "Akwakwak", "Férosinge", "Colossinge", "Caninos", "Arcanin", "Ptitard", "Têtarte", "Tartard", "Abra",
     "Kadabra", "Alakazam", "Machoc", "Machopeur", "Mackogneur", "Chétiflor", "Boustiflor", "Empiflor", "Tentacool", "Tentacruel", "Racaillou", "Gravalanch",
     "Grolem", "Ponyta", "Galopa", "Ramoloss", "Flagadoss", "Magnéti", "Magnéton", "Canarticho", "Doduo", "Dodrio", "Otaria", "Lamantine", "Tadmorv", "Grotadmorv",
     "Kokiyas", "Crustabri", "Fantominus", "Spectrum", "Ectoplasma", "Onix", "Soporifik", "Hypnomade", "Krabby", "Krabboss", "Voltorbe", "Électrode", "Noeunoeuf",
     "Noadkoko", "Osselait", "Ossatueur", "Kicklee", "Tygnon", "Excelangue", "Smogo", "Smogogo", "Rhinocorne", "Rhinoféros", "Leveinard", "Saquedeneu", "Kangourex",
     "Hypotrempe", "Hypocéan", "Poissirène", "Poissoroy", "Stari", "Staross", "M. Mime", "Insécateur", "Lippoutou", "Élektek", "Magmar", "Scarabrute", "Tauros",
     "Magicarpe", "Léviator", "Lokhlass", "Métamorph", "Évoli", "Aquali", "Voltali", "Pyroli", "Porygon", "Amonita", "Amonistar", "Kabuto", "Kabutops", "Ptéra",
     "Ronflex", "Artikodin", "Électhor", "Sulfura", "Minidraco", "Draco", "Dracolosse", "Mewtwo", "Mew", 
    
    # Gen 2
    "Germignon", "Macronium", "Méganium", "Héricendre", "Feurisson", "Typhlosion", "Kaiminus", "Crocrodil", "Aligatueur", "Fouinette", "Fouinar",
    "Hoothoot", "Noarfang", "Coxy", "Coxyclaque", "Mimigal", "Migalos", "Nostenfer", "Loupio", "Lanturn", "Pichu", "Mélo", "Toudoudou", "Togepi", "Togetic",
    "Natu", "Xatu", "Wattouat", "Lainergie", "Pharamp", "Joliflor", "Marill", "Azumarill", "Simularbre", "Tarpaud", "Granivol", "Floravol", "Cotovol", "Capumain",
    "Tournegrin", "Héliatronc", "Yanma", "Axoloto", "Maraiste", "Mentali", "Noctali", "Cornèbre", "Roigada", "Feuforêve", "Zarbi", "Qulbutoké", "Girafarig",
    "Pomdepik", "Foretress", "Insolourdo", "Scorplane", "Steelix", "Snubbull", "Granbull", "Qwilfish", "Cizayox", "Caratroc", "Scarhino", "Farfuret", "Teddiursa",
    "Ursaring", "Limagma", "Volcaropod", "Marcacrin", "Cochignon", "Corayon", "Rémoraid", "Octillery", "Cadoizo", "Démanta", "Airmure", "Malosse", "Démolosse",
    "Hyporoi", "Phanpy", "Donphan", "Porygon2", "Cerfrousse", "Queulorior", "Debugant", "Kapoera", "Lippouti", "Élekid", "Magby", "Écrémeuh", "Leuphorie",
    "Raikou", "Entei", "Suicune", "Embrylex", "Ymphect", "Tyranocif", "Lugia", "Ho-Oh", "Celebi",
    
    # Gen 3
    "Arcko", "Massko", "Jungko", "Poussifeu", "Galifeu", "Braségali", "Gobou", "Flobio", "Laggron", "Medhyèna", "Grahyèna", "Zigzaton", "Linéon", "Chenipotte",
    "Armulys", "Charmillon", "Blindalys", "Papinox", "Nénupiot", "Lombre", "Ludicolo", "Grainipiot", "Pifeuil", "Tengalice", "Nirondelle", "Hélédelle", "Goélise",
    "Bekipan", "Tarsal", "Kirlia", "Gardevoir", "Arakdo", "Maskadra", "Balignon", "Chapignon", "Parecool", "Vigoroth", "Monaflèmit", "Ningale", "Ninjask","Munja",
    "Chuchmur", "Ramboum", "Brouhabam", "Makuhita", "Hariyama", "Azurill", "Tarinor", "Skitty", "Delcatty", "Ténéfix", "Mysdibule", "Galekid", "Galegon",
    "Galeking", "Méditikka", "Charmina", "Dynavolt", "Élecsprint", "Posipi", "Négapi", "Muciole", "Lumivole", "Rosélia", "Gloupti", "Avaltout", "Carvanha",
    "Sharpedo", "Wailmer", "Wailord", "Chamallot", "Camérupt", "Chartor", "Spoink", "Groret", "Spinda", "Kraknoix", "Vibraninf", "Libégon", "Cacnea", "Cacturne",
    "Tylton", "Altaria", "Mangriff", "Séviper", "Séléroc", "Solaroc", "Barloche", "Barbicha", "Écrapince", "Colhomard", "Balbuto", "Kaorine", "Lilia", "Vacilys",
    "Anorith", "Armaldo", "Barpau", "Milobellus", "Morphéo", "Kecleon", "Polichombr", "Branette", "Skelénox", "Téraclope", "Tropius", "Éoko", "Absol", "Okéoké",
    "Stalgamin", "Oniglali", "Obalie", "Phogleur", "Kaimorse", "Coquiperl", "Serpang", "Rosabyss", "Relicanth", "Lovdisc", "Draby", "Drackhaus", "Drattak",
    "Terhal", "Métang", "Métalosse", "Regirock", "Regice", "Registeel", "Latias", "Latios", "Kyogre", "Groudon", "Rayquaza", "Jirachi", "Deoxys",
    
    # Gen 4
    "Tortipouss", "Boskara", "Torterra", "Ouisticram", "Chimpenfeu", "Simiabraz", "Tiplouf", "Prinplouf", "Pingoléon", "Étourmi", "Étourvol", "Étouraptor",
    "Keunotor", "Castorno", "Crikzik", "Mélokrik", "Lixy", "Luxio", "Luxray", "Rozbouton", "Roserade", "Kranidos", "Charkos", "Dinoclier", "Bastiodon", "Cheniti",
    "Cheniselle", "Papilord", "Apitrini", "Apireine", "Pachirisu", "Mustébouée", "Mustéflott", "Ceribou", "Ceriflor", "Sancoki", "Tritosor", "Capidextre",
    "Baudrive", "Grodrive", "Laporeille", "Lockpin", "Magirêve", "Corboss", "Chaglam", "Chaffreux", "Korillon", "Moufouette", "Moufflair", "Archéomire",
    "Archéodong", "Manzaï", "Mime Jr.", "Ptiravi", "Pijako", "Spiritomb", "Griknot", "Carmache", "Carchacrok", "Goinfrex", "Riolu", "Lucario", "Hippopotas",
    "Hippodocus", "Rapion", "Drascore", "Cradopaud", "Coatox", "Vortente", "Écayon", "Luminéon", "Babimanta", "Blizzi", "Blizzaroi", "Dimoret", "Magnézone",
    "Coudlangue", "Rhinastoc", "Bouldeneu", "Élekable", "Maganon", "Togekiss", "Yanméga", "Phyllali", "Givrali", "Scorvol", "Mammochon", "Porygon-Z", "Gallame",
    "Tarinorme", "Noctunoir", "Momartik", "Motisma", "Créhelf", "Créfollet", "Créfadet", "Dialga", "Palkia", "Heatran", "Regigigas", "Giratina", "Cresselia",
    "Phione", "Manaphy", "Darkrai", "Shaymin", "Arceus"
]

MOVE_NAMES = [
    # Gen 1
    "unknown", "Écras'Face", "Poing Karaté", "Torgnoles", "Poing Comète", "Ultimapoing", "Jackpot", "Poing Feu", "Poing Glace", "Poing-Éclair", "Griffe",
    "Force Poigne", "Guillotine", "Coupe-Vent", "Danse Lames", "Coupe", "Tornade", "Cru-Ailes", "Cyclone", "Vol", "Étreinte", "Souplesse", "Fouet Lianes",
    "Écrasement", "Double Pied", "Ultimawashi", "Pied Sauté", "Mawashi Geri", "Jet de Sable", "Coup d'Boule", "Koud'Korne", "Furie", "Empal'Korne", "Charge",
    "Plaquage", "Ligotage", "Bélier", "Mania", "Damoclès", "Mimi-Queue", "Dard-Venin", "Double Dard", "Dard-Nuée", "Groz'Yeux", "Morsure", "Rugissement",
    "Hurlement", "Berceuse", "Ultrason", "SonicBoom", "Entrave", "Acide", "Flammèche", "Lance-Flammes", "Brume", "Pistolet à O", "Hydrocanon", "Surf",
    "Laser Glace", "Blizzard", "Rafale Psy", "Bulles d'O", "Onde Boréale", "Ultralaser", "Picpic", "Bec Vrille", "Sacrifice", "Balayage", "Riposte", "Frappe Atlas",
    "Force", "Vol-Vie", "Méga-Sangsue", "Vampigraine", "Croissance", "Tranch'Herbe", "Lance-Soleil", "Poudre Toxik", "Para-Spore", "Poudre Dodo", "Danse Fleurs",
    "Sécrétion", "Draco-Rage", "Danse Flammes", "Éclair", "Tonnerre", "Cage-Éclair", "Fatal-Foudre", "Jet-Pierres", "Séisme", "Abîme", "Tunnel", "Toxik",
    "Choc Mental", "Psyko", "Hypnose", "Yoga", "Hâte", "Vive-attaque", "Frénésie", "Téléport", "Ténèbres", "Copie", "Grincement", "Reflet", "Soin", "Armure",
    "Lilliput", "Brouillard", "Onde Folie", "Repli", "Boul'Armure", "Bouclier", "Mur Lumière", "Buée Noire", "Protection", "Puissance", "Patience", "Métronome",
    "Mimique", "Destruction", "Bombe Oeuf", "Léchouille", "Purédpois", "Détritus", "Massd'Os", "Déflagration", "Cascade", "Claquoir", "Météores", "Coud'Krâne",
    "Picanon", "Constriction", "Amnésie", "Télékinésie", "E-Coque", "Pied Voltige", "Intimidation", "Dévorêve", "Gaz Toxik", "Pilonnage", "Vampirisme", "Grobisou",
    "Piqué", "Morphing", "Écume", "Uppercut", "Spore", "Flash", "Vague Psy", "Trempette", "Acidarmure", "Pince-Masse", "Explosion", "Combo-Griffe", "Osmerang",
    "Repos", "Éboulement", "Croc de Mort", "Affûtage", "Conversion", "Triplattaque", "Croc Fatal", "Tranche", "Clonage", "Lutte",
      
    # Gen 2
    "Gribouille", "Triple Pied", "Larcin", "Toile", "Lire-Esprit", "Cauchemar", "Roue de Feu", "Ronflement", "Malédiction", "Fléau", "Conversion2", "Aéroblast",
    "Spore Coton", "Contre", "Dépit", "Poudreuse", "Abri", "Mach Punch", "Grimace", "Feinte", "Doux Baiser", "Cognobidon", "Bombe Beurk", "Coud'Boue", "Octazooka",
    "Picots", "Élecanon", "Clairvoyance", "Prlvt Destin", "Requiem", "Vent Glace", "Détection", "Charge Os", "Verrouillage", "Colère", "Tempête de Sable",
    "Giga-Sangsue", "Ténacité", "Charme", "Roulade", "Faux-Chage", "Vantardise", "Lait à Boire", "Étincelle", "Taillade", "Ailes d'Acier", "Regard Noir", "Attraction",
    "Blabla Dodo", "Glas de Soin", "Retour", "Cadeau", "Frustration", "Rune Protect", "Balance", "Feu Sacré", "Ampleur", "Dynamopoing", "Mégacorne", "Dracosouffle",
    "Relais", "Encore", "Poursuite", "Tour Rapide", "Doux Parfum", "Queue de Fer", "Griffe Acier", "Corps Perdu", "Aurore", "Synthèse", "Rayon Lune", "Puissance Cachée",
    "Coup Croix", "Ouragan", "Danse Pluie", "Zénith", "Mâchouille", "Voile Miroir", "Boost", "Vit.Extrême", "Pouv.Antique", "Ball'Ombre", "Prescience", "Éclate-Roc",
    "Siphon", "Baston",
    
    # Gen 3
    "Bluff", "Brouhaha", "Stockage", "Relâche", "Avale", "Canicule", "Grêle", "Tourmente", "Flatterie", "Feu Follet", "Souvenir", "Façade", "Mitra-Poing", "Stimulant",
    "Par Ici", "Force Nature", "Chargeur", "Provoc", "Coup d'Main", "Tourmagik", "Imitation", "Voeu", "Assistance", "Racines", "Surpuissance", "Reflet Magik", "Recyclage",
    "Vendetta", "Casse-Brique", "Bâillement", "Sabotage", "Effort", "Éruption", "Échange", "Possessif", "Régénération", "Rancune", "Saisie", "Force Cachée", "Plongée",
    "Cogne", "Camouflage", "Lumi-Queue", "Lumi-Éclat", "Ball'Brume", "Danse Plumes", "Danse Folle", "Pied Brûleur", "Lance-Boue", "Ball'Glace", "Poing Dard", "Paresse",
    "Mégaphone", "Crochet Venin", "Éclate Griffe", "Rafale Feu", "Hydroblast", "Poing Météore", "Étonnement", "Ball'Météo", "Aromathérapie", "Croco Larme", "Tranch'Air",
    "Surchauffe", "Flair", "Tomberoche", "Vent Argenté", "Strido-Son", "Siffl'Herbe", "Chatouille", "Force Cosmique", "Giclédo", "Rayon Signal", "Poing Ombre",
    "Extrasenseur", "Stratopercut", "Tourbi-Sable", "Glaciation", "Ocroupi", "Balle Graine", "Aéropique", "Stalagtite", "Mur de Fer", "Barrage", "Grondement", "Draco-Griffe",
    "Végé-Attaque", "Gonflette", "Rebond", "Tir de Boue", "Queue-Poison", "Implore", "Électacle", "Feuillemagik", "Tourniquet", "Plénitude", "Lame-Feuille", "Danse Draco",
    "Boule Roc", "Onde de Choc", "Vibraqua", "Carnareket", "Psycho Boost",
    
    # Gen 4
    "Atterrissage", "Gravité", "Oeil Miracle", "Réveil Forcé", "Marto-Poing", "Gyroballe", "Voeu Soin", "Saumure", "Don Naturel", "Ruse", "Picore", "Vent Arrière",
    "Acupression", "Fulmifer", "Demi-Tour", "Close Combat", "Représailles", "Assurance", "Embargo", "Dégommage", "Échange Psy", "Atout", "Anti-Soin", "Essorage",
    "Astuce Force", "Suc Digestif", "Air Veinard", "Moi d'Abord", "Photocopie", "Permuforce", "Permugarde", "Punition", "Dernier Recours", "Soucigraine", "Coup Bas",
    "Pics Toxik", "Permucoeur", "Anneau Hydro", "Vol Magnétik", "Boutefeu", "Forte-Paume", "Aurasphère", "Poliroche", "Direct Toxik", "Vibrobscur", "Tranche-Nuit",
    "Hydroqueue", "Canon Graine", "Lame d'Air", "Plaie Croix", "Bourdon", "Draco-Choc", "Draco-Charge", "Rayon Gemme", "Vampipoing", "Onde Vide", "Exploforce", "Éco-Sphère",
    "Rapace", "Telluriforce", "Passe-Passe", "Giga Impact", "Machination", "Pisto-Poing", "Avalanche", "Éclats Glace", "Griffe Ombre", "Crocs Éclair", "Crocs Givre",
    "Crocs Feu", "Ombre Portée", "Boue-Bombe", "Coupe Psycho", "Psykoud'Boul", "Miroi-Tir", "Luminocanon", "Escalade", "Anti-Brume", "Distorsion", "Draco-Météore",
    "Coup d'Jus", "Ébullilave", "Tempête Verte", "Mégafouet", "Roc-Boulet", "Poison Croix", "Détricanon", "Tête de Fer", "Bombe Aimant", "Lame de Roc", "Séduction",
    "Piège de Roc", "Noeud Herbe", "Babil", "Jugement", "Piqûre", "Rayon Chargé", "Martobois", "Aqua-Jet", "Appel Attak", "Appel Défens", "Appel Soins", "Fracass'Tête",
    "Coup Double", "Hurle-Temps", "Spatio-Rift", "Danse Lune", "Presse", "Vortex Magma", "Trou Noir", "Fulmigraine", "Vent Mauvais", "Revenant"
]

ABILITY_LIST = [
    # Gen 3
    "unknown", "Puanteur", "Crachin", "Turbo", "Armurbaston", "Fermeté", "Moiteur", "Échauffement", "Voile Sable", "Statik", "Absorb Volt", "Absorb Eau", "Benêt",
    "Ciel Gris", "Oeil Composé", "Insomnia", "Homochromie", "Vaccin", "Torche", "Écran Poudre", "Tempo Perso", "Ventouse", "Intimidation", "Marque Ombre", "Peau Dure",
    "Garde Mystik", "Lévitation", "Pose Spore", "Synchro", "Corps Sain", "Médic Nature", "Paratonnerre", "Sérénité", "Glissade", "Chlorophylle", "Lumiattirance", "Calque",
    "Coloforce", "Point Poison", "Attention", "Armumagma", "Ignifu-Voile", "Magnépiège", "Anti-Bruit", "Cuvette", "Sable Volant", "Pression", "Isograisse", "Matinal",
    "Corps Ardent", "Fuite", "Regard Vif", "Hyper Cutter", "Ramassage", "Absentéisme", "Agitation", "Joli Sourire", "Plus", "Minus", "Météo", "Glue", "Mue", "Cran",
    "Écaille Spé.", "Suintement", "Engrais", "Brasier", "Torrent", "Essaim", "Tête de Roc", "Sécheresse", "Piège Sable", "Esprit Vital", "Écran Fumée", "Force Pure",
    "Coque Armure", "Air Lock",
    
    # Gen 4
    "Pieds Confus", "Motorisé", "Rivalité", "Impassible", "Rideau Neige", "Gloutonnerie", "Colérique", "Délestage", "Ignifugé", "Simple", "Peau Sèche", "Télécharge",
    "Poing de Fer", "Soin Poison", "Adaptabilité", "Multi-Coups", "Hydratation", "Force Soleil", "Pied Véloce", "Normalise", "Sniper", "Garde Magik", "Annule Garde",
    "Frein", "Technicien", "Feuille Garde", "Maladresse", "Brise Moule", "Chanceux", "Boom Final", "Anticipation", "Prédiction", "Inconscient", "Lentiteintée", "Filtre",
    "Début Calme", "Querelleur", "Lavabo", "Corps Gel", "Solide Roc", "Alerte Neige", "Cherche Miel", "Fouille", "Téméraire", "Multi-Type", "Don Floral", "Mauvais Rêve"
]

NATURE_LIST = ["Hardi","Solo","Brave","Rigide","Mauvais","Assuré","Docile","Relax","Malin","Lâche","Timide","Pressé","Sérieux","Jovial",
    "Naïf","Modeste","Doux","Discret","Pudique","Foufou","Calme","Gentil","Malpoli","Prudent","Bizarre"
]

TYPE_LIST = ["Combat","Vol","Poison","Sol","Roche","Insecte","Spectre","Acier","Feu","Eau","Plante","Électrik","Psy","Glace","Dragon","Ténèbres"]

HM_LIST = [
    FLY_ID, # Vol
    DIG_ID, # Tunnel
    15,  # Coupe
    29,  # Coup d'Boule
    57,  # Surf
    70,  # Force
    100, # Téléport
    127, # Cascade
    135, # E-Coque
    148, # Flash
    208, # Lait à Boire
    230, # Doux Parfum
    249, # Éclate-Roc
    250, # Siphon
    290, # Force Cachée
    291, # Plongée
    431, # Escalade
    432, # Anti-Brume
    448, # Babil
] 