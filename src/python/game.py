import img
import bag
import memory

CLOSEBAGMENU = 24

class Game:
    def __init__(self, repelSteps, selectedBagSection, selectedBagItemId):
        self.repelSteps = repelSteps
        self.selectedBagSection = None

        # Data only valid if in the bag menu
        if (0 <= selectedBagSection <= 7):
            self.selectedBagSection = selectedBagSection
            self.closeBag = False

            # Id 24 could be an item or the close menu button
            if (selectedBagItemId == CLOSEBAGMENU):
                if (selectedBagSection in [0,1]):
                    self.closeBag = img.closeBagMenuSelected.isOnScreen(img.getScreenshot())

                    # Regular itemId, get item from id
                    if (not self.closeBag):
                        self.selectedBagItem = bag.getItemFromBagId(selectedBagSection, selectedBagItemId)
                else:
                    self.closeBag = True

            # Retrieve item as usual
            else:
                self.selectedBagItem = bag.getItemFromBagId(selectedBagSection, selectedBagItemId)

    def __str__(self):
        return str(self.repelSteps) + " repel steps remaining"

def getGameData():
    return Game(**memory.readGameData())