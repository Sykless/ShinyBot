import memory

FRAMES_RELEASE_TIME = 5

ROCKSMASH = {"dialogue": 80, "useDialogue": 40, "animation": 100}
CUT = {"dialogue": 80, "useDialogue": 40, "animation": 100}
SURF = {"dialogue": 70, "useDialogue": 30, "animation": 30}
WATERFALL = {"dialogue": 70, "useDialogue": 35, "animation": 215}

# Frames needed to move 1 cell
# Bike Speed   : 12 -> 8  -> 6  -> 4  -> 4
# Bike Regular : 6  -> 6  -> 6  -> 6  -> 6
# Walk         : 16 -> 16 -> 16 -> 16 -> 16
# Run          : 8  -> 8  -> 8  -> 8  -> 8

def writeRawInput(inputSequence):
    print(inputSequence)
    memory.writeMemoryData("joypad", inputSequence)

def writeInput(inputSequence, endSequence = None):

    frameByFrameInputSequence = "".join(
        [input * FRAMES_RELEASE_TIME # Press button for FRAMES_RELEASE_TIME frames
         + "@" * FRAMES_RELEASE_TIME # Release input for FRAMES_RELEASE_TIME frames
         for input in inputSequence])
    
    if (endSequence):
        frameByFrameInputSequence += endSequence
    
    writeRawInput(frameByFrameInputSequence)

def writePathfindingInput(nodeList, playerDirection):

    # Only move if there are at least two nodes
    if (nodeList is not None and len(nodeList) > 1):

        # Begin the path stopped and at second position
        nodeId = 1
        stopped = True
        skipNode = False
        strengthUsed = False
        destroyedObstacle = []

        previousNode = nodeList[0]
        frameByFrameInputSequence = ""

        while (nodeId < len(nodeList)):
            node = nodeList[nodeId]
            position = node.position

            # Only start moving after the first position
            diffY = position.Y - previousNode.position.Y
            diffX = position.X - previousNode.position.X

            if (diffY > 0):
                inputButton = "d"
            elif (diffY < 0):
                inputButton = "u"
            elif (diffX > 0):
                inputButton = "r"
            elif (diffX < 0):
                inputButton = "l"

            print(position)
            print(node.cellType)
            print()

            # Stopped : apply animation lag
            if (stopped):
                stopped = False # Start moving
                frameByFrameInputSequence += getStartingAnimationInputs(inputButton, playerDirection)

            # Already moving
            else:
                # Ledge
                if (node.cellType in ["L","R","D","U"]):
                    frameByFrameInputSequence += (8 * inputButton # Run animation
                        + 16 * inputButton)                       # Ledge jump animation

                # Rock smash - Cut
                elif (node.cellType in ["r","t"]):

                    # Check if the obstacle has already been destroyed
                    if (node.position in destroyedObstacle):
                        frameByFrameInputSequence += 8 * inputButton # 8 frames per input during run animation
                    else:
                        # Apply Rock Smash/Cut inputs to destroy obstacle
                        frameByFrameInputSequence += getHmInputs(ROCKSMASH, inputButton)

                        # Start moving again to reach actual cell position
                        frameByFrameInputSequence += getStartingAnimationInputs(inputButton, inputButton)

                        # Obstacle is destroyed, we can ignore it if we go through it next time
                        destroyedObstacle.append(node.position)

                # Water when not previously on water
                elif (node.cellType in ["W","d"] and previousNode.cellType not in ["W","w","d"]):
                    # Apply Surf inputs to start surfing
                    frameByFrameInputSequence += getHmInputs(SURF, inputButton)

                    # Start moving again
                    playerDirection = inputButton
                    stopped = True

                # Strength
                elif (node.pushBoulder):

                    if (not strengthUsed):
                        # Apply Strength inputs to gain strength
                        frameByFrameInputSequence += getStrengthInputs(inputButton)
                        strengthUsed = True

                        # Start moving to push the boulder
                        frameByFrameInputSequence += getStartingAnimationInputs(inputButton, inputButton)
                    
                    # Don't have to use HM, just push the boulder
                    else:
                        frameByFrameInputSequence += 8 * inputButton # 8 frames per input during run animation

                    frameByFrameInputSequence += 35 * "@"  # Boulder being pushed

                    # Start moving again to reach actual cell position
                    frameByFrameInputSequence += getStartingAnimationInputs(inputButton, inputButton)

                # Waterfall
                elif (node.cellType == "w"):

                    # Going up : need to use Waterfall HM
                    if (inputButton == "u"):
                        # Apply Waterfall inputs to start swimming up
                        frameByFrameInputSequence += getHmInputs(WATERFALL, inputButton)

                    # Going down : just need to go down and wait for the animation to end
                    else:
                        frameByFrameInputSequence += 8 * inputButton + WATERFALL["animation"] * "@"

                    # Skip next node since we already reached it
                    skipNode = True

                    # Start moving again
                    playerDirection = inputButton
                    stopped = True

                # Rock climb
                elif (node.cellType == "C"):

                    # Calculate distance to rock climb end position
                    position.setDistanceTo(nodeList[nodeId + 1].position)

                    # Rock climb animation depends on the number of rocks climbed
                    rockClimbAnimation = {"dialogue": 70,
                                            "useDialogue": 35,
                                            "animation": 50 + 8*position.distance}
                    
                    # Apply Rock climb inputs to start climbing
                    frameByFrameInputSequence += getHmInputs(rockClimbAnimation, inputButton)

                    # Skip next node since we already reached it
                    skipNode = True

                    # Start moving again
                    playerDirection = inputButton
                    stopped = True

                # Land when previously on water
                elif (node.cellType not in ["W","d"] and previousNode.cellType in ["W","d"]):
                    frameByFrameInputSequence += (10 * inputButton # Jump on the shore animation
                                                 + 10 * "@")       # Release direction mid-animation in case we need to turn
                    
                    # Start moving again
                    playerDirection = inputButton
                    stopped = True

                # Regular cell
                else:
                    frameByFrameInputSequence += 8 * inputButton # 8 frames per input during run/swim animation

            if (skipNode):
                previousNode = nodeList[nodeId + 1]
                nodeId += 2
                skipNode = False
            else:
                previousNode = node
                nodeId += 1

        print(frameByFrameInputSequence)

        # Set run flag to true and write input sequence
        memory.setMemoryFlag(runFlag = True)
        memory.writeMemoryData("joypad", frameByFrameInputSequence)

def getHmInputs(hm, inputButton):
    return  (8 * inputButton       # Face the tree/rock/water/etc
        + 6 * "@"                  # Turning animation
        + 5 * "@"                  # Just for safety
        + 5 * "A"                  # Interact with tree/rock/water/etc
        + hm["dialogue"] * "@"     # Wait for dialogue
        + 5 * "A"                  # Use HM
        + hm["useDialogue"] * "@"  # HM dialogue
        + 5 * "A"                  # Skip dialogue
        + 125 * "@"                # Trainer HM Animation
        + hm["animation"] * "@"    # Actual HM Animation
    )

def getStrengthInputs(inputButton):
    return  (8 * inputButton  # Face the boulder
        + 6 * "@"             # Turning animation
        + 5 * "@"             # Just for safety
        + 5 * "A"             # Interact with boulder
        + 70 * "@"            # Wait for dialogue
        + 5 * "A"             # Skip dialogue
        + 35 * "@"            # Wait for dialogue
        + 5 * "A"             # Use HM
        + 30 * "@"            # HM dialogue
        + 5 * "A"             # Skip dialogue
        + 125 * "@"           # Trainer HM Animation
        + 70 * "@"            # Use HM Dialogue
        + 5 * "A"             # Skip dialogue
    )

def getStartingAnimationInputs(inputButton, playerDirection):
    return inputButton * (
        5   # 5 frames of input lag
        + 6 * (inputButton != playerDirection) # 6 frames to turn around
        + 6 # 6 frames to start run animation
        - 5 # -5 frames to change direction at frame 1 of start animation
    )