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

def writeRunInput(pathInputSequence, playerDirection):

    if (pathInputSequence):
        # Determine how many frames the first input needs to be pressed
        frameByFrameInputSequence = pathInputSequence[0] * ( 
            5 # 5 frames of input lag
        + 6 * (pathInputSequence[0] != playerDirection) # 6 frames to turn around
        + 6 # 6 frames to start run animation
        - 5 # -5 frames to change direction at frame 1 of start animation
        )

        # Process the rest of the inputs
        for inputButton in pathInputSequence[1:]:
            # 8 frames per input during run animation
            frameByFrameInputSequence += 8 * inputButton

        print(frameByFrameInputSequence)

        # Set run flag to true and write input sequence
        memory.setMemoryFlag(runFlag = True)
        memory.writeMemoryData("joypad", frameByFrameInputSequence)