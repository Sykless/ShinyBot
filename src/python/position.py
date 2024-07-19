class Position:
    def __init__(self, positionX, positionY, zone = None):
        self.X = positionX
        self.Y = positionY
        self.zone = zone

    def setZone(self, zone):
        self.zone = zone

    def __eq__(self, other):
        if isinstance(other, Position):
            return self.X == other.X and self.Y == other.Y and self.zone.zoneId == other.zone.zoneId
        return False

    def __str__(self):
        return "Position (" + str(self.X) + "," + str(self.Y) + ") à " + self.zone.name