
class Zone():
    def __init__(self, position, destination):
        self.position = position
        self.destination = destination

class Location():
    def __init__(self, name, zoneIds, mapFile):
        self.name = name
        self.zoneIds = zoneIds
        self.siblings = []

        self.map = open('src/python/data/map/' + mapFile + '.map').readlines()

OVERWORLD = Location("Overworld",
                     [3,   # Féli-Cité
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
                      350, # Route 206 - Sud
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
                      472] # Passage Marin
, "overworld")


LITTORELLA_CENTREPOKEMON = Location("Littorella - Centre Pokémon", [420], "littorella-centrePokemon")
FELICITE_CENTREPOKEMON = Location("Féli-Cité - Centre Pokémon", [6], "felicite-centrePokemon")
CHARBOURG_CENTREPOKEMON = Location("Charbourg - Centre Pokémon", [48], "charbourg-centrePokemon")
FLORAVILLE_CENTREPOKEMON = Location("Floraville - Centre Pokémon", [428], "floraville-centrePokemon")
VESTIGION_CENTREPOKEMON = Location("Vestigion - Centre Pokémon", [69], "vestigion-centrePokemon")
UNIONPOLIS_CENTREPOKEMON = Location("Unionpolis - Centre Pokémon", [101], "unionpolis-centrePokemon")
BONVILLE_CENTREPOKEMON = Location("Bonville - Centre Pokémon", [435], "bonville-centrePokemon")
VOILAROC_CENTREPOKEMON = Location("Voilaroc - Centre Pokémon", [134], "voilaroc-centrePokemon")
VERCHAMPS_CENTREPOKEMON = Location("Verchamps - Centre Pokémon", [123], "verchamps-centrePokemon")
CELESTIA_CENTREPOKEMON = Location("Célestia - Centre Pokémon", [443], "celestia-centrePokemon")
JOLIBERGES_CENTREPOKEMON = Location("Joliberges - Centre Pokémon", [36], "joliberges-centrePokemon")
FRIMAPIC_CENTREPOKEMON = Location("Frimapic - Centre Pokémon", [168], "frimapic-centrePokemon")
RIVAMAR_CENTREPOKEMON = Location("Rivamar - Centre Pokémon", [151], "rivamar-centrePokemon")
ROUTEVICTOIRE_CENTREPOKEMON = Location("Route Victoire - Centre Pokémon", [173], "ligue-centrePokemon")
AIREDECOMBAT_CENTREPOKEMON = Location("Aire de Combat - Centre Pokémon", [189], "airedecombat-centrePokemon")
AIREDESURVIE_CENTREPOKEMON = Location("Aire de Survie - Centre Pokémon", [452], "airedesurvie-centrePokemon")
AIREDEDETENTE_CENTREPOKEMON = Location("Aire de Détente - Centre Pokémon", [459], "airededetente-centrePokemon")

LITTORELLA_SHOP = Location("Littorella - Shop", [419], "littorella-shop")
FELICITE_SHOP = Location("Féli-Cité - Shop", [4], "felicite-shop")
CHARBOURG_SHOP = Location("Charbourg - Shop", [46], "charbourg-shop")
FLORAVILLE_SHOP = Location("Floraville - Shop", [427], "floraville-shop")
VESTIGION_SHOP = Location("Vestigion - Shop", [66], "vestigion-shop")
UNIONPOLIS_SHOP = Location("Unionpolis - Shop", [87], "unionpolis-shop")
BONVILLE_SHOP = Location("Bonville - Shop", [434], "bonville-shop")
VERCHAMPS_SHOP = Location("Verchamps - Shop", [121], "verchamps-shop")
CELESTIA_SHOP = Location("Célestia - Shop", [446], "celestia-shop")
JOLIBERGES_SHOP = Location("Joliberges - Shop", [34], "joliberges-shop")
FRIMAPIC_SHOP = Location("Frimapic - Shop", [166], "frimapic-shop")
RIVAMAR_SHOP = Location("Rivamar - Shop", [153], "rivamar-shop")
AIREDECOMBAT_SHOP = Location("Aire de Combat - Shop", [191], "airedecombat-shop")
AIREDESURVIE_SHOP = Location("Aire de Survie - Shop", [451], "airedesurvie-shop")

LIGUEPOKEMON = Location("Ligue Pokémon", [175], "liguePokemon")
VOILAROC_CENTRECOMMERCIAL = Location("Voilaroc - Centre Commercial", [137], "centreCommercial-1")
VOILAROC_CENTRECOMMERCIALETAGE1 = Location("Voilaroc - Centre Commercial Étage 1", [138], "centreCommercial-2")
VOILAROC_CENTRECOMMERCIALETAGE2 = Location("Voilaroc - Centre Commercial Étage 2", [139], "centreCommercial-3")
VOILAROC_CENTRECOMMERCIALETAGE3 = Location("Voilaroc - Centre Commercial Étage 3", [140], "centreCommercial-4")
VOILAROC_CENTRECOMMERCIALETAGE4 = Location("Voilaroc - Centre Commercial Étage 4", [141], "centreCommercial-5")
VOILAROC_CENTRECOMMERCIALASCENSEUR = Location("Voilaroc - Centre Commercial Ascenseur", [142], "centreCommercial-7")
VOILAROC_CENTRECOMMERCIALSOUSSOL1 = Location("Voilaroc - Centre Commercial Sous-Sol 1", [566], "centreCommercial-6")

ENTREECHARBOURG = Location("Entrée Charbourg", [258], "entreeCharbourg-1")
ENTREECHARBOURG_SOUSSOL1 = Location("Entrée Charbourg - Sous-Sol 1", [259], "entreeCharbourg-2")
CHEMINROCHEUX = Location("Chemin Rocheux", [254], "cheminRocheux")
GROTTEREVECHE = Location("Grotte Revêche", [284], "grotteReveche-1")
GROTTEREVECHE_SOUSSOL = Location("Grotte Revêche - Sous-Sol", [285], "grotteReveche-2")
FORETVESTIGION = Location("Forêt de Vestigion", [203], "foretVestigion")

MONTCOURONNE_PASSAGECHARBOURG = Location("Mont Couronné - Passage Charbourg", [207], "montCouronne-1")
MONTCOURONNE_SALLE1 = Location("Mont Couronné - Salle 1", [208], "montCouronne-2")
MONTCOURONNE_SALLE2 = Location("Mont Couronné - Salle 2", [209], "montCouronne-3")
MONTCOURONNE_EXTERIEUR2 = Location("Mont Couronné - Extérieur 2", [210], "montCouronne-6")
MONTCOURONNE_EXTERIEUR1 = Location("Mont Couronné - Extérieur 1", [211], "montCouronne-4")
MONTCOURONNE_SALLE3 = Location("Mont Couronné - Salle 3", [212], "montCouronne-5")
MONTCOURONNE_SALLE4 = Location("Mont Couronné - Salle 4", [213], "montCouronne-7")
MONTCOURONNE_SALLE5 = Location("Mont Couronné - Salle 5", [214], "montCouronne-8")
MONTCOURONNE_SALLE6 = Location("Mont Couronné - Salle 6", [215], "montCouronne-9")
MONTCOURONNE_SALLE7 = Location("Mont Couronné - Salle 7", [216], "montCouronne-10")
MONTCOURONNE_PASSAGEFRIMAPIC = Location("Mont Couronné - Passage Frimapic", [217], "montCouronne-13")
MONTCOURONNE_PASSAGEVESTIGION = Location("Mont Couronné - Passage Vestigion", [218], "montCouronne-11")
MONTCOURONNE_SALLE8 = Location("Mont Couronné - Salle 8", [219], "montCouronne-12")
SALLEORIGINELLE = Location("Salle Originelle", [510], "salleOriginelle")
COLONNESLANCES = Location("Colonnes Lances", [584], "colonnesLances")

ILEDEFER_REZDECHAUSSEE = Location("Ile de Fer - Rez-de-Chaussée", [289], "ileDeFer-1")
ILEDEFER_SOUSSOL1OUEST = Location("Ile de Fer - Sous-Sol 1 Ouest", [290], "ileDeFer-2")
ILEDEFER_SOUSSOL1EST = Location("Ile de Fer - Sous-Sol 1 Est", [291], "ileDeFer-3")
ILEDEFER_SOUSSOL2EST = Location("Ile de Fer - Sous-Sol 2 Est", [292], "ileDeFer-4")
ILEDEFER_SOUSSOL2OUEST = Location("Ile de Fer - Sous-Sol 2 Ouest", [293], "ileDeFer-5")
ILEDEFER_SORTIE = Location("Ile de Fer - Sortie", [294], "ileDeFer-6")

ROUTEVICTOIRE = Location("Route Victoire", [244], "routeVictoire-1")
ROUTEVICTOIRE_SALLEOUEST = Location("Route Victoire - Salle Ouest", [245], "routeVictoire-2")
ROUTEVICTOIRE_SALLEEST = Location("Route Victoire - Salle Est", [246], "routeVictoire-3")
ROUTEVICTOIRE_SALLEBRUME = Location("Route Victoire - Salle Brume", [247], "routeVictoire-5")
ROUTEVICTOIRE_PASSAGEEST = Location("Route Victoire - Passage Est", [248], "routeVictoire-4")
ROUTEVICTOIRE_PASSAGEROUTE224 = Location("Route Victoire - Passage Route 224", [249], "routeVictoire-6")

MONTABRUPT_SALLE1 = Location("Mont Abrupt - Salle 1", [263], "montAbrupt-1")
MONTABRUPT_SALLE2 = Location("Mont Abrupt - Salle 2", [264], "montAbrupt-2")
MONTABRUPT_SALLEHEATRAN = Location("Mont Abrupt - Salle Heatran", [265], "montAbrupt-3")

SOURCEADIEU = Location("Source Adieu", [267], "sourceAdieu")
GROTTERETOUR_ENTREE = Location("Grotte Retour - Entrée", [268], "grotteRetour-entree")
GROTTERETOUR_SALLEPILIER = Location("Grotte Retour - Salle Pilier", [269], "grotteRetour-pilier")
GROTTERETOUR_SALLEGIRATINA = Location("Grotte Retour - Salle Giratina", [270], "grotteRetour-giratina")
GROTTERETOUR_SALLE2 = Location("Grotte Retour - Salle 1", [518], "grotteRetour-1")
GROTTERETOUR_SALLE2 = Location("Grotte Retour - Salle 2", [519], "grotteRetour-2")
GROTTERETOUR_SALLE3 = Location("Grotte Retour - Salle 3", [520], "grotteRetour-3")
GROTTERETOUR_SALLE4 = Location("Grotte Retour - Salle 4", [521], "grotteRetour-4")
GROTTERETOUR_SALLE5 = Location("Grotte Retour - Salle 5", [522], "grotteRetour-5")
GROTTERETOUR_SALLE6 = Location("Grotte Retour - Salle 6", [523], "grotteRetour-6")
GROTTERETOUR_SALLE8 = Location("Grotte Retour - Salle 8", [525], "grotteRetour-8")
GROTTERETOUR_SALLE9 = Location("Grotte Retour - Salle 9", [526], "grotteRetour-9")
GROTTERETOUR_SALLE10 = Location("Grotte Retour - Salle 10", [527], "grotteRetour-10")
GROTTERETOUR_SALLE11 = Location("Grotte Retour - Salle 11", [528], "grotteRetour-11")
GROTTERETOUR_SALLE12 = Location("Grotte Retour - Salle 12", [529], "grotteRetour-12")
GROTTERETOUR_SALLE13 = Location("Grotte Retour - Salle 13", [530], "grotteRetour-13")
GROTTERETOUR_SALLE14 = Location("Grotte Retour - Salle 14", [531], "grotteRetour-14")
GROTTERETOUR_SALLE15 = Location("Grotte Retour - Salle 15", [532], "grotteRetour-15")
GROTTERETOUR_SALLE41 = Location("Grotte Retour - Salle 41", [271], "grotteRetour-41")
GROTTERETOUR_SALLE42 = Location("Grotte Retour - Salle 42", [272], "grotteRetour-42")
GROTTERETOUR_SALLE43 = Location("Grotte Retour - Salle 43", [273], "grotteRetour-43")

LACVERITE = Location("Lac Vérité", [312], "lacVérité")
LACVERITE_CAVERNEVERITE = Location("Lac Vérité - Caverne Vérité", [313], "grotteCre")
LACCOURAGE = Location("Lac Courage", [315], "lacCourage")
LACCOURAGE_GROTTECOURAGE = Location("Lac Courage - Grotte Courage", [316], "grotteCre")
LACSAVOIR = Location("Lac Savoir", [318], "lacSavoir")
LACSAVOIR_CAVERNESAVOIR = Location("Lac Savoir - Caverne Savoir", [319], "grotteCre")

ILEDEFER_GROTTEREGISTEEL = Location("Ile de Fer - Grotte Registeel", [587], "grotteRegi")
MONTCOURONNE_GROTTEREGICE = Location("Mont Couronné - Grotte Regice", [589], "grotteRegi")
ROUTE228_GROTTEREGIROCK = Location("Route 228 - Grotte Regirock", [591], "grotteRegi")
ILENOUVELLUNE = Location("Ile Nouvellune - Intérieur", [321], "ileNouvellune")
ILEPLEINELUNE = Location("Ile Pleine Lune - Intérieur", [261], "ilePleineLune")
