import img
import memory

from data import ITEM_NAMES

ITEMS_SECTION = 0
MEDECINE_SECTION = 1
BALLS_SECTION = 2
TMHM_SECTION = 3
BERRIES_SECTION = 4
MAIL_SECTION = 5
BATTLEITEMS_SECTION = 6
KEYITEMS_SECTION = 7

POKEBALL_ID = 4
REPEL_ID = 79
SUPERREPEL_ID = 76
MAXREPEL_ID = 77
OLDROD_ID = 445
GOODROD_ID = 446
SUPERROD_ID = 447
BIKE_ID = 450

class Item:
    def __init__(self, id, quantity = None):
        self.id = id
        self.name = ITEM_NAMES[id]
        self.quantity = quantity

    def __str__(self):
        return self.name + " x" + str(self.quantity) + " (" + str(self.id) + ")\n"
    
    def __repr__(self):
        return str(self)

class Bag:
    def __init__(self, generalItems, keyItems, TMHM, mail, medecine, berries, balls, battleItems):

        self.items = [
            [Item(**jsonItem) for jsonItem in generalItems],
            [Item(**jsonItem) for jsonItem in medecine],
            [Item(**jsonItem) for jsonItem in balls],
            [Item(**jsonItem) for jsonItem in TMHM],
            [Item(**jsonItem) for jsonItem in berries],
            [Item(**jsonItem) for jsonItem in mail],
            [Item(**jsonItem) for jsonItem in battleItems],
            [Item(**jsonItem) for jsonItem in keyItems],
        ]

# Read JSON Bag data from memory file and convert it to Bag object
def getBagData():
    return Bag(**memory.readBagData())

# Get bag section from item id, process most common sections first
def getBagSection(itemId):
    if (68 <= itemId <= 136 or 213 <= itemId <= 327): return ITEMS_SECTION
    elif (0 <= itemId <= 16): return BALLS_SECTION
    elif (17 <= itemId <= 54): return MEDECINE_SECTION
    elif (428 <= itemId <= 467): return KEYITEMS_SECTION
    elif (137 <= itemId <= 212): return BERRIES_SECTION
    elif (55 <= itemId <= 67): return BATTLEITEMS_SECTION
    elif (328 <= itemId <= 427): return TMHM_SECTION
    elif (149 <= itemId <= 148): return MAIL_SECTION
    else: return None

# Selected item is only coded on a byte, so we have to add 256 for higher ids
def getItemFromBagId(selectedBagSection, selectedBagItemId):
    # TM/HM - Key Items
    if (selectedBagSection in [TMHM_SECTION, KEYITEMS_SECTION]):
        return Item(selectedBagItemId + 256)
    
    # Heal Items - Balls - Berries - Mail - Battle Items
    elif (selectedBagSection in [MEDECINE_SECTION, BALLS_SECTION, BERRIES_SECTION, MAIL_SECTION, BATTLEITEMS_SECTION]):
        return Item(selectedBagItemId)

    # Items
    else:
        # Blind spot : Can be 68 -> 71 or 324 -> 327
        if (68 <= selectedBagItemId <= 71):

            # Clear those blind spots by directly checking the screenshot
            screenshot = img.getScreenshot()

            match selectedBagItemId:
                case 68: return Item(68 + 256 * img.cdDouteuxSelected.isOnScreen(screenshot))
                case 69: return Item(69 + 256 * img.tissuFaucheSelected.isOnScreen(screenshot))
                case 70: return Item(70 + 256 * img.griffeRasoirSelected.isOnScreen(screenshot))
                case 71: return Item(71 + 256 * img.crocRasoirSelected.isOnScreen(screenshot))

        # Rest of the IDs, add 256 if needed
        elif (selectedBagItemId > 71):
            return Item(selectedBagItemId)
        elif (selectedBagItemId < 68):
            return Item(selectedBagItemId + 256)

def findItemInBag(itemId):

    # Retrieve bag data from memory
    bag = getBagData()
    bagSectionId = getBagSection(itemId)
    bagSection = bag.items[bagSectionId]

    # Iterate on bag items
    for bagItemId in range(len(bagSection)):
        if (bagSection[bagItemId].id == itemId):
            return bagItemId
        
    # Item not found in the bag
    return None

def getRepelLocation():
    repelLocation = -1
    superRepelLocation = -1
    maxRepelLocation = -1

    # Retrieve bag data from memory
    bag = getBagData()
    itemsSection = bag.items[ITEMS_SECTION]

    # Search for Poké Ball location
    for itemId in range(len(itemsSection)):
        if (itemsSection[itemId].id == REPEL_ID):
            repelLocation = itemId
        elif (itemsSection[itemId].id == SUPERREPEL_ID):
            superRepelLocation = itemId
        elif (itemsSection[itemId].id == MAXREPEL_ID):
            maxRepelLocation = itemId

        # When all repels locations have been found, exit the loop
        if (repelLocation >= 0 and superRepelLocation >= 0 and maxRepelLocation >= 0):
            break

    # Return best repel when available, return None if we don't have any
    if (maxRepelLocation >= 0):
        return maxRepelLocation
    elif (superRepelLocation >= 0):
        return superRepelLocation
    elif (repelLocation >= 0):
        return repelLocation
    else:
        return None

