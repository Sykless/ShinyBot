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

            # Ledge
            if (node.cellType in ["L","R","D","U"]):
                frameByFrameInputSequence += (getStartingAnimationInputs(inputButton, playerDirection) # Start moving lag
                                            + 26 * inputButton) # Ledge jump animation
                stopped = False # Start moving
                skipNode = True # Takes two cells to jump so we can skip the second one

            # Rock smash - Cut
            elif (node.cellType in ["r","t"]):

                # Check if the obstacle has already been destroyed
                if (node.position in destroyedObstacles):
                    frameByFrameInputSequence += getFramesToProgressCell(isOnBike, stopped, inputButton, playerDirection) # Move as usual
                    stopped = False # Start moving
                else:
                    # Apply Rock Smash/Cut inputs to destroy obstacle
                    frameByFrameInputSequence += getHmInputs(ROCKSMASH, inputButton)

                    # Start moving again to reach actual cell position
                    frameByFrameInputSequence += getStartingAnimationInputs(inputButton, inputButton)
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
                    frameByFrameInputSequence += getStartingAnimationInputs(inputButton, inputButton)
                
                # Don't have to use HM, just push the boulder
                else:
                    frameByFrameInputSequence += getFramesToProgressCell(isOnBike, stopped, inputButton, playerDirection) # Move as usual

                frameByFrameInputSequence += 35 * "@"  # Boulder being pushed

                # Start moving again to reach actual cell position
                frameByFrameInputSequence += getStartingAnimationInputs(inputButton, inputButton)
                stopped = False

            # Waterfall
            elif (node.cellType == "w"):

                # Going up : need to use Waterfall HM
                if (inputButton == "u"):
                    # Apply Waterfall inputs to start swimming up
                    frameByFrameInputSequence += getHmInputs(WATERFALL, inputButton)

                # Going down : just need to go down and wait for the animation to end
                else:
                    frameByFrameInputSequence += 8 * inputButton + WATERFALL["animation"] * "@"

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
                frameByFrameInputSequence += (getStartingAnimationInputs(inputButton, playerDirection) # Start moving lag
                                              + 20 * "@")       # Release direction mid-animation to completely stop
                
                # Prepare to start moving again
                stopped = True
            
            ### Non-working methods as is ###
            # # Non-Bike-cell when previously on bike
            # elif (isOnBike and not canBike(node)):
            #     frameByFrameInputSequence += (15 * "@"            # Release direction because bonk
            #                                 + 5 * "Y" + 10 * "@") # Get off from bike
                
            #     # Start moving again to reach actual cell position
            #     isOnBike = False
            #     stopped = False
            #     frameByFrameInputSequence += getStartingAnimationInputs(inputButton, inputButton)
            # # Bike-cell when previously not on bike
            # elif (not isOnBike and canBike(node)):
            #     frameByFrameInputSequence += (15 * "@"            # Release direction to stop running
            #                                 + 5 * "Y" + 10 * "@") # Get on the bike
                
            #     # Start moving again to reach actual cell position
            #     isOnBike = True
            #     stopped = False
            #     frameByFrameInputSequence += getStartingAnimationInputs(inputButton, inputButton)

            # Going up a slope/ramp : need to increase bike speed and follow specific nodes
            elif (node.onABikeSlope or node.onABikeRamp):

                # Very first slope/ramp node, prepare variables and start input sequence
                if (node.bikeSlopeDestination or node.bikeRampDestination):
                    bikeCellCounter = 0
                    destination = node.bikeSlopeDestination if node.onABikeSlope else node.bikeRampDestination
                    frameByFrameInputSequence += (getFramesToProgressCell(isOnBike, stopped, inputButton, playerDirection) # Move as usual
                                                    + 10 * "@" # Make sure we stopped
                                                    + 2 * "B") # Increase bike speed (Check speed beforehand)
                # Specific case : if starting in front of the slope, start the process right away
                elif (nodeId == 1):
                    bikeCellCounter = 1
                    destination = previousNode.bikeSlopeDestination if node.onABikeSlope else previousNode.bikeRampDestination
                    frameByFrameInputSequence += 2 * "B" # Increase bike speed (Check speed beforehand)

                # Go to momentum cell to build up speed and go back to slope/ramp with max speed
                if (bikeCellCounter == 1): frameByFrameInputSequence += getStartingAnimationInputs(inputButton, playerDirection)
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
                frameByFrameInputSequence += (getFramesToProgressCell(isOnBike, stopped, inputButton, playerDirection) # Slide down
                                            + 16 * "@") # Let it slide
                
                # The slope is two cells long, we skip the whole slope and directly teleport down
                skipTwoNodes = True

                # Prepare to start moving again
                stopped = True

            # Regular cell
            else:
                # Not on bike and should be : press Y to use bike
                if (canBike(previousNode) and not isOnBike):
                    frameByFrameInputSequence += 5 * "Y" + 10 * "@"
                    isOnBike = True

                frameByFrameInputSequence += getFramesToProgressCell(isOnBike, stopped, inputButton, playerDirection)
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

        # Write input sequence
        memory.writeMemoryData("joypad", frameByFrameInputSequence)


def canBikeOnCell(cellType):
    return cellType not in ["W","w","S","1","2","3","4","g"]

def canBike(node):
    return node.position.zone.canBike and not node.isSurfing and node.cellType not in ["W","w","S","1","2","3","4","g"]

def getFramesToProgressCell(isOnBike, stopped, inputButton, playerDirection):

    # Inputs depends on if we're stopped or not
    if (stopped):
        return getStartingAnimationInputs(inputButton, playerDirection) # Start moving lag
    else:
        return (6 if isOnBike else 8) * inputButton # 8 frames per input during run/swim animation, 6 on a low-speed bike

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
        + 6 * (inputButton != playerDirection) # 6 frames to turn around
        + 6) # 6 frames to start running animation (vary between 3 and 4, take 6 to make sure we don't run late)