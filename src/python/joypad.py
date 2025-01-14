import player
import memory
from utils import waitFrames

FRAMES_RELEASE_TIME = 5
TURNAROUND_ANIMATION = 6

ROCKSMASH = {"dialogue": 80, "useDialogue": 40, "animation": 100}
CUT = {"dialogue": 80, "useDialogue": 40, "animation": 100}
SURF = {"dialogue": 70, "useDialogue": 30, "animation": 30}
WATERFALL = {"dialogue": 70, "useDialogue": 35, "animation": 215}

# Frames needed to move 1 cell
INPUTTIME = {
    "bike" : 6,
    "run" : 8,
    "walk" : 16,
    "snow" : 32,
    "deepsnow" : 64,
}

def writeRawInput(inputSequence):
    print(inputSequence)
    memory.writeMemoryData("joypad", inputSequence)

def writeRunSections(runSectionsString):
    print(runSectionsString)
    memory.writeMemoryData("runSections", runSectionsString)

def writeInput(inputSequence, endSequence = None):

    frameByFrameInputSequence = "".join(
        [input * FRAMES_RELEASE_TIME # Press button for FRAMES_RELEASE_TIME frames
         + "@" * FRAMES_RELEASE_TIME # Release input for FRAMES_RELEASE_TIME frames
         for input in inputSequence])
    
    if (endSequence):
        frameByFrameInputSequence += endSequence
    
    writeRawInput(frameByFrameInputSequence)

def writeInputAndWait(inputSequence, endSequence = None):
    writeInput(inputSequence, endSequence)

    # Exit method when all inputs have been processed
    while (memory.readJoypadData()):
        waitFrames(1)

def writePathfindingInput(nodeList, strengthUsed = False, destroyedObstacles = []):

    # Only move if there are at least two nodes
    if (nodeList is not None and len(nodeList) > 1):

        # Begin the path stopped and at second node
        nodeId = 1
        stopped = True
        previousNode = nodeList[0]

        # Use bike as much as possible
        playerData = player.getPlayerData()
        playerDirection = playerData.orientation
        isOnBike = playerData.isOnBike

        frameByFrameInputSequence = ""
        skipTwoNodes = False
        skipNode = False

        # Not on bike and should be : press Y to use bike
        if (canBike(previousNode) and not isOnBike):
            frameByFrameInputSequence += 5 * "Y" + 10 * "@"
            isOnBike = True

        # High speed bike is way too sensitive to be used by the bot since you need
        # to turn at exactly frame 1 out of the 4 moving animation frames, and the starting animation is not consistent
        # Since you should always be at Low speed, change speed if currently on High
        if (isOnBike and playerData.bikeSpeed == player.HIGH_BIKESPEED):
            frameByFrameInputSequence += "BB"

        runSectionStart = -1 if isOnBike else 0
        runSections = ""

        # Start the path
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

            # Not on bike and should be : press Y to use bike
            if (canBike(previousNode) and not isOnBike):
                frameByFrameInputSequence += 5 * "Y" + 10 * "@"
                isOnBike = True

            # Ledge
            if (node.cellType in ["L","R","D","U"]):
                frameByFrameInputSequence += (getInputsToProgressCell(isOnBike, previousNode.cellType, stopped, inputButton, playerDirection) # Start moving lag
                                            + 26 * inputButton) # Ledge jump animation
                stopped = False # Start moving
                skipNode = True # Takes two cells to jump so we can skip the second one

            # Rock smash - Cut
            elif (node.cellType in ["r","t"]):

                # Check if the obstacle has already been destroyed
                if (node.position in destroyedObstacles):
                    frameByFrameInputSequence += getInputsToProgressCell(isOnBike, previousNode.cellType, stopped, inputButton, playerDirection) # Move as usual
                    stopped = False # Start moving
                else:
                    # Apply Rock Smash/Cut inputs to destroy obstacle
                    frameByFrameInputSequence += getHmInputs(ROCKSMASH, inputButton)

                    # Start moving again to reach actual cell position
                    frameByFrameInputSequence += getInputsToProgressCell(isOnBike, previousNode.cellType, True, inputButton, inputButton)
                    stopped = False

                    # Obstacle is destroyed, we can ignore it if we go through it next time
                    destroyedObstacles.append(node.position)

            # Water when not previously on water
            elif (node.isSurfing and not previousNode.isSurfing):
                # Apply Surf inputs to start surfing
                frameByFrameInputSequence += getHmInputs(SURF, inputButton)
                isOnBike = False

                # Prepare to start moving again
                stopped = True

            # Strength
            elif (node.pushBoulder):

                if (not strengthUsed):
                    # Apply Strength inputs to gain strength
                    frameByFrameInputSequence += getStrengthInputs(inputButton)
                    strengthUsed = True

                    # Start moving to push the boulder
                    frameByFrameInputSequence += getInputsToProgressCell(isOnBike, previousNode.cellType, True, inputButton, inputButton)
                
                # Don't have to use HM, just push the boulder
                else:
                    frameByFrameInputSequence += getInputsToProgressCell(isOnBike, previousNode.cellType, stopped, inputButton, playerDirection) # Move as usual

                frameByFrameInputSequence += 35 * "@"  # Boulder being pushed

                # Start moving again to reach actual cell position
                frameByFrameInputSequence += getInputsToProgressCell(isOnBike, previousNode.cellType, stopped, inputButton, inputButton)
                stopped = False

            # Waterfall
            elif (node.cellType == "w"):

                # Going up : need to use Waterfall HM
                if (inputButton == "u"):
                    # Apply Waterfall inputs to start swimming up
                    frameByFrameInputSequence += getHmInputs(WATERFALL, inputButton)

                # Going down : just need to go down and wait for the animation to end
                else:
                    frameByFrameInputSequence += INPUTTIME["run"] * inputButton + WATERFALL["animation"] * "@"

                skipNode = True # Skip next node since we already reached it
                stopped = True # Prepare to start moving again

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

                skipNode = True # Skip next node since we already reached it
                stopped = True # Prepare to start moving again

            # Land when previously on water
            elif (not node.isSurfing and previousNode.isSurfing):
                frameByFrameInputSequence += (getInputsToProgressCell(isOnBike, previousNode.cellType, stopped, inputButton, playerDirection) # Start moving lag
                                              + 20 * "@")       # Release direction mid-animation to completely stop
                
                # Prepare to start moving again
                stopped = True

            # Going up a slope/ramp : need to increase bike speed and follow specific nodes
            elif (node.onABikeSlope or node.onABikeRamp):

                # Very first slope/ramp node, prepare variables and start input sequence
                if (node.bikeSlopeDestination or node.bikeRampDestination):
                    
                    # If we're not on bike, stop running
                    if (not isOnBike):
                        runSections += ("/" if runSections else "") + str(runSectionStart) + "-" + str(len(frameByFrameInputSequence))
                        runSectionStart = -1

                    bikeCellCounter = 0
                    destination = node.bikeSlopeDestination if node.onABikeSlope else node.bikeRampDestination
                    frameByFrameInputSequence += (getInputsToProgressCell(isOnBike, previousNode.cellType, stopped, inputButton, playerDirection) # Move as usual
                                                    + 10 * "@" # Make sure we stopped
                                                    + (5 * "@" + 5 * "Y" + 10 * "@" if not isOnBike else "")
                                                    + 2 * "B") # Increase bike speed
                    isOnBike = True

                # Specific case : if starting in front of the slope, start the process right away
                elif (nodeId == 1):
                    bikeCellCounter = 1
                    destination = previousNode.bikeSlopeDestination if node.onABikeSlope else previousNode.bikeRampDestination
                    
                    # Increase speed if we didn't already
                    if (frameByFrameInputSequence[-2:] == "BB"):
                        frameByFrameInputSequence = frameByFrameInputSequence[:-2] # Stay on high speed
                    else:
                        frameByFrameInputSequence += "BB" # Increase bike speed

                # Go to momentum cell to build up speed and go back to slope/ramp with max speed
                if (bikeCellCounter == 1): frameByFrameInputSequence += getInputsToProgressCell(isOnBike, previousNode.cellType, True, inputButton, playerDirection)
                elif (bikeCellCounter == 2): frameByFrameInputSequence += 12 * inputButton
                elif (bikeCellCounter == 3): frameByFrameInputSequence += 8 * inputButton
                elif (bikeCellCounter == 4): frameByFrameInputSequence += 6 * inputButton
                elif (bikeCellCounter == 5): frameByFrameInputSequence += 2 * inputButton + 2 * "@" # Start slowing down

                # Top of the slope/ramp
                if (bikeCellCounter >= 5):

                    # Speed is gradually building down
                    if (bikeCellCounter == 5): frameByFrameInputSequence += (4 if node.onABikeSlope else 8) * "@"
                    elif (bikeCellCounter == 6): frameByFrameInputSequence += (6 if node.onABikeSlope else 8) * "@"
                    elif (bikeCellCounter == 7): frameByFrameInputSequence += (10 if node.onABikeSlope else 8) * "@"
                    elif (bikeCellCounter == 8 and node.onABikeRamp): frameByFrameInputSequence += 6 * "@"
                    elif (bikeCellCounter == 9 and node.onABikeRamp): frameByFrameInputSequence += 10 * "@"

                    # Reached the end of the path
                    if (node.position == destination):
                        frameByFrameInputSequence += (6 * "@" # Make sure we stopped
                                                      + 2 * "B") # Go back to slow speed
                    
                        # Prepare to start moving again
                        stopped = True

                bikeCellCounter += 1

            # About to go down a bike slope
            elif (node.cellType == "V"):

                # Going down : just release button and slide down
                frameByFrameInputSequence += (getInputsToProgressCell(isOnBike, previousNode.cellType, stopped, inputButton, playerDirection) # Slide down
                                            + 16 * "@") # Let it slide
                
                # The slope is two cells long, we skip the whole slope and directly teleport down
                skipTwoNodes = True

                # Prepare to start moving again
                stopped = True

            # Non-Bike-cell when previously on bike
            elif (isOnBike and not canBike(node)):

                # Stop biking before reaching the cell, then start running
                frameByFrameInputSequence += (12 * "@"            # Release direction to stop moving
                                            + 5 * "Y" + 10 * "@") # Get off the bike
                runSectionStart = len(frameByFrameInputSequence)
                
                # Start moving again to reach actual cell position
                isOnBike = False
                frameByFrameInputSequence += getInputsToProgressCell(isOnBike, previousNode.cellType, True, inputButton, playerDirection)
                stopped = False

            # Bike-cell when previously not on bike
            elif (not isOnBike and canBike(node)):

                # Reach the bike cell
                frameByFrameInputSequence += getInputsToProgressCell(isOnBike, previousNode.cellType, stopped, inputButton, playerDirection)

                # Stop running and use bike
                runSections += ("/" if runSections else "") + str(runSectionStart) + "-" + str(len(frameByFrameInputSequence))
                runSectionStart = -1
                frameByFrameInputSequence += (12 * "@"            # Release direction to stop running
                                            + 5 * "Y" + 10 * "@") # Get on the bike
                
                # Start moving again to reach actual cell position
                isOnBike = True
                stopped = True

            # Regular cell
            else:
                frameByFrameInputSequence += getInputsToProgressCell(isOnBike, previousNode.cellType, stopped, inputButton, playerDirection)
                stopped = False # Start moving

            # New direction is the input we pressed to get there
            playerDirection = inputButton

            if (skipNode):
                previousNode = nodeList[nodeId + 1]
                nodeId += 2
                skipNode = False
            elif (skipTwoNodes):
                previousNode = nodeList[nodeId + 2]
                nodeId += 3
                skipTwoNodes = False
            else:
                previousNode = node
                nodeId += 1

        print(frameByFrameInputSequence)

        if (runSectionStart != -1):
            runSections += ("/" if runSections else "") + str(runSectionStart) + "-" + str(len(frameByFrameInputSequence))

        # Write input sequence
        memory.writeMemoryData("joypad", frameByFrameInputSequence)
        writeRunSections(runSections)


def canBikeOnCell(cellType):
    return cellType not in ["W","w","S","s","m","M","1","2","3","4","g"]

def canBike(node):
    return node.position.zone.canBike and canBikeOnCell(node.cellType) and not node.isSurfing

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

# Inputs are only read every two frames, so you have a 50% chance that the first input frame is not read
# There's a 3-frame animation lag when you start moving, however with the 50% chance, it might take 4
#
# Also, when you press a button during the time needed to move to the next cell, you actually go beyond it
# You need to stop pressing the input at a certain threshold, or else you'll go too far
# The threshold is the number of frames per cell - 2
#
# With all that in mind, to apply the input needed to start moving, you need to apply input for the longest time possible,
# But never for too long to not go beyond the wanted cell
# So the max starting input time = 3 (lowest animation lag) + threshold - 1 (to not cross it)
#                                = 3 + number of frames to go to a cell - 2 - 1
#                                = number of frames to go to a cell

def getInputsToProgressCell(isOnBike, cellType, stopped, inputButton, playerDirection):
    return inputButton * (
        getInputTime(isOnBike, cellType) # Number of frames depend on the type of cell you're on
        + TURNAROUND_ANIMATION * (stopped and inputButton != playerDirection)) # If you're stopped, there's a 6-frame animation to turn around

def getInputTime(isOnBike, cellType):
    # Low-speed bike
    if (isOnBike):
        return INPUTTIME["bike"]
    
    # Snow cells
    elif (cellType == "2"):
        return INPUTTIME["walk"]
    elif (cellType == "3"):
        return INPUTTIME["snow"]
    elif (cellType == "4"):
        return INPUTTIME["deepsnow"]
    
    # If you're not in a bike nor on a snow cell, you're running (surfing is the same as running)
    else:
        return INPUTTIME["run"]