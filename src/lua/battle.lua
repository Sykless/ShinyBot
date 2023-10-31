-- opposingPidAddress may vary so we must refresh its value from time to time
function refreshPID()
    -- Pointer : Reference address
    pointer = memory.read_u32_le(PLATINUM_ADDRESS)

    -- PID : Pokemon unique ID
    allyPidAddress = pointer + 0xD094
    opposingPidAddress = memory.read_u32_le(pointer + 0x352F4) + 0x7A0
end

function fillFramesArray(directionCoefficient)
    local framesArray = {}

    for i = 0, NUM_OF_FRAMES_PER_PRESS - 1 do
        framesArray[MODULO * directionCoefficient + i] = true
    end

    return framesArray
end