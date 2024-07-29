import memory

class Item:
    def __init__(self, id, quantity):
        self.id = id
        self.name = ITEM_NAMES[id]
        self.quantity = quantity

    def __str__(self):
        return self.name + " x" + str(self.quantity) + " (" + str(self.id) + ")\n"
    
    def __repr__(self):
        return str(self)

class Bag:
    def __init__(self, generalItems, keyItems, TMHM, mail, medecine, berries, balls, battleItems):
        self.generalItems = [Item(**jsonItem) for jsonItem in generalItems]
        self.keyItems = [Item(**jsonItem) for jsonItem in keyItems]
        self.TMHM = [Item(**jsonItem) for jsonItem in TMHM]
        self.mail = [Item(**jsonItem) for jsonItem in mail]
        self.medecine = [Item(**jsonItem) for jsonItem in medecine]
        self.berries = [Item(**jsonItem) for jsonItem in berries]
        self.balls = [Item(**jsonItem) for jsonItem in balls]
        self.battleItems = [Item(**jsonItem) for jsonItem in battleItems]

# Read JSON Bag data from memory file and convert it to Bag object
def getBagData():
    return Bag(**memory.readBagData())

def getPokeballLocation():
    bag = getBagData()
    pokeballLocation = -1

    # Search for Poké Ball location
    for ballId in range(len(bag.balls)):
        if (bag.balls[ballId].name == "Poké Ball"):
            pokeballLocation = ballId

    return pokeballLocation
    
ITEM_NAMES = [
    # Balls
    "unknown", "Master Ball", "Hyper Ball", "Super Ball", "Poké Ball", "Safari Ball", "Filet Ball", "Scuba Ball", "Faiblo Ball", "Bis Ball", "Chrono Ball", "Luxe Ball",
    "Honor Ball", "Sombre Ball", "Soin Ball", "Rapide Ball", "Mémoire Ball",

    # Heal Items
    "Potion", "Antidote", "Anti-Brûle", "Antigel", "Réveil", "Anti-Para", "Guérison", "Potion Max", "Hyper Potion", "Super Potion", "Total Soin", "Rappel", "Rappel Max",
    "Eau Fraîche", "Soda Cool", "Limonade", "Lait Meumeu", "Poudrénergie", "Racinénergie", "Poudre Soin", "Herbe Rappel", "Huile", "Huile Max", "Elixir", "Max Elixir",
    "Lava Cookie", "Jus de Baie", "Cendresacrée", "PV Plus", "Protéine", "Fer", "Carbone", "Calcium", "Super Bonbon", "PP Plus", "Zinc", "PP Max", "Vieux Gâteau",

    # Battle Items
    "Défense Spéc", "Muscle +", "Attaque +", "Défense +", "Vitesse +", "Précision +", "Spécial +", "Déf. Spé. +", "Poképoupée", "Queue Skitty", "Flûte Bleue",
    "Flûte Jaune", "Flûte Rouge",

    # Items
    "Flûte Noire", "Flûteblanche", "Sel Tréfonds", "Co. Tréfonds", "Tesson Rouge", "Tesson Bleu", "Tesson Jaune", "Tesson Vert", "Superepousse", "Max Repousse",
    "Corde Sortie", "Repousse", "Pierresoleil", "Pierre Lune", "Pierre Feu", "Pierrefoudre", "Pierre Eau", "Pierreplante", "Petit Champi", "Gros Champi", "Perle",
    "Grande Perle", "Pouss.Etoile", "Morc. Etoile", "Pépite", "Ecaillecoeur", "Miel", "Fertipousse", "Fertihumide", "Fertistable", "Fertiglu", "Foss. Racine", "Foss. Griffe",
    "Nautile", "Fossile Dôme", "Vieil Ambre", "Foss. Armure", "Foss. Crâne", "Os Rare", "Pierre Éclat", "Pierre Nuit", "Pierre Aube", "Pierre Ovale", "Clé de Voûte",
    "Orbe Platiné", "unknown", "unknown", "unknown", "unknown", "unknown", "unknown", "unknown", "unknown", "unknown", "unknown", "unknown", "unknown", "unknown", "unknown",
    "unknown", "unknown", "unknown", "unknown", "unknown", "unknown", "unknown", "unknown", "Orbe Adamant", "Orbe Perlé",

    # Mail
    "Lettre Herbe", "Lettre Feu", "Lettre Mer", "Lett. Pétale", "Lettre Mine", "Lettre Acier", "Lettre Coeur", "Lettre Neige", "Lettre Cosmo", "Lettre Avion",
    "Lettremosaïk", "Lettre Brik",

    # Berries
    "Baie Ceriz", "Baie Maron", "Baie Pêcha", "Baie Fraive", "Baie Willia", "Baie Mepo", "Baie Oran", "Baie Kika", "Baie Prine", "Baie Sitrus", "Baie Figuy", "Baie Wiki",
    "Baie Mago", "Baie Gowav", "Baie Papaya", "Baie Framby", "Baie Remu", "Baie Nanab", "Baie Repoi", "Baie Nanana", "Baie Grena", "Baie Alga", "Baie Qualot", "Baie Lonme",
    "Baie Résin", "Baie Tamato", "Baie Siam", "Baie Mangou", "Baie Rabuta", "Baie Tronci", "Baie Kiwan", "Baie Palma", "Baie Stekpa", "Baie Durin", "Baie Myrte", "Baie Chocco",
    "Baie Pocpoc", "Baie Parma", "Baie Ratam", "Baie Nanone", "Baie Pomroz", "Baie Kébia", "Baie Jouca", "Baie Cobaba", "Baie Yapap", "Baie Panga", "Baie Charti", "Baie Sédra",
    "Baie Fraigo", "Baie Lampou", "Baie Babiri", "Baie Zalis", "Baie Lichii", "Baie Lingan", "Baie Sailak", "Baie Pitaye", "Baie Abriko", "Baie Lansat", "Baie Frista",
    "Baie Enigma", "Baie Micle", "Baie Chérim", "Baie Jacoba", "Baie Pommo",

    # Held Items
    "Poudreclaire", "Herbeblanche", "Brac. Macho", "Multi Exp", "Vive Griffe", "Grelot Zen", "Herbe Mental", "Bandeau Choix", "Roche Royale", "Poudre Arg.", "Pièce Rune",
    "Rune Purif.", "Rosée Ame", "Dent Océan", "Ecailleocéan", "Boule Fumée", "Pierre Stase", "Bandeau", "Oeuf Chance", "Lentilscope", "Peau Metal", "Restes", "EcailleDraco",
    "Ballelumière", "Sable Doux", "Pierre Dure", "Grain Mirac", "Lunet.Noires", "Ceint.Noire", "Aimant", "Eau Mystique", "Bec Pointu", "Pic Venin", "Glacéternel", "Rune Sort",
    "Cuillertordu", "Charbon", "Croc Dragon", "Mouch. Soie", "Améliorator", "Grelot Coque", "Encens Mer", "Encens Doux", "Poing Chance", "Poudre Métal", "Masse Os", "Bâton",
    "Foul. Rouge", "Foul. Bleu", "Foul. Rose", "Foul. Vert", "Foul. Jaune", "Loupe", "Band. Muscle", "Lunet. Sages", "Ceinture Pro", "Lumargile", "Orbe Vie", "Herbe Pouv.",
    "Orbe Toxique", "Orbe Flamme", "Poudre Vite", "Ceint. Force", "Lentil. Zoom", "Métronome", "Balle Fer", "Ralentiqueue", "Noeud Destin", "Boue Noire", "Roche Glace",
    "Roche Lisse", "Roche Chaude", "Roche Humide", "Accro Griffe", "Mouch. Choix", "Piquants", "Poign. Pouv.", "Ceint. Pouv.", "Lent. Pouv.", "Band. Pouv.", "Chaîne Pouv.",
    "Poids Pouv.", "Carapace Mue", "Grosseracine", "Lunet. Choix", "Plaque Flam", "Plaque Hydro", "Plaque Volt", "Plaque Herbe", "Plaque Glace", "Plaque Poing", "Plaque Toxic",
    "Plaque Terre", "Plaque Ciel", "Plaquesprit", "Plaquinsect", "Plaque Roc", "Plaque Fantô", "Plaque Draco", "Plaque Ombre", "Plaque Fer", "Bizar.Encens", "Encens Roc",
    "Encens Plein", "Encens Vague", "Encens Fleur", "Encens Veine", "Encens Pur", "Protecteur", "Electiriseur", "Magmariseur", "CD Douteux", "Tissu Fauche", "Grif. Rasoir",
    "Croc Rasoir",

    # TM
    "CT01", "CT02", "CT03", "CT04", "CT05", "CT06", "CT07", "CT08", "CT09", "CT10", "CT11", "CT12", "CT13", "CT14", "CT15", "CT16", "CT17", "CT18", "CT19", "CT20", "CT21",
    "CT22", "CT23", "CT24", "CT25", "CT26", "CT27", "CT28", "CT29", "CT30", "CT31", "CT32", "CT33", "CT34", "CT35", "CT36", "CT37", "CT38", "CT39", "CT40", "CT41", "CT42",
    "CT43", "CT44", "CT45", "CT46", "CT47", "CT48", "CT49", "CT50", "CT51", "CT52", "CT53", "CT54", "CT55", "CT56", "CT57", "CT58", "CT59", "CT60", "CT61", "CT62", "CT63",
    "CT64", "CT65", "CT66", "CT67", "CT68", "CT69", "CT70", "CT71", "CT72", "CT73", "CT74", "CT75", "CT76", "CT77", "CT78", "CT79", "CT80", "CT81", "CT82", "CT83", "CT84",
    "CT85", "CT86", "CT87", "CT88", "CT89", "CT90", "CT91", "CT92", "CS01", "CS02", "CS03", "CS04", "CS05", "CS06", "CS07", "CS08",

    # Key Items
    "Explorakit", "Sac Butin", "Livre Règles", "Poké Radar", "Carte Points", "Journal", "Boîte Sceaux", "Coffret Mode", "Sac Sceaux", "Registre Ami", "Clé Centrale",
    "Vieux Grigri", "Clé Galaxie", "Chaîne Rouge", "Carte", "Cherche VS", "Boîte Jetons", "Canne", "Super Canne", "Méga Canne", "Kwakarrosoir", "Boîte Poffin", "Bicyclette",
    "Clé Chambre", "Lettre Chen", "Lun'Aile", "Carte Membre", "Flûte Azur", "Passe Bateau", "Passe Concours", "Pierre Magma", "Colis", "Bon 1", "Bon 2", "Bon 3", "Clé Stockage",
    "Potion Secrète", "Magnéto VS", "Gracidée", "Clé Secrète"
]