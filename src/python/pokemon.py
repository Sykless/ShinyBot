from utils import formatNumber
from utils import getShinyValue
from bag import Item

import memory

class Move:
    def __init__(self, id, PP, PPUp):
        self.id = id
        self.name = MOVE_NAMES[id]
        self.PP = PP
        self.PPUp = PPUp
    
    def isHM(self):
            return self.name in ["Chatter", "Cut", "Defog", "Dig", "Dive", "Flash", "Fly", "Headbutt", "Milk Drink",
                                "Rock Climb", "Rock Smash", "Secret Power", "Soft-Boiled", "Strength", "Surf",
                                "Sweet Scent", "Teleport", "Waterfall", "Whirlpool"]
    
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

    def __init__(self):
        self.pid = 0

        self.pokedexId = 0
        self.name = None
        self.level = 0
        self.moves = []
        self.ability = None
        self.item = None
        self.currentHP = 0
        self.stats = None
        self.IV = None
        self.EV = None
        self.experience = 0
        self.status = None

        self.OT = None
        self.met = None
        self.nicknamed = False
        self.nickname = None
        self.isEgg = False
        self.pokeball = None
        self.female = False
        self.genderless = False
        self.friendship = 0
        self.pokerus = 0
        self.alternateForms = 0
        self.originalLanguage = None
        self.originGame = None

        self.ribbons = None
        self.contest = None
        self.markings = 0
        self.capsule = 0
        self.sealCoordinates = 0

        self.shinyValue = 0
        self.isShiny = False

    def __init__(self, experience = None, ribbons = None, stats = None, sealCoordinates = None, currentHP = None, moves = None, met = None,
                 alternateForms = None, pokedexId = None, IV = None, OT = None, status = None, level = None, EV = None, pokeballId = None,
                 contest = None, female = None, pokerus = None, originalLanguage = None, markings = None, nickname = None, capsule = None,
                 genderless = None, originGame = None, nicknamed = None, item = None, pid = None, friendship = None, abilityId = None,
                 isEgg = None):

        # Allow empty Pokemon creation if pid is None
        if (pid != None and 0 <= pokedexId <= 493):
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
        
        # Pokemon not shiny by default if pid is None
        self.isShiny = pid != None and self.shinyValue < 255

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
                + " =============================================\n")
    
def isFlyAvailable():
    jsonTeamData = memory.readPokemonTeamData()

    for pokemonPosition in range(len(jsonTeamData)):
        movePosition = 0
        pokemon = Pokemon(**jsonTeamData[pokemonPosition])

        for move in pokemon.moves:
            if (move.isHM()):
                movePosition += 1

                # Return first pokemon with Fly available
                if (move.name == "Fly"):
                    return [pokemonPosition, movePosition]
    
    # No Pokemon with Fly
    print("No Pokemon with Fly")
    return [None, None]

POKEMON_NAMES =  ["MissingNo","Bulbasaur", "Ivysaur", "Venusaur", "Charmander", "Charmeleon", "Charizard",
    "Squirtle", "Wartortle", "Blastoise", "Caterpie", "Metapod", "Butterfree",
    "Weedle", "Kakuna", "Beedrill", "Pidgey", "Pidgeotto", "Pidgeot", "Rattata", "Raticate",
    "Spearow", "Fearow", "Ekans", "Arbok", "Pikachu", "Raichu", "Sandshrew", "Sandslash",
    "NidoranF", "Nidorina", "Nidoqueen", "NidoranM", "Nidorino", "Nidoking",
    "Clefairy", "Clefable", "Vulpix", "Ninetales", "Jigglypuff", "Wigglytuff",
    "Zubat", "Golbat", "Oddish", "Gloom", "Vileplume", "Paras", "Parasect", "Venonat", "Venomoth",
    "Diglett", "Dugtrio", "Meowth", "Persian", "Psyduck", "Golduck", "Mankey", "Primeape",
    "Growlithe", "Arcanine", "Poliwag", "Poliwhirl", "Poliwrath", "Abra", "Kadabra", "Alakazam",
    "Machop", "Machoke", "Machamp", "Bellsprout", "Weepinbell", "Victreebel", "Tentacool", "Tentacruel",
    "Geodude", "Graveler", "Golem", "Ponyta", "Rapidash", "Slowpoke", "Slowbro",
    "Magnemite", "Magneton", "Farfetch'd", "Doduo", "Dodrio", "Seel", "Dewgong", "Grimer", "Muk",
    "Shellder", "Cloyster", "Gastly", "Haunter", "Gengar", "Onix", "Drowzee", "Hypno",
    "Krabby", "Kingler", "Voltorb", "Electrode", "Exeggcute", "Exeggutor", "Cubone", "Marowak",
    "Hitmonlee", "Hitmonchan", "Lickitung", "Koffing", "Weezing", "Rhyhorn", "Rhydon", "Chansey",
    "Tangela", "Kangaskhan", "Horsea", "Seadra", "Goldeen", "Seaking", "Staryu", "Starmie",
    "Mr. Mime", "Scyther", "Jynx", "Electabuzz", "Magmar", "Pinsir", "Tauros", "Magikarp", "Gyarados",
    "Lapras", "Ditto", "Eevee", "Vaporeon", "Jolteon", "Flareon", "Porygon", "Omanyte", "Omastar",
    "Kabuto", "Kabutops", "Aerodactyl", "Snorlax", "Articuno", "Zapdos", "Moltres",
    "Dratini", "Dragonair", "Dragonite", "Mewtwo", "Mew",
    "Chikorita", "Bayleef", "Meganium", "Cyndaquil", "Quilava", "Typhlosion",
    "Totodile", "Croconaw", "Feraligatr", "Sentret", "Furret", "Hoothoot", "Noctowl",
    "Ledyba", "Ledian", "Spinarak", "Ariados", "Crobat", "Chinchou", "Lanturn", "Pichu", "Cleffa",
    "Igglybuff", "Togepi", "Togetic", "Natu", "Xatu", "Mareep", "Flaaffy", "Ampharos", "Bellossom",
    "Marill", "Azumarill", "Sudowoodo", "Politoed", "Hoppip", "Skiploom", "Jumpluff", "Aipom",
    "Sunkern", "Sunflora", "Yanma", "Wooper", "Quagsire", "Espeon", "Umbreon", "Murkrow", "Slowking",
    "Misdreavus", "Unown", "Wobbuffet", "Girafarig", "Pineco", "Forretress", "Dunsparce", "Gligar",
    "Steelix", "Snubbull", "Granbull", "Qwilfish", "Scizor", "Shuckle", "Heracross", "Sneasel",
    "Teddiursa", "Ursaring", "Slugma", "Magcargo", "Swinub", "Piloswine", "Corsola", "Remoraid", "Octillery",
    "Delibird", "Mantine", "Skarmory", "Houndour", "Houndoom", "Kingdra", "Phanpy", "Donphan",
    "Porygon2", "Stantler", "Smeargle", "Tyrogue", "Hitmontop", "Smoochum", "Elekid", "Magby", "Miltank",
    "Blissey", "Raikou", "Entei", "Suicune", "Larvitar", "Pupitar", "Tyranitar", "Lugia", "Ho-Oh", "Celebi",			
    "Treecko", "Grovyle", "Sceptile", "Torchic", "Combusken", "Blaziken", "Mudkip", "Marshtomp", 
    "Swampert", "Poochyena", "Mightyena", "Zigzagoon", "Linoone", "Wurmple", "Silcoon", "Beautifly",
    "Cascoon", "Dustox", "Lotad", "Lombre", "Ludicolo", "Seedot", "Nuzleaf", "Shiftry", 
    "Taillow", "Swellow", "Wingull", "Pelipper", "Ralts", "Kirlia", "Gardevoir", "Surskit", 
    "Masquerain", "Shroomish", "Breloom", "Slakoth", "Vigoroth", "Slaking", "Nincada", "Ninjask", 
    "Shedinja", "Whismur", "Loudred", "Exploud", "Makuhita", "Hariyama", "Azurill", "Nosepass", 
    "Skitty", "Delcatty", "Sableye", "Mawile", "Aron", "Lairon", "Aggron", "Meditite", "Medicham",
    "Electrike", "Manectric", "Plusle", "Minun", "Volbeat", "Illumise", "Roselia", "Gulpin", 
    "Swalot", "Carvanha", "Sharpedo", "Wailmer", "Wailord", "Numel", "Camerupt", "Torkoal", 
    "Spoink", "Grumpig", "Spinda", "Trapinch", "Vibrava", "Flygon", "Cacnea", "Cacturne", "Swablu",
    "Altaria", "Zangoose", "Seviper", "Lunatone", "Solrock", "Barboach", "Whiscash", "Corphish",
    "Crawdaunt", "Baltoy", "Claydol", "Lileep", "Cradily", "Anorith", "Armaldo", "Feebas", 
    "Milotic", "Castform", "Kecleon", "Shuppet", "Banette", "Duskull", "Dusclops", "Tropius", 
    "Chimecho", "Absol", "Wynaut", "Snorunt", "Glalie", "Spheal", "Sealeo", "Walrein", "Clamperl",
    "Huntail", "Gorebyss", "Relicanth", "Luvdisc", "Bagon", "Shelgon", "Salamence", "Beldum", 
    "Metang", "Metagross", "Regirock", "Regice", "Registeel", "Latias", "Latios", "Kyogre", 
    "Groudon", "Rayquaza", "Jirachi", "Deoxys",			
    "Turtwig", "Grotle", "Torterra", "Chimchar", "Monferno", "Infernape", "Piplup", "Prinplup", 
    "Empoleon", "Starly", "Staravia", "Staraptor", "Bidoof", "Bibarel", "Kricketot", "Kricketune", 
    "Shinx", "Luxio", "Luxray", "Budew", "Roserade", "Cranidos", "Rampardos", "Shieldon", "Bastiodon", 
    "Burmy", "Wormadam", "Mothim", "Combee", "Vespiquen", "Pachirisu", "Buizel", "Floatzel", "Cherubi", 
    "Cherrim", "Shellos", "Gastrodon", "Ambipom", "Drifloon", "Drifblim", "Buneary", "Lopunny", 
    "Mismagius", "Honchkrow", "Glameow", "Purugly", "Chingling", "Stunky", "Skuntank", "Bronzor", 
    "Bronzong", "Bonsly", "Mime Jr.", "Happiny", "Chatot", "Spiritomb", "Gible", "Gabite", "Garchomp", 
    "Munchlax", "Riolu", "Lucario", "Hippopotas", "Hippowdon", "Skorupi", "Drapion", "Croagunk", 
    "Toxicroak", "Carnivine", "Finneon", "Lumineon", "Mantyke", "Snover", "Abomasnow", "Weavile", 
    "Magnezone", "Lickilicky", "Rhyperior", "Tangrowth", "Electivire", "Magmortar", "Togekiss", 
    "Yanmega", "Leafeon", "Glaceon", "Gliscor", "Mamoswine", "Porygon-Z", "Gallade", "Probopass", 
    "Dusknoir", "Froslass", "Rotom", "Uxie", "Mesprit", "Azelf", "Dialga", "Palkia", "Heatran", 
    "Regigigas", "Giratina", "Cresselia", "Phione", "Manaphy", "Darkrai", "Shaymin", "Arceus",
]

MOVE_NAMES = ["unknown", "Pound", "Karate Chop", "DoubleSlap", "Comet Punch", "Mega Punch", "Pay Day", "Fire Punch", "Ice Punch", "ThunderPunch",
    "Scratch", "ViceGrip", "Guillotine", "Razor Wind", "Swords Dance", "Cut", "Gust", "Wing Attack", "Whirlwind", "Fly",
    "Bind", "Slam", "Vine Whip", "Stomp", "Double Kick", "Mega Kick", "Jump Kick", "Rolling Kick", "Sand-Attack", "Headbutt",
    "Horn Attack", "Fury Attack", "Horn Drill", "Tackle", "Body Slam", "Wrap", "Take Down", "Thrash", "Double-Edge",
    "Tail Whip", "Poison Sting", "Twineedle", "Pin Missile", "Leer", "Bite", "Growl", "Roar", "Sing", "Supersonic", "SonicBoom", 
    "Disable", "Acid", "Ember", "Flamethrower", "Mist", "Water Gun", "Hydro Pump", "Surf", "Ice Beam", "Blizzard", "Psybeam",
    "BubbleBeam", "Aurora Beam", "Hyper Beam", "Peck", "Drill Peck", "Submission", "Low Kick", "Counter", "Seismic Toss", "Strength",
    "Absorb", "Mega Drain", "Leech Seed", "Growth", "Razor Leaf", "SolarBeam", "PoisonPowder", "Stun Spore", "Sleep Powder",
    "Petal Dance", "String Shot", "Dragon Rage", "Fire Spin", "ThunderShock", "Thunderbolt", "Thunder Wave", "Thunder", "Rock Throw",
    "Earthquake", "Fissure", "Dig", "Toxic", "Confusion", "Psychic", "Hypnosis", "Meditate", "Agility", "Quick Attack", "Rage", 
    "Teleport", "Night Shade", "Mimic", "Screech", "Double Team", "Recover", "Harden", "Minimize", "SmokeScreen", "Confuse Ray", 
    "Withdraw", "Defense Curl", "Barrier", "Light Screen", "Haze", "Reflect", "Focus Energy", "Bide", "Metronome", "Mirror Move",
    "Selfdestruct", "Egg Bomb", "Lick", "Smog", "Sludge", "Bone Club", "Fire Blast", "Waterfall", "Clamp", "Swift", "Skull Bash",
    "Spike Cannon", "Constrict", "Amnesia", "Kinesis", "Softboiled", "Hi Jump Kick", "Glare", "Dream Eater", "Poison Gas", "Barrage",
    "Leech Life", "Lovely Kiss", "Sky Attack", "Transform", "Bubble", "Dizzy Punch", "Spore", "Flash", "Psywave", "Splash",
    "Acid Armor", "Crabhammer", "Explosion", "Fury Swipes", "Bonemerang", "Rest", "Rock Slide", "Hyper Fang", "Sharpen", "Conversion",
    "Tri Attack", "Super Fang", "Slash", "Substitute", "Struggle", "Sketch", "Triple Kick", "Thief", "Spider Web", "Mind Reader",
    "Nightmare", "Flame Wheel", "Snore", "Curse", "Flail", "Conversion 2", "Aeroblast", "Cotton Spore", "Reversal", "Spite", "Powder Snow",
    "Protect", "Mach Punch", "Scary Face", "Faint Attack", "Sweet Kiss", "Belly Drum", "Sludge Bomb", "Mud-Slap", "Octazooka", "Spikes",
    "Zap Cannon", "Foresight", "Destiny Bond", "Perish Song", "Icy Wind", "Detect", "Bone Rush", "Lock-On", "Outrage", "Sandstorm",
    "Giga Drain", "Endure", "Charm", "Rollout", "False Swipe", "Swagger", "Milk Drink", "Spark", "Fury Cutter", "Steel Wing", "Mean Look",
    "Attract", "Sleep Talk","Heal Bell", "Return", "Present", "Frustration", "Safeguard", "Pain Split", "Sacred Fire", "Magnitude",
    "DynamicPunch", "Megahorn", "DragonBreath", "Baton Pass", "Encore", "Pursuit", "Rapid Spin", "Sweet Scent", "Iron Tail", "Metal Claw",
    "Vital Throw", "Morning Sun", "Synthesis", "Moonlight", "Hidden Power", "Cross Chop", "Twister", "Rain Dance", "Sunny Day", "Crunch",
    "Mirror Coat", "Psych Up", "ExtremeSpeed", "AncientPower", "Shadow Ball", "Future Sight", "Rock Smash", "Whirlpool", "Beat Up",
    "Fake Out", "Uproar", "Stockpile", "Spit Up", "Swallow", "Heat Wave", "Hail", "Torment", "Flatter", "Will-O-Wisp", "Memento", "Facade",
    "Focus Punch", "SmellingSalt", "Follow Me", "Nature Power", "Charge", "Taunt", "Helping Hand", "Trick", "Role Play", "Wish", "Assist",
    "Ingrain", "Superpower", "Magic Coat", "Recycle", "Revenge", "Brick Break", "Yawn", "Knock Off", "Endeavor", "Eruption", "Skill Swap",
    "Imprison", "Refresh", "Grudge", "Snatch", "Secret Power", "Dive", "Arm Thrust", "Camouflage", "Tail Glow", "Luster Purge", "Mist Ball",
    "FeatherDance", "Teeter Dance", "Blaze Kick", "Mud Sport", "Ice Ball", "Needle Arm", "Slack Off", "Hyper Voice", "Poison Fang",
    "Crush Claw", "Blast Burn", "Hydro Cannon", "Meteor Mash", "Astonish", "Weather Ball", "Aromatherapy", "Fake Tears", "Air Cutter",
    "Overheat", "Odor Sleuth", "Rock Tomb", "Silver Wind", "Metal Sound", "GrassWhistle", "Tickle", "Cosmic Power", "Water Spout",
    "Signal Beam", "Shadow Punch", "Extrasensory", "Sky Uppercut", "Sand Tomb", "Sheer Cold", "Muddy Water", "Bullet Seed", "Aerial Ace",
    "Icicle Spear", "Iron Defense", "Block", "Howl", "Dragon Claw", "Frenzy Plant", "Bulk Up", "Bounce", "Mud Shot", "Poison Tail",
    "Covet", "Volt Tackle", "Magical Leaf", "Water Sport", "Calm Mind", "Leaf Blade", "Dragon Dance", "Rock Blast", "Shock Wave",
    "Water Pulse", "Doom Desire", "Psycho Boost", "Roost", "Gravity", "Miracle Eye", "Wake-Up Slap", "Hammer Arm", "Gyro Ball",
    "Healing Wish", "Brine", "Natural Gift", "Feint", "Pluck", "Tailwind", "Acupressure", "Metal Burst", "U-turn", "Close Combat",
    "Payback", "Assurance", "Embargo", "Fling", "Psycho Shift", "Trump Card", "Heal Block", "Wring Out", "Power Trick", "Gastro Acid",
    "Lucky Chant", "Me First", "Copycat", "Power Swap", "Guard Swap", "Punishment", "Last Resort", "Worry Seed", "Sucker Punch",
    "Toxic Spikes", "Heart Swap", "Aqua Ring", "Magnet Rise", "Flare Blitz", "Force Palm", "Aura Sphere", "Rock Polish", "Poison Jab",
    "Dark Pulse", "Night Slash", "Aqua Tail", "Seed Bomb", "Air Slash", "X-Scissor", "Bug Buzz", "Dragon Pulse", "Dragon Rush", "Power Gem",
    "Drain Punch", "Vacuum Wave", "Focus Blast", "Energy Ball", "Brave Bird", "Earth Power", "Switcheroo", "Giga Impact", "Nasty Plot",
    "Bullet Punch", "Avalanche", "Ice Shard", "Shadow Claw", "Thunder Fang", "Ice Fang", "Fire Fang", "Shadow Sneak", "Mud Bomb", "Psycho Cut",
    "Zen Headbutt", "Mirror Shot", "Flash Cannon", "Rock Climb", "Defog", "Trick Room", "Draco Meteor", "Discharge", "Lava Plume", "Leaf Storm",
    "Power Whip", "Rock Wrecker", "Cross Poison", "Gunk Shot", "Iron Head", "Magnet Bomb", "Stone Edge", "Captivate", "Stealth Rock",
    "Grass Knot", "Chatter", "Judgment", "Bug Bite", "Charge Beam", "Wood Hammer", "Aqua Jet", "Attack Order", "Defend Order", "Heal Order",
    "Head Smash", "Double Hit", "Roar of Time", "Spacial Rend", "Lunar Dance", "Crush Grip", "Magma Storm", "Dark Void", "Seed Flare",
    "Ominous Wind", "Shadow Force"
]

ABILITY_LIST = ["unknown", "Stench", "Drizzle", "Speed Boost", "Battle Armor", "Sturdy", "Damp", "Limber", "Sand Veil", "Static", "Volt Absorb",
    "Water Absorb", "Oblivious", "Cloud Nine", "Compound Eyes", "Insomnia", "Color Change", "Immunity", "Flash Fire", "Shield Dust", "Own Tempo",
    "Suction Cups", "Intimidate", "Shadow Tag", "Rough skin", "Wonder Guard", "Levitate", "Effect Spore", "Synchronize", "Clear Body", "Natural Cure",
    "Lightning Rod", "Serene Grace", "Swift Swim", "Chlorophyll", "Illuminate", "Trace", "Huge Power", "Poison Point", "Inner Focus", "Magma Armor",
    "Water Veil", "Magnet Pull", "Soundproof", "Rain Dish", "Sand Stream", "Pressure", "Thick Fat", "Early Bird", "Flame Body", "Run Away",
    "Keen Eye", "Hyper Cutter", "Pickup", "Truant", "Hustle", "Cute Charm", "Plus", "Minus", "Forecast", "Sticky Hold",
    "Shed Skin", "Guts", "Marvel Scale", "Liquid Ooze", "Overgrow", "Blaze", "Torrent", "Swarm", "Rock Head", "Drought",
    "Arena Trap", "Vital Spirit", "White Smoke", "Pure Power", "Shell Armor", "Air Lock", "Tangled Feet", "Motor Drive", "Rivalry", "Steadfast",
    "Snow Cloak", "Gluttony", "Anger Point", "Unburden", "Heatproof", "Simple", "Dry Skin", "Download", "Iron Fist", "Poison Heal",
    "Adaptability", "Skill Link", "Hydration", "Solar Power", "Quick Feet", "Normalize", "Sniper", "Magic Guard", "No Guard", "Stall",
    "Technician", "Leaf Guard", "Klutz", "Mold Breaker", "Super Luck", "Aftermath", "Anticipation", "Forewarn", "Unaware", "Tinted Lens",
    "Filter", "Slow Start", "Scrappy", "Storm Drain", "Ice Body", "Solid Rock", "Snow Warning", "Honey Gather", "Frisk", "Reckless",
    "Multitype", "Flower Gift", "Bad Dreams"
]

NATURE_LIST = ["Hardy","Lonely","Brave","Adamant","Naughty","Bold","Docile","Relaxed","Impish","Lax","Timid","Hasty","Serious","Jolly",
    "Naive","Modest","Mild","Quiet","Bashful","Rash","Calm","Gentle","Sassy","Careful","Quirky"
]

TYPE_LIST = ["Fighting","Flying","Poison","Ground","Rock","Bug","Ghost","Steel","Fire","Water","Grass","Electric","Psychic","Ice","Dragon","Dark"]