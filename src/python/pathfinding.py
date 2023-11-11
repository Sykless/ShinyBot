from trainer import Position
from utils import waitFrames

import img
import joypad
import memory

# Credits :
# - Python Implementation : https://medium.com/@nicholas.w.swift/easy-a-star-pathfinding-7e6689c7f7b2
# - Improving Heuristics calculation : https://theory.stanford.edu/~amitp/GameProgramming/Heuristics.html

mapFile = open('src/python/data/platinumMap.map')
PLATINUM_MAP = mapFile.readlines()

CELL_COST = {
    "O": 1, # Regular cell
    "D": 2, # One-way ledge to go down
    "L": 2, # One-way ledge to go left
    "U": 2, # One-way ledge to go up
    "R": 2, # One-way ledge to go right
    "G": 3, # Grass
    "W": 5  # Water
}

SOLID_BLOCKS = [
    "X", # Wall, NPC
    "S"  # Sign
]

DIRECTIONS = [
    {"orientation": (0, -1), "solidLedges": ["D","U","R"]}, # Left
    {"orientation": (0, 1),  "solidLedges": ["D","L","U"]}, # Right
    {"orientation": (-1, 0), "solidLedges": ["D","L","R"]}, # Up
    {"orientation": (1, 0),  "solidLedges": ["L","U","R"]}  # Down
]

# Node class for A* Pathfinding
class Node():
    
    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.g = 0
        self.h = 0
        self.f = 0

        # Special process for ledge nodes since we don't actually step on them
        self.isLedge = False

    def __str__(self):
        return (
            "(" + str(self.position[0]) + "," + str(self.position[1]) + ") - " + str(self.f) + " (" + str(self.g) + " + " + str(self.h) + ")"
              + ("" if not self.parent else
              " - parent : (" + str(self.parent.position[0]) + "," + str(self.parent.position[1]) + ") - " + str(self.parent.f) + " (" + str(self.parent.g) + " + " + str(self.parent.h) + ")"))

# Use A* algorithm to find most efficient path
def astar(maze, start, end):

    # Create start and end node
    start_node = Node(None, start)
    end_node = Node(None, end)

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

            while current is not None:
                # Don't add ledge position to the path, we don't walk on the ledge, only go through it
                # The optimal way would be to process ledge cells during input frame calculation
                if (not current.isLedge):
                    path.append(current.position)

                current = current.parent

            # Return reversed path
            return path[::-1]

        # Generate children
        children = []
        for new_position in DIRECTIONS: # Adjacent squares

            # Get node position
            node_position = (current_node.position[0] + new_position["orientation"][0], current_node.position[1] + new_position["orientation"][1])

            # Can't walk through solid blocks
            if maze[node_position[0]][node_position[1]] in SOLID_BLOCKS + new_position["solidLedges"]:
                continue

            # Don't go up if a sign is just above since it triggers a dialogue
            if (maze[node_position[0] - 1][node_position[1]] == "S" and new_position["orientation"] == (-1, 0)):
                continue

            # We can walk through the block : add node to the children list
            new_node = Node(current_node, node_position)
            children.append(new_node)

        # Loop through children
        for child in children:

            # Child is already in the closed list : don't process it
            if len([closed_child for closed_child in closed_list if closed_child.position == child.position]) > 0:
                continue

            childPositionY = child.position[0]
            childPositionX = child.position[1]
            cellType = maze[childPositionY][childPositionX]

            # Special process for ledge cells, see path processing
            child.isLedge = (cellType in ["L","U","R","D"])

            # Create the f, g, and h values
            child.g = current_node.g + CELL_COST.get(cellType, 999) # Default cell cost is 999, basically solid block
            child.h = abs(childPositionY - end_node.position[0]) + abs(childPositionX - end_node.position[1]) # Manhattan distance
            child.f = child.g + child.h

            # Child is already in the open list and a similar or better path exists : don't process it
            if len([open_node for open_node in open_list if child.position == open_node.position and child.g >= open_node.g]) > 0:
                continue

            # Add the child to the open list
            open_list.append(child)

def getPathCoordinates(startPosition, endPosition):

    # Get most effective path from startPosition to endPosition
    path = astar(PLATINUM_MAP, (startPosition.Y, startPosition.X), (endPosition.Y, endPosition.X))
    pathInputSequence = ""

    # Convert path to joypad inputs
    if (path):
        previousPosition = (startPosition.Y, startPosition.X)

        for position in path:
            diffY = position[0] - previousPosition[0]
            diffX = position[1] - previousPosition[1]

            if (diffY > 0):
                pathInputSequence += "d"
            elif (diffY < 0):
                pathInputSequence += "u"
            elif (diffX > 0):
                pathInputSequence += "r"
            elif (diffX < 0):
                pathInputSequence += "l"

            previousPosition = position

    return path, pathInputSequence

def writePathInputs(location):
    screenshot = img.getScreenshot()
    playerPosition = Position(**memory.readPositionData())
    playerDirection = img.getPlayerPosition(screenshot)

    # Retrieve all inputs needed to go to specified location
    path, pathInputSequence = getPathCoordinates(playerPosition, location)
    joypad.writeRunInput(pathInputSequence, playerDirection)

    return path

def goToLocation(location):

    # Calculate path from current position
    playerPosition = Position(**memory.readPositionData())
    path = writePathInputs(location)
    pathIndex = 0

    # Unfortunately, the running animation time is not consistent
    # and we might bump into moving NPCs
    # So we need to make sure the player follows the right path
    #
    # Only stop path processing when all inputs have been pressed
    # and the player is at desired location
    while memory.readJoypadData() or (playerPosition.Y, playerPosition.X) != path[-1]:
        playerPosition = Position(**memory.readPositionData())

        # Check character progression through the path
        if (path[pathIndex] != (playerPosition.Y, playerPosition.X)):

            # Normal behavior : character went to next position
            if (path[pathIndex + 1] == (playerPosition.Y, playerPosition.X)):
                pathIndex += 1

            # Wrong path : recalculate from current position
            else:

                # Make sure player is not moving anymore
                memory.clearMemoryData("joypad") # Clear input
                waitFrames(12) # Wait 12 frames (9 for a full animation cycle + 3 for stop running animation)

                # Calculate new path from new position
                path = writePathInputs(location)
                pathIndex = 0

        # Pressed all inputs : check if we're at desired location
        elif (not memory.readJoypadData()):

            # Make sure player is not moving anymore
            waitFrames(12) # Wait 12 frames (9 for a full animation cycle + 3 for stop running animation)

            # Get final position after player stopped moving
            playerPosition = Position(**memory.readPositionData())

            # Check if player position is last path position
            if ((playerPosition.Y, playerPosition.X) != path[-1]):

                # Calculate new path from new position
                path = writePathInputs(location)
                pathIndex = 0

    # Stop running after location has been reached
    memory.setMemoryFlag(runFlag = False)