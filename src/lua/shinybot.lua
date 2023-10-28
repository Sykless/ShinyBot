dofile "data.lua"
dofile "utils.lua"
dofile "battle.lua"
dofile "memory.lua"
dofile "decryptPokemon.lua"

console.clear()
console.log("\nShinybot started\n")

PLATINUM_ADDRESS = 0x02101F0C
MAGIC_ADDRESS = 0x022DCFA0

NUM_OF_FRAMES_PER_PRESS = 5
RELEASE_TIME = 2 * NUM_OF_FRAMES_PER_PRESS
NUM_OF_POSITIONS = 4

MODULO = NUM_OF_POSITIONS * RELEASE_TIME

UP_FRAMES = fillFramesArray(0)
RIGHT_FRAMES = fillFramesArray(0.25)
DOWN_FRAMES = fillFramesArray(0.5)
LEFT_FRAMES = fillFramesArray(0.75)

FRAMES_TO_WAIT = 16

-- Pokemon object
local pokemon = {}

-- Calculate PID memory addresses needed for data processing
refreshPID()

console.log("pointer : 0x" .. getHexValue(pointer))
console.log("Ally PID address : 0x" .. getHexValue(allyPidAddress))
console.log("Ally PID : 0x" .. getHexValue(memory.read_u32_le(allyPidAddress)))
console.log("Opposing PID address : 0x" .. getHexValue(opposingPidAddress))
console.log("Opposing PID : 0x" .. getHexValue(memory.read_u32_le(opposingPidAddress)))

wildPidValue = memory.read_u32_le(opposingPidAddress)
currentWildPid = wildPidValue

resetBattle()

while true do
    -- Check every second if a new wild Pokemon has been found
    if emu.framecount() % 60 == 0 then
        refreshPID()
        wildPidValue = memory.read_u32_le(opposingPidAddress)
    end

    -- Wild PID = 0 or same as before in the overworld, start spinning
    if (overworld and (wildPidValue == 0 or wildPidValue == currentWildPid)) then
        -- Spin to encounter wild Pokemon
        if UP_FRAMES[emu.framecount() % MODULO] then
            joypad.set({["Up"] = "True"})
        elseif RIGHT_FRAMES[emu.framecount() % MODULO] then
            joypad.set({["Right"] = "True"})
        elseif DOWN_FRAMES[emu.framecount() % MODULO] then
            joypad.set({["Down"] = "True"})
        elseif LEFT_FRAMES[emu.framecount() % MODULO] then
            joypad.set({["Left"] = "True"})
        end

    -- New wild PID while in overworld, new battle, process wild Pokemon data
    elseif (overworld) then
        overworld = false
        framedWaited = 0
        currentWildPid = wildPidValue
        
        console.log("Wild Pokemon !")
        pokemon = decryptPokemonData(opposingPidAddress) -- Get Pokemon encrypted data from PID address
        displayPokemonInfo(pokemon, opposingPidAddress) -- Display Pokemon stats

        shinyPokemon = isShiny(pokemon)

    -- Battle is starting, wait for the magic bit to update
    elseif (memory.read_u32_le(MAGIC_ADDRESS) == 0 and battleStarted == false) then
        -- DO NOTHING

    -- Pokemon have been sent
    elseif (memory.read_u32_le(MAGIC_ADDRESS) ~= 0) then
        battleStarted = true

    elseif (shinyPokemon) then
        -- TODO : CATCH POKEMON

    -- Wait for menu to be displayed then run away
    elseif (memory.read_u32_le(MAGIC_ADDRESS) == 0) then
        framedWaited = framedWaited + 1

        if (framedWaited > FRAMES_TO_WAIT and framedWaited <= FRAMES_TO_WAIT + 5) then
            joypad.set({["Down"] = "True"})
        elseif (framedWaited > FRAMES_TO_WAIT + 10 and framedWaited <= FRAMES_TO_WAIT + 15) then
            joypad.set({["Down"] = "True"})
        elseif (framedWaited > FRAMES_TO_WAIT + 20 and framedWaited <= FRAMES_TO_WAIT + 25) then
            joypad.set({["Right"] = "True"})
        elseif (framedWaited > FRAMES_TO_WAIT + 30 and framedWaited <= FRAMES_TO_WAIT + 35) then
            joypad.set({["A"] = "True"})
        elseif (framedWaited > FRAMES_TO_WAIT + 35) then
            resetBattle()
        end
    end

    -- Next frame
    emu.frameadvance()
end