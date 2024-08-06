from zone import Door
from zone import Position
from utils import waitFrames

import heapq

import game
import zone
import action
import player
import joypad
import memory

# Credits :
# - Python Implementation : https://medium.com/@nicholas.w.swift/easy-a-star-pathfinding-7e6689c7f7b2
# - Improving Heuristics calculation : https://theory.stanford.edu/~amitp/GameProgramming/Heuristics.html

DOOR_GRAPH = {}

PUZZLE_BOULDERS = [
    (Position(25,16,zone.MONTABRUPT_SALLE1), Position(26,16,zone.MONTABRUPT_SALLE1)),
    (Position(6,31,zone.ROUTEVICTOIRE_SALLEOUEST), Position(6,32,zone.ROUTEVICTOIRE_SALLEOUEST)),
    (Position(18,42,zone.MONTCOURONNE_PASSAGEVESTIGION), Position(18,43,zone.MONTCOURONNE_PASSAGEVESTIGION))
]

PLAYER_POSITION = 0
BOULDER_POSITION = 1

CELL_COST = {
    # Traveling cells
    "O": 1, # Regular cell
    "Z": 1, # Zone (door, cave entrance)
    "S": 10, # Swamp
    "1": 1, # 1-depth snow
    "2": 2, # 2-depth snow
    "3": 4, # 3-depth snow
    "4": 8, # 4-depth snow
    "V": 5, # Bike slope
    "G": 3, # Grass
    "g": 3, # Tall grass
    "E": 1, # Elevator
    "e": 1, # Elevator door

    # HM Obstacles
    "t": 5, # Tree
    "r": 5, # Rock
    "W": 5, # Water
    "w": 7, # Waterfall
    "C": 5, # Climb

    # Height-depending cells
    "A": 1, # Above ground (bridge)
    "a": 1, # Above ground (bike bridge)
    "@": 1, # Above solid block (bridge)
    "B": 1, # Below bridge
    "d": 5, # Below bridge on water

    # Orientation-depending cells
    "D": 3, # One-way ledge to go down
    "L": 3, # One-way ledge to go left
    "U": 3, # One-way ledge to go up
    "R": 3, # One-way ledge to go right
}

SOLID_BLOCKS = [
    "X", # Wall, Tree, etc
    "N", # NPC
    "s", # Sign (Special process since it displays a message if coming from the bottom)
    "I", # Interactable (Static encounter, Shop, etc)
    "b", # Boulder (Cannot be removed like Cut or Rock Smash, so is actually an obsctacle)
    "v", # Bike ramp
]

DIRECTIONS = [
    {"orientation": (-1, 0), "solidLedges": ["D","L","R"]}, # Up
    {"orientation": (0, -1), "solidLedges": ["D","U","R"]}, # Left
    {"orientation": (0, 1),  "solidLedges": ["D","L","U"]}, # Right
    {"orientation": (1, 0),  "solidLedges": ["L","U","R"]}, # Down
]

# Node class for A* Pathfinding
class Node():
    def __init__(self, position: Position, zoneMap, parent = None):
        self.parent = parent
        self.position = position
        self.cellType = zoneMap[position.Y][position.X]

        # A* core parameters
        self.g = 0
        self.h = 0
        self.f = 0

        self.pushBoulder = False
        self.isSurfing = self.cellType in ["W","w","d"]
        
        self.onABikeSlope = False
        self.bikeSlopeDestination = None
        self.bikeSlopeMomentumCell = None

        self.onABikeRamp = False
        self.bikeRampDestination = None

        ### Special process for bridges since two cells share the same position, see solid blocks processing ###
        # We avoid starting on a bridge, so on starting node we consider we're below (except on a @ cell which is impossible)
        if (not parent):
            self.isBelow = self.cellType in  ["B","d","A","a"] 
            self.isAbove = self.cellType in  ["@"]

        # If you were below a bridge, you're leaving when not on Above or Below cell
        elif (parent.isBelow):
            
            self.isBelow = self.cellType in ["A","a","@","B","d"]
            self.isAbove = False

            # Can only start/stop surfing through B and d cells
            if (self.cellType == "d" and parent.cellType == "B"):
                self.isSurfing = True
            elif (self.cellType == "B" and parent.cellType == "d"):
                self.isSurfing = False
            else:
                self.isSurfing = parent.isSurfing
        
        # If you were not, above/below condition just depends on current cell value
        else:
            self.isBelow = self.cellType in ["B","d"]
            self.isAbove = self.cellType in ["A","a","@"]

    # Two nodes may share the same position but be above or below a bridge, so we must check those conditions as well
    def __eq__(self, other):
        if isinstance(other, Node):
            return self.position == other.position and self.isBelow == other.isBelow and self.isAbove == other.isAbove
        return False

    def __str__(self):
        return (str(self.position) + " - " + self.cellType 
            + (" is below" if self.isBelow else " is not below")
            + (" and is above !" if self.isAbove else " and is not above !")
            + (" (parent = (" + str(self.parent.position.X) + "," + str(self.parent.position.Y) + "))" if self.parent else "")
            + (" PUSH !" if self.pushBoulder else "")
            + (" SURF !" if self.isSurfing else "")
            + (" ON A SLOPE !" + (" (destination = " + str(self.bikeSlopeDestination) + ")" if self.bikeSlopeDestination else "") if self.onABikeSlope else "")
            + (" ON A RAMP !" + (" (destination = " + str(self.bikeRampDestination) + ")" if self.bikeRampDestination else "") if self.onABikeRamp else "")
            + "\n")

    def __repr__(self):
        return str(self)

# DoorNode class for Dijkstra Pathfinding
class DoorNode():
    def __init__(self, fromDoor: Door, toDoor: Door, path = None):
        self.fromDoor = fromDoor
        self.toDoor = toDoor
        self.path = path

        if (path):
            self.weight = self.path[-1].g
        else:
            self.weight = fromDoor.position.getDistanceTo(toDoor.position)

    def __eq__(self, other):
        if isinstance(other, DoorNode):
            return self.fromDoor == other.fromDoor and self.toDoor == other.toDoor
        return False
    
    def __str__(self):
        return "Weight " + str(self.weight) + " from (" + str(self.fromDoor) + ") to (" + str(self.toDoor) + ")"
    
    def __repr__(self):
        return str(self)



def updateMapWithPushedBoulders(zoneMap, boulderPosition, playerPosition):
        
    # Operations will depend on the player and boulders positions
    xDiff = boulderPosition.X - playerPosition.X
    yDiff = boulderPosition.Y - playerPosition.Y

    # Update the map to take into account the pushed boulder
    if (xDiff == 1):
        zoneMap[boulderPosition.Y] = zoneMap[boulderPosition.Y][:boulderPosition.X] + "Ob" + zoneMap[boulderPosition.Y][boulderPosition.X+2:]
    elif (xDiff == -1):
        zoneMap[boulderPosition.Y] = zoneMap[boulderPosition.Y][:boulderPosition.X-1] + "bO" + zoneMap[boulderPosition.Y][boulderPosition.X+1:]
    else:
        zoneMap[boulderPosition.Y] = zoneMap[boulderPosition.Y][:boulderPosition.X] + "O" + zoneMap[boulderPosition.Y][boulderPosition.X+1:]
        zoneMap[boulderPosition.Y + yDiff] = zoneMap[boulderPosition.Y + yDiff][:boulderPosition.X] + "b" + zoneMap[boulderPosition.Y + yDiff][boulderPosition.X+1:]


def getMapAtCurrentState(processedNodes, originalMap):

    # Keep track of boulders and obstacles for the input process
    pushedBoulder = False
    destroyedObstacles = []

    # Create a copy of the original map that we can updatz
    updatedMap = originalMap[:]

    # Check every already processed node for pushed boulders
    if (len(processedNodes) > 0):

        # If a boulder has been pushed, update the map accordingly
        for node in processedNodes:
            if (node.pushBoulder): 
                updateMapWithPushedBoulders(updatedMap, node.position, node.parent.position)
                pushedBoulder = True

            if (node.cellType in ["r","t"]):
                destroyedObstacles.append(node.position)

    return updatedMap, pushedBoulder, destroyedObstacles

def isBoulderPushable(zoneMap, playerPosition, boulderPosition, orientation, blockingBoulders):

    # Boulder is pushable if the cell after that is an empty one, and the boulder hasn't already been processed
    return (zoneMap[boulderPosition.Y + orientation[0]][boulderPosition.X + orientation[1]] == "O" 
                and (playerPosition, boulderPosition) not in blockingBoulders)

def getRockClimbEndPosition(zoneMap, playerPosition, orientation):
    
    # Try to find the first cell after rock climb
    for i in range(1,11):

        # Found the end position of rock climb
        if (zoneMap[playerPosition.Y + i*orientation[0]][playerPosition.X + i*orientation[1]] != "C"):
            return Position(playerPosition.X + i*orientation[1], playerPosition.Y + i*orientation[0], playerPosition.zone)
        
    # No position has been found after 10 cells, not theoretically possible
    return playerPosition

def findSlopeDestinationCell(slopePosition):
    # Check for the furthest free cell up the slope 
    if (slopePosition.zone.map[slopePosition.Y - 3][slopePosition.X] == "X"):
        return Position(slopePosition.X, slopePosition.Y - 2, slopePosition.zone)
    elif (slopePosition.zone.map[slopePosition.Y - 4][slopePosition.X] == "X"):
        return Position(slopePosition.X, slopePosition.Y - 3, slopePosition.zone)
    else:
        return Position(slopePosition.X, slopePosition.Y - 4, slopePosition.zone)

def findSlopeMomentumCell(slopePosition):
    zoneMap = slopePosition.zone.map

    # Search for a close free cell to gain momentum in order to go up the slope
    for orientation in [(1,0),(0,-1),(0,1)]: # Down, Left, Right
        if (zoneMap[slopePosition.Y + 1 + orientation[0]][slopePosition.X + orientation[1]] in ["O","G","B"]):
            return Position(slopePosition.X + orientation[1], slopePosition.Y + 1 + orientation[0], slopePosition.zone)

def findRampDestinationCell(rampPosition, orientation):
    # Check for the furthest free cell after jumping from the ramp
    if (rampPosition.zone.map[rampPosition.Y][rampPosition.X + 5 * orientation] == "X"):
        return Position(rampPosition.X + 4 * orientation, rampPosition.Y, rampPosition.zone)
    elif (rampPosition.zone.map[rampPosition.Y][rampPosition.X + 6 * orientation] == "X"):
        return Position(rampPosition.X + 5 * orientation, rampPosition.Y, rampPosition.zone)
    else:
        return Position(rampPosition.X + 6 * orientation, rampPosition.Y, rampPosition.zone)

def generateSlopeNodePath(slopeNode, destinationNode, zoneMap):
        
    slopePath = []
    slopePath.append(slopeNode)
    slopePath.append(Node(slopeNode.bikeSlopeMomentumCell, zoneMap, slopePath[-1])) # Momentum Cell
    slopePath.append(Node(slopeNode.position, zoneMap, slopePath[-1])) # Cell in front of the slope
    
    slopeDestinationId = 1

    # Add nodes until we're at the top
    while (destinationNode.position.Y < slopeNode.position.Y - slopeDestinationId):
        slopePath.append(Node(Position(slopeNode.position.X, slopeNode.position.Y - slopeDestinationId, slopeNode.position.zone), zoneMap, slopePath[-1]))
        slopeDestinationId += 1

    for node in slopePath:
        node.onABikeSlope = True

    destinationNode.onABikeSlope = True
    destinationNode.parent = slopePath[-1]

    return slopePath[::-1]

def areThreeRampCellsFree(zoneMap, currentPosition, orientation):

    # Can only jump bike ramps if facing left or right
    if (orientation[0] == 0):
        # Can only jump bike ramps if we have free side cells to accelerate
        if (orientation[1] == 1):
            return zoneMap[currentPosition.Y][currentPosition.X-2:currentPosition.X+1] == "OOO"
        elif (orientation[1] == -1):
            return zoneMap[currentPosition.Y][currentPosition.X:currentPosition.X+3] == "OOO"
        else:
            return False
    else:
        return False

def generateRampNodePath(rampNode, destinationNode, zoneMap):
        
    rampOrientation = -1 if destinationNode.position.X < rampNode.position.X else 1

    rampPath = []
    rampPath.append(rampNode) # Start on Ramp cell
    rampPath.append(Node(Position(rampNode.position.X - rampOrientation, rampNode.position.Y, rampNode.position.zone), zoneMap, rampPath[-1])) # Go to Momentum Cell

    # Add nodes until we're at the destination cell
    for i in range(-2,6):
        rampPath.append(Node(Position(rampNode.position.X + i * rampOrientation, rampNode.position.Y, rampNode.position.zone), zoneMap, rampPath[-1]))

    for node in rampPath:
        node.onABikeRamp = True

    destinationNode.onABikeRamp = True
    destinationNode.parent = rampPath[-1]

    return rampPath[::-1]

def sortBoulders(boulderList, endPosition):

    # Calculate boulder distance to endPosition
    for boulder in boulderList:
        boulder[1].setDistanceTo(endPosition)

    # Sort by distance to endPosition
    sortedList = sorted(boulderList, key=lambda x: x[1].distance)

    # Specific process for particular boulders that need to be pushed last
    for boulder in PUZZLE_BOULDERS:
        if (boulder in sortedList):
            sortedList.remove(boulder)
            sortedList.append(boulder)

    return sortedList

def removeAllBoulders(zoneMap):
    return [row.replace('b', 'O') for row in zoneMap]

def getMostEfficientPath(start: Position, end: Position, zoneMap, isBelow = None):
    print("Get most effective path from " + str(start) + " to " + str(end) + " (" + zoneMap[end.Y][end.X] + ")")

    if (start.zone != end.zone):
        print("Positions not in the same zone !")
        return None

    # Boulders might block the way, we'll track them and process them if needed
    possiblePath, blockingBoulders = astar(start, end, zoneMap, isBelow)

    # No path found, checking for boulders
    if (not possiblePath and len(blockingBoulders) > 0):

        # First try to check if pushing the boulders is actually worth it
        boulderFreeMap = removeAllBoulders(zoneMap)

        # No point in pushing boulders if no path can be found on a boulder-free map
        if (not astar(start, end, boulderFreeMap, isBelow)[0]):
            # print("No path even without boulders, we definetly can't find a path")
            return None

        # Push the boulders close to endPosition first
        blockingBoulders = sortBoulders(blockingBoulders, end)
        playerPosition = blockingBoulders[0][PLAYER_POSITION]
        boulderPosition = blockingBoulders[0][BOULDER_POSITION]
        bouldersToPush = [(playerPosition, boulderPosition)]
        pushCounter = 0

        # Operations will depend on the player and boulders positions
        xDiff = boulderPosition.X - playerPosition.X
        yDiff = boulderPosition.Y - playerPosition.Y

        # Create a copy of the map since we'll edit it
        newMap = zoneMap[:]

        # Try to push the boulder all the way
        while True:

            # Push the boulder in the direction the player is facing
            updatedBoulder = Position(boulderPosition.X + xDiff, boulderPosition.Y + yDiff, boulderPosition.zone)
            updatedPlayer = Position(playerPosition.X + xDiff, playerPosition.Y + yDiff, playerPosition.zone)
            pushCounter += 1

            # Update the map to take into account the pushed boulder
            updateMapWithPushedBoulders(newMap, boulderPosition, playerPosition)

            # Try to find a way now that the boulder has been pushed
            possiblePath, newBlockingBoulders = astar(playerPosition, end, newMap)

            # A path has been found, return it
            if (possiblePath):
                # print("Found a path after pushing " + str(pushCounter) + " boulders !")

                # Create a new map and update it everytime a boulder is pushed
                newMap = zoneMap[:]

                # Create a path that goes from start to end while pushing all boulders in bouldersToPush
                boulderPath = [Node(start, newMap)]
                previousPosition = start

                for boulder in bouldersToPush:

                    # Go from previous position to boulder pushing position
                    pathToPlayerPosition = astar(previousPosition, boulder[PLAYER_POSITION], newMap)[0]
                    lastNode = pathToPlayerPosition[-1]

                    # Remove start node to link it to the previous path
                    pathToPlayerPosition.pop(0)
                    
                    # Go from boulder pushing position to boulder position while pushing it
                    pushingBoulder = Node(boulder[BOULDER_POSITION], newMap, lastNode)
                    pushingBoulder.pushBoulder = True
                    pathToPlayerPosition.append(pushingBoulder)

                    # Update the map to take into account the pushed boulder
                    updateMapWithPushedBoulders(newMap, boulder[BOULDER_POSITION], boulder[PLAYER_POSITION])

                    # Link subpath to global path
                    boulderPath.extend(pathToPlayerPosition)
                    previousPosition = boulder[BOULDER_POSITION]

                # Go from last boulder to end, remove last boulder node to link it to the previous path
                pathToEnd = astar(previousPosition, end, newMap)[0]
                pathToEnd.pop(0)
                boulderPath.extend(pathToEnd)

                return boulderPath

            # No path has been found but boulder can still be pushed, keep trying
            elif ((updatedPlayer, updatedBoulder) in newBlockingBoulders):
                # print("Still pushing the boulder... " + str(updatedBoulder))
                playerPosition = updatedPlayer
                boulderPosition = updatedBoulder
                bouldersToPush.append((playerPosition, boulderPosition))

            # Boulder has been pushed all the way and still no path found
            # Try another boulder but keep the same map
            elif (len(newBlockingBoulders) > 0):
                # print("Cannot push the boulder anymore, trying another boulder")

                # Push the boulders close to endPosition first
                newBlockingBoulders = sortBoulders(newBlockingBoulders, end)
                playerPosition = newBlockingBoulders[0][PLAYER_POSITION]
                boulderPosition = newBlockingBoulders[0][BOULDER_POSITION]
                bouldersToPush.append((playerPosition, boulderPosition))

                xDiff = boulderPosition.X - playerPosition.X
                yDiff = boulderPosition.Y - playerPosition.Y

            # No boulder left to push and no path found
            else:
                # print("Cannot push the boulder anymore, we definetly can't find a path")
                return None
    else:
        return possiblePath

# Use A* algorithm to find most efficient path
def astar(start: Position, end: Position, zoneMap, isBelow = None):

    # Boulders might block the way, we'll track them and process them if needed
    blockingBoulders = []

    # Cell cost might change if repel is active or if we're on a bike
    repelActive = game.getGameData().repelSteps > 0
    canUseBike = start.zone.canBike

    # Create start and end node
    start_node = Node(start, zoneMap)
    end_node = Node(end, zoneMap)

    # If provided, add isBelow and isAbove status (help to differentiate if starting on a a/A cell) 
    if (isBelow is not None):
        start_node.isBelow = isBelow
        start_node.isAbove = not isBelow

    # Initialize both open and closed list
    open_list = []
    closed_list = []

    # Add the start node
    open_list.append(start_node)

    # Loop until you find the end
    while len(open_list) > 0:

        # Get the node with most efficient path
        current_node = open_list[0]
        current_index = 0
        for index, item in enumerate(open_list):
            if item.f < current_node.f:
                current_node = item
                current_index = index

        # Pop the node off open list, add to closed list
        open_list.pop(current_index)
        closed_list.append(current_node)

        # Found the goal
        if current_node.position == end_node.position:
            path = []
            current = current_node

            # Retrace back the complete path
            while current is not None:

                # Add nodes following a specific path for bike slopes or ramps
                if (current.bikeSlopeDestination and current.bikeSlopeDestination == path[-1].position):
                    path.extend(generateSlopeNodePath(current, path[-1], zoneMap))

                elif (current.bikeRampDestination and current.bikeRampDestination == path[-1].position):
                    path.extend(generateRampNodePath(current, path[-1], zoneMap))

                # Regular node processing
                else:
                    path.append(current)
                
                current = current.parent

            # Return reversed path
            return path[::-1], []
        
        # Generate children
        children = []
        for new_position in DIRECTIONS: # Adjacent squares

            # Get node position
            node_position = Position(current_node.position.X + new_position["orientation"][1],
                                     current_node.position.Y + new_position["orientation"][0],
                                     current_node.position.zone)
            
            nextCellValue = zoneMap[node_position.Y][node_position.X]
            topCellValue = zoneMap[node_position.Y - 1][node_position.X]

            # Can't walk through solid blocks
            if nextCellValue in SOLID_BLOCKS + new_position["solidLedges"]:

                # If the solid block is a boulder and the cell after that is a free cell, we can try pushing the boulder
                if (nextCellValue == "b" and isBoulderPushable(zoneMap,current_node.position,node_position,new_position["orientation"],blockingBoulders)):
                    blockingBoulders.append((current_node.position, node_position))

                # If the solid block is a bike ramp, we might be able to jump 4 cells left or right if we find 3 cells to accelerate
                if (nextCellValue == "v" and areThreeRampCellsFree(zoneMap, current_node.position, new_position["orientation"])):
                    node_position = findRampDestinationCell(current_node.position, new_position["orientation"][1])

                    current_node.bikeRampDestination = node_position
                    nextCellValue = zoneMap[node_position.Y][node_position.X]
                    topCellValue = zoneMap[node_position.Y - 1][node_position.X]

                # Default : don't take the node
                else:
                    continue

            # If on a bridge, don't go on Below cells
            if (current_node.isAbove and nextCellValue in ["B","d"]):
                continue

            # If under a bridge
            if (current_node.isBelow):

                # Only leave by passing on a Below cell (d if surfing, B if not)
                if (current_node.cellType in ["a","A"] and nextCellValue not in ["a","A",("d" if current_node.isSurfing else "B")]):
                    continue

                # Don't go on blocked below cells
                if (current_node.cellType in ["B","d"] and nextCellValue == "@"):
                    continue

            # Don't go up if a sign is just above since it triggers a dialogue
            if (topCellValue == "s" and new_position["orientation"] == (-1, 0)):
                continue
            
            # Go up the slope, teleport up to three cells after the slope
            if (nextCellValue == "V" and new_position["orientation"] == (-1, 0)):

                # Search for specific cells needed to go up the slope
                current_node.bikeSlopeDestination = findSlopeDestinationCell(node_position)
                current_node.bikeSlopeMomentumCell = findSlopeMomentumCell(node_position)
                node_position = current_node.bikeSlopeDestination

            # Rock Climb : teleport to position after climbing
            if (current_node.cellType == "C" and nextCellValue == "C"):
                node_position = getRockClimbEndPosition(zoneMap, current_node.position, new_position["orientation"])

            # We can walk through the block : add node to the children list
            new_node = Node(node_position, zoneMap, current_node)
            children.append(new_node)

        # Loop through children
        for child in children:

            # Child is already in the closed list : don't process it
            if len([closed_child for closed_child in closed_list if closed_child == child]) > 0:
                continue

            # Default cell cost is 999, basically solid block
            cellCost = CELL_COST.get(child.cellType, 999)

            # If surfing, reduce water cells cost and increase the rest
            if (child.parent.isSurfing):
                cellCost += (4 if child.cellType not in ["W","w","d"] else -2)
            
            # If repel is active, reduce encounter cells cost
            if (repelActive):
                cellCost -= (2 if child.cellType in ["W","G","g"] else 0)

            # If biking is possible, increase non-bike cells cost when on a bike cell, and vice-versa
            if (canUseBike):
                if (child.parent.cellType in ["W","S","1","2","3","4","g"]):
                    cellCost += (2 if child.cellType in ["O","G"] else 0)
                else:
                    cellCost += (2 if child.cellType in ["W","S","1","2","3","4","g"] else 0)

            # Create the f, g, and h values (see A* algorith processing for more details)
            child.g = current_node.g + cellCost
            child.h = abs(child.position.Y - end_node.position.Y) + abs(child.position.X - end_node.position.X) # Manhattan distance
            child.f = child.g + child.h

            # Child is already in the open list and a similar or better path exists : don't process it
            if len([open_node for open_node in open_list if child == open_node and child.g >= open_node.g]) > 0:
                continue

            # Add the child to the open list
            open_list.append(child)

    # We reached the end of the loop so no path has been found, maybe boulders are blocking the way
    return None, blockingBoulders


def writePathInputsFromCurrentState(nodeList, breakNodeId):

    # Make sure player is not moving anymore
    memory.clearJoypadInputs() # Clear input
    waitFrames(15) # Wait 15 frames (time needed to completely stop on speed bike)

    # Get final position after player stopped moving
    playerData = player.getPlayerData()

    # If on a bike slope, just wait, we'll slide down eventually
    while (playerData.position.getCell() == "V"):
        waitFrames(1)
        playerData = player.getPlayerData()

    # a/A cells are either above or below a bridge, check the first remaining node to differentiate
    if (playerData.position.getCell() in ["a","A"]):
        isBelow = nodeList[breakNodeId].isBelow
    else:
        isBelow = None

    print("Wrong path ! Start again from " + str(playerData.position))

    # If we need a new path while on a bike slope, start the go-up-the-slope sequence again
    while (breakNodeId >= 0 and nodeList[breakNodeId].onABikeSlope):
        breakNodeId -= 1

    # Split the original nodeList into processed and remaining nodes
    processedNodes = nodeList[:breakNodeId]
    remainingNodes = nodeList[breakNodeId:]

    # Update the map to take into account the pushed boulder and destroyed obstacles
    updatedMap, strengthUsed, destroyedObstacles = getMapAtCurrentState(processedNodes, nodeList[0].position.zone.map)

    # Go from player position to first node of the remaining nodes
    firstNode = remainingNodes.pop(0)
    nodeList = getMostEfficientPath(playerData.position, firstNode.position, updatedMap, isBelow)
    nodeList.extend(remainingNodes)
    print(nodeList)

    # Retrieve all inputs needed to go to specified location
    joypad.writePathfindingInput(nodeList, strengthUsed, destroyedObstacles)

    return nodeList



def goToLocation(location: Position):

    # Calculate path from current position
    playerData = player.getPlayerData()
    playerPosition = playerData.position

    # We only manage pathfinding within the same zone for now
    if (playerPosition.zone.zoneId != location.zone.zoneId):
        return None
    
    # Location is a position, just get path to this location
    path = getMostEfficientPath(playerData.position, location, location.zone.map)

    if (not path):
        print("No path has been found from " + str(playerPosition) + " to " + str(location))
        return None
    
    # Go from starting node to ending node
    processPath(path)
    

def processPath(nodeList):

    # Send all inputs needed to go to specified location to emulator
    joypad.writePathfindingInput(nodeList)
    
    # Make sure the path is followed, correct it if needed
    checkPathIsFollowed(nodeList)


def checkPathIsFollowed(path):

    # We might bump into walls or moving NPCs, ecounter wild Pokémon, etc
    # So we need to make sure the player follows the right path
    #
    # Only stop path processing when all inputs have been pressed and the player is at desired location

    gameData = game.getGameData()
    playerPosition = player.getPlayerData().position

    isRepelActive = (gameData.repelSteps > 0)
    pathIndex = 0

    while memory.readJoypadData() or playerPosition != path[-1].position:

        # Get current game and player data
        gameData = game.getGameData()
        playerPosition = player.getPlayerData().position

        # Non-0 PID : we're in a battle - stop pathfinding and let main script take over
        if (memory.readWildPokemonData().get("pid",0) != 0):
            print("Encountered wild Pokémon")
            memory.clearJoypadInputs() # Clear input
            break

        # Repel no longer active, stop moving and use another one
        elif (isRepelActive and gameData.repelSteps == 0):
            memory.clearJoypadInputs() # Clear input
            joypad.writeInput("@@@@A") # Wait for the dialogue to be displayed and skip it
            action.useRepel() # Use Repel and go back to overworld

        # Reached the end or went to another zone, clear all inputs and go back to main loop
        elif (playerPosition == path[-1].position or playerPosition.zone.zoneId != path[-1].position.zone.zoneId):
            memory.clearJoypadInputs() # Clear input
            break

        # Check character progression through the path
        elif (path[pathIndex].position != playerPosition):

            # Normal behavior : character went to next position
            if (path[pathIndex + 1].position == playerPosition):
                pathIndex += 1

            # Specific case : we don't keep track of Rock Climb positions, false positive
            elif (playerPosition.zone.map[playerPosition.Y][playerPosition.X] == "C"):
                continue

            # Specific case : Waterfall position is skipped, false positive
            elif (path[pathIndex + 1].cellType == "w"):
                pathIndex += 1
                continue

            # Wrong path : recalculate from current position
            else:
                # Calculate path from new position to the rest of the correct path
                path = writePathInputsFromCurrentState(path, pathIndex + 1)
                pathIndex = 0

        # No more inputs left to process
        elif (not memory.readJoypadData()):
            
            # Reached the end, go back to main loop
            if (playerPosition == path[-1].position):
                break
            # Not at the desired location, calculate path from this position to the rest of the correct path
            else:
                path = writePathInputsFromCurrentState(path, pathIndex + 1)
                pathIndex = 0


# Populate DOOR_GRAPH by adding every neighbour to every possible door
def initDoorGraph():

    # Iterate on every single Door
    for zoneObject in zone.ZONELIST:
        for door in zoneObject.doorList:

            # Only process doors connected to another door
            if (not door.connectedDoor):
                continue

            # Create tuple object used as key from the door and its connected door
            doorKey = door.createDoorKey()

            for otherDoorInZone in zoneObject.doorList:

                # Only process the other doors connected to another zone
                if (not otherDoorInZone.connectedDoor or door == otherDoorInZone):
                    continue

                # For complex maps (Mont Couronné + Route Victoire), we're using A* instead of regular position distance
                if (zoneObject in zone.MONTCOURONNE_ZONES or zoneObject in zone.ROUTEVICTOIRE_ZONES):
                    doorPath = getMostEfficientPath(door.connectedDoor.destination, otherDoorInZone.position, otherDoorInZone.position.zone.map)

                    # Only add the door path if there's an actual path
                    if (doorPath):
                        DOOR_GRAPH.setdefault(doorKey, []).append(DoorNode(door, otherDoorInZone, doorPath))

                # Regular maps, we only use distance from door to door
                else:
                    DOOR_GRAPH.setdefault(doorKey, []).append(DoorNode(door, otherDoorInZone))

    # Save graph as a file to easily retrieve it at a later execution
    memory.saveGraph(DOOR_GRAPH, 'src/python/data/pkl/graph.pkl')

def getPathFromGraph(startDoor: Door, endDoor: Door):
    
    # Get shortest door-to-door path between two doors
    path = getShortestDoorPath(startDoor, endDoor)

    # Remove initial door, we're starting from it
    path.pop(0)

    # We're using currentDoor and nextDoorKey to navigate from path to path, starting from start door
    completePath = []
    currentDoor = startDoor
    nextDoorKey = path.pop(0)

    while True:
        # Get all paths from the current door
        possiblePaths = DOOR_GRAPH[currentDoor.createDoorKey()]

        for doorNode in possiblePaths:

            # Search all possible paths until we found a door leading to the next door in the global path
            if (doorNode.fromDoor == currentDoor and doorNode.toDoor in nextDoorKey):

                # Add subpath to global path and continue the process with the next door
                completePath.append(doorNode.path)
                currentDoor = doorNode.toDoor.connectedDoor

                # Keep searching if there are doors left in the path
                if (len(path) > 0):
                    nextDoorKey = path.pop(0)
                else:
                    return completePath
                
                # We found a path from current door to next door, we can skip the rest of the possible paths
                break

            # Not supposed to reach this point, print debug logs for now
            elif (doorNode == possiblePaths[-1]):
                print("\nDidn't find a path from " + str(currentDoor) + " to " + str(nextDoorKey))
                print(*possiblePaths, sep = "\n", end = "\n")
                return None


def getShortestDoorPath(start, end):
    print("Find shortest path from " + str(start) + " to " + str(end))

    # Create keys from doors in order to read in the DOOR_GRAPH
    keyStart = start.createDoorKey()
    keyEnd = end.createDoorKey()

    # Use Dijkstra to retrieve every possible path from starting door
    paths = dijkstra(keyStart)

    # Retrieve the path from end door to starting door
    fullPath = [keyEnd]
    subPath = paths.get(keyEnd, None)

    # Go from door to door
    while subPath is not None:
        fullPath.append(subPath)
        subPath = paths.get(subPath, None)

    # Reverse the full path to get path from start to end
    return fullPath[::-1]

def dijkstra(startingDoor):

    # Map the path/distance from each possible door to the starting door
    path = {}
    visited = {startingDoor: 0}

    # Retrieve every possible door from the doorGraph, we'll remove them once processed
    doors = set(DOOR_GRAPH.keys())
    queue = [(0, startingDoor)]
    
    # We keep searching while there are doors to process
    while doors and queue:

        # Take the closest door in the queue
        current_distance, current_door = heapq.heappop(queue)

        # Door has already been processed or does not exist, take another door
        if current_door not in doors:
            continue

        # We're processing the door, remove them from the set
        doors.remove(current_door)

        # Take every neighbour door
        for door_node in DOOR_GRAPH[current_door]:

            # Retrievei its destination and ts distance to the current door
            neighbor = door_node.toDoor.createDoorKey()
            distance = current_distance + door_node.weight

            # We keep the neighbor if it hasn't ben processed or if the current path is shorter
            if neighbor not in visited or distance < visited[neighbor]:
                
                # We'll check for its neighbors in another iteration
                heapq.heappush(queue, (distance, neighbor))

                # Update the path and distance from starting door
                path[neighbor] = current_door
                visited[neighbor] = distance

    # Once there's no more door to process, return the whole map
    return path