dofile "data.lua"
dofile "memory.lua"
dofile "findPointer.lua"
dofile "decryptPokemon.lua"

console.clear()
console.log("\nShinybot started\n")

function formatNumber(number)
    if (string.len(number) == 1) then
        return " "..number.." "
    elseif (string.len(number) == 2) then
        return " "..number
    else
        return number
    end
end

function fillFramesArray(directionCoefficient)
    local framesArray = {}

    for i = 0, NUM_OF_FRAMES_PER_PRESS - 1 do
        framesArray[MODULO * directionCoefficient + i] = true
    end

    return framesArray
end

function displayPokemonInfo()
    if pokemon["Move1"] ~= nil then
        console.log(
            pokemon[" Name "] .. " " .. (pokemon["Female"] == "0" and "♀" or "♂")
            .. " level " .. pokemon["Level"] .. " (" .. pokemon["Ability"] .. ")\n"
            .. " - " .. pokemon["Move1"] .. " (" .. pokemon["Move1PP"] .."/".. pokemon["Move1PP"] .. ")\n"
            .. (pokemon["Move2"] and (" - " .. pokemon["Move2"] .. " (" .. pokemon["Move2PP"] .."/".. pokemon["Move2PP"] .. ")\n") or "")
            .. (pokemon["Move3"] and (" - " .. pokemon["Move3"] .. " (" .. pokemon["Move3PP"] .."/".. pokemon["Move3PP"] .. ")\n") or "")
            .. (pokemon["Move4"] and (" - " .. pokemon["Move4"] .. " (" .. pokemon["Move4PP"] .."/".. pokemon["Move4PP"] .. ")\n") or "")
        )

        console.log(
            " =============================================\n"
            .. " =       =  HP = ATQ = DEF = SPA = SPD = SPE =\n"
            .. " =============================================\n"
            .. " = STATS = ".. formatNumber(pokemon["HPMax"]) .." = ".. formatNumber(pokemon["Attack"]) .." = ".. formatNumber(pokemon["Defense"]) .." = ".. formatNumber(pokemon["SpecialAttack"]) .." = ".. formatNumber(pokemon["SpecialDefense"]) .." = ".. formatNumber(pokemon["Speed"]) .." =\n"
            .. " =============================================\n"
            .. " = IV    = ".. formatNumber(pokemon["IV-HP"]) .." = ".. formatNumber(pokemon["IV-ATQ"]) .." = ".. formatNumber(pokemon["IV-DEF"]) .." = ".. formatNumber(pokemon["IV-SPA"]) .." = ".. formatNumber(pokemon["IV-SPD"]) .." = ".. formatNumber(pokemon["IV-SPE"]) .." =\n"
            .. " =============================================\n"
            .. " = EV    = ".. formatNumber(pokemon["EV-HP"]) .." = ".. formatNumber(pokemon["EV-ATQ"]) .." = ".. formatNumber(pokemon["EV-DEF"]) .." = ".. formatNumber(pokemon["EV-SPA"]) .." = ".. formatNumber(pokemon["EV-SPD"]) .." = ".. formatNumber(pokemon["EV-SPE"]) .." =\n"
            .. " =============================================\n"
        )
    else
        console.log("Frère j'ai cherché là j'ai pas trouvé : 0x" .. getHexValue(pidAddress) .. "("..addressToLine(pidAddress)..")")
        console.log(pokemon)
    end
end

function refreshPID()
    -- Pointer : Reference address
    pointer = memory.read_u32_le(platinumAddress) -- 0x2271404

    -- PID : Pokemon unique ID
    allyPidAddress = pointer + 0xD094
    opposingPidAddress = memory.read_u32_le(pointer + 0x352F4) + 0x7A0
end

-- Pokemon object
pokemon = {}

platinumWrongAddress = 0x02101D2C
platinumAddress = 0x02101F0C
refreshPID()

console.log("pointer : 0x" .. getHexValue(pointer))
console.log("Ally PID : 0x" .. getHexValue(memory.read_u32_le(allyPidAddress)))
console.log("Opposing PID : 0x" .. getHexValue(memory.read_u32_le(opposingPidAddress)))

-- Display info of first Pokemon in the team
pidAddress = allyPidAddress -- Select the PID address to use
decryptPokemonData() -- Get Pokemon encrypted data from PID address
displayPokemonInfo() -- Display Pokemon stats

pidAddress = opposingPidAddress
wildPidValue = memory.read_u32_le(opposingPidAddress)

loopPlayer = true

NUM_OF_FRAMES_PER_PRESS = 5
RELEASE_TIME = 2 * NUM_OF_FRAMES_PER_PRESS
NUM_OF_POSITIONS = 4

MODULO = NUM_OF_POSITIONS * RELEASE_TIME

UP_FRAMES = fillFramesArray(0)
RIGHT_FRAMES = fillFramesArray(0.25)
DOWN_FRAMES = fillFramesArray(0.5)
LEFT_FRAMES = fillFramesArray(0.75)

while loopPlayer do
    -- Loop player to encounter wild Pokemon
    if UP_FRAMES[emu.framecount() % MODULO] then
        joypad.set({["Up"] = "True"})
    elseif RIGHT_FRAMES[emu.framecount() % MODULO] then
        joypad.set({["Right"] = "True"})
    elseif DOWN_FRAMES[emu.framecount() % MODULO] then
        joypad.set({["Down"] = "True"})
    elseif LEFT_FRAMES[emu.framecount() % MODULO] then
        joypad.set({["Left"] = "True"})
    end

    -- Check every second if a new wild Pokemon has been found
    if emu.framecount() % 60 == 0 then
        newWildPidValue = memory.read_u32_le(opposingPidAddress)

        if (newWildPidValue ~= 0 and newWildPidValue ~= wildPidValue) then
            console.log("Wild Pokemon !")
            decryptPokemonData() -- Get Pokemon encrypted data from PID address
            displayPokemonInfo() -- Display Pokemon stats

            wildPidValue = newWildPidValue
        end
    end

    -- Next frame
    emu.frameadvance()
end