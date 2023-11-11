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
    "S", # Sign
    "D", # One-way ledge to go down
    "L", # One-way ledge to go left
    "U", # One-way ledge to go up
    "R"  # One-way ledge to go right
]

# Node class for A* Pathfinding
class Node():
    
    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.g = 0
        self.h = 0
        self.f = 0

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
                path.append(current.position)
                current = current.parent
            return path[::-1] # Return reversed path

        # Generate children
        children = []
        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]: # Adjacent squares

            # Get node position
            node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

            # Can't walk through solid blocks
            if maze[node_position[0]][node_position[1]] in SOLID_BLOCKS:
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
            cellValue = maze[childPositionY][childPositionX]

            # Create the f, g, and h values
            child.g = current_node.g + CELL_COST.get(cellValue, 999) # Default cell cost is 999, basically solid block
            child.h = abs(childPositionY - end_node.position[0]) + abs(childPositionX - end_node.position[1]) # Manhattan distance
            child.f = child.g + child.h

            # Child is already in the open list and a similar or better path exists : don't process it
            if len([open_node for open_node in open_list if child.position == open_node.position and child.g >= open_node.g]) > 0:
                continue

            # Add the child to the open list
            open_list.append(child)

def getPathCoordinates(startPosition, endPosition):
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