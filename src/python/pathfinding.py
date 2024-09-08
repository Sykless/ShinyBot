from zone import Door
from zone import DoorKey
from zone import Position
from utils import waitFrames

import time
import heapq

import img
import game
import zone
import action
import player
import joypad
import memory
import pokemon

# Credits for A* algorithm implementation :
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
    "G": 3, # Grass
    "g": 3, # Tall grass
    "1": 1, # 1-depth snow
    "2": 2, # 2-depth snow
    "3": 4, # 3-depth snow
    "4": 8, # 4-depth snow
    "s": 1, # Swamp
    "S": 10, # Deep swamp
    "m": 3, # Marsh (Grass in swamp)
    "M": 12, # Deep marsh (Grass in deep swamp)
    "V": 5, # Bike slope
    "E": 1, # Elevator
    "e": 1, # Elevator door

    # HM Obstacles
    "t": 5, # Tree
    "r": 5, # Rock
    "W": 5, # Water
    "w": 7, # Waterfall
    "C": 1, # Climb

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
    "P", # Post (Special process since it displays a message if coming from the bottom)
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






##################################################################################################
#                                                                                                #
#     Methods responsible of using A* algorithm to find the best path between two positions      #
#                                                                                                #
##################################################################################################

#################################
# Node class for A* Pathfinding #
#################################
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

        ### Special process for bridges since two above/below cells share the same X,Y position, see solid blocks processing ###
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

    def getNodeKey(self):
        return (self.position.X, self.position.Y, self.isAbove)

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


#########################################################################################################
# Find best possible path between two points in the same zone, while trying to push boulders if needeed #
#########################################################################################################
def getMostEfficientPath(start: Position, end: Position, zoneMap = None, isBelow = None, maxCost = None):

    # Log pathfinding calculation time
    startTime = time.time()

    # Default : if not provided, zone map is end position zone map
    if (zoneMap is None):
        zoneMap = end.zone.map

    # A* algorithm only works for positions in the same zone
    if (start.zone != end.zone):
        return None
    
    # Make sure the location is reachable
    if (not zone.checkPositionValidity(start, zoneMap) or not zone.checkPositionValidity(end, zoneMap)):
        return None

    # Boulders might block the way, we'll track them and process them if needed
    possiblePath, blockingBoulders = astar(start, end, zoneMap, isBelow, maxCost)

    # No path found, checking for boulders
    if (not possiblePath and len(blockingBoulders) > 0):

        # First try to check if pushing the boulders is actually worth it
        boulderFreeMap = removeAllBoulders(zoneMap)

        # No point in pushing boulders if no path can be found on a boulder-free map
        if (not astar(start, end, boulderFreeMap, isBelow, maxCost)[0]):
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
            possiblePath, newBlockingBoulders = astar(playerPosition, end, newMap, maxCost = maxCost)

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
                    pathToPlayerPosition = astar(previousPosition, boulder[PLAYER_POSITION], newMap,  maxCost = maxCost)[0]
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
                pathToEnd = astar(previousPosition, end, newMap, maxCost = maxCost)[0]
                pathToEnd.pop(0)
                boulderPath.extend(pathToEnd)

                print("Get most effective path (with boulders) from " + str(start) + " to " + str(end) + " (" + zoneMap[end.Y][end.X] + ") : " + str(round(time.time() - startTime,2)) + " seconds")
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
        print("Get most effective path from " + str(start) + " to " + str(end) + " (" + zoneMap[end.Y][end.X] + ") : " + str(round(time.time() - startTime,2)) + " seconds")
        return possiblePath


#######################################################################################
# Use A* algorithm to find most efficient path between two positions in the same zone #
#######################################################################################
def astar(start: Position, end: Position, zoneMap, isBelow = None, maxCost = None):

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
    open_dict = {}
    closed_dict = {}

    # Add the start node
    open_dict[start_node.getNodeKey()] = start_node

    # Loop until you find the end
    while len(open_dict) > 0:

        # Get the node with most efficient path
        current_key = next(iter(open_dict))
        current_node = open_dict[current_key]

        for key, item in open_dict.items():
            if item.f < current_node.f:
                current_node = item
                current_key = key

        # Pop the node off open list, add to closed list
        open_dict.pop(current_key)
        closed_dict[current_key] = current_node

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

            # Don't go up if a post is just above since it triggers a dialogue
            if (topCellValue == "P" and new_position["orientation"] == (-1, 0)):
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

            # Create the NodeKey item to read inside the closed and open dictionnaries
            childNodeKey = child.getNodeKey()

            # Child is already in the closed_dict : don't process it
            if childNodeKey in closed_dict:
                continue

            # Default cell cost is 999, basically solid block
            cellCost = CELL_COST.get(child.cellType, 999)

            # If surfing, reduce water cells cost and increase the rest
            if (child.parent.isSurfing):
                cellCost += (4 if child.cellType not in ["W","w","d"] else -2)
            
            # If repel is active, reduce encounter cells cost
            if (repelActive):
                cellCost -= (2 if child.cellType in ["W","G","g","m","M"] else 0)

            # If biking is possible, increase non-bike cells cost when on a bike cell, and vice-versa
            if (canUseBike):
                if (child.parent.cellType in ["W","g","s","S","m","M","1","2","3","4"]):
                    cellCost += (2 if child.cellType in ["O","G"] else 0)
                else:
                    cellCost += (2 if child.cellType in ["W","g","s","S","m","M","1","2","3","4"] else 0)

            # Don't add nodes that go above maxCost if provided
            if (maxCost is not None and current_node.g + cellCost > maxCost):
                continue

            # Create the f, g, and h values (see A* algorith processing for more details)
            child.g = current_node.g + cellCost
            child.h = abs(child.position.Y - end_node.position.Y) + abs(child.position.X - end_node.position.X) # Manhattan distance
            child.f = child.g + child.h

            # Child is already in the open list and a similar or better path exists : don't process it
            if childNodeKey in open_dict:
                existing_node = open_dict[childNodeKey]
                if child.g >= existing_node.g:
                    continue

            # Add the child to the open list
            open_dict[childNodeKey] = child

    # We reached the end of the loop so no path has been found, maybe boulders are blocking the way
    return None, blockingBoulders






#########################################################################
#                                                                       #
#     Methods responsible of dealing with obstacles in A* algorithm     #
#                                                                       #
#########################################################################

#####################################################################################
# Retrieve every pushed boulder from processed nodes and update the map accordingly #
#####################################################################################
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


#########################################################
# Update boulder position on the map after being pushed #
#########################################################
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


################################################
# Sort boulder list by distance to destination #
################################################
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


#############################################################################################################
# Boulder is pushable if the cell after that is an empty one, and the boulder hasn't already been processed #
#############################################################################################################
def isBoulderPushable(zoneMap, playerPosition, boulderPosition, orientation, blockingBoulders):
    return (zoneMap[boulderPosition.Y + orientation[0]][boulderPosition.X + orientation[1]] == "O" 
                and (playerPosition, boulderPosition) not in blockingBoulders)


###################################################
# Replace all boulders with free cells on the map #
###################################################
def removeAllBoulders(zoneMap):
    return [row.replace('b', 'O') for row in zoneMap]


#############################################
# Get final position after using Rock Climb #
#############################################
def getRockClimbEndPosition(zoneMap, playerPosition, orientation):
    
    # Try to find the first cell after rock climb
    for i in range(1,11):

        # Found the end position of rock climb
        if (zoneMap[playerPosition.Y + i*orientation[0]][playerPosition.X + i*orientation[1]] != "C"):
            return Position(playerPosition.X + i*orientation[1], playerPosition.Y + i*orientation[0], playerPosition.zone)
        
    # No position has been found after 10 cells, not theoretically possible
    return playerPosition


##################################################
# Get final position after going up a bike slope #
##################################################
def findSlopeDestinationCell(slopePosition):
    # Check for the furthest free cell up the slope 
    if (slopePosition.zone.map[slopePosition.Y - 3][slopePosition.X] == "X"):
        return Position(slopePosition.X, slopePosition.Y - 2, slopePosition.zone)
    elif (slopePosition.zone.map[slopePosition.Y - 4][slopePosition.X] == "X"):
        return Position(slopePosition.X, slopePosition.Y - 3, slopePosition.zone)
    else:
        return Position(slopePosition.X, slopePosition.Y - 4, slopePosition.zone)


################################################################################
# Find cell needed to be reached to gain momentum before going up a bike slope #
################################################################################
def findSlopeMomentumCell(slopePosition):
    zoneMap = slopePosition.zone.map

    # Search for a close free cell to gain momentum in order to go up the slope
    for orientation in [(1,0),(0,-1),(0,1)]: # Down, Left, Right
        if (zoneMap[slopePosition.Y + 1 + orientation[0]][slopePosition.X + orientation[1]] in ["O","G","B"]):
            return Position(slopePosition.X + orientation[1], slopePosition.Y + 1 + orientation[0], slopePosition.zone)


####################################################
# Generate every node needed to go up a bike slope #
####################################################
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


#####################################################
# Get final position after jumping from a bike ramp #
#####################################################
def findRampDestinationCell(rampPosition, orientation):
    # Check for the furthest free cell after jumping from the ramp
    if (rampPosition.zone.map[rampPosition.Y][rampPosition.X + 5 * orientation] == "X"):
        return Position(rampPosition.X + 4 * orientation, rampPosition.Y, rampPosition.zone)
    elif (rampPosition.zone.map[rampPosition.Y][rampPosition.X + 6 * orientation] == "X"):
        return Position(rampPosition.X + 5 * orientation, rampPosition.Y, rampPosition.zone)
    else:
        return Position(rampPosition.X + 6 * orientation, rampPosition.Y, rampPosition.zone)


######################################################################
# Check if there is enough space to gain momentum before a bike ramp #
######################################################################
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


#######################################################
# Generate every node needed to jump from a bike ramp #
#######################################################
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






##########################################################################################################
#                                                                                                        #
#     Methods responsible of exploiting paths generated by A* algorithm and generating input presses     #
#                                                                                                        #
##########################################################################################################

###################################################################
# Generate the best path to go to location and process the inputs #
###################################################################
def goToLocation(location: Position):

    # Calculate path from current position
    playerData = player.getPlayerData()
    playerPosition = playerData.position

    # We only manage pathfinding within the same zone for now
    if (playerPosition.zone.zoneId != location.zone.zoneId):
        return None
    
    # Location is a position, just get path to this location
    path = getMostEfficientPath(playerData.position, location)

    if (not path):
        print("No path has been found from " + str(playerPosition) + " to " + str(location))
        return None
    
    # Go from starting node to ending node
    processPath(path)


######################################################################################################
# Generate every input needed to go through the provided node list and check if the path is followed #
######################################################################################################
def processPath(nodeList):
    print("Going from " + str(nodeList[0]) + " to " + str(nodeList[-1]))

    # Send all inputs needed to go to specified location to emulator
    joypad.writePathfindingInput(nodeList)
    
    # Make sure the path is followed, correct it if needed
    checkPathIsFollowed(nodeList)


##############################################################################
# Make sure the player is following the provided path, and correct if needed #
##############################################################################
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

        # Don't check memory more than once a frame to avoid overloading the CPU
        waitFrames(1)

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

            # We could be at a different position because we're in a different zone, go back to main loop
            elif (path[pathIndex].position.zone != playerPosition.zone):
                break

            # Wrong path : recalculate from current position
            else:
                memory.clearJoypadInputs() # Clear input

                # Make sure player is not moving anymore before starting moving again
                waitFrames(10) # Wait 10 frames (time needed to completely stop on a bike)

                # Calculate path from new position to the rest of the correct path
                path = writePathInputsFromCurrentState(path, pathIndex + 1)
                pathIndex = 0

        # No more inputs left to process
        elif (not memory.readJoypadData()):

            # Make sure player is not moving anymore before checking his position
            waitFrames(10) # Wait 10 frames (time needed to completely stop on a bike)
            playerPosition = player.getPlayerData().position
            screenshot = img.getScreenshot()

            # Poketch not visible, we changed zone, go back to main loop
            if (not img.poketch.isOnScreen(screenshot)):
                break
            # Reached the end, go back to main loop
            elif (playerPosition == path[-1].position):
                break
            # Not at the desired location, calculate path from this position to the rest of the correct path
            else:
                path = writePathInputsFromCurrentState(path, pathIndex + 1)
                pathIndex = 0


##############################################################################################
# Erase inputs and start again from the already processed nodes and the current player state #
##############################################################################################
def writePathInputsFromCurrentState(nodeList, breakNodeId):

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

    # Retrieve all inputs needed to go to specified location
    joypad.writePathfindingInput(nodeList, strengthUsed, destroyedObstacles)

    return nodeList






#########################################################################################################
#                                                                                                       #
#     Methods responsible of using Dijsktra's algorithm to find door-to-door paths across the world     #
#                                                                                                       #
#########################################################################################################

###########################################
# DoorNode class for Dijkstra Pathfinding #
###########################################
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
        return "Weight " + str(self.weight) + " from (" + str(self.fromDoor) + ")\n           to (" + str(self.toDoor) + ")\n"
    
    def __repr__(self):
        return str(self)


########################################################################
# Populate DOOR_GRAPH by adding every neighbour to every possible door #
# Takes around 50 minutes to generate, so we store it in a pkl file    #
########################################################################
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

                # Calculate A* path from each door to its neigbours 
                doorPath = getMostEfficientPath(door.connectedDoor.destination, otherDoorInZone.position)

                # Only add the door path if there's an actual path
                if (doorPath):
                    DOOR_GRAPH.setdefault(doorKey, []).append(DoorNode(door, otherDoorInZone, doorPath))

    # Save graph as a file to easily retrieve it at a later execution
    memory.saveGraph(DOOR_GRAPH, 'src/python/data/pkl/graph.pkl')


###################################################################################
# Retrieve the best possible path from any door to another and process the inputs #
###################################################################################
def goToWorldLocation(location):

    needToDig = False
    playerPosition = player.getPlayerData().position
    flyCity, completePath = generateWorldPath(location)

    # Location is too far from current player position, so we fly to a close city before
    if (flyCity):

        # If we need to fly, we also need to be in a zone that enables it, or at least dig our way out
        if (not playerPosition.zone.canFly):

            # Get out of the zone before using Dig or Fly
            if (not playerPosition.zone.canDig):
                endPosition, pathToExit = findClosestFlyDigZone(playerPosition)
                processWorldPath(pathToExit, endPosition)

                needToDig = not endPosition.zone.canFly

            # We can Dig our way out to go to a zone enabling Fly
            else:
                needToDig = True

            # Still can't Fly but can Dig : use HM
            if (needToDig):
                action.useHM(pokemon.DIG_ID)

        # Use Fly to go to the closest city
        action.useHM(pokemon.FLY_ID, flyCity)

    # Process generated path
    processWorldPath(completePath, location.destination if isinstance(location, Door) else None)


def processWorldPath(worldPath, endPosition):

    completeNodePath = []
    lastDoors = []

    # Each subpath can be either a door-to-door or a node-no-node path
    for subPath in worldPath:

        if (subPath):
            pathList = []
            firstElement = subPath[0]
            
            # Node-to-node path
            if (isinstance(firstElement, Node)):
                pathList = [subPath]

            # Door-to-door path
            elif (isinstance(firstElement, DoorKey)):
                pathList = getPathFromGraph(subPath)

            # Add each door in a list to later retrieve transition time between zones
            for path in pathList:
                lastPosition = path[-1].position
                lastDoors.append(lastPosition.zone.getDoorByPosition(lastPosition))

            completeNodePath += pathList
            
    # Process every subpath between each doors
    for pathId in range(len(completeNodePath)):

        # Process current path
        currentPath = completeNodePath[pathId]

        # Go from starting node to ending node
        processPath(currentPath)

        # Only apply door animation between paths, or if the final position is a door destination
        if (pathId + 1 < len(completeNodePath) or endPosition):

            # Wait until we reach the first position of the next zone
            nextPosition = completeNodePath[pathId + 1][0].position if pathId + 1 < len(completeNodePath) else endPosition
            while (player.getPlayerData().position != nextPosition):
                waitFrames(1)

            # Wait poketch is visible (after transition screen)
            while (not img.poketch.isOnScreen(img.getScreenshot())):
                waitFrames(1)

            # Moving from door to actual end position, wait for walking animation to be over
            print("Wait " + str(lastDoors[pathId].transitionTime) + " frames")
            waitFrames(lastDoors[pathId].transitionTime)


####################################################################
# Generate all nodes lists needed to go from one door to any other #
####################################################################
def getPathFromGraph(doorToDoorPath):
    
    # Cannot find path if there's only one door
    if (len(doorToDoorPath) > 1):
        
        # We're using currentDoorKey and nextDoorKey to navigate from path to path, starting from start door
        completePath = []
        currentDoorKey = doorToDoorPath.pop(0)
        nextDoorKey = doorToDoorPath.pop(0)

        while True:
            # Get all paths from the current door
            possiblePaths = DOOR_GRAPH[currentDoorKey]

            for doorNode in possiblePaths:

                # Search all possible paths until we found a door leading to the next door in the global path
                if (doorNode.fromDoor in currentDoorKey and doorNode.toDoor in nextDoorKey):

                    # Add subpath to global path and continue the process with the next door
                    completePath.append(doorNode.path)
                    currentDoorKey = doorNode.toDoor.connectedDoor.createDoorKey()

                    # Keep searching if there are doors left in the path
                    if (len(doorToDoorPath) > 0):
                        nextDoorKey = doorToDoorPath.pop(0)
                    else:
                        return completePath
                    
                    # We found a path from current door to next door, we can skip the rest of the possible paths
                    break

                # Not supposed to reach this point, print debug logs for now
                elif (doorNode == possiblePaths[-1]):
                    print("\nDidn't find a path from " + str(currentDoorKey) + " to " + str(nextDoorKey))
                    print(*possiblePaths, sep = "\n", end = "\n")
                    return None


#######################################################
# Find best path from a door to another in DOOR_GRAPH #
#######################################################
def getShortestDoorPath(start: Door, end: Door):
    print("Find shortest path from " + str(start) + " to " + str(end))

    # Create keys from doors in order to read in the DOOR_GRAPH
    keyStart = start.createDoorKey()
    
    # Use Dijkstra to retrieve every possible path from starting door
    paths = dijkstra(keyStart)[0]

    # Make the path readable and return it
    return processDijkstraPath(paths, end)


#######################################################################################
# Take paths generated by Dijsktra's and find the one leading to the destination door #
#######################################################################################
def processDijkstraPath(paths, destination):

    # Create key from destination door in order to read in the DOOR_GRAPH
    if isinstance(destination, Door):
        keyEnd = destination.createDoorKey()
    else:
        keyEnd = destination

    # Retrieve the path from end door to starting door
    subPath = paths.get(keyEnd, None)

     # Return None if no path has been found
    if (not subPath):
        return None
    
    # Init fullPath to end position
    fullPath = [keyEnd]
    
    # Go from door to door
    while subPath is not None:
        fullPath.append(subPath)
        subPath = paths.get(subPath, None)

    # Reverse the full path to get path from start to end
    return fullPath[::-1]


########################################################################
# Use Dijsktra's algorithm to find all paths and distances from a door #
########################################################################
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
    return path, visited


################################################################################################
# Path class used by generateWorldPath method to store path data from city or current position #
################################################################################################
class Path():
    def __init__(self):
        self.lastDoorDestination = None # First position the player will be after going through the last door
        self.dijsktraPath = None        # Complete path the player needs to follow from position to last door
        self.dijsktraDistance = 0       # Distance from position to last door
        self.finalPath = None           # Complete path the player needs to follow from last door to reach destination
        self.finalDistance = 0          # Distance from last door to destination


#######################################################################################################
# Choose between flying to a position or directly go to it, and return the complete node-to-node path #
#######################################################################################################
def generateWorldPath(location, skipAllCityProcesses = False):

    # Need to go to a Position but only Door paths are pretermined, find closest Door
    if isinstance(location, Position):
        closestDoor = getClosestDoor(location)
        destination = location

    # Need to go to a Door, just use predetermined paths
    elif isinstance(location, Door):
        closestDoor = location
        destination = location.position

    minDistanceFromCity = 9999
    closestCity = None
    locationDoorKey = closestDoor.createDoorKey()

    # Check every possible city and keep the closest
    for city in zone.CITY_LIST:
        cityDoorKey = city.flyDoor.createDoorKey()

        # Get all possible paths from city
        paths, distances = dijkstra(cityDoorKey)

        # Only search for cities that can actually reach location
        if (locationDoorKey in distances):
            distanceFromLocation = distances[locationDoorKey]

            # Save closest city when distance to location is the lowest
            if (distanceFromLocation < minDistanceFromCity):
                minDistanceFromCity = distanceFromLocation
                distancesFromCity = distances
                pathsFromCity = paths
                closestCity = city

    # We found location's closest city, but there might be a better path from our current position
    playerPosition = player.getPlayerData().position
    playerPath = Path()
    cityPath = Path()
    
    # Generate complete dijsktra path from city to closest door
    cityPath.dijsktraPath = processDijkstraPath(pathsFromCity, locationDoorKey)
    cityPath.dijsktraDistance = minDistanceFromCity
    skipAllCurrentPositionProcesses = False

    # Check if we can reach the location from our current position
    directPathFromCurrentPosition = getMostEfficientPath(playerPosition, destination)

    # Direct path between player and destination
    if (directPathFromCurrentPosition):
        playerPath.finalDistance = directPathFromCurrentPosition[-1].g
        playerPath.dijsktraPath = [directPathFromCurrentPosition]

    # No direct path available from player position, find the nearest door to current position to estimate the distance
    else:
        closestPositionDoor, pathToDoor = getBestPathDoor(playerPosition, closestDoor.createDoorKey())

        # There might be no door from our current position that leads to destination (probably on another island)
        if (not closestPositionDoor):
            print("Can't reach destination from current position, we have to fly")
            skipAllCurrentPositionProcesses = True
    
        # Populate playerPath object by calculating final door, distance to door and distance from door
        if (not skipAllCurrentPositionProcesses):
            getPlayerDistance(playerPath, destination, closestDoor, closestPositionDoor, pathToDoor)

    # Don't fly if the destination or the city is close to our current position
    if (not skipAllCurrentPositionProcesses):

        # If the destination is within 100 cells, directly go to it
        if (playerPath.dijsktraDistance + playerPath.finalDistance < 50):
            print("If the destination is within 50 cells, directly go to it")
            skipAllCityProcesses = True

        # If the city is within 50 cells, don't fly to it
        elif (getMostEfficientPath(playerPosition, closestCity.flyDoor.position, maxCost = 50)):
            print("Don't fly to the closest city if it is within 50 cells")
            skipAllCityProcesses = True


    # Populate cityPath object by calculating final door, distance to door and distance from door
    if (not skipAllCityProcesses and isinstance(location, Position)):
        getCityDistance(cityPath, destination, closestDoor, closestCity, distancesFromCity)
    else:
        cityPath.dijsktraPath = [cityPath.dijsktraPath]

    # Just fly to city if the distance is 0
    if (not skipAllCityProcesses and cityPath.dijsktraDistance + cityPath.finalDistance == 0):
        print("Just fly to city if the distance is 0")
        skipAllCurrentPositionProcesses = True


    # We'll use a distance ratio, fly if the player is too far and bike otherwise
    if (not skipAllCityProcesses and not skipAllCurrentPositionProcesses):
        distanceRatio = (playerPath.dijsktraDistance + playerPath.finalDistance) / (cityPath.dijsktraDistance + cityPath.finalDistance)
        print("(" + str(playerPath.dijsktraDistance) + " + " + str(playerPath.finalDistance) + ") / (" + str(cityPath.dijsktraDistance) + " + " + str(cityPath.finalDistance) + ") = " + str(distanceRatio))

    # Ratio is in favor of flying
    if (not skipAllCityProcesses and (skipAllCurrentPositionProcesses or distanceRatio > 1.2)):
        return closestCity, cityPath.dijsktraPath + ([cityPath.finalPath] if isinstance(location, Position) else [])

    # Ratio is neutral or in favor of direct path, and if neutral we choose the direct path
    else:
        return None, playerPath.dijsktraPath + ([playerPath.finalPath] if isinstance(location, Position) else [])


#############################################################################################################
# Returns last door you need to go through, its distance from the city, and its distance to the destination #
#############################################################################################################
def getCityDistance(cityPath, destination, closestDoor, closestCity, distancesFromCity):

    # Closest door is Pokemon Center door, there's only a direct path to calculate
    if (closestDoor in [closestCity.flyDoor, closestCity.flyDoor.connectedDoor]):
        cityPath.lastDoorDestination = closestDoor.connectedDoor.destination
        cityPath.finalPath = getMostEfficientPath(cityPath.lastDoorDestination, destination)
        cityPath.finalDistance = cityPath.finalPath[-1].g

        # Direct path from outside door : skip dijsktraPath
        if (closestDoor == closestCity.flyDoor):
            cityPath.dijsktraPath = []
            cityPath.dijsktraDistance = 0
        
        # Direct path from inside door : just go through the door
        else:
            cityPath.dijsktraPath = [getMostEfficientPath(closestCity.flyDoor.connectedDoor.destination, closestCity.flyDoor.position)] # Just go up
            cityPath.dijsktraDistance = cityPath.dijsktraPath[0][-1].g # Normally just 1

    # Need to go through at least one door
    else:
        nextDoor = cityPath.dijsktraPath[1][0]
        insideZone = closestCity.flyDoor.destination.zone
        insideDoor = False

        # Check if we're starting from outside or inside door
        if (insideZone in [nextDoor.destination.zone, nextDoor.position.zone]):
            lastSubpathDoor = closestCity.flyDoor
            insideDoor = True
        else:
            lastSubpathDoor = closestCity.flyDoor.connectedDoor

        # Check if any of the doors before closestDoor can reach the destination
        for doorId in range(0, len(cityPath.dijsktraPath)):

            # Check if we can directly reach destination from there
            cityPath.finalPath = getMostEfficientPath(lastSubpathDoor.destination, destination)

            if (cityPath.finalPath):
                break

            # We couldn't find a path from last door, keep following the path
            lastSubpathDoor = getLastDoorInPath(cityPath.dijsktraPath[doorId], cityPath.dijsktraPath[doorId + 1])

        # Update dijsktraPath with the new last door destination
        cityPath.lastDoorDestination = lastSubpathDoor.destination
        cityPath.dijsktraPath = [cityPath.dijsktraPath[:doorId + 1]]
        cityPath.finalDistance = cityPath.finalPath[-1].g 

        # Direct path between city and closestDoor
        if (len(cityPath.dijsktraPath[0]) == 1):
            cityPath.dijsktraPath = [] # Skip dijsktraPath
            cityPath.dijsktraDistance = 0

        # Need to go through doors
        else:
            cityPath.dijsktraDistance = distancesFromCity[cityPath.dijsktraPath[0][-1]]

        # If we're starting from inside, we just need to add the path to actually enter the door
        if (insideDoor):
            cityPath.dijsktraPath = [getMostEfficientPath(closestCity.flyDoor.connectedDoor.destination, closestCity.flyDoor.position)] + cityPath.dijsktraPath # Just go up
            cityPath.dijsktraDistance += cityPath.dijsktraPath[0][-1].g # Normally just 1



###############################################################################################################
# Returns last door you need to go through, its distance from the player, and its distance to the destination #
###############################################################################################################
def getPlayerDistance(playerPath, destination, closestDoor, closestPositionDoor, pathToDoor):

    # We already ruled out direct path to destination, so we have to go through at least one door
    if (closestPositionDoor.connectedDoor == closestDoor):
        playerPath.lastDoorDestination = closestPositionDoor.destination
        playerPath.dijsktraPath = [pathToDoor]
        playerPath.dijsktraDistance = pathToDoor[-1].g
        playerPath.finalPath = getMostEfficientPath(playerPath.lastDoorDestination, destination)
        playerPath.finalDistance = playerPath.finalPath[-1].g

    # Need to go through at least one door
    else:
        # Calculate distance from current position's nearest door to location's nearest door
        paths, distancesFromPlayer = dijkstra(closestPositionDoor.createDoorKey())
        dijsktraPlayerPath = processDijkstraPath(paths, closestDoor.createDoorKey())

        lastSubpathDoor = closestPositionDoor

        # Check if any of the doors before closestDoor can reach the destination
        for doorId in range(0, len(dijsktraPlayerPath)):

            # Check if we can directly reach destination from there
            playerPath.finalPath = getMostEfficientPath(lastSubpathDoor.destination, destination)

            if (playerPath.finalPath):
                break

            # We couldn't find a path from last door, keep following the path
            lastSubpathDoor = getLastDoorInPath(dijsktraPlayerPath[doorId], dijsktraPlayerPath[doorId + 1])

        # Update dijsktraPath with the new last door destination
        dijsktraPlayerPath = dijsktraPlayerPath[:doorId + 1]
        playerPath.lastDoorDestination = lastSubpathDoor.destination
        playerPath.finalDistance = playerPath.finalPath[-1].g

        # Only one door : skip dijsktraPlayerPath
        if (len(dijsktraPlayerPath) == 1):
            playerPath.dijsktraDistance = pathToDoor[-1].g
            playerPath.dijsktraPath = [pathToDoor] + [playerPath.finalPath]

        # Need to go through at least two doors : keep dijsktraPlayerPath
        else:
            playerPath.dijsktraDistance = pathToDoor[-1].g + distancesFromPlayer[lastSubpathDoor.createDoorKey()]
            playerPath.dijsktraPath = [pathToDoor] + [dijsktraPlayerPath] + [playerPath.finalPath]


#############################################
# Find closest door to the desired location #
#############################################
def getClosestDoor(location: Position):

    # Get all doors in the zone and sort them by distance to the desired location
    closestDoors = sorted(location.zone.doorList, key = lambda door: door.position.getDistanceTo(location))
    currentClosestDoor = None
    doorCost = None

    # Retrieve the closest possible door that can actually lead to the location
    for door in closestDoors:

        # Get the path from the nearest door
        doorPath = getMostEfficientPath(door.connectedDoor.destination, location, maxCost = doorCost)

        # If a second path has been found with maxCost on, return it, if not the currentClosestDoor is the better option
        if (currentClosestDoor):
            return door if doorPath else currentClosestDoor

        # First path has been found, since we're most likely between two doors, we'll compare them
        if (doorPath):
            currentClosestDoor = door
            doorCost = doorPath[-1].g

    # Default : maybe there only was one available path, return currentClosestDoor
    return currentClosestDoor


#######################################################################
# Get the closest door to the player that can lead to the destination #
#######################################################################
def getBestPathDoor(playerPosition, destinationDoorKey):

    # Sort doors by distance to destination
    doorListByTrueDistance = []

    # Calculate distance from every door in the zone to destination
    for door in playerPosition.zone.doorList:
        distances = dijkstra(door.createDoorKey())[1]

        if (destinationDoorKey in distances):
             doorListByTrueDistance.append([distances[destinationDoorKey], door])

    # Sort doors by true distance to destination
    closestDoors = sorted(doorListByTrueDistance, key = lambda door: door[0])

    # Retrieve the closest possible door that the player can reach
    for door in closestDoors:

        # Get the path from current position to best door
        doorPath = getMostEfficientPath(playerPosition, door[1].position)

        # Path has been found to a near door, return it
        if (doorPath):
            return door[1], doorPath
        
    return None, None


###########################################################
# Get last position after going from startDoor to endDoor #
###########################################################
def getLastDoorInPath(startDoorKey, endDoorKey):

    # Retrieve every path from the starting door
    possiblePaths = DOOR_GRAPH[startDoorKey]

    # Find its connection to the last door to get the final door
    for doorNode in possiblePaths:
        if (doorNode.fromDoor in startDoorKey and doorNode.toDoor in endDoorKey):
            return doorNode.toDoor
        

#############################################################################################
# Find closest zone to current player position where you can Dig or Fly and return its path #
#############################################################################################
def findClosestFlyDigZone(playerPosition: Position):

    # Find closest door to the player
    closestNeighbourDoors = sorted(playerPosition.zone.doorList, key = lambda door: door.position.getDistanceTo(playerPosition))
    startingDoor = closestNeighbourDoors[0]

    # Get all possible paths from closest door sorted by distance
    paths, distances = dijkstra(startingDoor.createDoorKey())
    closestDoors = sorted(distances.items(), key = lambda distance: distance[1])

    # Find closest door that leads to a zone you can dig or fly
    for doorKey, distance in closestDoors:
        if (doorKey[0].destination.zone.canFly or doorKey[0].destination.zone.canDig):
            endDoor = doorKey[0]
            break

        if (doorKey[1].destination.zone.canFly or doorKey[1].destination.zone.canDig):
            endDoor = doorKey[1]
            break

    # Return complete path
    return endDoor.destination, generateWorldPath(endDoor, skipAllCityProcesses = True)[1]
