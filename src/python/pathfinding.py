from zone import Position
from utils import waitFrames

import img
import zone
import player
import joypad
import memory

# Credits :
# - Python Implementation : https://medium.com/@nicholas.w.swift/easy-a-star-pathfinding-7e6689c7f7b2
# - Improving Heuristics calculation : https://theory.stanford.edu/~amitp/GameProgramming/Heuristics.html

PUZZLE_BOULDERS = [
    (Position(25,16,zone.MONTABRUPT_SALLE1), Position(26,16,zone.MONTABRUPT_SALLE1)),
    (Position(6,31,zone.ROUTEVICTOIRE_SALLEOUEST), Position(6,32,zone.ROUTEVICTOIRE_SALLEOUEST))
]

PLAYER_POSITION = 0
BOULDER_POSITION = 1

CELL_COST = {
    # Traveling cells
    "O": 1, # Regular cell
    "Z": 1, # Zone (door, cave entrance)
    "S": 10, # Swamp
    "1": 2, # 1-depth snow
    "2": 3, # 2-depth snow
    "3": 4, # 3-depth snow
    "4": 5, # 4-depth snow
    "V": 1, # Bike slope
    "G": 3, # Grass
    "g": 5, # Tall grass
    "E": 5, # Elevator
    "e": 5, # Elevator door

    # HM Obstacles
    "t": 5, # Tree
    "r": 5, # Rock
    "W": 5, # Water
    "w": 5, # Waterfall
    "C": 5, # Climb

    # Height-depending cells
    "A": 1, # Above ground (bridge)
    "a": 1, # Above ground (bike bridge)
    "@": 1, # Above solid block (bridge)
    "B": 1, # Below bridge
    "d": 1, # Below bridge on water

    # Orientation-depending cells
    "D": 2, # One-way ledge to go down
    "L": 2, # One-way ledge to go left
    "U": 2, # One-way ledge to go up
    "R": 2, # One-way ledge to go right
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
    {"orientation": (0, -1), "solidLedges": ["D","U","R"]}, # Left
    {"orientation": (0, 1),  "solidLedges": ["D","L","U"]}, # Right
    {"orientation": (-1, 0), "solidLedges": ["D","L","R"]}, # Up
    {"orientation": (1, 0),  "solidLedges": ["L","U","R"]}  # Down
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

        # Special process for bridges since two cells share the same position, see solid blocks processing
        if (parent and parent.isBelow):
            # If you were below a bridge, you're leaving when not on Above or Below cell
            self.isBelow = self.cellType in ["A","a","@","B","d"]
            self.isAbove = False
        else:
            # If you were not, above/below condition just depends on current cell value
            self.isBelow = self.cellType in ["B","d"]
            self.isAbove = self.cellType in ["A","a","@"]

    # Two nodes may share the same position but be above or below a bridge, so we must check those conditions as well
    def __eq__(self, other):
        if isinstance(other, Node):
            return self.position == other.position and self.isBelow == other.isBelow and self.isAbove == other.isAbove
        return False

    def __str__(self):
        return (str(self.position) + " - " + self.cellType 
            + (" (parent = (" + str(self.parent.position.X) + "," + str(self.parent.position.Y) + "))" if self.parent else "")
            + (" PUSH !" if self.pushBoulder else "") + "\n")

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


def getMapAtCurrentState(processedNodes):

    # Check every already processed node for pushed boulders
    if (len(processedNodes) > 0):

        # Retrieve original map from starting position
        originalMap = processedNodes[0].position.zone.map
        updatedMap = originalMap[:]

        # If a boulder has been pushed, update the map accordingly
        for node in processedNodes:
            if (node.pushBoulder): 
                updateMapWithPushedBoulders(updatedMap, node.position, node.parent.position)

        return updatedMap

def areThreeSideCellsFree(zoneMap, currentPosition, orientation):

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

def getMostEfficientPath(start: Position, end: Position, zoneMap):

    print("Get most effective path from " + str(start) + " to " + str(end))

    # Boulders might block the way, we'll track them and process them if needed
    possiblePath, blockingBoulders = astar(start, end, zoneMap)

    # No path found, checking for boulders
    if (not possiblePath and len(blockingBoulders) > 0):
        
        # Push the boulders close to endPosition first
        blockingBoulders = sortBoulders(blockingBoulders, end)
        playerPosition = blockingBoulders[0][PLAYER_POSITION]
        boulderPosition = blockingBoulders[0][BOULDER_POSITION]
        bouldersToPush = [(playerPosition, boulderPosition)]

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

            # Update the map to take into account the pushed boulder
            updateMapWithPushedBoulders(newMap, boulderPosition, playerPosition)

            # Try to find a way now that the boulder has been pushed
            possiblePath, newBlockingBoulders = astar(playerPosition, end, newMap)

            # A path has been found, return it
            if (possiblePath):
                # print("Found a path !\n")

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
                # print("\nCannot push the boulder anymore, trying another boulder")

                # Push the boulders close to endPosition first
                newBlockingBoulders = sortBoulders(newBlockingBoulders, end)
                playerPosition = newBlockingBoulders[0][PLAYER_POSITION]
                boulderPosition = newBlockingBoulders[0][BOULDER_POSITION]
                bouldersToPush.append((playerPosition, boulderPosition))

                xDiff = boulderPosition.X - playerPosition.X
                yDiff = boulderPosition.Y - playerPosition.Y

            # No boulder left to push and no path found
            else:
                print("\nCannot push the boulder anymore, we definetly can't find a path\n")
                return None
    else:
        return possiblePath

# Use A* algorithm to find most efficient path
def astar(start: Position, end: Position, zoneMap):

    # Boulders might block the way, we'll track them and process them if needed
    blockingBoulders = []

    # Create start and end node
    start_node = Node(start, zoneMap)
    end_node = Node(end, zoneMap)

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

                # If the solid block is a bike ramp, we might be able to jump 3 cells left or right if we find 3 cells to accelerate
                if (nextCellValue == "v" and areThreeSideCellsFree(zoneMap, current_node.position, new_position["orientation"])):
                    node_position = Position(current_node.position.X + 4*new_position["orientation"][1],
                                            current_node.position.Y, 
                                            current_node.position.zone)
                    nextCellValue = zoneMap[node_position.Y][node_position.X]
                    topCellValue = zoneMap[node_position.Y - 1][node_position.X]
                else:
                    continue

            # If on a bridge, don't go on Below cells
            if (current_node.isAbove and nextCellValue == "B"):
                continue

            # If under a bridge, only leave by passing on a Below cell
            if (current_node.isBelow and current_node.cellType == "A" and nextCellValue not in ["A","B"]):
                continue

            # Don't go up if a sign is just above since it triggers a dialogue
            if (topCellValue == "S" and new_position["orientation"] == (-1, 0)):
                continue

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

            # Create the f, g, and h values
            child.g = current_node.g + CELL_COST.get(child.cellType, 999) # Default cell cost is 999, basically solid block
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
    memory.clearMemoryData("joypad") # Clear input
    waitFrames(25) # Wait 25 frames (time needed to completely stop on speed bike)

    # Get final position after player stopped moving
    playerData = player.getPlayerData()
    print("Wrong path ! Start again from " + str(playerData.position))

    # Split the original nodeList into processed and remaining nodes
    processedNodes = nodeList[:breakNodeId]
    remainingNodes = nodeList[breakNodeId:]

    # Update the map to take into account the pushed boulder
    updatedMap = getMapAtCurrentState(processedNodes)

    # Go from player position to first node of the remaining nodes
    firstNode = remainingNodes.pop(0)
    nodeList = getMostEfficientPath(playerData.position, firstNode.position, updatedMap)
    nodeList.extend(remainingNodes)
    print(nodeList)

    # Retrieve all inputs needed to go to specified location
    joypad.writePathfindingInput(nodeList, playerData.orientation)

    return nodeList

def writePathInputs(location):

    # Get most effective path from player position to location
    playerData = player.getPlayerData()

    # Location is a position, just get path to this location
    nodeList = getMostEfficientPath(playerData.position, location, location.zone.map)
    print(nodeList)

    # Retrieve all inputs needed to go to specified location
    joypad.writePathfindingInput(nodeList, playerData.orientation)

    return nodeList


def goToLocation(location: Position):

    # Calculate path from current position
    playerPosition = player.getPlayerData().position
    path = writePathInputs(location)

    if (not path):
        print("No path has been found from " + str(playerPosition) + " to " + str(location))
        return None

    pathIndex = 0

    # Unfortunately, the running animation time is not consistent
    # and we might bump into walls or moving NPCs, ecounter wild Pokémon, etc
    # So we need to make sure the player follows the right path
    #
    # Only stop path processing when all inputs have been pressed
    # and the player is at desired location
    while memory.readJoypadData() or playerPosition != path[-1].position:
        playerPosition = player.getPlayerData().position

        # Non-0 PID : we're in a battle - stop pathfinding and let main script take over
        if (memory.readWildPokemonData().get("pid",0) != 0):
            print("Encountered wild Pokémon")
            memory.clearMemoryData("joypad") # Clear input
            break

        # Reached the end, clear all inputs and go back to main loop
        elif (playerPosition == path[-1].position):
            memory.clearMemoryData("joypad") # Clear input
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

    # Stop running after location has been reached
    memory.setMemoryFlag(runFlag = False)