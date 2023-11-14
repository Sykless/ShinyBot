from position import Position
from utils import waitFrames

import img
import joypad
import memory

# Credits :
# - Python Implementation : https://medium.com/@nicholas.w.swift/easy-a-star-pathfinding-7e6689c7f7b2
# - Improving Heuristics calculation : https://theory.stanford.edu/~amitp/GameProgramming/Heuristics.html

mapFile = open('src/python/data/overworld.map')
PLATINUM_MAP = mapFile.readlines()

CELL_COST = {
    "O": 1, # Regular cell
    "A": 1, # Above ground (bridge)
    "B": 1, # Below bridge
    "Z": 1, # Zone (door, cave entrance)
    "D": 2, # One-way ledge to go down
    "L": 2, # One-way ledge to go left
    "U": 2, # One-way ledge to go up
    "R": 2, # One-way ledge to go right
    "G": 3, # Grass
    "W": 5, # Water
    "t": 5, # Tree
    "r": 5, # Rock
}

SOLID_BLOCKS = [
    "X", # Wall, Tree, etc
    "S", # Sign
    "N"  # NPC
]

DIRECTIONS = [
    {"orientation": (0, -1), "solidLedges": ["D","U","R"]}, # Left
    {"orientation": (0, 1),  "solidLedges": ["D","L","U"]}, # Right
    {"orientation": (-1, 0), "solidLedges": ["D","L","R"]}, # Up
    {"orientation": (1, 0),  "solidLedges": ["L","U","R"]}  # Down
]

# Node class for A* Pathfinding
class Node():
    def __init__(self, maze, position, parent = None):
        self.parent = parent
        self.position = position
        self.cellType = maze[position[0]][position[1]]

        # A* core parameters
        self.g = 0
        self.h = 0
        self.f = 0

        # Special process for bridges since two cells share the same position, see solid blocks processing
        if (parent and parent.isBelow):
            # If you were below a bridge, you're leaving when not on Above or Below cell
            self.isBelow = self.cellType in ["A","B"]
            self.isAbove = False
        else:
            # If you were not, above/below condition just depends on current cell value
            self.isBelow = self.cellType == "B"
            self.isAbove = self.cellType == "A"

    # Two nodes may share the same position but be above or below a bridge, so we must check those conditions as well
    def __eq__(self, other):
        if isinstance(other, Node):
            return self.position == other.position and self.isBelow == other.isBelow and self.isAbove == other.isAbove
        return False

    def __str__(self):
        return (
            "(" + str(self.position[0]) + "," + str(self.position[1]) + ") - " + str(self.f) + " (" + str(self.g) + " + " + str(self.h) + ")"
              + ("" if not self.parent else
              " - parent : (" + str(self.parent.position[0]) + "," + str(self.parent.position[1]) + ") - " + str(self.parent.f) + " (" + str(self.parent.g) + " + " + str(self.parent.h) + ")"))

# Use A* algorithm to find most efficient path
def astar(maze, start, end):

    # Create start and end node
    start_node = Node(maze, start)
    end_node = Node(maze, end)

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
                # Don't add ledge node to the path, we don't walk on the ledge, only go through it
                # The optimal way would be to calculate ledge cells jump animation during input frame calculation
                if (current.cellType not in ["L","U","R","D"]):
                    path.append(current.position)

                current = current.parent

            # Return reversed path
            return path[::-1]
        
        # Generate children
        children = []
        for new_position in DIRECTIONS: # Adjacent squares

            # Get node position
            node_position = (current_node.position[0] + new_position["orientation"][0], current_node.position[1] + new_position["orientation"][1])
            nextCellValue = maze[node_position[0]][node_position[1]]
            topCellValue = maze[node_position[0] - 1][node_position[1]]

            # Can't walk through solid blocks
            if nextCellValue in SOLID_BLOCKS + new_position["solidLedges"]:
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

            # We can walk through the block : add node to the children list
            new_node = Node(maze, node_position, current_node)
            children.append(new_node)

        # Loop through children
        for child in children:

            # Child is already in the closed list : don't process it
            if len([closed_child for closed_child in closed_list if closed_child == child ]) > 0:
                continue

            # Create the f, g, and h values
            child.g = current_node.g + CELL_COST.get(child.cellType, 999) # Default cell cost is 999, basically solid block
            child.h = abs(child.position[0] - end_node.position[0]) + abs(child.position[1] - end_node.position[1]) # Manhattan distance
            child.f = child.g + child.h

            # Child is already in the open list and a similar or better path exists : don't process it
            if len([open_node for open_node in open_list if child == open_node and child.g >= open_node.g]) > 0:
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

        # Non-0 PID : we're in a battle - stop pathfinding and let main script take over
        if (memory.readPokemonData().get("pid",0) != 0):
            print("Not in overworld !")
            memory.clearMemoryData("joypad") # Clear input
            break

        # Check character progression through the path
        elif (path[pathIndex] != (playerPosition.Y, playerPosition.X)):

            # Normal behavior : character went to next position
            if (path[pathIndex + 1] == (playerPosition.Y, playerPosition.X)):
                pathIndex += 1

            # Wrong path : recalculate from current position
            else:
                print("Wrong path !")

                # Make sure player is not moving anymore
                memory.clearMemoryData("joypad") # Clear input
                waitFrames(12) # Wait 12 frames (9 for a full animation cycle + 3 for stop running animation)

                # Calculate new path from new position
                path = writePathInputs(location)
                pathIndex = 0

        # Pressed all inputs : check if we're at desired location
        elif (not memory.readJoypadData()):
            print("Not arrived !")

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