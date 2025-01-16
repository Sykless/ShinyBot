
import img
import joypad

# Button located on touchscreen that can interacted with
class TouchscreenButton():
    def __init__(self, positionX = None, positionY = None, width = None, height = None, template = None):
        
        # Retrieve button and size from an image Template
        if (template):
            self.positionX = template.positionX
            self.positionY = template.positionY
            self.width = template.width
            self.height = template.height

        # Button size and position has been directly provided
        else:
            self.positionX = positionX
            self.positionY = positionY
            self.width = width
            self.height = height

        # Calculate touchscreen center position to click on it
        self.coordinates = (self.positionX + self.width // 2, self.positionY + self.height // 2 - 192)

    # Send button coordinates to emulator to simulate screen touch
    def pressButton(self):
        joypad.writeTouchInput(self.coordinates[0], self.coordinates[1], wait = True)

attackButton = TouchscreenButton(39, 236, 178, 78)
bagButton = TouchscreenButton(12, 346, 56, 33)
pokemonButton = TouchscreenButton(188, 346, 56, 33)
nextPageButton = TouchscreenButton(47, 352, 26, 26)
runawayButton = TouchscreenButton(template = img.runaway)
pokeballLastUsedButton = TouchscreenButton(template = img.pokeballLastUsed)
returnButton = TouchscreenButton(template = img.returnButton)
useItemButton = TouchscreenButton(template = img.useItem)

BATTLE_FOURCHOICES_BUTTONS = [
    TouchscreenButton(15, 227, 98, 40),
    TouchscreenButton(143, 227, 98, 40),
    TouchscreenButton(15, 291, 98, 40),
    TouchscreenButton(143, 291, 98, 40)
]

BATTLE_SIXCHOICES_BUTTONS = [
    TouchscreenButton(7, 207, 114, 37),
    TouchscreenButton(135, 207, 114, 37),
    TouchscreenButton(7, 255, 114, 37),
    TouchscreenButton(135, 255, 114, 37),
    TouchscreenButton(7, 303, 114, 37),
    TouchscreenButton(135, 303, 114, 37),
]