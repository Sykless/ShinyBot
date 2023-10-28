function isShiny(pokemon)
    xorPid = getBits(pokemon["PID"],0,16) ~ getBits(pokemon["PID"],16,16)
    xorOT = pokemon["OT"] ~ pokemon["OTSecretID"]
    shinyValue = xorPid ~ xorOT

    return shinyValue < 255
end

-- Reset battle parameters to overworld values 
function resetBattle()
    framedWaited = 0
    overworld = true
    battleStarted = false
    shinyPokemon = false
end

-- opposingPidAddress may vary so we must refresh its value from time to time
function refreshPID()
    -- Pointer : Reference address
    pointer = memory.read_u32_le(PLATINUM_ADDRESS) -- Is value always 0x2271404 ?
    if (pointer ~= 0x2271404) then
        -- console.log("## UPDATE ##\nPointer is actually 0x" .. getHexValue(pointer))
    end 

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