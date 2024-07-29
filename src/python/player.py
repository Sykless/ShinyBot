import memory
from zone import Position

class Player:
    def __init__(self, positionX, positionY, zone, orientation, repelSteps, isOnBike, bikeSpeed):
        self.position = Position(positionX, positionY, zone)
        self.orientation = orientation
        self.bikeSpeed = bikeSpeed
        self.isOnBike = isOnBike
        self.repelSteps = repelSteps

    def __str__(self):
        return (
            "Player currently on " + ("a bike" if self.isOnBike else "foot") + " with bike speed " + str(self.bikeSpeed)
            + " facing " + self.orientation + " located in " + str(self.position) + ", " + str(self.repelSteps) + " repel steps remaining"
        )

def getPlayerData():
    return Player(**memory.readPlayerData())