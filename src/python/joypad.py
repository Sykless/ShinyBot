import player
import memory

FRAMES_RELEASE_TIME = 5

ROCKSMASH = {"dialogue": 80, "useDialogue": 40, "animation": 100}
CUT = {"dialogue": 80, "useDialogue": 40, "animation": 100}
SURF = {"dialogue": 70, "useDialogue": 30, "animation": 30}
WATERFALL = {"dialogue": 70, "useDialogue": 35, "animation": 215}

# Frames needed to move 1 cell
# Bike Speed   : 12 -> 8  -> 6  -> 4  -> 4
# Bike Regular : 6  -> 6  -> 6  -> 6  -> 6
# Run          : 8  -> 8  -> 8  -> 8  -> 8
# Walk         : 16 -> 16 -> 16 -> 16 -> 16

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

def writePathfindingInput(nodeList, playerDirection, strengthUsed = False, destroyedObstacles = []):

    # Only move if there are at least two nodes
    if (nodeList is not None and len(nodeList) > 1):

        # Begin the path stopped and at second node
        nodeId = 1
        stopped = True
        previousNode = nodeList[0]

        # Use bike as much as possible
        playerData = player.getPlayerData()
        isOnBike = playerData.isOnBike
        bikeSpeed = playerData.bikeSpeed

        frameByFrameInputSequence = ""
        skipTwoNodes = False
        skipNode = False

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

            # Stopped : apply starting animation lag
            if (stopped):

                # Not on bike and should be : press Y to use bike
                if (canBike(previousNode) and not isOnBike):
                    frameByFrameInputSequence += 5 * "Y" + 10 * "@"
                    isOnBike = True
                    
                stopped = False # Start moving
                frameByFrameInputSequence += getStartingAnimationInputs(inputButton, playerDirection, isOnBike, bikeSpeed) # Start moving lag
                bikeSpeed = player.LOW_BIKESPEED

            # Already moving
            else:
                # Ledge
                if (node.cellType in ["L","R","D","U"]):
                    frameByFrameInputSequence += (32 * inputButton) # Ledge jump animation
                    skipNode = True # Takes two cells to jump so we can skip the second one

                # Rock smash - Cut
                elif (node.cellType in ["r","t"]):

                    # Check if the obstacle has already been destroyed
                    if (node.position in destroyedObstacles):
                        frameByFrameInputSequence += inputButton * getFramesToProgressCell(isOnBike) # Move as usual
                    else:
                        # Apply Rock Smash/Cut inputs to destroy obstacle
                        frameByFrameInputSequence += getHmInputs(ROCKSMASH, inputButton)

                        # Start moving again to reach actual cell position
                        frameByFrameInputSequence += getStartingAnimationInputs(inputButton, inputButton)

                        # Obstacle is destroyed, we can ignore it if we go through it next time
                        destroyedObstacles.append(node.position)

                # Water when not previously on water
                elif (node.isSurfing and not previousNode.isSurfing):
                    # Apply Surf inputs to start surfing
                    frameByFrameInputSequence += getHmInputs(SURF, inputButton)
                    isOnBike = False

                    # Prepare to start moving again
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
                        frameByFrameInputSequence += inputButton * getFramesToProgressCell(isOnBike) # Move as usual

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

                    # Prepare to start moving again
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

                    # Prepare to start moving again
                    playerDirection = inputButton
                    stopped = True

                # Land when previously on water
                elif (not node.isSurfing and previousNode.isSurfing):
                    frameByFrameInputSequence += (10 * inputButton # Jump on the shore animation
                                                 + 20 * "@")       # Release direction mid-animation to completely stop
                    
                    # Prepare to start moving again
                    playerDirection = inputButton
                    stopped = True
                
                # Non-Bike-cell when previously on bike
                elif (isOnBike and not canBike(node)):
                    frameByFrameInputSequence += (15 * "@"              # Release direction because bonk
                                                  + 5 * "Y" + 10 * "@") # Get off from bike
                    
                    # Start moving again to reach actual cell position
                    isOnBike = False
                    frameByFrameInputSequence += getStartingAnimationInputs(inputButton, inputButton)

                # Bike-cell when previously not on bike
                elif (not isOnBike and canBike(node)):
                    frameByFrameInputSequence += (15 * "@"              # Release direction to stop running
                                                  + 5 * "Y" + 10 * "@") # Get on the bike
                    
                    # Start moving again to reach actual cell position
                    isOnBike = True
                    frameByFrameInputSequence += getStartingAnimationInputs(inputButton, inputButton)

                # Going up a slope : need to increase the bike speed
                elif (node.onABikeSlope):

                    # Very first slope node, prepare variables and start input sequence
                    if (node.bikeSlopeDestination):
                        slopeCounter = -2
                        endSlope = node.position.Y - node.bikeSlopeDestination.Y
                        playerDirection = inputButton
                        frameByFrameInputSequence += (inputButton * getFramesToProgressCell(isOnBike) # Move as usual
                                                      + 10 * "@" # Make sure we stopped
                                                      + 2 * "B") # Increase bike speed (Check speed beforehand)

                    # Go to momentum cell
                    elif (slopeCounter == -1):
                        frameByFrameInputSequence += getStartingAnimationInputs(inputButton, playerDirection)

                    # Go back the other way with high-speed bike slow start animation time (12 frames)
                    elif (slopeCounter == 0):
                        frameByFrameInputSequence += 12 * inputButton

                    # Start going up the slope while accelerating with the high-speed bike (8 frames)
                    elif (slopeCounter == 1):
                        frameByFrameInputSequence += 8 * inputButton

                    # Going up the slope, almost at max speed with the high-speed bike (6 frames)
                    elif (slopeCounter == 2):
                        frameByFrameInputSequence += 6 * inputButton

                    # Almost at the top of the slope, push just a bit harder at max speed with the high-speed bike
                    elif (slopeCounter >= 3):

                        if (slopeCounter == 3):
                            frameByFrameInputSequence += (2 * inputButton
                                                        + 6 * "@") # Start slowing down
                        elif (slopeCounter == 4):
                            frameByFrameInputSequence += 6 * "@"

                        elif (slopeCounter == 5):
                            frameByFrameInputSequence += 10 * "@"

                        # Reached the end of the slope
                        if (endSlope == slopeCounter):
                            frameByFrameInputSequence += 6 * "@" # Make sure we stopped
                        
                            # Prepare to start moving again, but lower bike speed when we actually start again
                            bikeSpeed = player.HIGH_BIKESPEED
                            playerDirection = "u"
                            stopped = True

                    slopeCounter += 1

                # About to go down a bike slope
                elif (node.cellType == "V"):

                    # Going down : just release button and slide down
                    frameByFrameInputSequence += (inputButton * getFramesToProgressCell(isOnBike) # Slide down
                                                + 16 * "@")                                       # Let it slide
                    
                    # The slope is two cells long, we skip the whole slope and directly teleport down
                    skipTwoNodes = True

                    # Prepare to start moving again
                    playerDirection = inputButton
                    stopped = True
 
                # Regular cell
                else:
                    frameByFrameInputSequence += inputButton * getFramesToProgressCell(isOnBike) # Move as usual

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

        # Set run flag to true and write input sequence
        memory.setMemoryFlag(runFlag = False)
        memory.writeMemoryData("joypad", frameByFrameInputSequence)


def canBikeOnCell(cellType):
    return cellType not in ["W","w","S","1","2","3","4","g"]

def canBike(node):
    return node.position.zone.canBike and not node.isSurfing and node.cellType not in ["W","w","S","1","2","3","4","g"]

def getFramesToProgressCell(isOnBike):
    return 6 if isOnBike else 8 # 8 frames per input during run/swim animation, 6 on a low-speed bike

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

def getStartingAnimationInputs(inputButton, playerDirection, isOnBike = False, bikeSpeed = None):

    speedChangingInputs = ""
    turnaroundInputs = inputButton * 6 * (inputButton != playerDirection) # 6 frames to turn around

    # High speed bike is way too sensitive to be used by the bot since you need
    # to turn at exactly frame 1 out of the 4 moving animation frames, and the starting animation is not consistent
    # Since you should always be at Low speed, change speed if currently on High
    if (isOnBike and bikeSpeed == player.HIGH_BIKESPEED):

        # We can actually insert the speed changing inputs in the turnaround inputs to save 2 frames
        if (len(turnaroundInputs) == 6):
            turnaroundInputs = turnaroundInputs[:1] + "BB" + turnaroundInputs[3:]
        else:
            speedChangingInputs = "BB"

    return (
        speedChangingInputs
        + turnaroundInputs
        + 6 * inputButton # 6 frames to start running animation (vary between 3 and 4, take 6 to make sure we started running)
    )