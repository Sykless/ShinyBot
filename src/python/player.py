import memory
from zone import Position

LOW_BIKESPEED = 3
HIGH_BIKESPEED = 4

class Player:
    def __init__(self, positionX, positionY, zone, orientation, isOnBike, bikeSpeed):
        self.position = Position(positionX, positionY, zone)
        self.orientation = orientation
        self.bikeSpeed = bikeSpeed
        self.isOnBike = isOnBike

        # Particular zones have 1000 added to their zoneIds, substract to get the actual value
        self.zoneId = zone if zone < 1000 else zone - 1000

    def __str__(self):
        return (
            "Player currently on " + ("a bike" if self.isOnBike else "foot") + " with bike speed " + str(self.bikeSpeed)
            + " facing " + self.orientation + " located in " + str(self.position)
        )

def getPlayerData():
    return Player(**memory.readPlayerData())