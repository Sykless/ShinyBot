import memory

FRAMES_RELEASE_TIME = 5

def writeInput(inputSequence, endSequence = None):

    frameByFrameInputSequence = "".join(
        [input * FRAMES_RELEASE_TIME # Press button for FRAMES_RELEASE_TIME frames
         + "@" * FRAMES_RELEASE_TIME # Release input for FRAMES_RELEASE_TIME frames
         for input in inputSequence])
    
    if (endSequence):
        frameByFrameInputSequence += endSequence
    
    print(frameByFrameInputSequence)
    memory.writeMemoryData("joypad", frameByFrameInputSequence)

def writePathfindingInput(nodeList, playerDirection):

    # Only move if there are at least two nodes
    if (len(nodeList) > 1):
        for nodeId in range(len(nodeList)):
            node = nodeList[nodeId]
            position = node.position

            # Only start moving after the first position
            if (nodeId > 0):
                diffY = position.Y - previousPosition.Y
                diffX = position.X - previousPosition.X

                if (diffY > 0):
                    inputButton = "d"
                elif (diffY < 0):
                    inputButton = "u"
                elif (diffX > 0):
                    inputButton = "r"
                elif (diffX < 0):
                    inputButton = "l"

                print(node.cellType)

                # First node : apply animation lag
                if (nodeId == 1):
                    frameByFrameInputSequence = inputButton * (
                        5 # 5 frames of input lag
                        + 6 * (inputButton != playerDirection) # 6 frames to turn around
                        + 6 # 6 frames to start run animation
                        - 5 # -5 frames to change direction at frame 1 of start animation
                    )
                else:
                    # Ledge
                    if (node.cellType in ["L","R","D","U"]):
                        frameByFrameInputSequence += 15 * inputButton # Ledge jump animation

                    # 8 frames per input during run animation
                    frameByFrameInputSequence += 8 * inputButton

            previousPosition = position

        print(frameByFrameInputSequence)

        # Set run flag to true and write input sequence
        memory.setMemoryFlag(runFlag = True)
        memory.writeMemoryData("joypad", frameByFrameInputSequence)